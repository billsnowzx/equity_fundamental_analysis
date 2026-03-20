"""Tests for batch analysis orchestration and output generation."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.orchestration.run_batch_analysis import _parse_tickers, run_batch_analysis


def test_batch_smoke_with_partial_failure(repo_root, fixture_provider_runtime) -> None:
    output_root = repo_root / "tests" / "artifacts" / "batch_smoke"

    result = run_batch_analysis(
        tickers=["TSLA", "MSFT", "BAD"],
        output_root=output_root,
        provider_runtime=fixture_provider_runtime,
    )

    summary = result["summary"]
    assert result["summary_csv"].is_file()
    assert result["summary_json"].is_file()
    assert result["summary_md"].is_file()
    assert summary.loc[summary["ticker"] == "TSLA", "status"].item() == "success"
    assert summary.loc[summary["ticker"] == "MSFT", "status"].item() == "success"
    assert summary.loc[summary["ticker"] == "BAD", "status"].item() == "failed"
    assert summary.loc[summary["ticker"] == "BAD", "error"].item() is not None

    tsla_report = summary.loc[summary["ticker"] == "TSLA", "report_path"].item()
    msft_report = summary.loc[summary["ticker"] == "MSFT", "report_path"].item()
    assert Path(tsla_report).is_file()
    assert Path(msft_report).is_file()
    assert (output_root / "stocks" / "tsla" / "scorecards" / "tsla_scorecard.csv").is_file()
    assert (output_root / "stocks" / "msft" / "scorecards" / "msft_scorecard.csv").is_file()


def test_batch_top_n_reports_only_writes_ranked_subset(repo_root, fixture_provider_runtime) -> None:
    output_root = repo_root / "tests" / "artifacts" / "batch_top_n"

    result = run_batch_analysis(
        tickers=["TSLA", "MSFT"],
        output_root=output_root,
        provider_runtime=fixture_provider_runtime,
        top_n_reports=1,
    )

    summary = result["summary"]
    msft_row = summary.loc[summary["ticker"] == "MSFT"].iloc[0]
    tsla_row = summary.loc[summary["ticker"] == "TSLA"].iloc[0]

    assert result["reports_generated"] == 1
    assert msft_row["screen_rank"] == 1
    assert bool(msft_row["report_generated"])
    assert Path(msft_row["report_path"]).is_file()
    assert tsla_row["screen_rank"] == 2
    assert not bool(tsla_row["report_generated"])
    assert pd.isna(tsla_row["report_path"])
    assert not (output_root / "stocks" / "tsla" / "reports" / "tsla_analysis_report.md").exists()


def test_parse_tickers_from_csv_with_sector_filter(repo_root) -> None:
    ticker_file = repo_root / "tests" / "artifacts" / "sector_universe.csv"
    ticker_file.parent.mkdir(parents=True, exist_ok=True)
    ticker_file.write_text("ticker,sector\nTSLA,Automotive\nMSFT,Technology\nNVDA,Technology\n")

    tickers = _parse_tickers(None, str(ticker_file), sectors="Technology")

    assert tickers == ["MSFT", "NVDA"]


def test_parse_tickers_from_json_sector_map(repo_root) -> None:
    ticker_file = repo_root / "tests" / "artifacts" / "sector_map.json"
    ticker_file.parent.mkdir(parents=True, exist_ok=True)
    ticker_file.write_text(json.dumps({"Technology": ["MSFT", "NVDA"], "Automotive": ["TSLA"]}))

    tickers = _parse_tickers(None, str(ticker_file), sectors="Automotive")

    assert tickers == ["TSLA"]


def test_parse_tickers_from_named_watchlist(repo_root) -> None:
    watchlist_dir = repo_root / "config" / "watchlists"
    watchlist_dir.mkdir(parents=True, exist_ok=True)
    (watchlist_dir / "named_watchlist.csv").write_text("ticker,sector\nTSLA,Automotive\nMSFT,Technology\n")

    tickers = _parse_tickers(None, None, watchlist="named_watchlist", sectors="Technology")

    assert tickers == ["MSFT"]


def test_parse_tickers_rejects_sector_filter_for_plain_text(repo_root) -> None:
    ticker_file = repo_root / "tests" / "artifacts" / "tickers.txt"
    ticker_file.parent.mkdir(parents=True, exist_ok=True)
    ticker_file.write_text("TSLA\nMSFT\n")

    with pytest.raises(ValueError, match="Sector filtering requires"):
        _parse_tickers(None, str(ticker_file), sectors="Technology")


def test_batch_rejects_negative_top_n_reports(repo_root, fixture_provider_runtime) -> None:
    with pytest.raises(ValueError, match="top_n_reports"):
        run_batch_analysis(
            tickers=["TSLA"],
            output_root=repo_root / "tests" / "artifacts" / "invalid_top_n",
            provider_runtime=fixture_provider_runtime,
            top_n_reports=-1,
        )
