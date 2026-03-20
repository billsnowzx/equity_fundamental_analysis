# Equity Fundamental Analysis

Modular, provider-agnostic Python tooling for listed-company fundamental analysis.

The repository supports both single-stock analysis and batch stock screening/report generation through provider-backed orchestration.

## Repository Layout

- `src/` contains provider adapters, normalization, analysis, reporting, and orchestration
- `tests/` contains pytest coverage for normalization, metrics, provider runtime, live adapter mapping, batch execution, watchlists, top-N report generation, and AkShare A-share mapping
- `config/watchlists/` contains reusable stock universes for batch runs
- `data/fixtures/` contains runnable sample JSON data for `json-directory` mode plus sample ticker universes
- `outputs/` stores generated batch summaries, reports, charts, and scorecards
- `.agents/skills/` contains repo-local Codex skills

## Setup

```powershell
python -m pip install -r requirements.txt
```

## Run Tests

```powershell
python -m pytest
```

## Provider Modes

Supported provider backends:
- `live`
- `yfinance`
- `akshare`
- `json-directory`

Current behavior:
- `live` uses the concrete Yahoo Finance adapter
- `yfinance` is an explicit alias for the same live adapter
- `akshare` targets mainland China A-shares through AkShare-backed statement, price, profile, share-capital, and peer-multiple adapters
- `json-directory` is the runnable sample mode and reads per-ticker JSON files from a configured directory

Environment variables:
- `EFA_PROVIDER_BACKEND`
- `EFA_PROVIDER_DATA_DIR`

## Run a Single Stock

Sample provider data:

```powershell
python -m src.orchestration.run_analysis --ticker TSLA --provider json-directory --provider-data-dir data/fixtures --output-root outputs
```

US live provider path:

```powershell
python -m src.orchestration.run_analysis --ticker MSFT --provider live --output-root outputs
```

China A-share provider path:

```powershell
python -m src.orchestration.run_analysis --ticker 600519 --provider akshare --output-root outputs/china_akshare
```

## Run a Batch

Direct tickers:

```powershell
python -m src.orchestration.run_batch_analysis --tickers TSLA,MSFT --provider json-directory --provider-data-dir data/fixtures --output-root outputs
```

Ticker-file workflow:

```powershell
python -m src.orchestration.run_batch_analysis --ticker-file data/fixtures/sample_sector_universe.csv --provider json-directory --provider-data-dir data/fixtures --output-root outputs
```

Watchlist workflow:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_us_watchlist --provider live --output-root outputs
```

China watchlist workflow:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist china_consumer_watchlist --provider akshare --output-root outputs/china_batch
```

Sector-filtered watchlist workflow:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_sector_watchlist --sectors Technology --provider json-directory --provider-data-dir data/fixtures --output-root outputs
```

Top-N report generation after screening:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_us_watchlist --provider json-directory --provider-data-dir data/fixtures --top-n-reports 1 --output-root outputs/watchlist_batch
```

Batch outputs:
- `outputs/batch_summary.csv`
- `outputs/batch_summary.json`
- `outputs/batch_summary.md`

Per-stock outputs:
- `outputs/stocks/<ticker>/reports/`
- `outputs/stocks/<ticker>/charts/`
- `outputs/stocks/<ticker>/scorecards/`

When `--top-n-reports` is set, every ticker is still screened and ranked, but only the highest-ranked successful names receive full report/chart/scorecard artifacts.

## Watchlists

Use `config/watchlists/` for reusable universes you want to keep outside development fixtures.

Supported formats:
- plain text: one ticker per line
- CSV or TSV: `ticker` or `symbol`, optional `sector`
- JSON list: strings or objects with `ticker` and optional `sector`
- JSON sector map: `{ "Technology": ["MSFT", "NVDA"] }`

Sample files:
- `config/watchlists/sample_us_watchlist.csv`
- `config/watchlists/sample_sector_watchlist.json`
- `config/watchlists/china_consumer_watchlist.csv`

## Repo-Local Skill

Use the repo-local skill in `.agents/skills/batch-stock-analysis/` when you want Codex to run the batch workflow without restating the repo instructions each time.

## Current Limitations

- The live adapter depends on Yahoo Finance response shape and network availability.
- The `akshare` backend is currently tuned for mainland Shanghai and Shenzhen A-shares, not Hong Kong, US ADRs, or a full China-market cross-listing model.
- AkShare peer multiples are supported when peers are provided explicitly or inferred from the batch watchlist, but live China runs still depend on upstream AkShare source stability.
- Transcript parsing and annual report parsing remain out of scope.
- The shipped JSON datasets are deterministic sample data for development and validation, not canonical market feeds.
- Provider-reported statement units are not normalized to one narrative display unit, so report prose avoids absolute money magnitudes where that would be misleading.

