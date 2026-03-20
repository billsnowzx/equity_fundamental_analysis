"""Shared pytest fixtures for repository validation and analysis tests."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.processing.normalize_financials import normalize_annual_financials
from src.providers.factory import build_provider_runtime
from src.shared.schemas import FinancialStatementRecord


@pytest.fixture()
def repo_root() -> Path:
    """Return the repository root for filesystem assertions."""

    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def fixture_data_dir(repo_root: Path) -> Path:
    """Return the repo-local JSON provider directory used in tests."""

    return repo_root / "data" / "fixtures"


@pytest.fixture()
def fixture_provider_runtime(fixture_data_dir):
    """Return the configured json-directory provider runtime used across tests."""

    return build_provider_runtime(backend="json-directory", data_dir=fixture_data_dir)


@pytest.fixture()
def tesla_statement_records(repo_root: Path) -> list[FinancialStatementRecord]:
    """Load deterministic Tesla-shaped annual financial records."""

    fixture_path = repo_root / "tests" / "fixtures" / "tesla_annual_financials.json"
    payload = json.loads(fixture_path.read_text())
    return [FinancialStatementRecord(**item) for item in payload]


@pytest.fixture()
def tesla_normalized_financials(tesla_statement_records) -> object:
    """Return the normalized Tesla annual dataframe used across tests."""

    return normalize_annual_financials(tesla_statement_records)


@pytest.fixture()
def tesla_market_data(repo_root: Path) -> pd.DataFrame:
    """Load Tesla market data fixture for valuation and orchestration tests."""

    payload = json.loads((repo_root / "data" / "fixtures" / "tsla_market_data.json").read_text())
    return pd.DataFrame(payload)


@pytest.fixture()
def tesla_shares_outstanding(repo_root: Path) -> pd.DataFrame:
    """Load Tesla shares outstanding fixture for valuation and red-flag tests."""

    payload = json.loads((repo_root / "data" / "fixtures" / "tsla_shares_outstanding.json").read_text())
    return pd.DataFrame(payload)


@pytest.fixture()
def tesla_peer_multiples(repo_root: Path) -> pd.DataFrame:
    """Load Tesla peer multiples fixture for valuation tests."""

    payload = json.loads((repo_root / "data" / "fixtures" / "tsla_peer_multiples.json").read_text())
    return pd.DataFrame(payload)
