"""AkShare provider adapters for mainland China A-share equities."""

from __future__ import annotations

import importlib
import math
import time
from collections.abc import Mapping
from datetime import date, timedelta
from typing import Any

import pandas as pd

from src.providers.base import (
    CompanyProfileResolver,
    FinancialStatementsProvider,
    MarketDataProvider,
    PeerMultiplesProvider,
    SharesOutstandingProvider,
)
from src.providers.errors import ProviderConfigurationError, ProviderDataError
from src.shared.schemas import (
    CompanyProfile,
    FinancialStatementRecord,
    MarketDataPoint,
    PeerMultipleRecord,
    SharesOutstandingRecord,
)

INCOME_STATEMENT_LABELS = {
    "revenue": ["营业总收入", "营业收入"],
    "gross_profit": ["营业毛利", "毛利润"],
    "operating_cost": ["营业成本"],
    "ebitda": ["息税折旧摊销前利润", "EBITDA"],
    "operating_income": ["营业利润"],
    "net_income": ["净利润", "归属于母公司股东的净利润"],
    "interest_expense": ["利息支出", "减:利息支出", "减：利息支出", "其中:利息费用", "其中：利息费用"],
}

BALANCE_SHEET_LABELS = {
    "total_assets": ["资产总计"],
    "total_equity": ["所有者权益(或股东权益)合计", "股东权益合计", "归属于母公司股东权益合计", "归属于母公司股东权益"],
    "current_assets": ["流动资产合计"],
    "current_liabilities": ["流动负债合计"],
    "cash_and_equivalents": ["货币资金", "现金及存放中央银行款项", "现金及现金等价物余额"],
    "accounts_receivable": ["应收账款", "应收票据及应收账款", "应收账款及应收票据"],
    "inventory": ["存货"],
}

DEBT_COMPONENT_LABELS = [
    "短期借款",
    "一年内到期的非流动负债",
    "长期借款",
    "应付债券",
    "租赁负债",
    "长期应付款",
    "长期借款及应付债券",
]

CASH_FLOW_LABELS = {
    "operating_cash_flow": ["经营活动产生的现金流量净额"],
    "capital_expenditures": ["购建固定资产、无形资产和其他长期资产支付的现金", "购建固定资产、无形资产和其他长期资产所支付的现金"],
}

CURRENT_SHARE_ITEM = "总股本"
SHARE_COUNT_UNIT_MULTIPLIER = 10000.0


class AkShareAStockFinancialStatementsProvider(FinancialStatementsProvider):
    """Fetch annual A-share financial statements via AkShare."""

    def __init__(self, akshare_module: Any | None = None) -> None:
        self._ak = akshare_module or _load_akshare_module()

    def get_annual_financial_statements(
        self,
        company: CompanyProfile,
    ) -> list[FinancialStatementRecord]:
        symbol = _normalize_ashare_symbol(company.ticker)
        sina_symbol = _to_sina_symbol(symbol)
        currency = company.reporting_currency or "CNY"

        income_frame = _call_with_retry(self._ak.stock_financial_report_sina, stock=sina_symbol, symbol="利润表")
        balance_frame = _call_with_retry(self._ak.stock_financial_report_sina, stock=sina_symbol, symbol="资产负债表")
        cashflow_frame = _call_with_retry(self._ak.stock_financial_report_sina, stock=sina_symbol, symbol="现金流量表")

        records: list[FinancialStatementRecord] = []
        records.extend(_build_income_statement_records(income_frame, currency))
        records.extend(_build_balance_sheet_records(balance_frame, currency))
        records.extend(_build_cash_flow_records(cashflow_frame, currency))

        if not records:
            raise ProviderDataError(f"AkShare did not return annual financial statements for {company.ticker}.")
        return records


