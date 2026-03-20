# Equity Fundamental Analysis

Modular, provider-agnostic Python tooling for listed-company fundamental analysis.

The project supports:
- single-stock analysis
- batch screening and ranked summaries
- reusable watchlists
- US live analysis through Yahoo Finance
- mainland China A-share analysis through AkShare
- deterministic fixture-backed runs for testing and development

## What It Produces

For each successful stock run, the pipeline can generate:
- a markdown report
- scorecard CSV and JSON files
- red-flag and metric snapshot CSV files
- chart images

For batch runs, the pipeline also writes:
- `batch_summary.csv`
- `batch_summary.json`
- `batch_summary.md`

## Repository Layout

- `src/` contains providers, normalization, analysis, scoring, reporting, and orchestration
- `tests/` contains pytest coverage for metrics, normalization, providers, batch workflows, and report generation
- `config/watchlists/` contains reusable stock universes for batch runs
- `data/fixtures/` contains deterministic sample provider data and sample ticker universes
- `outputs/` stores generated summaries, reports, charts, and scorecards
- `.agents/skills/` contains repo-local Codex skills

## Requirements

- Python 3.11+
- `pandas` for tabular financial outputs
- provider-specific packages from `requirements.txt`

## Setup

```powershell
python -m pip install -r requirements.txt
```

## Run Tests

```powershell
python -m pytest
```

## Provider Backends

Supported provider modes:
- `json-directory`
- `live`
- `yfinance`
- `akshare`

Behavior:
- `json-directory` reads local per-ticker JSON files from a configured directory
- `live` uses the Yahoo Finance live adapter
- `yfinance` is an explicit alias for the same Yahoo Finance adapter
- `akshare` targets mainland China A-shares using AkShare-backed statements, prices, company profiles, shares outstanding, and peer multiples

Environment variables:
- `EFA_PROVIDER_BACKEND`
- `EFA_PROVIDER_DATA_DIR`

## Quick Start

Fixture-backed Tesla run:

```powershell
python -m src.orchestration.run_analysis --ticker TSLA --provider json-directory --provider-data-dir data/fixtures --output-root outputs
```

US live run:

```powershell
python -m src.orchestration.run_analysis --ticker MSFT --provider live --output-root outputs
```

China A-share live run:

```powershell
python -m src.orchestration.run_analysis --ticker 600519 --provider akshare --output-root outputs/china_akshare
```

## Batch Workflows

Direct ticker list:

```powershell
python -m src.orchestration.run_batch_analysis --tickers TSLA,MSFT --provider json-directory --provider-data-dir data/fixtures --output-root outputs
```

Ticker file:

```powershell
python -m src.orchestration.run_batch_analysis --ticker-file data/fixtures/sample_sector_universe.csv --provider json-directory --provider-data-dir data/fixtures --output-root outputs
```

Named watchlist:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_us_watchlist --provider live --output-root outputs
```

China watchlist:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist china_consumer_watchlist --provider akshare --output-root outputs/china_batch
```

Sector filter:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_sector_watchlist --sectors Technology --provider json-directory --provider-data-dir data/fixtures --output-root outputs
```

Top-N report generation after screening:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_us_watchlist --provider json-directory --provider-data-dir data/fixtures --top-n-reports 1 --output-root outputs/watchlist_batch
```

When `--top-n-reports` is set, every ticker is still screened and ranked, but only the highest-ranked successful names receive full report artifacts.

## Watchlists

Use `config/watchlists/` for reusable stock universes you want to keep outside test fixtures.

Supported watchlist formats:
- plain text: one ticker per line
- CSV or TSV: `ticker` or `symbol`, optional `sector`
- JSON list: strings or objects with `ticker` and optional `sector`
- JSON sector map: `{ "Technology": ["MSFT", "NVDA"] }`

Sample watchlists:
- `config/watchlists/sample_us_watchlist.csv`
- `config/watchlists/sample_sector_watchlist.json`
- `config/watchlists/china_consumer_watchlist.csv`

## Output Layout

Batch outputs:
- `outputs/batch_summary.csv`
- `outputs/batch_summary.json`
- `outputs/batch_summary.md`

Per-stock outputs:
- `outputs/stocks/<ticker>/reports/`
- `outputs/stocks/<ticker>/charts/`
- `outputs/stocks/<ticker>/scorecards/`

Single-stock outputs use the same report, chart, and scorecard structure under the selected output root.

## Repo-Local Skill

Use `.agents/skills/batch-stock-analysis/` when you want Codex to run the repository workflow without repeating the repo instructions in every prompt.

## Current Limitations

- The Yahoo Finance live adapter depends on upstream response shape and network availability.
- The `akshare` backend is currently limited to mainland Shanghai and Shenzhen A-shares.
- China live runs depend on AkShare source stability and endpoint availability.
- Transcript parsing and annual report PDF parsing are intentionally out of scope.
- The shipped JSON datasets are deterministic development fixtures, not canonical market feeds.
- Provider-reported statement units are not normalized to one narrative display unit, so report prose avoids potentially misleading absolute-money narration.
