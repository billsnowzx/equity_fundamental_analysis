"""Abstract provider contracts for external data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any

from src.shared.schemas import (
    CompanyProfile,
    FinancialStatementRecord,
    MarketDataPoint,
    PeerMultipleRecord,
    SharesOutstandingRecord,
)


class FinancialStatementsProvider(ABC):
    """Supplies annual company financial statements."""

    @abstractmethod
    def get_annual_financial_statements(
        self,
        company: CompanyProfile,
    ) -> Sequence[FinancialStatementRecord]:
        """Return annual statements for the requested company."""


class MarketDataProvider(ABC):
    """Supplies historical market price data."""

    @abstractmethod
    def get_historical_prices(self, company: CompanyProfile) -> Sequence[MarketDataPoint]:
        """Return historical market prices for the requested company."""


class SharesOutstandingProvider(ABC):
    """Supplies shares-outstanding history."""

    @abstractmethod
    def get_shares_outstanding(
        self,
        company: CompanyProfile,
    ) -> Sequence[SharesOutstandingRecord]:
        """Return shares-outstanding history for the requested company."""


class PeerMultiplesProvider(ABC):
    """Supplies optional peer valuation multiples."""

    @abstractmethod
    def get_peer_multiples(self, company: CompanyProfile) -> Sequence[PeerMultipleRecord]:
        """Return peer valuation multiples for the requested company."""


class CompanyProfileResolver(ABC):
    """Resolves optional company metadata defaults from a provider backend."""

    @abstractmethod
    def resolve_profile_defaults(self, ticker: str) -> Mapping[str, Any]:
        """Return default profile fields for a ticker."""
