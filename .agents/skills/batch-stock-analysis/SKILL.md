---
name: batch-stock-analysis
description: Run this repository's listed-company fundamental analysis workflow for one or more tickers, generate a ranked batch screening summary, write per-stock reports/charts/scorecards under outputs, and compare results. Use when Codex needs to analyze multiple stocks in D:\AI\equity_fundamental_analysis, including larger universes provided through --ticker-file, --watchlist, or sector-tagged stock lists, and when the user wants the same workflow applied to mainland China A-shares through AkShare.
---

# Batch Stock Analysis

1. Inspect the repo state and confirm the entrypoints still exist:
   - `src/orchestration/run_analysis.py`
   - `src/orchestration/run_batch_analysis.py`
2. Confirm dependencies are available before running analysis:
   - `python -m pytest`
   - provider configuration or explicit `--provider` arguments
3. Resolve the provider mode explicitly.
   - Prefer `--provider live` for Yahoo Finance-backed runs.
   - Use `--provider akshare` for mainland China A-shares.
   - For deterministic repo-local runs, use `--provider json-directory --provider-data-dir data/fixtures`.
4. For multiple stocks, prefer the batch entrypoint.

Direct ticker list:

```powershell
python -m src.orchestration.run_batch_analysis --tickers AAPL,MSFT,NVDA --provider live --output-root outputs
```

Named watchlist:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_us_watchlist --provider live --output-root outputs
```

China watchlist:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist china_consumer_watchlist --provider akshare --output-root outputs/china_batch
```

Top-N reporting after screening:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_us_watchlist --provider json-directory --provider-data-dir data/fixtures --top-n-reports 1 --output-root outputs/watchlist_batch
```

5. Save outputs under `outputs/` and keep the ranked batch summary first in the response.
6. After the run, summarize:
   - ranked tickers with label and score
   - whether a full report was generated for each ticker
   - failures per ticker without hiding them
   - report paths for each successful stock that received artifacts
7. Do not duplicate business logic in the skill. If scoring, reporting, provider configuration, watchlist resolution, or output layout needs to change, edit application code instead.

Read `references/provider-config.md` when you need provider assumptions, watchlist formats, or output layout.
