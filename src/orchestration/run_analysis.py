"""Runnable orchestration for one company analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.orchestration.service import classify_runtime_failure, resolve_company_profile, run_company_analysis
from src.providers.factory import ProviderRuntime, build_provider_runtime
from src.shared.schemas import AnalysisRequest


def run_analysis(
    request: AnalysisRequest,
    provider_runtime: ProviderRuntime | None = None,
    *,
    provider_backend: str | None = None,
    provider_data_dir: str | Path | None = None,
) -> dict[str, Path | str | float | int | None]:
    """Run the full MVP analysis pipeline for one company."""

    runtime = provider_runtime or build_provider_runtime(
        backend=provider_backend,
        data_dir=provider_data_dir,
    )
    return run_company_analysis(request, runtime)


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser used by the single-company entry point."""

    parser = argparse.ArgumentParser(description="Run company fundamental analysis.")
    parser.add_argument("--ticker", required=True, help="Ticker symbol, for example TSLA.")
    parser.add_argument("--company-name", default=None, help="Optional company name override.")
    parser.add_argument("--exchange", default=None, help="Optional exchange override.")
    parser.add_argument("--currency", default=None, help="Optional reporting currency override.")
    parser.add_argument(
        "--output-root",
        default="outputs",
        help="Root directory for generated reports, charts, and scorecards.",
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="Provider backend. Supported values: live, yfinance, akshare, json-directory.",
    )
    parser.add_argument(
        "--provider-data-dir",
        default=None,
        help="Directory containing per-ticker JSON provider files for json-directory mode.",
    )
    return parser


def main() -> None:
    """CLI entry point for running the single-company pipeline."""

    parser = build_parser()
    args = parser.parse_args()
    try:
        runtime = build_provider_runtime(backend=args.provider, data_dir=args.provider_data_dir)
        company = resolve_company_profile(
            ticker=args.ticker,
            provider_runtime=runtime,
            company_name=args.company_name,
            exchange=args.exchange,
            currency=args.currency,
        )
        artifacts = run_analysis(
            AnalysisRequest(company=company, output_root=Path(args.output_root)),
            provider_runtime=runtime,
        )
    except Exception as exc:  # noqa: BLE001
        failure_category, error_message = classify_runtime_failure(exc)
        raise SystemExit(f"{failure_category} error: {error_message}") from exc

    for name, path in artifacts.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