class AkShareAStockMarketDataProvider(MarketDataProvider):
    """Fetch A-share historical price data via AkShare."""

    def __init__(self, akshare_module: Any | None = None) -> None:
        self._ak = akshare_module or _load_akshare_module()

    def get_historical_prices(self, company: CompanyProfile) -> list[MarketDataPoint]:
        symbol = _normalize_ashare_symbol(company.ticker)
        end_date = date.today()
        start_date = end_date - timedelta(days=120)
        frame = _call_with_retry(self._ak.stock_zh_a_hist,
            symbol=symbol,
            period="daily",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            adjust="",
        )
        if frame is None or frame.empty:
            raise ProviderDataError(f"AkShare did not return market data for {company.ticker}.")

        result: list[MarketDataPoint] = []
        for _, row in frame.sort_values("日期").iterrows():
            result.append(
                MarketDataPoint(
                    date=pd.Timestamp(row["日期"]).date(),
                    close=float(row["收盘"]),
                    volume=_float_or_none(row.get("成交量")),
                    currency="CNY",
                )
            )
        return result


class AkShareAStockSharesOutstandingProvider(SharesOutstandingProvider):
    """Fetch A-share share-capital history via AkShare."""

    def __init__(self, akshare_module: Any | None = None) -> None:
        self._ak = akshare_module or _load_akshare_module()

    def get_shares_outstanding(self, company: CompanyProfile) -> list[SharesOutstandingRecord]:
        symbol = _normalize_ashare_symbol(company.ticker)
        frame = _call_with_retry(self._ak.stock_share_change_cninfo,
            symbol=symbol,
            start_date="20150101",
            end_date=date.today().strftime("%Y%m%d"),
        )

        records: list[SharesOutstandingRecord] = []
        if frame is not None and not frame.empty and {"变动日期", "总股本"}.issubset(frame.columns):
            prepared = frame[["变动日期", "总股本"]].copy()
            prepared["变动日期"] = pd.to_datetime(prepared["变动日期"], errors="coerce")
            prepared["总股本"] = pd.to_numeric(prepared["总股本"], errors="coerce")
            prepared = prepared.dropna(subset=["变动日期", "总股本"]).sort_values("变动日期")
            if not prepared.empty:
                annual = prepared.groupby(prepared["变动日期"].dt.year).tail(1)
                for _, row in annual.iterrows():
                    records.append(
                        SharesOutstandingRecord(
                            date=pd.Timestamp(row["变动日期"]).date(),
                            shares_outstanding=float(row["总股本"]) * SHARE_COUNT_UNIT_MULTIPLIER,
                        )
                    )

        if records:
            return records

        info_frame = _call_with_retry(self._ak.stock_individual_info_em, symbol=symbol)
        info_map = _item_value_map(info_frame)
        current_shares = _float_or_none(info_map.get(CURRENT_SHARE_ITEM))
        if current_shares is None:
            raise ProviderDataError(f"AkShare did not return shares outstanding for {company.ticker}.")
        return [
            SharesOutstandingRecord(
                date=date.today(),
                shares_outstanding=current_shares * SHARE_COUNT_UNIT_MULTIPLIER,
            )
        ]


