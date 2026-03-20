"""Profitability analysis for annual normalized financials."""

from __future__ import annotations

import pandas as pd

from src.analysis.common import prepare_financials, safe_divide


REQUIRED_COLUMNS = [
    "fiscal_year",
    "revenue",
    "gross_profit",
    "ebitda",
    "operating_income",
    "net_income",
]


def analyze_profitability(financials: pd.DataFrame) -> pd.DataFrame:
    """Compute profitability margins from normalized annual financials."""

    prepared = prepare_financials(financials, REQUIRED_COLUMNS, module_name="profitability")
    revenue = prepared["revenue"]

    return pd.DataFrame(
        {
            "fiscal_year": prepared["fiscal_year"],
            "gross_margin": safe_divide(prepared["gross_profit"], revenue),
            "ebitda_margin": safe_divide(prepared["ebitda"], revenue),
            "ebit_margin": safe_divide(prepared["operating_income"], revenue),
            "net_margin": safe_divide(prepared["net_income"], revenue),
        }
    )
