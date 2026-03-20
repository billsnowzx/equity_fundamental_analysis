"""Red-flag analysis for annual normalized financials."""

from __future__ import annotations

import math

import pandas as pd

from src.analysis.common import prepare_financials, safe_divide


REQUIRED_COLUMNS = [
    "fiscal_year",
    "revenue",
    "gross_profit",
    "net_income",
    "operating_cash_flow",
    "accounts_receivable",
    "inventory",
    "total_debt",
    "total_equity",
]

GROSS_MARGIN_DETERIORATION_THRESHOLD = 0.02
NET_MARGIN_DETERIORATION_THRESHOLD = 0.015
BROAD_MARGIN_DECLINE_THRESHOLD = 0.005


def analyze_red_flags(
    financials: pd.DataFrame,
    shares_outstanding: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Detect the core MVP red flags from normalized annual data."""

    prepared = prepare_financials(financials, REQUIRED_COLUMNS, module_name="red_flags").copy()
    prepared["revenue_yoy_growth"] = prepared["revenue"].pct_change(fill_method=None)
    prepared["receivables_yoy_growth"] = prepared["accounts_receivable"].pct_change(fill_method=None)
    prepared["inventory_yoy_growth"] = prepared["inventory"].pct_change(fill_method=None)
    prepared["gross_margin"] = safe_divide(prepared["gross_profit"], prepared["revenue"])
    prepared["net_margin"] = safe_divide(prepared["net_income"], prepared["revenue"])
    prepared["debt_to_equity"] = safe_divide(prepared["total_debt"], prepared["total_equity"])

    latest = prepared.iloc[-1]
    previous = prepared.iloc[-2] if len(prepared) >= 2 else None
    previous_two = prepared.iloc[-3] if len(prepared) >= 3 else None

    triggered_cfo_gap = False
    if len(prepared) >= 2:
        recent = prepared.tail(2)
        triggered_cfo_gap = bool((recent["operating_cash_flow"] < recent["net_income"]).all())

    triggered_rising_leverage = False
    if previous is not None and previous_two is not None:
        triggered_rising_leverage = bool(
            latest["debt_to_equity"] > previous["debt_to_equity"] > previous_two["debt_to_equity"]
        )

    share_dilution_triggered = False
    share_dilution_detail = "Shares outstanding data not available."
    if shares_outstanding is not None and not shares_outstanding.empty:
        shares = shares_outstanding.copy()
        shares["date"] = pd.to_datetime(shares["date"])
        shares = shares.sort_values("date").reset_index(drop=True)
        latest_shares = float(shares.iloc[-1]["shares_outstanding"])
        comparison_index = max(0, len(shares) - 4)
        base_shares = float(shares.iloc[comparison_index]["shares_outstanding"])
        dilution = _safe_growth(latest_shares, base_shares)
        share_dilution_triggered = bool(pd.notna(dilution) and dilution > 0.05)
        share_dilution_detail = (
            f"Shares outstanding changed by {dilution:.1%} versus {shares.iloc[comparison_index]['date'].date()}."
            if pd.notna(dilution)
            else "Share dilution could not be evaluated."
        )

    flags = [
        _build_flag(
            flag="receivables_growth_faster_than_revenue",
            triggered=_is_growth_flagged(latest["receivables_yoy_growth"], latest["revenue_yoy_growth"]),
            severity="medium",
            detail=f"Receivables growth {_format_pct(latest['receivables_yoy_growth'])} versus revenue growth {_format_pct(latest['revenue_yoy_growth'])}.",
        ),
        _build_flag(
            flag="inventory_growth_faster_than_revenue",
            triggered=_is_growth_flagged(latest["inventory_yoy_growth"], latest["revenue_yoy_growth"]),
            severity="low",
            detail=f"Inventory growth {_format_pct(latest['inventory_yoy_growth'])} versus revenue growth {_format_pct(latest['revenue_yoy_growth'])}.",
        ),
        _build_flag(
            flag="cfo_below_net_income_for_two_years",
            triggered=triggered_cfo_gap,
            severity="high",
            detail="Operating cash flow is below net income in each of the last two fiscal years.",
        ),
        _build_flag(
            flag="rising_leverage",
            triggered=triggered_rising_leverage,
            severity="medium",
            detail="Debt-to-equity has risen for three consecutive annual observations.",
        ),
        _build_flag(
            flag="share_dilution",
            triggered=share_dilution_triggered,
            severity="low",
            detail=share_dilution_detail,
        ),
        _build_flag(
            flag="margin_deterioration_despite_sales_growth",
            triggered=_margin_deterioration(latest, previous),
            severity="medium",
            detail=_margin_detail(latest, previous),
        ),
    ]

    return pd.DataFrame(flags)


def _build_flag(flag: str, triggered: bool, severity: str, detail: str) -> dict[str, object]:
    return {
        "flag": flag,
        "triggered": bool(triggered),
        "severity": severity,
        "detail": detail,
    }


def _is_growth_flagged(candidate_growth: float, revenue_growth: float) -> bool:
    if pd.isna(candidate_growth) or pd.isna(revenue_growth):
        return False
    return candidate_growth > revenue_growth and revenue_growth > 0


def _margin_deterioration(latest: pd.Series, previous: pd.Series | None) -> bool:
    if previous is None:
        return False
    revenue_growth = latest["revenue_yoy_growth"]
    if pd.isna(revenue_growth) or revenue_growth <= 0:
        return False

    gross_margin_change = latest["gross_margin"] - previous["gross_margin"]
    net_margin_change = latest["net_margin"] - previous["net_margin"]
    broad_margin_decline = bool(
        pd.notna(gross_margin_change)
        and pd.notna(net_margin_change)
        and gross_margin_change <= -BROAD_MARGIN_DECLINE_THRESHOLD
        and net_margin_change <= -BROAD_MARGIN_DECLINE_THRESHOLD
    )
    material_gross_decline = bool(
        pd.notna(gross_margin_change)
        and gross_margin_change <= -GROSS_MARGIN_DETERIORATION_THRESHOLD
    )
    material_net_decline = bool(
        pd.notna(net_margin_change)
        and net_margin_change <= -NET_MARGIN_DETERIORATION_THRESHOLD
    )
    return bool(
        broad_margin_decline
        or material_gross_decline
        or material_net_decline
    )


def _margin_detail(latest: pd.Series, previous: pd.Series | None) -> str:
    if previous is None:
        return "Not enough history to evaluate margin deterioration."
    return (
        f"Revenue growth {_format_pct(latest['revenue_yoy_growth'])}; "
        f"gross margin moved from {_format_pct(previous['gross_margin'])} to {_format_pct(latest['gross_margin'])}; "
        f"net margin moved from {_format_pct(previous['net_margin'])} to {_format_pct(latest['net_margin'])}."
    )


def _safe_growth(current: float, base: float) -> float:
    if base == 0 or math.isnan(base) or math.isnan(current):
        return math.nan
    return (current / base) - 1


def _format_pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.1%}"
