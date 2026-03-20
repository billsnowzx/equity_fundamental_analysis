"""Yahoo Finance live-provider adapters."""

from __future__ import annotations

import importlib
from collections.abc import Mapping
from datetime import date
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

INCOME_STATEMENT_MAP = {
    "revenue": ["Total Revenue"],
    "gross_profit": ["Gross Profit"],
    "ebitda": ["EBITDA"],
    "operating_income": ["Operating Income"],
    "net_income": ["Net Income"],
    "interest_expense": ["Interest Expense"],
}

BALANCE_SHEET_MAP = {
    "total_assets": ["Total Assets"],
    "total_equity": ["Stockholders Equity", "Total Equity Gross Minority Interest"],
    "current_assets": ["Current Assets"],
    "current_liabilities": ["Current Liabilities"],
    "cash_and_equivalents": ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"],
    "total_debt": ["Total Debt"],
    "accounts_receivable": ["Accounts Receivable"],
    "inventory": ["Inventory"],
}

CASH_FLOW_MAP = {
    "operating_cash_flow": ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"],
    "capital_expenditures": ["Capital Expenditure", "Capital Expenditures"],
}


class YFinanceFinancialStatementsProvider(FinancialStatementsProvider):
    """Fetch annual financial statements from Yahoo Finance."""

    def __init__(self, yfinance_module: Any | None = None) -> None:
        self._yf = yfinance_module or _load_yfinance_module()

    def get_annual_financial_statements(
        self,
        company: CompanyProfile,
    ) -> list[FinancialStatementRecord]:
        ticker = self._yf.Ticker(company.ticker)
        info = _safe_info(ticker)
        currency = str(info.get("financialCurrency") or info.get("currency") or company.reporting_currency)

        frames = [
            ("income_statement", _get_statement_frame(ticker, "income_stmt", "get_income_stmt"), INCOME_STATEMENT_MAP),
            ("balance_sheet", _get_statement_frame(ticker, "balance_sheet", "get_balance_sheet"), BALANCE_SHEET_MAP),
            ("cash_flow", _get_statement_frame(ticker, "cashflow", "get_cashflow"), CASH_FLOW_MAP),
        ]

        records: list[FinancialStatementRecord] = []
        for statement_type, frame, mapping in frames:
            if frame is None or frame.empty:
                continue
            for period_end, values in _frame_to_statement_values(frame, mapping).items():
                records.append(
                    FinancialStatementRecord(
                        period_end=period_end,
                        fiscal_year=period_end.year,
                        period_type="annual",
                        statement_type=statement_type,
                        currency=currency,
                        values=values,
                    )
                )

        if not records:
            raise ProviderDataError(f"Yahoo Finance did not return annual financial statements for {company.ticker}.")
        return records


class YFinanceMarketDataProvider(MarketDataProvider):
    """Fetch recent market data from Yahoo Finance."""

    def __init__(self, yfinance_module: Any | None = None) -> None:
        self._yf = yfinance_module or _load_yfinance_module()

    def get_historical_prices(self, company: CompanyProfile) -> list[MarketDataPoint]:
        ticker = self._yf.Ticker(company.ticker)
        history = ticker.history(period="1mo", interval="1d", auto_adjust=False)
        if history is None or history.empty:
            raise ProviderDataError(f"Yahoo Finance did not return market data for {company.ticker}.")
        currency = str(_safe_info(ticker).get("currency") or company.reporting_currency)
        result: list[MarketDataPoint] = []
        for period_end, row in history.sort_index().iterrows():
            result.append(
                MarketDataPoint(
                    date=pd.Timestamp(period_end).date(),
                    close=float(row["Close"]),
                    volume=None if pd.isna(row.get("Volume")) else float(row.get("Volume")),
                    currency=currency,
                )
            )
        return result


