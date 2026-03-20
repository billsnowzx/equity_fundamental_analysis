"""Weighted scorecard generation for the MVP pipeline."""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd


CATEGORY_WEIGHTS = {
    "revenue": 0.16,
    "profitability": 0.16,
    "returns": 0.16,
    "balance_sheet": 0.16,
    "cashflow": 0.16,
    "valuation": 0.10,
    "red_flags": 0.10,
}

SEVERITY_DEDUCTIONS = {
    "low": 10,
    "medium": 15,
    "high": 25,
}


def score_company(
    metric_frames: Mapping[str, pd.DataFrame],
    red_flags: pd.DataFrame,
) -> pd.DataFrame:
    """Create a weighted scorecard across the MVP analysis categories."""

    revenue_row = _latest_row(metric_frames["revenue"])
    profitability_row = _latest_row(metric_frames["profitability"])
    returns_row = _latest_row(metric_frames["returns"])
    balance_row = _latest_row(metric_frames["balance_sheet"])
    cashflow_row = _latest_row(metric_frames["cashflow"])
    valuation_row = _latest_row(metric_frames["valuation"])

    scores = [
        _row(
            "revenue",
            _score_revenue(revenue_row),
            "Strong multi-year growth receives the highest weight in the model.",
        ),
        _row(
            "profitability",
            _score_profitability(profitability_row),
            "Margins measure structural business quality and pricing power.",
        ),
        _row(
            "returns",
            _score_returns(returns_row),
            "Return ratios reward efficient use of capital and assets.",
        ),
        _row(
            "balance_sheet",
            _score_balance_sheet(balance_row),
            "Leverage and liquidity determine resilience through weaker cycles.",
        ),
        _row(
            "cashflow",
            _score_cashflow(cashflow_row),
            "Cash conversion and free cash flow anchor the quality check.",
        ),
        _row(
            "valuation",
            _score_valuation(valuation_row),
            "Valuation is intentionally harsh on expensive equities.",
        ),
        _row(
            "red_flags",
            _score_red_flags(red_flags),
            "Triggered red flags reduce confidence in the headline metrics.",
        ),
    ]

    scorecard = pd.DataFrame(scores)
    scorecard["weight"] = scorecard["category"].map(CATEGORY_WEIGHTS)
    scorecard["weighted_score"] = scorecard["score"] * scorecard["weight"]
    overall_score = scorecard["weighted_score"].sum()
    valuation_score = float(scorecard.loc[scorecard["category"] == "valuation", "score"].iloc[0])
    red_flag_score = float(scorecard.loc[scorecard["category"] == "red_flags", "score"].iloc[0])
    revenue_score = float(scorecard.loc[scorecard["category"] == "revenue", "score"].iloc[0])

    overall = pd.DataFrame(
        [
            {
                "category": "overall",
                "score": overall_score,
                "weight": 1.0,
                "weighted_score": overall_score,
                "summary": _determine_label(overall_score, valuation_score, red_flag_score, revenue_score),
            }
        ]
    )
    return pd.concat([scorecard, overall], ignore_index=True)


def _latest_row(frame: pd.DataFrame) -> pd.Series:
    return frame.iloc[-1]


def _row(category: str, score: float, summary: str) -> dict[str, object]:
    return {
        "category": category,
        "score": min(max(float(score), 0.0), 100.0),
        "summary": summary,
    }


def _score_revenue(row: pd.Series) -> float:
    score = 0.0
    score += _threshold_points(row.get("revenue_yoy_growth"), [(0.15, 45), (0.08, 30), (0.0, 15)])
    score += _threshold_points(row.get("revenue_cagr_3y"), [(0.20, 35), (0.12, 25), (0.05, 10)])
    score += _threshold_points(row.get("revenue_cagr_5y"), [(0.15, 20), (0.08, 10), (0.03, 5)])
    return score


def _score_profitability(row: pd.Series) -> float:
    score = 0.0
    score += _threshold_points(row.get("gross_margin"), [(0.22, 30), (0.17, 20), (0.12, 10)])
    score += _threshold_points(row.get("ebitda_margin"), [(0.18, 20), (0.14, 15), (0.10, 8)])
    score += _threshold_points(row.get("ebit_margin"), [(0.12, 25), (0.08, 18), (0.04, 8)])
    score += _threshold_points(row.get("net_margin"), [(0.10, 25), (0.07, 15), (0.03, 8)])
    return score


