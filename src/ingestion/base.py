"""Base ingestion service abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.shared.schemas import CompanyDataBundle, CompanyProfile


class BaseIngestionService(ABC):
    """Defines the contract for ingesting provider data into a shared bundle."""

    @abstractmethod
    def load(self, company: CompanyProfile) -> CompanyDataBundle:
        """Load provider data for one company."""
