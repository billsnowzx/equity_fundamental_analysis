"""Return-ratio analysis for annual normalized financials."""

from __future__ import annotations

import pandas as pd

from src.analysis.common import average_with_prior, prepare_financials, safe_divide


REQUIRED_COLUMNS = [
    "fiscal_year",
    "revenue",
    "net_income",
    "operating_income",
    "total_assets",
    "total_equity",
    "current_liabilities",
]


def analyze_returns(financials: pd.DataFrame) -> pd.DataFrame:
    """Compute return ratios from normalized annual financials."""

    prepared = prepare_financials(financials, REQUIRED_COLUMNS, module_name="returns")
    average_assets = average_with_prior(prepared["total_assets"])
    average_equity = average_with_prior(prepared["total_equity"])
    capital_employed = prepared["total_assets"] - prepared["current_liabilities"]
    average_capital_employed = average_with_prior(capital_employed)

    return pd.DataFrame(
        {
            "fiscal_year": prepared["fiscal_year"],
            "roe": safe_divide(prepared["net_income"], average_equity),
            "roa": safe_divide(prepared["net_income"], average_assets),
            "roce": safe_divide(prepared["operating_income"], average_capital_employed),
            "asset_turnover": safe_divide(prepared["revenue"], average_assets),
        }
    )
