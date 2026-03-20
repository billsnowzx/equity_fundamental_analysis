"""Market data ingestion placeholders."""

from __future__ import annotations

from collections.abc import Sequence

from src.providers.base import MarketDataProvider, SharesOutstandingProvider
from src.shared.schemas import CompanyProfile, MarketDataPoint, SharesOutstandingRecord


class MarketDataIngestionService:
    """Wrapper around provider interfaces for market inputs."""

    def __init__(
        self,
        market_data_provider: MarketDataProvider,
        shares_provider: SharesOutstandingProvider | None = None,
    ) -> None:
        self._market_data_provider = market_data_provider
        self._shares_provider = shares_provider

    def load_historical_prices(self, company: CompanyProfile) -> Sequence[MarketDataPoint]:
        """Return market price observations for a company."""

        return self._market_data_provider.get_historical_prices(company)

    def load_shares_outstanding(
        self,
        company: CompanyProfile,
    ) -> Sequence[SharesOutstandingRecord]:
        """Return shares-outstanding history when a provider is configured."""

        if self._shares_provider is None:
            return []
        return self._shares_provider.get_shares_outstanding(company)
