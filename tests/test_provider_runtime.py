"""Tests for provider configuration and provider-backed runtime failures."""

from __future__ import annotations

import pytest

from src.orchestration.run_analysis import run_analysis
from src.providers.base import FinancialStatementsProvider, MarketDataProvider, PeerMultiplesProvider, SharesOutstandingProvider
from src.providers.errors import ProviderConfigurationError, ProviderDataError
from src.providers.factory import ProviderRuntime, build_provider_runtime
from src.shared.schemas import AnalysisRequest, CompanyProfile, FinancialStatementRecord, MarketDataPoint, SharesOutstandingRecord


class StaticFinancialsProvider(FinancialStatementsProvider):
    def __init__(self, records):
        self._records = records

    def get_annual_financial_statements(self, company: CompanyProfile):
        return self._records


class StaticMarketDataProvider(MarketDataProvider):
    def get_historical_prices(self, company: CompanyProfile):
        return [MarketDataPoint(date="2024-12-31", close=100.0, currency="USD")]


class StaticSharesProvider(SharesOutstandingProvider):
    def get_shares_outstanding(self, company: CompanyProfile):
        return [SharesOutstandingRecord(date="2024-12-31", shares_outstanding=1000)]


class EmptyPeerProvider(PeerMultiplesProvider):
    def get_peer_multiples(self, company: CompanyProfile):
        return []


@pytest.fixture()
def base_company() -> CompanyProfile:
    return CompanyProfile(
        ticker="TEST",
        company_name="Test Corp",
        exchange="NASDAQ",
        reporting_currency="USD",
    )


def test_build_provider_runtime_requires_installed_live_dependency(monkeypatch) -> None:
    monkeypatch.delenv("EFA_PROVIDER_BACKEND", raising=False)
    monkeypatch.delenv("EFA_PROVIDER_DATA_DIR", raising=False)
    monkeypatch.setattr(
        "src.providers.yfinance_live.importlib.import_module",
        lambda name: (_ for _ in ()).throw(ImportError("missing")),
    )

    with pytest.raises(ProviderConfigurationError, match="yfinance live provider is not installed"):
        build_provider_runtime()


def test_build_provider_runtime_requires_installed_akshare_dependency(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.providers.akshare_cn.importlib.import_module",
        lambda name: (_ for _ in ()).throw(ImportError("missing")),
    )

    with pytest.raises(ProviderConfigurationError, match="akshare provider is not installed"):
        build_provider_runtime(backend="akshare")


def test_json_directory_backend_requires_data_dir() -> None:
    with pytest.raises(ProviderConfigurationError, match="provider-data-dir"):
        build_provider_runtime(backend="json-directory")


def test_run_analysis_rejects_missing_required_annual_data(base_company, repo_root) -> None:
    runtime = ProviderRuntime(
        backend="static",
        financial_statements_provider=StaticFinancialsProvider([]),
        market_data_provider=StaticMarketDataProvider(),
        shares_outstanding_provider=StaticSharesProvider(),
        peer_multiples_provider=EmptyPeerProvider(),
        company_profile_resolver=None,
    )
    request = AnalysisRequest(company=base_company, output_root=repo_root / "tests" / "artifacts" / "provider_missing")

    with pytest.raises(ProviderDataError, match="No annual financial statements"):
        run_analysis(request, provider_runtime=runtime)


def test_run_analysis_rejects_mixed_currency(base_company, repo_root) -> None:
    runtime = ProviderRuntime(
        backend="static",
        financial_statements_provider=StaticFinancialsProvider(
            [
                FinancialStatementRecord(
                    period_end="2024-12-31",
                    fiscal_year=2024,
                    period_type="annual",
                    statement_type="income_statement",
                    currency="USD",
                    values={"revenue": 100, "net_income": 10},
                ),
                FinancialStatementRecord(
                    period_end="2024-12-31",
                    fiscal_year=2024,
                    period_type="annual",
                    statement_type="balance_sheet",
                    currency="EUR",
                    values={"total_assets": 100, "total_equity": 50, "current_assets": 60, "current_liabilities": 20, "cash_and_equivalents": 10, "total_debt": 5},
                ),
            ]
        ),
        market_data_provider=StaticMarketDataProvider(),
        shares_outstanding_provider=StaticSharesProvider(),
        peer_multiples_provider=EmptyPeerProvider(),
        company_profile_resolver=None,
    )
    request = AnalysisRequest(company=base_company, output_root=repo_root / "tests" / "artifacts" / "provider_currency")

    with pytest.raises(ValueError, match="single reporting currency"):
        run_analysis(request, provider_runtime=runtime)


def test_run_analysis_rejects_non_annual_provider_records(base_company, repo_root) -> None:
    runtime = ProviderRuntime(
        backend="static",
        financial_statements_provider=StaticFinancialsProvider(
            [
                FinancialStatementRecord(
                    period_end="2024-09-30",
                    fiscal_year=2024,
                    period_type="quarterly",
                    statement_type="income_statement",
                    currency="USD",
                    values={"revenue": 100, "net_income": 10},
                )
            ]
        ),
        market_data_provider=StaticMarketDataProvider(),
        shares_outstanding_provider=StaticSharesProvider(),
        peer_multiples_provider=EmptyPeerProvider(),
        company_profile_resolver=None,
    )
    request = AnalysisRequest(company=base_company, output_root=repo_root / "tests" / "artifacts" / "provider_period")

    with pytest.raises(ValueError, match="annual statement records only"):
        run_analysis(request, provider_runtime=runtime)
