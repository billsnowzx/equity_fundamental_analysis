"""Batch stock analysis entry point."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.orchestration.service import (
    build_batch_summary_rows,
    persist_company_analysis_outputs,
    prepare_company_analysis,
    render_batch_summary_markdown,
    resolve_company_profile,
    summarize_company_analysis,
)
from src.providers.factory import ProviderRuntime, build_provider_runtime
from src.shared.schemas import AnalysisRequest, CompanyProfile


DEFAULT_WATCHLIST_DIR = Path("config") / "watchlists"
WATCHLIST_SUFFIXES = [".csv", ".tsv", ".json", ".txt", ".lst", ".tickers"]


def run_batch_analysis(
    tickers: list[str],
    output_root: str | Path,
    provider_runtime: ProviderRuntime | None = None,
    *,
    provider_backend: str | None = None,
    provider_data_dir: str | Path | None = None,
    top_n_reports: int | None = None,
) -> dict[str, Any]:
    """Run analysis for multiple tickers and persist a ranked batch summary."""

    if top_n_reports is not None and top_n_reports < 0:
        raise ValueError("top_n_reports must be zero or greater.")

    runtime = provider_runtime or build_provider_runtime(
        backend=provider_backend,
        data_dir=provider_data_dir,
    )
    root = Path(output_root)
    stocks_root = root / "stocks"
    stocks_root.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    successful_analyses: list[dict[str, Any]] = []
    for ticker in tickers:
        stock_output_root = stocks_root / ticker.lower()
        try:
            company = resolve_company_profile(ticker=ticker, provider_runtime=runtime)
            company = _ensure_batch_peer_list(company, tickers)
            request = AnalysisRequest(company=company, output_root=stock_output_root)
            analysis_context = prepare_company_analysis(request, runtime)
            result = summarize_company_analysis(request, analysis_context)
            results.append(result)
            successful_analyses.append(
                {
                    "ticker": ticker.upper(),
                    "request": request,
                    "analysis_context": analysis_context,
                    "result": result,
                }
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "ticker": ticker.upper(),
                    "company_name": ticker.upper(),
                    "status": "failed",
                    "overall_label": None,
                    "overall_score": None,
                    "price_to_earnings": None,
                    "ev_to_sales": None,
                    "fcf_yield": None,
                    "red_flag_count": None,
                    "screen_rank": None,
                    "report_generated": False,
                    "report_path": None,
                    "scorecard_csv": None,
                    "scorecard_json": None,
                    "red_flags_csv": None,
                    "metric_snapshot_csv": None,
                    "charts_dir": None,
                    "report_dir": None,
                    "scorecard_dir": None,
                    "error": str(exc),
                }
            )

    ranked_successes = sorted(
        successful_analyses,
        key=lambda item: (-float(item["result"]["overall_score"]), item["ticker"]),
    )
    for rank, item in enumerate(ranked_successes, start=1):
        item["result"]["screen_rank"] = rank

    if top_n_reports is None:
        report_targets = ranked_successes
    else:
        report_targets = ranked_successes[:top_n_reports]

    for item in report_targets:
        artifacts = persist_company_analysis_outputs(item["request"], item["analysis_context"])
        item["result"].update({name: str(path) for name, path in artifacts.items()})
        item["result"]["report_generated"] = True

    summary = build_batch_summary_rows(results)
    summary_csv = root / "batch_summary.csv"
    summary_json = root / "batch_summary.json"
    summary_md = root / "batch_summary.md"
    summary.to_csv(summary_csv, index=False)
    summary.to_json(summary_json, orient="records", indent=2)
    summary_md.write_text(render_batch_summary_markdown(summary))

    return {
        "summary": summary,
        "summary_csv": summary_csv,
        "summary_json": summary_json,
        "summary_md": summary_md,
        "stocks_root": stocks_root,
        "report_limit": top_n_reports,
        "reports_generated": len(report_targets),
    }


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser used by the batch entry point."""

    parser = argparse.ArgumentParser(description="Run batch fundamental analysis.")
    parser.add_argument(
        "--tickers",
        default=None,
        help="Comma-separated ticker list, for example AAPL,MSFT,NVDA.",
    )
    parser.add_argument(
        "--ticker-file",
        default=None,
        help="Optional file containing tickers. Supports txt, csv/tsv, and json formats.",
    )
    parser.add_argument(
        "--watchlist",
        default=None,
        help="Named watchlist in config/watchlists or an explicit watchlist file path.",
    )
    parser.add_argument(
        "--sectors",
        default=None,
        help="Optional comma-separated sector filter used with csv/json ticker files that include sector metadata.",
    )
    parser.add_argument(
        "--top-n-reports",
        type=int,
        default=None,
        help="Optional report cap. Screen every ticker, but only write full report artifacts for the top N successes.",
    )
    parser.add_argument(
        "--output-root",
        default="outputs",
        help="Root directory for generated batch outputs.",
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
    """CLI entry point for running batch analysis."""

    parser = build_parser()
    args = parser.parse_args()
    tickers = _parse_tickers(args.tickers, args.ticker_file, sectors=args.sectors, watchlist=args.watchlist)
    if not tickers:
        raise SystemExit("At least one ticker is required via --tickers, --ticker-file, or --watchlist.")

    result = run_batch_analysis(
        tickers=tickers,
        output_root=args.output_root,
        provider_backend=args.provider,
        provider_data_dir=args.provider_data_dir,
        top_n_reports=args.top_n_reports,
    )
    _print_ranked_summary(result["summary"])
    print(f"reports_generated: {result['reports_generated']}")
    print(f"batch_summary_csv: {result['summary_csv']}")
    print(f"batch_summary_json: {result['summary_json']}")
    print(f"batch_summary_md: {result['summary_md']}")

    summary = result["summary"]
    if not summary.empty and (summary["status"] == "success").sum() == 0:
        raise SystemExit(1)


def _ensure_batch_peer_list(company: CompanyProfile, tickers: list[str]) -> CompanyProfile:
    if company.peer_list:
        return company
    peer_list = [ticker.upper() for ticker in tickers if ticker.upper() != company.ticker.upper()]
    return CompanyProfile(
        ticker=company.ticker,
        company_name=company.company_name,
        exchange=company.exchange,
        reporting_currency=company.reporting_currency,
        peer_list=peer_list,
    )


def _parse_tickers(
    tickers_arg: str | None,
    ticker_file: str | None,
    *,
    sectors: str | None = None,
    watchlist: str | None = None,
) -> list[str]:
    values: list[str] = []
    sector_filter = _parse_sector_filter(sectors)

    if tickers_arg:
        values.extend([ticker.strip().upper() for ticker in tickers_arg.split(",") if ticker.strip()])
    if ticker_file:
        values.extend(_load_tickers_from_file(Path(ticker_file), sector_filter))
    if watchlist:
        values.extend(_load_tickers_from_watchlist(watchlist, sector_filter))

    deduped: list[str] = []
    seen: set[str] = set()
    for ticker in values:
        if ticker not in seen:
            seen.add(ticker)
            deduped.append(ticker)
    return deduped


def _load_tickers_from_watchlist(watchlist: str, sector_filter: set[str]) -> list[str]:
    return _load_tickers_from_file(_resolve_watchlist_path(watchlist), sector_filter)


def _resolve_watchlist_path(watchlist: str) -> Path:
    candidate = Path(watchlist)
    search_paths: list[Path] = []

    if candidate.is_file():
        return candidate

    if not candidate.is_absolute():
        search_paths.append(DEFAULT_WATCHLIST_DIR / candidate)
        if not candidate.suffix:
            for suffix in WATCHLIST_SUFFIXES:
                search_paths.append(DEFAULT_WATCHLIST_DIR / f"{watchlist}{suffix}")

    for path in search_paths:
        if path.is_file():
            return path

    raise ValueError(f"Watchlist not found: {watchlist}")


def _load_tickers_from_file(path: Path, sector_filter: set[str]) -> list[str]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".lst", ".tickers", ""}:
        if sector_filter:
            raise ValueError("Sector filtering requires csv, tsv, or json ticker files with sector metadata.")
        return [line.strip().upper() for line in path.read_text().splitlines() if line.strip() and not line.strip().startswith("#")]
    if suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        return _load_tickers_from_delimited_file(path, delimiter, sector_filter)
    if suffix == ".json":
        return _load_tickers_from_json(path, sector_filter)
    raise ValueError(f"Unsupported ticker-file format: {path}")


