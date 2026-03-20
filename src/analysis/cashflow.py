"""Cash-flow analysis for annual normalized financials."""

from __future__ import annotations

import pandas as pd

from src.analysis.common import prepare_financials, safe_divide


REQUIRED_COLUMNS = [
    "fiscal_year",
    "operating_cash_flow",
    "capital_expenditures",
    "net_income",
    "revenue",
]


def analyze_cashflow(financials: pd.DataFrame) -> pd.DataFrame:
    """Compute cash-flow metrics from normalized annual financials."""

    prepared = prepare_financials(financials, REQUIRED_COLUMNS, module_name="cashflow")
    capex = prepared["capital_expenditures"].abs()

    return pd.DataFrame(
        {
            "fiscal_year": prepared["fiscal_year"],
            "operating_cash_flow": prepared["operating_cash_flow"],
            "free_cash_flow": prepared["operating_cash_flow"] - capex,
            "cfo_to_net_income": safe_divide(prepared["operating_cash_flow"], prepared["net_income"]),
            "capex": capex,
            "capex_to_revenue": safe_divide(capex, prepared["revenue"]),
            "capex_yoy_growth": safe_divide(capex - capex.shift(1), capex.shift(1)),
        }
    )
