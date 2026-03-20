"""Shared data contracts used across the analysis pipeline."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field

Numeric = float | int
LineItemMap = dict[str, Numeric | None]


class CompanyProfile(BaseModel):
    """Core company identifiers used throughout the pipeline."""

    ticker: str
    company_name: str
    exchange: str
    reporting_currency: str
    peer_list: list[str] = Field(default_factory=list)


class FinancialStatementRecord(BaseModel):
    """Represents one annual company statement for one reporting period."""

    period_end: date
    fiscal_year: int
    period_type: str = "annual"
    statement_type: str
    currency: str
    values: LineItemMap = Field(default_factory=dict)


class MarketDataPoint(BaseModel):
    """Represents one historical price observation."""

    date: date
    close: Numeric
    volume: Numeric | None = None
    currency: str | None = None


class SharesOutstandingRecord(BaseModel):
    """Represents the share count for a reporting date."""

    date: date
    shares_outstanding: Numeric


class PeerMultipleRecord(BaseModel):
    """Represents simple peer valuation multiple data."""

    ticker: str
    pe: Numeric | None = None
    pb: Numeric | None = None
    ev_to_ebitda: Numeric | None = None
    ev_to_sales: Numeric | None = None


class CompanyDataBundle(BaseModel):
    """Aggregates provider outputs before normalization and analysis."""

    company: CompanyProfile
    financial_statements: list[FinancialStatementRecord] = Field(default_factory=list)
    market_prices: list[MarketDataPoint] = Field(default_factory=list)
    shares_outstanding: list[SharesOutstandingRecord] = Field(default_factory=list)
    peer_multiples: list[PeerMultipleRecord] = Field(default_factory=list)


class AnalysisRequest(BaseModel):
    """Input contract for an analysis entry point."""

    company: CompanyProfile
    output_root: Path = Path("outputs")
    as_of_date: date | None = None
