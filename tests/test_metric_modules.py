"""Tests for Phase 2 metric modules using Tesla-shaped annual fixtures."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from src.analysis.balance_sheet import analyze_balance_sheet
from src.analysis.cashflow import analyze_cashflow
from src.analysis.profitability import analyze_profitability
from src.analysis.revenue_analysis import analyze_revenue
from src.analysis.returns import analyze_returns


@pytest.fixture()
def financials_by_year(tesla_normalized_financials) -> pd.DataFrame:
    """Index normalized financials by fiscal year for easier assertions."""

    return tesla_normalized_financials.set_index("fiscal_year", drop=False)


def test_revenue_metrics(financials_by_year) -> None:
    result = analyze_revenue(financials_by_year.reset_index(drop=True)).set_index("fiscal_year")

    assert pd.isna(result.loc[2019, "revenue_yoy_growth"])
    assert result.loc[2021, "revenue_yoy_growth"] == pytest.approx((53823 / 31536) - 1, rel=1e-6)
    assert result.loc[2022, "revenue_cagr_3y"] == pytest.approx((81462 / 24578) ** (1 / 3) - 1, rel=1e-6)
    assert result.loc[2024, "revenue_cagr_5y"] == pytest.approx((105000 / 24578) ** (1 / 5) - 1, rel=1e-6)


def test_profitability_metrics(financials_by_year) -> None:
    result = analyze_profitability(financials_by_year.reset_index(drop=True)).set_index("fiscal_year")

    assert result.loc[2022, "gross_margin"] == pytest.approx(20853 / 81462, rel=1e-6)
    assert result.loc[2022, "ebitda_margin"] == pytest.approx(17100 / 81462, rel=1e-6)
    assert result.loc[2023, "ebit_margin"] == pytest.approx(8890 / 96773, rel=1e-6)
    assert result.loc[2024, "net_margin"] == pytest.approx(8100 / 105000, rel=1e-6)


def test_return_metrics(financials_by_year) -> None:
    result = analyze_returns(financials_by_year.reset_index(drop=True)).set_index("fiscal_year")

    average_equity_2022 = (30189 + 44704) / 2
    average_assets_2022 = (62131 + 82338) / 2
    average_capital_employed_2022 = ((62131 - 19065) + (82338 - 28748)) / 2

    assert result.loc[2022, "roe"] == pytest.approx(12556 / average_equity_2022, rel=1e-6)
    assert result.loc[2022, "roa"] == pytest.approx(12556 / average_assets_2022, rel=1e-6)
    assert result.loc[2022, "roce"] == pytest.approx(13832 / average_capital_employed_2022, rel=1e-6)
    assert result.loc[2024, "asset_turnover"] == pytest.approx(105000 / ((106618 + 118000) / 2), rel=1e-6)


def test_balance_sheet_metrics(financials_by_year) -> None:
    result = analyze_balance_sheet(financials_by_year.reset_index(drop=True)).set_index("fiscal_year")

    assert result.loc[2024, "debt_to_equity"] == pytest.approx(5200 / 68000, rel=1e-6)
    assert result.loc[2024, "net_debt_to_ebitda"] == pytest.approx((5200 - 31000) / 15300, rel=1e-6)
    assert result.loc[2024, "current_ratio"] == pytest.approx(52200 / 33000, rel=1e-6)
    assert result.loc[2024, "interest_coverage"] == pytest.approx(9200 / 160, rel=1e-6)
    assert result.loc[2024, "working_capital"] == pytest.approx(52200 - 33000, rel=1e-6)
    assert result.loc[2024, "working_capital_pct_revenue"] == pytest.approx((52200 - 33000) / 105000, rel=1e-6)


def test_cashflow_metrics(financials_by_year) -> None:
    result = analyze_cashflow(financials_by_year.reset_index(drop=True)).set_index("fiscal_year")

    assert result.loc[2024, "free_cash_flow"] == pytest.approx(15000 - 9500, rel=1e-6)
    assert result.loc[2024, "cfo_to_net_income"] == pytest.approx(15000 / 8100, rel=1e-6)
    assert result.loc[2024, "capex"] == pytest.approx(9500, rel=1e-6)
    assert result.loc[2024, "capex_to_revenue"] == pytest.approx(9500 / 105000, rel=1e-6)
    assert result.loc[2024, "capex_yoy_growth"] == pytest.approx((9500 - 8899) / 8899, rel=1e-6)
