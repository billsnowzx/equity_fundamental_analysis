# Watchlists

Store reusable batch universes here instead of under `data/fixtures/`.

Supported formats:
- plain text: one ticker per line
- CSV or TSV: `ticker` or `symbol`, optional `sector`
- JSON list: `["MSFT", "NVDA"]` or `[{"ticker": "MSFT", "sector": "Technology"}]`
- JSON sector map: `{ "Technology": ["MSFT", "NVDA"] }`

Usage examples:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_us_watchlist --provider live --output-root outputs
python -m src.orchestration.run_batch_analysis --watchlist sample_sector_watchlist --sectors Technology --provider json-directory --provider-data-dir data/fixtures --top-n-reports 1 --output-root outputs
python -m src.orchestration.run_batch_analysis --watchlist china_consumer_watchlist --provider akshare --output-root outputs/china_batch
```
