"""Annual financial normalization for the Phase 2 MVP."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Final

import pandas as pd

from src.shared.schemas import FinancialStatementRecord

LOGGER = logging.getLogger(__name__)

NORMALIZED_METADATA_COLUMNS: Final[list[str]] = [
    "fiscal_year",
    "period_end",
    "period_type",
    "currency",
]

NORMALIZED_LINE_ITEM_COLUMNS: Final[list[str]] = [
    "revenue",
    "gross_profit",
    "ebitda",
    "operating_income",
    "net_income",
    "interest_expense",
    "total_assets",
    "total_equity",
    "current_assets",
    "current_liabilities",
    "cash_and_equivalents",
    "total_debt",
    "accounts_receivable",
    "inventory",
    "operating_cash_flow",
    "capital_expenditures",
]

NORMALIZED_FINANCIAL_COLUMNS: Final[list[str]] = [
    *NORMALIZED_METADATA_COLUMNS,
    *NORMALIZED_LINE_ITEM_COLUMNS,
]


def normalize_annual_financials(
    records: Sequence[FinancialStatementRecord],
) -> pd.DataFrame:
    """Normalize annual statement records into one dataframe per fiscal year."""

    if not records:
        return pd.DataFrame(columns=NORMALIZED_FINANCIAL_COLUMNS)

    currencies = {record.currency for record in records}
    if len(currencies) != 1:
        raise ValueError("Normalization requires a single reporting currency.")

    normalized_rows: dict[int, dict[str, object]] = {}

    for record in records:
        if record.period_type.lower() != "annual":
            raise ValueError("Normalization supports annual statement records only.")

        row = normalized_rows.setdefault(
            record.fiscal_year,
            {
                "fiscal_year": record.fiscal_year,
                "period_end": record.period_end,
                "period_type": "annual",
                "currency": record.currency,
            },
        )

        if row["currency"] != record.currency:
            raise ValueError("Mixed currencies detected within the same fiscal year.")

        row["period_end"] = max(row["period_end"], record.period_end)

        for line_item, value in record.values.items():
            if line_item not in NORMALIZED_LINE_ITEM_COLUMNS:
                LOGGER.warning("Ignoring unsupported line item during normalization: %s", line_item)
                continue

            existing_value = row.get(line_item)
            if existing_value is not None and value is not None and existing_value != value:
                raise ValueError(
                    f"Conflicting values for '{line_item}' in fiscal year {record.fiscal_year}."
                )

            row[line_item] = value

    dataframe = pd.DataFrame(normalized_rows.values())
    dataframe = dataframe.reindex(columns=NORMALIZED_FINANCIAL_COLUMNS)
    dataframe = dataframe.sort_values("fiscal_year").reset_index(drop=True)

    for column in NORMALIZED_LINE_ITEM_COLUMNS:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    _log_missing_line_items(dataframe)
    validate_normalized_annual_financials(dataframe)
    return dataframe


def validate_normalized_annual_financials(financials: pd.DataFrame) -> None:
    """Validate the normalized annual dataframe contract."""

    missing_columns = [
        column for column in NORMALIZED_FINANCIAL_COLUMNS if column not in financials.columns
    ]
    if missing_columns:
        raise ValueError(f"Normalized financials are missing columns: {missing_columns}")

    period_types = set(financials["period_type"].dropna().astype(str).str.lower())
    if period_types and period_types != {"annual"}:
        raise ValueError("Normalized financials must contain annual data only.")

    currencies = set(financials["currency"].dropna().astype(str))
    if len(currencies) > 1:
        raise ValueError("Normalized financials must use a single reporting currency.")


def _log_missing_line_items(financials: pd.DataFrame) -> None:
    """Log missing expected line items without failing normalization."""

    missing_columns = [
        column for column in NORMALIZED_LINE_ITEM_COLUMNS if financials[column].isna().all()
    ]
    if missing_columns:
        LOGGER.warning("Normalized financials are missing expected line items: %s", missing_columns)