def _score_returns(row: pd.Series) -> float:
    score = 0.0
    score += _threshold_points(row.get("roe"), [(0.18, 30), (0.12, 22), (0.08, 12)])
    score += _threshold_points(row.get("roa"), [(0.09, 20), (0.06, 15), (0.03, 8)])
    score += _threshold_points(row.get("roce"), [(0.15, 30), (0.10, 22), (0.07, 12)])
    score += _threshold_points(row.get("asset_turnover"), [(0.9, 20), (0.7, 14), (0.5, 8)])
    return score


def _score_balance_sheet(row: pd.Series) -> float:
    score = 0.0
    score += _inverse_threshold_points(row.get("debt_to_equity"), [(0.20, 30), (0.50, 20), (1.00, 8)])
    score += _inverse_threshold_points(row.get("net_debt_to_ebitda"), [(0.0, 25), (1.0, 20), (2.0, 10)])
    score += _threshold_points(row.get("current_ratio"), [(1.5, 20), (1.2, 14), (1.0, 8)])
    score += _threshold_points(row.get("interest_coverage"), [(10.0, 25), (5.0, 16), (2.0, 8)])
    return score


def _score_cashflow(row: pd.Series) -> float:
    score = 0.0
    score += 25 if pd.notna(row.get("operating_cash_flow")) and row.get("operating_cash_flow") > 0 else 0
    score += 30 if pd.notna(row.get("free_cash_flow")) and row.get("free_cash_flow") > 0 else 0
    score += _threshold_points(row.get("cfo_to_net_income"), [(1.1, 25), (0.9, 18), (0.7, 8)])
    score += _inverse_threshold_points(row.get("capex_to_revenue"), [(0.08, 20), (0.12, 12), (0.18, 6)])
    return score


def _score_valuation(row: pd.Series) -> float:
    score = 0.0
    score += _inverse_threshold_points(row.get("price_to_earnings"), [(15.0, 30), (25.0, 20), (40.0, 10)])
    score += _inverse_threshold_points(row.get("price_to_book"), [(3.0, 20), (6.0, 10), (10.0, 5)])
    score += _inverse_threshold_points(row.get("ev_to_ebitda"), [(10.0, 25), (18.0, 15), (30.0, 5)])
    score += _inverse_threshold_points(row.get("ev_to_sales"), [(2.0, 15), (4.0, 10), (8.0, 5)])
    score += _threshold_points(row.get("fcf_yield"), [(0.08, 10), (0.04, 6), (0.02, 3)])
    return score


def _score_red_flags(red_flags: pd.DataFrame) -> float:
    triggered = red_flags.loc[red_flags["triggered"]]
    deductions = triggered["severity"].map(SEVERITY_DEDUCTIONS).fillna(10).sum()
    return 100 - float(deductions)


def _threshold_points(value: float, thresholds: list[tuple[float, float]]) -> float:
    if pd.isna(value):
        return 0.0
    for threshold, points in thresholds:
        if value >= threshold:
            return points
    return 0.0


def _inverse_threshold_points(value: float, thresholds: list[tuple[float, float]]) -> float:
    if pd.isna(value):
        return 0.0
    for threshold, points in thresholds:
        if value <= threshold:
            return points
    return 0.0


def _determine_label(
    overall_score: float,
    valuation_score: float,
    red_flag_score: float,
    revenue_score: float,
) -> str:
    if red_flag_score < 40 or overall_score < 45:
        return "value trap / governance trap"
    if overall_score >= 85 and valuation_score >= 45 and red_flag_score >= 80:
        return "high-quality compounder"
    if overall_score >= 70 and valuation_score < 35:
        return "good business, too expensive"
    if overall_score >= 60 and valuation_score >= 55 and revenue_score < 60:
        return "cyclical opportunity"
    if overall_score >= 55:
        return "watchlist only"
    return "value trap / governance trap"

