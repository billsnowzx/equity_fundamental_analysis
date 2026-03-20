"""Revenue analysis for annual normalized financials."""

from __future__ import annotations

import pandas as pd

from src.analysis.common import cagr, prepare_financials, safe_divide


REQUIRED_COLUMNS = ["fiscal_year", "revenue"]


def analyze_revenue(financials: pd.DataFrame) -> pd.DataFrame:
    """Compute revenue growth metrics from normalized annual financials."""

    prepared = prepare_financials(financials, REQUIRED_COLUMNS, module_name="revenue_analysis")
    revenue = prepared["revenue"]
    fiscal_years = prepared["fiscal_year"]

    return pd.DataFrame(
        {
            "fiscal_year": fiscal_years,
            "revenue": revenue,
            "revenue_yoy_growth": safe_divide(revenue - revenue.shift(1), revenue.shift(1)),
            "revenue_cagr_3y": cagr(revenue, fiscal_years, 3),
            "revenue_cagr_5y": cagr(revenue, fiscal_years, 5),
        }
    )
