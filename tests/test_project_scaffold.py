"""Phase 1 verification tests for scaffold and import health."""

from __future__ import annotations

from importlib import import_module

from src.shared.schemas import AnalysisRequest, CompanyProfile


def test_required_directories_exist(repo_root) -> None:
    expected_directories = [
        "config",
        "data",
        "data/raw",
        "data/processed",
        "data/cache",
        "data/fixtures",
        "outputs",
        "outputs/reports",
        "outputs/charts",
        "outputs/scorecards",
        "src",
        "tests",
        "tests/fixtures",
    ]

    for relative_path in expected_directories:
        assert (repo_root / relative_path).is_dir()


def test_required_project_files_exist(repo_root) -> None:
    expected_files = [
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "src/shared/schemas.py",
        "src/providers/base.py",
        "src/processing/normalize_financials.py",
        "src/orchestration/run_analysis.py",
    ]

    for relative_path in expected_files:
        assert (repo_root / relative_path).is_file()


def test_placeholder_modules_import() -> None:
    module_names = [
        "src.shared.schemas",
        "src.providers.base",
        "src.ingestion.base",
        "src.ingestion.financials",
        "src.ingestion.market_data",
        "src.processing.normalize_financials",
        "src.analysis.revenue_analysis",
        "src.analysis.profitability",
        "src.analysis.returns",
        "src.analysis.balance_sheet",
        "src.analysis.cashflow",
        "src.analysis.valuation",
        "src.analysis.red_flags",
        "src.analysis.scoring",
        "src.analysis.thesis_builder",
        "src.reporting.charts",
        "src.reporting.report_generator",
        "src.orchestration.run_analysis",
    ]

    for module_name in module_names:
        assert import_module(module_name) is not None


def test_analysis_request_uses_pathlib_defaults() -> None:
    company = CompanyProfile(
        ticker="TSLA",
        company_name="Tesla, Inc.",
        exchange="NASDAQ",
        reporting_currency="USD",
    )

    request = AnalysisRequest(company=company)

    assert request.output_root.name == "outputs"