class YFinanceSharesOutstandingProvider(SharesOutstandingProvider):
    """Fetch current or historical shares outstanding from Yahoo Finance."""

    def __init__(self, yfinance_module: Any | None = None) -> None:
        self._yf = yfinance_module or _load_yfinance_module()

    def get_shares_outstanding(self, company: CompanyProfile) -> list[SharesOutstandingRecord]:
        ticker = self._yf.Ticker(company.ticker)
        shares_series = None
        if hasattr(ticker, "get_shares_full"):
            try:
                shares_series = ticker.get_shares_full(start="2015-01-01")
            except Exception:  # noqa: BLE001
                shares_series = None

        records: list[SharesOutstandingRecord] = []
        if shares_series is not None and not getattr(shares_series, "empty", True):
            annual = pd.Series(shares_series).dropna()
            annual.index = pd.to_datetime(annual.index)
            grouped = annual.groupby(annual.index.year).tail(1)
            for period_end, value in grouped.sort_index().items():
                records.append(
                    SharesOutstandingRecord(
                        date=pd.Timestamp(period_end).date(),
                        shares_outstanding=float(value),
                    )
                )

        if records:
            return records

        info = _safe_info(ticker)
        current_shares = info.get("sharesOutstanding")
        if current_shares is None:
            raise ProviderDataError(f"Yahoo Finance did not return shares outstanding for {company.ticker}.")
        return [
            SharesOutstandingRecord(
                date=date.today(),
                shares_outstanding=float(current_shares),
            )
        ]


class YFinancePeerMultiplesProvider(PeerMultiplesProvider):
    """Fetch simple peer valuation multiples from Yahoo Finance."""

    def __init__(self, yfinance_module: Any | None = None) -> None:
        self._yf = yfinance_module or _load_yfinance_module()

    def get_peer_multiples(self, company: CompanyProfile) -> list[PeerMultipleRecord]:
        if not company.peer_list:
            return []
        peers: list[PeerMultipleRecord] = []
        for peer in company.peer_list:
            try:
                info = _safe_info(self._yf.Ticker(peer))
            except Exception:  # noqa: BLE001
                continue
            peers.append(
                PeerMultipleRecord(
                    ticker=peer,
                    pe=_float_or_none(info.get("trailingPE")),
                    pb=_float_or_none(info.get("priceToBook")),
                    ev_to_ebitda=_float_or_none(info.get("enterpriseToEbitda")),
                    ev_to_sales=_float_or_none(info.get("enterpriseToRevenue")),
                )
            )
        return peers


class YFinanceCompanyProfileResolver(CompanyProfileResolver):
    """Resolve basic company metadata from Yahoo Finance."""

    def __init__(self, yfinance_module: Any | None = None) -> None:
        self._yf = yfinance_module or _load_yfinance_module()

    def resolve_profile_defaults(self, ticker: str) -> Mapping[str, Any]:
        info = _safe_info(self._yf.Ticker(ticker))
        return {
            "company_name": info.get("longName") or info.get("shortName") or ticker.upper(),
            "exchange": info.get("exchange") or info.get("fullExchangeName") or "UNKNOWN",
            "reporting_currency": info.get("financialCurrency") or info.get("currency") or "USD",
            "peer_list": [],
        }


def _load_yfinance_module() -> Any:
    try:
        return importlib.import_module("yfinance")
    except ImportError as exc:
        raise ProviderConfigurationError(
            "The yfinance live provider is not installed. Install dependencies from requirements.txt or "
            "add yfinance to the environment before using live mode."
        ) from exc


def _safe_info(ticker: Any) -> dict[str, Any]:
    info = getattr(ticker, "info", None)
    if callable(info):
        info = info()
    if isinstance(info, dict):
        return info
    return {}


def _get_statement_frame(ticker: Any, attribute_name: str, method_name: str) -> pd.DataFrame | None:
    frame = getattr(ticker, attribute_name, None)
    if callable(frame):
        frame = frame()
    if frame is None and hasattr(ticker, method_name):
        method = getattr(ticker, method_name)
        try:
            frame = method(freq="yearly")
        except TypeError:
            frame = method()
    if frame is None:
        return None
    dataframe = pd.DataFrame(frame)
    if dataframe.empty:
        return None
    return dataframe


def _frame_to_statement_values(
    frame: pd.DataFrame,
    mapping: dict[str, list[str]],
) -> dict[date, dict[str, float | None]]:
    result: dict[date, dict[str, float | None]] = {}
    normalized_frame = pd.DataFrame(frame)
    normalized_frame.columns = [pd.Timestamp(column) for column in normalized_frame.columns]
    for period_end in sorted(normalized_frame.columns):
        period_values: dict[str, float | None] = {}
        for target_key, source_labels in mapping.items():
            period_values[target_key] = _extract_mapped_value(normalized_frame, source_labels, period_end)
        result[pd.Timestamp(period_end).date()] = period_values
    return result


def _extract_mapped_value(frame: pd.DataFrame, labels: list[str], period_end: pd.Timestamp) -> float | None:
    for label in labels:
        if label in frame.index:
            value = frame.at[label, period_end]
            if pd.notna(value):
                return float(value)
    return None


def _float_or_none(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)