class AkShareAStockPeerMultiplesProvider(PeerMultiplesProvider):
    """Fetch peer valuation multiples for mainland A-shares via AkShare."""

    def __init__(self, akshare_module: Any | None = None) -> None:
        self._ak = akshare_module or _load_akshare_module()
        self._spot_cache: pd.DataFrame | None = None
        self._financial_snapshot_cache: dict[str, dict[str, float | None]] = {}

    def get_peer_multiples(self, company: CompanyProfile) -> list[PeerMultipleRecord]:
        if not company.peer_list:
            return []

        spot_frame = self._get_spot_frame()
        results: list[PeerMultipleRecord] = []
        for peer in company.peer_list:
            try:
                symbol = _normalize_ashare_symbol(peer)
            except ProviderDataError:
                continue

            match = spot_frame.loc[spot_frame["代码"] == symbol]
            if match.empty:
                continue
            spot_row = match.iloc[0]
            snapshot = self._get_financial_snapshot(symbol)

            market_cap = _float_or_none(spot_row.get("总市值"))
            revenue = snapshot.get("revenue")
            ebitda = snapshot.get("ebitda")
            total_debt = snapshot.get("total_debt")
            cash = snapshot.get("cash_and_equivalents")
            enterprise_value = None
            if market_cap is not None:
                enterprise_value = market_cap
                if total_debt is not None:
                    enterprise_value += total_debt
                if cash is not None:
                    enterprise_value -= cash

            results.append(
                PeerMultipleRecord(
                    ticker=symbol,
                    pe=_float_or_none(spot_row.get("市盈率-动态")),
                    pb=_float_or_none(spot_row.get("市净率")),
                    ev_to_ebitda=_safe_ratio(enterprise_value, ebitda),
                    ev_to_sales=_safe_ratio(enterprise_value, revenue),
                )
            )
        return results

    def _get_spot_frame(self) -> pd.DataFrame:
        if self._spot_cache is None:
            frame = _call_with_retry(self._ak.stock_zh_a_spot_em)
            if frame is None or frame.empty:
                raise ProviderDataError("AkShare did not return A-share spot data for peer multiple analysis.")
            self._spot_cache = frame.copy()
            self._spot_cache["代码"] = self._spot_cache["代码"].astype(str).str.zfill(6)
        return self._spot_cache

    def _get_financial_snapshot(self, symbol: str) -> dict[str, float | None]:
        if symbol not in self._financial_snapshot_cache:
            sina_symbol = _to_sina_symbol(symbol)
            income_frame = _call_with_retry(self._ak.stock_financial_report_sina, stock=sina_symbol, symbol="利润表")
            balance_frame = _call_with_retry(self._ak.stock_financial_report_sina, stock=sina_symbol, symbol="资产负债表")
            latest_income = _latest_annual_row(income_frame)
            latest_balance = _latest_annual_row(balance_frame)
            operating_income = _coalesce_numeric(latest_income, INCOME_STATEMENT_LABELS["operating_income"])
            ebitda = _coalesce_numeric(latest_income, INCOME_STATEMENT_LABELS["ebitda"])
            if ebitda is None:
                ebitda = operating_income
            self._financial_snapshot_cache[symbol] = {
                "revenue": _coalesce_numeric(latest_income, INCOME_STATEMENT_LABELS["revenue"]),
                "ebitda": ebitda,
                "total_debt": _sum_numeric(latest_balance, DEBT_COMPONENT_LABELS),
                "cash_and_equivalents": _coalesce_numeric(latest_balance, BALANCE_SHEET_LABELS["cash_and_equivalents"]),
            }
        return self._financial_snapshot_cache[symbol]


class AkShareAStockCompanyProfileResolver(CompanyProfileResolver):
    """Resolve A-share company metadata via AkShare."""

    def __init__(self, akshare_module: Any | None = None) -> None:
        self._ak = akshare_module or _load_akshare_module()

    def resolve_profile_defaults(self, ticker: str) -> Mapping[str, Any]:
        symbol = _normalize_ashare_symbol(ticker)
        try:
            info_frame = _call_with_retry(self._ak.stock_individual_info_em, symbol=symbol)
            info_map = _item_value_map(info_frame)
        except Exception:  # noqa: BLE001
            info_map = {}
        return {
            "company_name": str(info_map.get("股票简称") or symbol),
            "exchange": _exchange_name_for_symbol(symbol),
            "reporting_currency": "CNY",
            "peer_list": [],
        }


def _load_akshare_module() -> Any:
    try:
        return importlib.import_module("akshare")
    except ImportError as exc:
        raise ProviderConfigurationError(
            "The akshare provider is not installed. Install dependencies from requirements.txt or add akshare "
            "to the environment before using the akshare backend."
        ) from exc


