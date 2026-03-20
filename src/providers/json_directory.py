"""JSON-directory provider adapters for deterministic offline datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.providers.base import (
    CompanyProfileResolver,
    FinancialStatementsProvider,
    MarketDataProvider,
    PeerMultiplesProvider,
    SharesOutstandingProvider,
)
from src.providers.errors import ProviderDataError
from src.shared.schemas import (
    CompanyProfile,
    FinancialStatementRecord,
    MarketDataPoint,
    PeerMultipleRecord,
    SharesOutstandingRecord,
)


class JsonDirectoryFinancialStatementsProvider(FinancialStatementsProvider):
    """Load annual financial statements from per-ticker JSON files."""

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir

    def get_annual_financial_statements(
        self,
        company: CompanyProfile,
    ) -> list[FinancialStatementRecord]:
        payload = _read_required_json(self._data_dir / f"{company.ticker.lower()}_annual_financials.json")
        records = [FinancialStatementRecord(**item) for item in payload]
        if not records:
            raise ProviderDataError(f"No annual financial statements found for {company.ticker}.")
        return records


class JsonDirectoryMarketDataProvider(MarketDataProvider):
    """Load market data from per-ticker JSON files."""

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir

    def get_historical_prices(self, company: CompanyProfile) -> list[MarketDataPoint]:
        payload = _read_required_json(self._data_dir / f"{company.ticker.lower()}_market_data.json")
        records = [MarketDataPoint(**item) for item in payload]
        if not records:
            raise ProviderDataError(f"No market data found for {company.ticker}.")
        return records


class JsonDirectorySharesOutstandingProvider(SharesOutstandingProvider):
    """Load shares-outstanding data from per-ticker JSON files."""

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir

    def get_shares_outstanding(self, company: CompanyProfile) -> list[SharesOutstandingRecord]:
        payload = _read_required_json(self._data_dir / f"{company.ticker.lower()}_shares_outstanding.json")
        records = [SharesOutstandingRecord(**item) for item in payload]
        if not records:
            raise ProviderDataError(f"No shares outstanding data found for {company.ticker}.")
        return records


class JsonDirectoryPeerMultiplesProvider(PeerMultiplesProvider):
    """Load optional peer multiples from per-ticker JSON files."""

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir

    def get_peer_multiples(self, company: CompanyProfile) -> list[PeerMultipleRecord]:
        path = self._data_dir / f"{company.ticker.lower()}_peer_multiples.json"
        if not path.exists():
            return []
        payload = json.loads(path.read_text())
        return [PeerMultipleRecord(**item) for item in payload]


class JsonDirectoryCompanyProfileResolver(CompanyProfileResolver):
    """Resolve optional company-profile metadata from JSON configuration."""

    def __init__(self, data_dir: Path) -> None:
        self._profiles_path = data_dir / "company_profiles.json"

    def resolve_profile_defaults(self, ticker: str) -> dict[str, Any]:
        if not self._profiles_path.exists():
            return {}
        profiles = json.loads(self._profiles_path.read_text())
        return profiles.get(ticker.upper(), {})


def _read_required_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise ProviderDataError(f"Required provider file is missing: {path}")
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise ProviderDataError(f"Provider file must contain a list payload: {path}")
    return payload
