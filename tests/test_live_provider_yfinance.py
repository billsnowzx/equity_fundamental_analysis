"""Tests for the Yahoo Finance live provider adapter using fake module data."""

from __future__ import annotations

import pandas as pd
import pytest

from src.providers.yfinance_live import (
    YFinanceCompanyProfileResolver,
    YFinanceFinancialStatementsProvider,
    YFinanceMarketDataProvider,
    YFinancePeerMultiplesProvider,
    YFinanceSharesOutstandingProvider,
)
from src.shared.schemas import CompanyProfile


class FakeTicker:
    def __init__(self, ticker: str):
        self.symbol = ticker.upper()
        self.info = {
            "financialCurrency": "USD",
            "currency": "USD",
            "longName": f"{self.symbol} Holdings",
            "exchange": "NASDAQ",
            "sharesOutstanding": 1000,
            "trailingPE": 20.0,
            "priceToBook": 5.0,
            "enterpriseToEbitda": 15.0,
            "enterpriseToRevenue": 4.0,
        }
        index_income = ["Total Revenue", "Gross Profit", "EBITDA", "Operating Income", "Net Income", "Interest Expense"]
        index_balance = ["Total Assets", "Stockholders Equity", "Current Assets", "Current Liabilities", "Cash And Cash Equivalents", "Total Debt", "Accounts Receivable", "Inventory"]
        index_cash = ["Operating Cash Flow", "Capital Expenditure"]
        columns = [pd.Timestamp("2023-12-31"), pd.Timestamp("2024-12-31")]
        self.income_stmt = pd.DataFrame(
            {
                columns[0]: [100, 40, 25, 20, 15, 2],
                columns[1]: [120, 50, 30, 24, 18, 2],
            },
            index=index_income,
        )
        self.balance_sheet = pd.DataFrame(
            {
                columns[0]: [200, 100, 80, 30, 20, 10, 12, 8],
                columns[1]: [240, 120, 90, 35, 22, 8, 14, 9],
            },
            index=index_balance,
        )
        self.cashflow = pd.DataFrame(
            {
                columns[0]: [28, -9],
                columns[1]: [32, -10],
            },
            index=index_cash,
        )
        self._history = pd.DataFrame(
            {
                "Close": [99.0, 101.5],
                "Volume": [1000000, 1200000],
            },
            index=[pd.Timestamp("2024-12-30"), pd.Timestamp("2024-12-31")],
        )
        self._shares = pd.Series(
            [900, 950, 1000],
            index=[pd.Timestamp("2022-12-31"), pd.Timestamp("2023-12-31"), pd.Timestamp("2024-12-31")],
        )

    def history(self, period: str, interval: str, auto_adjust: bool):
        return self._history

    def get_shares_full(self, start: str):
        return self._shares


class FakeYFinanceModule:
    def Ticker(self, ticker: str):
        return FakeTicker(ticker)


def test_yfinance_financial_provider_maps_statement_rows() -> None:
    provider = YFinanceFinancialStatementsProvider(yfinance_module=FakeYFinanceModule())
    company = CompanyProfile(ticker="ABCD", company_name="ABCD Holdings", exchange="NASDAQ", reporting_currency="USD", peer_list=[])

    records = provider.get_annual_financial_statements(company)

    assert len(records) == 6
    income_2024 = [record for record in records if record.statement_type == "income_statement" and record.fiscal_year == 2024][0]
    assert income_2024.values["revenue"] == pytest.approx(120)
    assert income_2024.values["net_income"] == pytest.approx(18)


def test_yfinance_market_shares_peer_and_profile_resolvers() -> None:
    module = FakeYFinanceModule()
    company = CompanyProfile(ticker="ABCD", company_name="ABCD Holdings", exchange="NASDAQ", reporting_currency="USD", peer_list=["PEER1"])

    market_provider = YFinanceMarketDataProvider(yfinance_module=module)
    shares_provider = YFinanceSharesOutstandingProvider(yfinance_module=module)
    peer_provider = YFinancePeerMultiplesProvider(yfinance_module=module)
    resolver = YFinanceCompanyProfileResolver(yfinance_module=module)

    market_data = market_provider.get_historical_prices(company)
    shares = shares_provider.get_shares_outstanding(company)
    peers = peer_provider.get_peer_multiples(company)
    defaults = resolver.resolve_profile_defaults("ABCD")

    assert market_data[-1].close == pytest.approx(101.5)
    assert shares[-1].shares_outstanding == pytest.approx(1000)
    assert peers[0].pe == pytest.approx(20.0)
    assert defaults["company_name"] == "ABCD Holdings"
    assert defaults["exchange"] == "NASDAQ"