def _normalize_ashare_symbol(ticker: str) -> str:
    raw = ticker.strip().upper().replace(".", "")
    if raw.startswith(("SH", "SZ", "BJ")):
        raw = raw[2:]
    if not raw.isdigit() or len(raw) != 6:
        raise ProviderDataError(
            f"AkShare currently expects a 6-digit mainland A-share ticker, for example 600519 or 000001. Received: {ticker}"
        )
    return raw


def _to_sina_symbol(symbol: str) -> str:
    prefix = _exchange_prefix_for_symbol(symbol)
    return f"{prefix}{symbol}"


def _exchange_prefix_for_symbol(symbol: str) -> str:
    if symbol.startswith(("600", "601", "603", "605", "688", "689", "900")):
        return "sh"
    if symbol.startswith(("000", "001", "002", "003", "300", "301", "200")):
        return "sz"
    if symbol.startswith(("430", "440", "830", "831", "832", "833", "834", "835", "836", "837", "838", "839", "870", "871", "872", "873", "874", "875", "876", "877", "878", "879", "880", "881", "882", "883", "884", "885", "886", "887", "888", "889")):
        raise ProviderDataError("The initial akshare backend currently targets Shanghai and Shenzhen A-shares only.")
    if symbol.startswith(("4", "8")):
        raise ProviderDataError("The initial akshare backend currently targets Shanghai and Shenzhen A-shares only.")
    raise ProviderDataError(f"Unable to infer mainland exchange prefix for ticker {symbol}.")


def _exchange_name_for_symbol(symbol: str) -> str:
    prefix = _exchange_prefix_for_symbol(symbol)
    return "SSE" if prefix == "sh" else "SZSE"


def _build_income_statement_records(frame: pd.DataFrame, currency: str) -> list[FinancialStatementRecord]:
    records: list[FinancialStatementRecord] = []
    for _, row in _iter_annual_statement_rows(frame):
        revenue = _coalesce_numeric(row, INCOME_STATEMENT_LABELS["revenue"])
        gross_profit = _coalesce_numeric(row, INCOME_STATEMENT_LABELS["gross_profit"])
        operating_cost = _coalesce_numeric(row, INCOME_STATEMENT_LABELS["operating_cost"])
        if gross_profit is None and revenue is not None and operating_cost is not None:
            gross_profit = revenue - operating_cost

        operating_income = _coalesce_numeric(row, INCOME_STATEMENT_LABELS["operating_income"])
        ebitda = _coalesce_numeric(row, INCOME_STATEMENT_LABELS["ebitda"])
        if ebitda is None and operating_income is not None:
            ebitda = operating_income

        interest_expense = _coalesce_numeric(row, INCOME_STATEMENT_LABELS["interest_expense"])
        if interest_expense is not None:
            interest_expense = abs(interest_expense)

        period_end = pd.Timestamp(row["报告日"]).date()
        records.append(
            FinancialStatementRecord(
                period_end=period_end,
                fiscal_year=period_end.year,
                period_type="annual",
                statement_type="income_statement",
                currency=currency,
                values={
                    "revenue": revenue,
                    "gross_profit": gross_profit,
                    "ebitda": ebitda,
                    "operating_income": operating_income,
                    "net_income": _coalesce_numeric(row, INCOME_STATEMENT_LABELS["net_income"]),
                    "interest_expense": interest_expense,
                },
            )
        )
    return records


