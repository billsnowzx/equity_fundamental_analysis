"""Financial statement ingestion placeholders."""

from __future__ import annotations

from collections.abc import Sequence

from src.providers.base import FinancialStatementsProvider
from src.shared.schemas import CompanyProfile, FinancialStatementRecord


class FinancialStatementIngestionService:
    """Small wrapper around a provider interface for annual statements."""

    def __init__(self, provider: FinancialStatementsProvider) -> None:
        self._provider = provider

    def load_annual_financials(
        self,
        company: CompanyProfile,
    ) -> Sequence[FinancialStatementRecord]:
        """Return provider data without imposing vendor-specific assumptions."""

        return self._provider.get_annual_financial_statements(company)
