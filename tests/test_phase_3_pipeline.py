"""Phase 3 tests for valuation, red flags, scoring, and pipeline orchestration."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analysis.balance_sheet import analyze_balance_sheet
from src.analysis.cashflow import analyze_cashflow
from src.analysis.profitability import analyze_profitability
from src.analysis.red_flags import analyze_red_flags
from src.analysis.revenue_analysis import analyze_revenue
from src.analysis.returns import analyze_returns
from src.analysis.scoring import score_company
from src.analysis.valuation import analyze_valuation
from src.orchestration.run_analysis import run_analysis
from src.shared.schemas import AnalysisRequest, CompanyProfile


@pytest.fixture()
def phase_3_metric_frames(tesla_normalized_financials, tesla_market_data, tesla_shares_outstanding, tesla_peer_multiples):
    financials = tesla_normalized_financials
    return {
        "revenue": analyze_revenue(financials),
        "profitability": analyze_profitability(financials),
        "returns": analyze_returns(financials),
        "balance_sheet": analyze_balance_sheet(financials),
        "cashflow": analyze_cashflow(financials),
        "valuation": analyze_valuation(financials, tesla_market_data, tesla_shares_outstanding, tesla_peer_multiples),
    }


def test_valuation_metrics(tesla_normalized_financials, tesla_market_data, tesla_shares_outstanding, tesla_peer_multiples) -> None:
    valuation = analyze_valuation(
        tesla_normalized_financials,
        tesla_market_data,
        tesla_shares_outstanding,
        tesla_peer_multiples,
    ).iloc[0]

    assert valuation["share_price"] == pytest.approx(250.20, rel=1e-6)
    assert valuation["shares_outstanding"] == pytest.approx(3200, rel=1e-6)
    assert valuation["market_cap"] == pytest.approx(800640, rel=1e-6)
    assert valuation["price_to_earnings"] == pytest.approx(800640 / 8100, rel=1e-6)
    assert valuation["ev_to_sales"] == pytest.approx((800640 + 5200 - 31000) / 105000, rel=1e-6)
    assert valuation["peer_pe_median"] == pytest.approx(7.0, rel=1e-6)


def test_red_flags_detect_expected_issues(tesla_normalized_financials, tesla_shares_outstanding) -> None:
    red_flags = analyze_red_flags(tesla_normalized_financials, tesla_shares_outstanding)
    triggered = red_flags.loc[red_flags["triggered"], "flag"].tolist()

    assert "inventory_growth_faster_than_revenue" in triggered
    assert "share_dilution" in triggered
    assert "margin_deterioration_despite_sales_growth" in triggered
    assert "receivables_growth_faster_than_revenue" not in triggered
    assert "rising_leverage" not in triggered


def test_margin_red_flag_ignores_minor_gross_margin_slip_when_net_margin_improves() -> None:
    financials = pd.DataFrame(
        [
            {
                "fiscal_year": 2023,
                "revenue": 100.0,
                "gross_profit": 69.8,
                "net_income": 36.0,
                "operating_cash_flow": 40.0,
                "accounts_receivable": 10.0,
                "inventory": 4.0,
                "total_debt": 12.0,
                "total_equity": 50.0,
            },
            {
                "fiscal_year": 2024,
                "revenue": 114.9,
                "gross_profit": 79.1,
                "net_income": 41.5,
                "operating_cash_flow": 45.0,
                "accounts_receivable": 12.3,
                "inventory": 3.0,
                "total_debt": 11.0,
                "total_equity": 54.0,
            },
        ]
    )

    red_flags = analyze_red_flags(financials)
    triggered = red_flags.set_index("flag")

    assert not bool(triggered.loc["margin_deterioration_despite_sales_growth", "triggered"])


def test_margin_red_flag_ignores_tiny_dual_margin_slip() -> None:
    financials = pd.DataFrame(
        [
            {
                "fiscal_year": 2023,
                "revenue": 100.0,
                "gross_profit": 92.1,
                "net_income": 51.5,
                "operating_cash_flow": 55.0,
                "accounts_receivable": 8.0,
                "inventory": 3.0,
                "total_debt": 5.0,
                "total_equity": 70.0,
            },
            {
                "fiscal_year": 2024,
                "revenue": 115.7,
                "gross_profit": 106.4,
                "net_income": 59.2,
                "operating_cash_flow": 62.0,
                "accounts_receivable": 7.8,
                "inventory": 3.4,
                "total_debt": 5.2,
                "total_equity": 74.0,
            },
        ]
    )

    red_flags = analyze_red_flags(financials)
    triggered = red_flags.set_index("flag")

    assert not bool(triggered.loc["margin_deterioration_despite_sales_growth", "triggered"])


def test_scorecard_classifies_tesla_as_good_business_too_expensive(phase_3_metric_frames, tesla_normalized_financials, tesla_shares_outstanding) -> None:
    red_flags = analyze_red_flags(tesla_normalized_financials, tesla_shares_outstanding)
    scorecard = score_company(phase_3_metric_frames, red_flags)
    overall = scorecard.loc[scorecard["category"] == "overall"].iloc[0]
    valuation_row = scorecard.loc[scorecard["category"] == "valuation"].iloc[0]

    assert overall["score"] >= 70
    assert overall["summary"] == "good business, too expensive"
    assert valuation_row["score"] < 35


def test_run_analysis_smoke(repo_root, fixture_provider_runtime) -> None:
    request = AnalysisRequest(
        company=CompanyProfile(
            ticker="TSLA",
            company_name="Tesla, Inc.",
            exchange="NASDAQ",
            reporting_currency="USD",
        ),
        output_root=repo_root / "tests" / "artifacts" / "smoke_test_single",
    )

    artifacts = run_analysis(request, provider_runtime=fixture_provider_runtime)

    assert artifacts["report_path"].is_file()
    assert artifacts["scorecard_csv"].is_file()
    assert artifacts["scorecard_json"].is_file()
    assert artifacts["red_flags_csv"].is_file()
    assert artifacts["metric_snapshot_csv"].is_file()
    assert (artifacts["charts_dir"] / "revenue_and_operating_cash_flow.png").is_file()
    assert (artifacts["charts_dir"] / "margin_profile.png").is_file()

    report_text = artifacts["report_path"].read_text()
    assert "Tesla, Inc. (TSLA) Fundamental Analysis" in report_text
    assert "good business, too expensive" in report_text
    assert "Free cash flow remains positive in the latest fiscal year." in report_text