def _build_balance_sheet_records(frame: pd.DataFrame, currency: str) -> list[FinancialStatementRecord]:
    records: list[FinancialStatementRecord] = []
    for _, row in _iter_annual_statement_rows(frame):
        total_debt = _sum_numeric(row, DEBT_COMPONENT_LABELS)
        period_end = pd.Timestamp(row["报告日"]).date()
        records.append(
            FinancialStatementRecord(
                period_end=period_end,
                fiscal_year=period_end.year,
                period_type="annual",
                statement_type="balance_sheet",
                currency=currency,
                values={
                    "total_assets": _coalesce_numeric(row, BALANCE_SHEET_LABELS["total_assets"]),
                    "total_equity": _coalesce_numeric(row, BALANCE_SHEET_LABELS["total_equity"]),
                    "current_assets": _coalesce_numeric(row, BALANCE_SHEET_LABELS["current_assets"]),
                    "current_liabilities": _coalesce_numeric(row, BALANCE_SHEET_LABELS["current_liabilities"]),
                    "cash_and_equivalents": _coalesce_numeric(row, BALANCE_SHEET_LABELS["cash_and_equivalents"]),
                    "total_debt": total_debt,
                    "accounts_receivable": _coalesce_numeric(row, BALANCE_SHEET_LABELS["accounts_receivable"]),
                    "inventory": _coalesce_numeric(row, BALANCE_SHEET_LABELS["inventory"]),
                },
            )
        )
    return records


def _build_cash_flow_records(frame: pd.DataFrame, currency: str) -> list[FinancialStatementRecord]:
    records: list[FinancialStatementRecord] = []
    for _, row in _iter_annual_statement_rows(frame):
        capex = _coalesce_numeric(row, CASH_FLOW_LABELS["capital_expenditures"])
        if capex is not None:
            capex = -abs(capex)
        period_end = pd.Timestamp(row["报告日"]).date()
        records.append(
            FinancialStatementRecord(
                period_end=period_end,
                fiscal_year=period_end.year,
                period_type="annual",
                statement_type="cash_flow",
                currency=currency,
                values={
                    "operating_cash_flow": _coalesce_numeric(row, CASH_FLOW_LABELS["operating_cash_flow"]),
                    "capital_expenditures": capex,
                },
            )
        )
    return records


def _iter_annual_statement_rows(frame: pd.DataFrame):
    if frame is None or frame.empty or "报告日" not in frame.columns:
        return []
    prepared = frame.copy()
    prepared["报告日"] = pd.to_datetime(prepared["报告日"], errors="coerce")
    prepared = prepared.dropna(subset=["报告日"]).sort_values("报告日")
    prepared = prepared.loc[(prepared["报告日"].dt.month == 12) & (prepared["报告日"].dt.day == 31)]
    return list(prepared.iterrows())


def _latest_annual_row(frame: pd.DataFrame) -> pd.Series:
    annual_rows = _iter_annual_statement_rows(frame)
    if not annual_rows:
        return pd.Series(dtype=object)
    return annual_rows[-1][1]


def _item_value_map(frame: pd.DataFrame) -> dict[str, Any]:
    if frame is None or frame.empty or not {"item", "value"}.issubset(frame.columns):
        return {}
    return {str(row["item"]): row["value"] for _, row in frame.iterrows()}


def _coalesce_numeric(row: pd.Series, labels: list[str]) -> float | None:
    for label in labels:
        if label in row.index:
            value = _float_or_none(row[label])
            if value is not None:
                return value
    return None


def _sum_numeric(row: pd.Series, labels: list[str]) -> float | None:
    values = [_float_or_none(row[label]) for label in labels if label in row.index]
    filtered = [value for value in values if value is not None]
    if not filtered:
        return None
    return float(sum(filtered))


def _safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0, 0.0):
        return None
    if pd.isna(numerator) or pd.isna(denominator):
        return None
    return float(numerator) / float(denominator)


def _call_with_retry(func: Any, /, *args: Any, **kwargs: Any) -> Any:
    last_error: Exception | None = None
    for delay in (0.0, 1.0, 2.0):
        if delay:
            time.sleep(delay)
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    assert last_error is not None
    raise last_error


def _float_or_none(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, str):
        normalized = value.replace(",", "").replace("万股", "").replace("股", "").replace("--", "").strip()
        if not normalized:
            return None
        try:
            return float(normalized)
        except ValueError:
            return None
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric_value):
        return None
    return numeric_value


