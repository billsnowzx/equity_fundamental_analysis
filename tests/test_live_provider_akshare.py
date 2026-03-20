"""Tests for the AkShare A-share provider adapter using fake module data."""

from __future__ import annotations

import pandas as pd
import pytest

from src.providers.akshare_cn import (
    AkShareAStockCompanyProfileResolver,
    AkShareAStockFinancialStatementsProvider,
    AkShareAStockMarketDataProvider,
    AkShareAStockPeerMultiplesProvider,
    AkShareAStockSharesOutstandingProvider,
)
from src.shared.schemas import CompanyProfile


class FakeAkShareModule:
    def stock_financial_report_sina(self, stock: str, symbol: str) -> pd.DataFrame:
        if stock == "sh600519":
            if symbol == "利润表":
                return pd.DataFrame(
                    [
                        {"报告日": "2024-12-31", "营业总收入": 1200, "营业成本": 450, "营业利润": 300, "净利润": 240, "利息支出": 10},
                    ]
                )
            if symbol == "资产负债表":
                return pd.DataFrame(
                    [
                        {"报告日": "2024-12-31", "资产总计": 3600, "股东权益合计": 1800, "流动资产合计": 1400, "流动负债合计": 800, "货币资金": 620, "短期借款": 120, "长期借款": 220, "应收账款": 210, "存货": 190},
                    ]
                )
            if symbol == "现金流量表":
                return pd.DataFrame(
                    [
                        {"报告日": "2024-12-31", "经营活动产生的现金流量净额": 320, "购建固定资产、无形资产和其他长期资产支付的现金": 80},
                    ]
                )
        if stock == "sz000858":
            if symbol == "利润表":
                return pd.DataFrame(
                    [
                        {"报告日": "2024-12-31", "营业总收入": 900, "营业成本": 300, "营业利润": 220, "净利润": 180, "利息支出": 8},
                    ]
                )
            if symbol == "资产负债表":
                return pd.DataFrame(
                    [
                        {"报告日": "2024-12-31", "资产总计": 2500, "股东权益合计": 1500, "流动资产合计": 1000, "流动负债合计": 500, "货币资金": 400, "短期借款": 50, "长期借款": 150, "应收账款": 120, "存货": 110},
                    ]
                )
            if symbol == "现金流量表":
                return pd.DataFrame(
                    [
                        {"报告日": "2024-12-31", "经营活动产生的现金流量净额": 260, "购建固定资产、无形资产和其他长期资产支付的现金": 60},
                    ]
                )
        raise AssertionError((stock, symbol))

    def stock_zh_a_hist(self, symbol: str, period: str, start_date: str, end_date: str, adjust: str) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"日期": "2024-12-30", "收盘": 100.5, "成交量": 100000},
                {"日期": "2024-12-31", "收盘": 102.0, "成交量": 120000},
            ]
        )

    def stock_share_change_cninfo(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"变动日期": "2022-12-31", "总股本": 900},
                {"变动日期": "2023-12-31", "总股本": 950},
                {"变动日期": "2024-12-31", "总股本": 1000},
            ]
        )

    def stock_individual_info_em(self, symbol: str) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"item": "股票简称", "value": "茅台示例" if symbol == "600519" else "五粮液示例"},
                {"item": "总股本", "value": 1000 if symbol == "600519" else 800},
                {"item": "行业", "value": "白酒"},
            ]
        )

    def stock_zh_a_spot_em(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"代码": "600519", "名称": "茅台示例", "市盈率-动态": 20.0, "市净率": 8.0, "总市值": 1800000000000.0},
                {"代码": "000858", "名称": "五粮液示例", "市盈率-动态": 18.0, "市净率": 6.0, "总市值": 900000000000.0},
            ]
        )


@pytest.fixture()
def china_company() -> CompanyProfile:
    return CompanyProfile(
        ticker="600519",
        company_name="贵州茅台",
        exchange="SSE",
        reporting_currency="CNY",
        peer_list=["000858"],
    )


def test_akshare_financial_provider_maps_statement_rows(china_company) -> None:
    provider = AkShareAStockFinancialStatementsProvider(akshare_module=FakeAkShareModule())

    records = provider.get_annual_financial_statements(china_company)

    assert len(records) == 3
    income_2024 = [record for record in records if record.statement_type == "income_statement" and record.fiscal_year == 2024][0]
    balance_2024 = [record for record in records if record.statement_type == "balance_sheet" and record.fiscal_year == 2024][0]
    cash_2024 = [record for record in records if record.statement_type == "cash_flow" and record.fiscal_year == 2024][0]

    assert income_2024.values["revenue"] == pytest.approx(1200)
    assert income_2024.values["gross_profit"] == pytest.approx(750)
    assert income_2024.values["ebitda"] == pytest.approx(300)
    assert income_2024.values["interest_expense"] == pytest.approx(10)
    assert balance_2024.values["total_debt"] == pytest.approx(340)
    assert cash_2024.values["capital_expenditures"] == pytest.approx(-80)


def test_akshare_market_shares_profile_and_peer_resolvers(china_company) -> None:
    module = FakeAkShareModule()
    market_provider = AkShareAStockMarketDataProvider(akshare_module=module)
    shares_provider = AkShareAStockSharesOutstandingProvider(akshare_module=module)
    peer_provider = AkShareAStockPeerMultiplesProvider(akshare_module=module)
    resolver = AkShareAStockCompanyProfileResolver(akshare_module=module)

    market_data = market_provider.get_historical_prices(china_company)
    shares = shares_provider.get_shares_outstanding(china_company)
    peers = peer_provider.get_peer_multiples(china_company)
    defaults = resolver.resolve_profile_defaults("600519")

    assert market_data[-1].close == pytest.approx(102.0)
    assert shares[-1].shares_outstanding == pytest.approx(1000 * 10000)
    assert defaults["company_name"] == "茅台示例"
    assert defaults["exchange"] == "SSE"
    assert defaults["reporting_currency"] == "CNY"
    assert peers[0].ticker == "000858"
    assert peers[0].pe == pytest.approx(18.0)
    assert peers[0].pb == pytest.approx(6.0)
    assert peers[0].ev_to_sales == pytest.approx((900000000000.0 + 200 - 400) / 900, rel=1e-6)
    assert peers[0].ev_to_ebitda == pytest.approx((900000000000.0 + 200 - 400) / 220, rel=1e-6)