def _load_tickers_from_delimited_file(path: Path, delimiter: str, sector_filter: set[str]) -> list[str]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        fieldnames = {name.lower(): name for name in (reader.fieldnames or [])}
        ticker_column = fieldnames.get("ticker") or fieldnames.get("symbol")
        sector_column = fieldnames.get("sector") or fieldnames.get("industry_group")
        if ticker_column is None:
            raise ValueError(f"Ticker file must include a ticker or symbol column: {path}")
        if sector_filter and sector_column is None:
            raise ValueError(f"Sector filtering requires a sector column in: {path}")

        values: list[str] = []
        for row in reader:
            ticker = (row.get(ticker_column) or "").strip().upper()
            if not ticker:
                continue
            row_sector = (row.get(sector_column) or "").strip().lower() if sector_column else ""
            if sector_filter and row_sector not in sector_filter:
                continue
            values.append(ticker)
        return values


def _load_tickers_from_json(path: Path, sector_filter: set[str]) -> list[str]:
    payload = json.loads(path.read_text())
    values: list[str] = []

    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, str):
                if sector_filter:
                    raise ValueError(f"Sector filtering requires sector metadata in JSON ticker file: {path}")
                values.append(item.strip().upper())
            elif isinstance(item, dict):
                ticker = str(item.get("ticker") or item.get("symbol") or "").strip().upper()
                if not ticker:
                    continue
                item_sector = str(item.get("sector") or item.get("industry_group") or "").strip().lower()
                if sector_filter and item_sector not in sector_filter:
                    continue
                values.append(ticker)
            else:
                raise ValueError(f"Unsupported JSON ticker item in {path}: {item!r}")
        return values

    if isinstance(payload, dict):
        for sector_name, sector_tickers in payload.items():
            normalized_sector = str(sector_name).strip().lower()
            if sector_filter and normalized_sector not in sector_filter:
                continue
            if not isinstance(sector_tickers, list):
                raise ValueError(f"Sector map entries must contain ticker lists in {path}")
            values.extend([str(ticker).strip().upper() for ticker in sector_tickers if str(ticker).strip()])
        return values

    raise ValueError(f"Unsupported JSON ticker file structure: {path}")


def _parse_sector_filter(sectors: str | None) -> set[str]:
    if not sectors:
        return set()
    return {sector.strip().lower() for sector in sectors.split(",") if sector.strip()}


def _print_ranked_summary(summary: pd.DataFrame) -> None:
    if summary.empty:
        print("No batch results were produced.")
        return
    ranked_columns = [
        column
        for column in [
            "screen_rank",
            "ticker",
            "status",
            "overall_label",
            "overall_score",
            "red_flag_count",
            "report_generated",
            "report_path",
            "error",
        ]
        if column in summary.columns
    ]
    print(summary[ranked_columns].to_string(index=False))


if __name__ == "__main__":
    main()



