"""Valuation analysis for annual normalized financials."""

from __future__ import annotations

import math

import pandas as pd

from src.analysis.common import prepare_financials, safe_divide


REQUIRED_FINANCIAL_COLUMNS = [
    "fiscal_year",
    "net_income",
    "total_equity",
    "ebitda",
    "revenue",
    "operating_cash_flow",
    "capital_expenditures",
    "total_debt",
    "cash_and_equivalents",
]


def analyze_valuation(
    financials: pd.DataFrame,
    market_data: pd.DataFrame,
    shares_outstanding: pd.DataFrame | None = None,
    peer_multiples: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compute point-in-time valuation metrics from the latest annual data."""

    prepared = prepare_financials(financials, REQUIRED_FINANCIAL_COLUMNS, module_name="valuation")
    latest_financials = prepared.iloc[-1]

    market_prepared = market_data.copy()
    market_prepared["date"] = pd.to_datetime(market_prepared["date"])
    latest_market = market_prepared.sort_values("date").iloc[-1]

    shares_value = math.nan
    shares_as_of = pd.NaT
    if shares_outstanding is not None and not shares_outstanding.empty:
        shares_prepared = shares_outstanding.copy()
        shares_prepared["date"] = pd.to_datetime(shares_prepared["date"])
        latest_shares = shares_prepared.sort_values("date").iloc[-1]
        shares_value = float(latest_shares["shares_outstanding"])
        shares_as_of = latest_shares["date"]

    share_price = float(latest_market["close"])
    market_cap = share_price * shares_value if not math.isnan(shares_value) else math.nan
    enterprise_value = market_cap + float(latest_financials["total_debt"]) - float(latest_financials["cash_and_equivalents"])
    free_cash_flow = float(latest_financials["operating_cash_flow"]) - abs(float(latest_financials["capital_expenditures"]))

    result = {
        "fiscal_year": int(latest_financials["fiscal_year"]),
        "as_of_date": latest_market["date"],
        "shares_as_of_date": shares_as_of,
        "share_price": share_price,
        "shares_outstanding": shares_value,
        "market_cap": market_cap,
        "enterprise_value": enterprise_value,
        "price_to_earnings": _safe_ratio(market_cap, float(latest_financials["net_income"])),
        "price_to_book": _safe_ratio(market_cap, float(latest_financials["total_equity"])),
        "ev_to_ebitda": _safe_ratio(enterprise_value, float(latest_financials["ebitda"])),
        "ev_to_sales": _safe_ratio(enterprise_value, float(latest_financials["revenue"])),
        "fcf_yield": _safe_ratio(free_cash_flow, market_cap),
    }

    if peer_multiples is not None and not peer_multiples.empty:
        peers = peer_multiples.copy()
        result["peer_pe_median"] = peers["pe"].median()
        result["peer_pb_median"] = peers["pb"].median()
        result["peer_ev_to_ebitda_median"] = peers["ev_to_ebitda"].median()
        result["peer_ev_to_sales_median"] = peers["ev_to_sales"].median()
        result["pe_premium_to_peer"] = _premium_to_peer(result["price_to_earnings"], result["peer_pe_median"])
        result["pb_premium_to_peer"] = _premium_to_peer(result["price_to_book"], result["peer_pb_median"])
        result["ev_to_ebitda_premium_to_peer"] = _premium_to_peer(result["ev_to_ebitda"], result["peer_ev_to_ebitda_median"])
        result["ev_to_sales_premium_to_peer"] = _premium_to_peer(result["ev_to_sales"], result["peer_ev_to_sales_median"])

    return pd.DataFrame([result])


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator in (0, 0.0) or pd.isna(denominator) or pd.isna(numerator):
        return math.nan
    return float(numerator) / float(denominator)


def _premium_to_peer(value: float, peer_value: float) -> float:
    if pd.isna(value) or pd.isna(peer_value) or peer_value == 0:
        return math.nan
    return (value / peer_value) - 1
