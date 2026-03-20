"""Balance-sheet analysis for annual normalized financials."""

from __future__ import annotations

import pandas as pd

from src.analysis.common import prepare_financials, safe_divide


REQUIRED_COLUMNS = [
    "fiscal_year",
    "total_debt",
    "total_equity",
    "cash_and_equivalents",
    "ebitda",
    "current_assets",
    "current_liabilities",
    "operating_income",
    "interest_expense",
    "revenue",
]


def analyze_balance_sheet(financials: pd.DataFrame) -> pd.DataFrame:
    """Compute leverage and liquidity metrics from normalized annual financials."""

    prepared = prepare_financials(financials, REQUIRED_COLUMNS, module_name="balance_sheet")
    working_capital = prepared["current_assets"] - prepared["current_liabilities"]
    net_debt = prepared["total_debt"] - prepared["cash_and_equivalents"]

    return pd.DataFrame(
        {
            "fiscal_year": prepared["fiscal_year"],
            "debt_to_equity": safe_divide(prepared["total_debt"], prepared["total_equity"]),
            "net_debt_to_ebitda": safe_divide(net_debt, prepared["ebitda"]),
            "current_ratio": safe_divide(prepared["current_assets"], prepared["current_liabilities"]),
            "interest_coverage": safe_divide(prepared["operating_income"], prepared["interest_expense"]),
            "working_capital": working_capital,
            "working_capital_pct_revenue": safe_divide(working_capital, prepared["revenue"]),
        }
    )
