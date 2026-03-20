"""Factory helpers for provider runtime selection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.providers.akshare_cn import (
    AkShareAStockCompanyProfileResolver,
    AkShareAStockFinancialStatementsProvider,
    AkShareAStockMarketDataProvider,
    AkShareAStockPeerMultiplesProvider,
    AkShareAStockSharesOutstandingProvider,
)
from src.providers.base import (
    CompanyProfileResolver,
    FinancialStatementsProvider,
    MarketDataProvider,
    PeerMultiplesProvider,
    SharesOutstandingProvider,
)
from src.providers.config import resolve_provider_runtime_config
from src.providers.errors import ProviderConfigurationError
from src.providers.json_directory import (
    JsonDirectoryCompanyProfileResolver,
    JsonDirectoryFinancialStatementsProvider,
    JsonDirectoryMarketDataProvider,
    JsonDirectoryPeerMultiplesProvider,
    JsonDirectorySharesOutstandingProvider,
)
from src.providers.yfinance_live import (
    YFinanceCompanyProfileResolver,
    YFinanceFinancialStatementsProvider,
    YFinanceMarketDataProvider,
    YFinancePeerMultiplesProvider,
    YFinanceSharesOutstandingProvider,
)


@dataclass(frozen=True)
class ProviderRuntime:
    """Resolved provider bundle used by orchestration."""

    backend: str
    financial_statements_provider: FinancialStatementsProvider
    market_data_provider: MarketDataProvider
    shares_outstanding_provider: SharesOutstandingProvider
    peer_multiples_provider: PeerMultiplesProvider
    company_profile_resolver: CompanyProfileResolver | None = None


def build_provider_runtime(
    backend: str | None = None,
    data_dir: str | Path | None = None,
) -> ProviderRuntime:
    """Build a provider runtime from configuration inputs."""

    config = resolve_provider_runtime_config(backend=backend, data_dir=data_dir)

    if config.backend == "json-directory":
        if config.data_dir is None:
            raise ProviderConfigurationError(
                "The json-directory backend requires EFA_PROVIDER_DATA_DIR or --provider-data-dir."
            )
        return ProviderRuntime(
            backend=config.backend,
            financial_statements_provider=JsonDirectoryFinancialStatementsProvider(config.data_dir),
            market_data_provider=JsonDirectoryMarketDataProvider(config.data_dir),
            shares_outstanding_provider=JsonDirectorySharesOutstandingProvider(config.data_dir),
            peer_multiples_provider=JsonDirectoryPeerMultiplesProvider(config.data_dir),
            company_profile_resolver=JsonDirectoryCompanyProfileResolver(config.data_dir),
        )

    if config.backend in {"live", "yfinance"}:
        return build_yfinance_provider_runtime()

    if config.backend == "akshare":
        return build_akshare_provider_runtime()

    raise ProviderConfigurationError(
        f"Unsupported provider backend '{config.backend}'. Supported backends: live, yfinance, akshare, json-directory."
    )


def build_yfinance_provider_runtime() -> ProviderRuntime:
    """Build the live runtime backed by Yahoo Finance."""

    return ProviderRuntime(
        backend="yfinance",
        financial_statements_provider=YFinanceFinancialStatementsProvider(),
        market_data_provider=YFinanceMarketDataProvider(),
        shares_outstanding_provider=YFinanceSharesOutstandingProvider(),
        peer_multiples_provider=YFinancePeerMultiplesProvider(),
        company_profile_resolver=YFinanceCompanyProfileResolver(),
    )


def build_akshare_provider_runtime() -> ProviderRuntime:
    """Build the mainland China A-share runtime backed by AkShare."""

    return ProviderRuntime(
        backend="akshare",
        financial_statements_provider=AkShareAStockFinancialStatementsProvider(),
        market_data_provider=AkShareAStockMarketDataProvider(),
        shares_outstanding_provider=AkShareAStockSharesOutstandingProvider(),
        peer_multiples_provider=AkShareAStockPeerMultiplesProvider(),
        company_profile_resolver=AkShareAStockCompanyProfileResolver(),
    )
