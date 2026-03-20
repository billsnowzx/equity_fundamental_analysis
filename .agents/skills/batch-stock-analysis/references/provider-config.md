# Provider Configuration and Outputs

## Provider assumptions

Supported provider backends:
- `live`
- `yfinance`
- `akshare`
- `json-directory`

Current behavior:
- `live` uses the concrete Yahoo Finance adapter.
- `yfinance` is an explicit alias for the same live adapter.
- `akshare` targets mainland China A-shares through AkShare-backed statements, prices, profile metadata, and share-capital history.
- `json-directory` is the deterministic sample mode for local validation and offline-like runs.

Resolve provider settings from CLI flags first, then environment variables:
- `EFA_PROVIDER_BACKEND`
- `EFA_PROVIDER_DATA_DIR`

## Current runnable sample modes

Use the repo-local JSON sample data with:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_us_watchlist --provider json-directory --provider-data-dir data/fixtures --top-n-reports 1 --output-root outputs/watchlist_batch
```

Use the China backend with:

```powershell
python -m src.orchestration.run_analysis --ticker 600519 --provider akshare --output-root outputs/china_akshare
```

## Batch input formats

Supported batch input sources:
- `--tickers`: direct comma-separated symbols
- `--ticker-file`: plain text, CSV/TSV, JSON list, or JSON sector map
- `--watchlist`: named watchlist under `config/watchlists/` or an explicit file path

Supported `--ticker-file` and watchlist formats:
- plain text: one ticker per line
- CSV or TSV: `ticker` or `symbol` column, optional `sector` column
- JSON list: `["AAPL", "MSFT"]` or `[{"ticker": "AAPL", "sector": "Technology"}]`
- JSON sector map: `{"Technology": ["MSFT", "NVDA"], "Automotive": ["TSLA"]}`

Sector filtering:
- use `--sectors` with CSV/TSV/JSON files that contain sector metadata
- do not use `--sectors` with plain text ticker files

Top-N reporting:
- use `--top-n-reports N` to screen every ticker but only generate full report artifacts for the highest-ranked `N` successful names
- batch summary files still include every screened ticker

## Output layout

Batch outputs:
- `outputs/batch_summary.csv`
- `outputs/batch_summary.json`
- `outputs/batch_summary.md`

Per-stock outputs:
- `outputs/stocks/<ticker>/reports/`
- `outputs/stocks/<ticker>/charts/`
- `outputs/stocks/<ticker>/scorecards/`

When `--top-n-reports` is set, lower-ranked successful tickers remain in the summary with `report_generated = False` and no per-stock artifact paths.

## Failure handling

- One failed ticker must not abort the whole batch when other tickers succeed.
- If every ticker fails, the batch command should exit non-zero.
- Do not silently substitute Tesla fixture data for arbitrary tickers.
- The `akshare` backend is currently intended for mainland Shanghai and Shenzhen A-shares, not a full China-market cross-listing surface.
