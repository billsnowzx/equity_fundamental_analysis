"""Tests for the normalized annual financial dataframe contract."""

from __future__ import annotations

import pandas as pd
import pytest

from src.processing.normalize_financials import (
    NORMALIZED_FINANCIAL_COLUMNS,
    normalize_annual_financials,
    validate_normalized_annual_financials,
)


def test_normalize_annual_financials_contract(tesla_normalized_financials) -> None:
    financials = tesla_normalized_financials

    assert list(financials.columns) == NORMALIZED_FINANCIAL_COLUMNS
    assert financials["fiscal_year"].tolist() == [2019, 2020, 2021, 2022, 2023, 2024]
    assert set(financials["period_type"].tolist()) == {"annual"}
    assert set(financials["currency"].tolist()) == {"USD"}
    assert financials.loc[financials["fiscal_year"] == 2022, "revenue"].item() == 81462
    assert financials.loc[financials["fiscal_year"] == 2024, "operating_cash_flow"].item() == 15000


def test_normalize_rejects_mixed_currency(tesla_statement_records) -> None:
    conflicting_record = tesla_statement_records[0].model_copy(update={"currency": "EUR"})

    with pytest.raises(ValueError, match="single reporting currency"):
        normalize_annual_financials([conflicting_record, *tesla_statement_records[1:]])


def test_normalize_rejects_non_annual_records(tesla_statement_records) -> None:
    quarterly_record = tesla_statement_records[0].model_copy(update={"period_type": "quarterly"})

    with pytest.raises(ValueError, match="annual statement records only"):
        normalize_annual_financials([quarterly_record, *tesla_statement_records[1:]])


def test_validate_normalized_financials_rejects_missing_columns(tesla_normalized_financials) -> None:
    invalid = tesla_normalized_financials.drop(columns=["revenue"])

    with pytest.raises(ValueError, match="missing columns"):
        validate_normalized_annual_financials(invalid)


def test_normalize_empty_records_returns_empty_contract() -> None:
    financials = normalize_annual_financials([])

    assert financials.empty
    assert list(financials.columns) == NORMALIZED_FINANCIAL_COLUMNS
    validate_normalized_annual_financials(financials)
