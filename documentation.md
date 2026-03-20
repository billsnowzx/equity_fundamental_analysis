# documentation.md

## Current status
Batch analysis skill, provider-backed batch orchestration, live adapter, ticker-file workflows, reusable watchlists, top-N reporting, Yahoo Finance live validation, and AkShare A-share support are complete.

The repository now supports:
- single-stock analysis through a configured provider runtime
- batch screening and per-stock report generation
- repo-local skill usage through `.agents/skills/batch-stock-analysis/`
- provider config resolution through CLI flags or environment variables
- US and global live-provider runs through a concrete Yahoo Finance adapter
- mainland China A-share runs through an AkShare-backed provider runtime
- sector-filtered ticker-file workflows for larger stock universes
- reusable named watchlists under `config/watchlists/`
- screening-first top-N report generation that only writes full artifacts for the highest-ranked successful names
- calibrated red-flag thresholds that avoid flagging immaterial margin drift as deterioration

## Milestones
- [x] Scaffold repo
- [x] Shared schemas and provider interfaces
- [x] Normalization layer
- [x] Revenue analysis
- [x] Profitability analysis
- [x] Return ratios
- [x] Balance sheet
- [x] Cash flow
- [x] Valuation
- [x] Red flags
- [x] Scoring
- [x] Thesis builder
- [x] Reporting
- [x] Orchestration
- [x] Batch orchestration
- [x] Repo-local skill
- [x] Live Yahoo Finance adapter
- [x] AkShare A-share adapter
- [x] Ticker-file and sector-list workflows
- [x] Reusable watchlists
- [x] Top-N report generation
- [x] Live batch validation
- [x] Tests passing

## Decisions made
- Single-agent Codex workflow first
- Repo root is `D:\AI\equity_fundamental_analysis`
- MVP uses annual structured financial data only
- Transcript parsing and annual report PDF parsing remain out of scope
- Core analysis, scoring, and reporting logic remain provider-agnostic
- Provider selection is explicit through CLI flags or `EFA_PROVIDER_BACKEND` and `EFA_PROVIDER_DATA_DIR`
- The first concrete general live adapter is Yahoo Finance, exposed as both `live` and `yfinance`
- The mainland China backend is `akshare`, currently targeted at Shanghai and Shenzhen A-shares
- `json-directory` remains the deterministic sample backend for offline and validation runs
- Batch outputs are screening-first and still generate full reports for every successfully screened stock unless `--top-n-reports` is set
- One failed ticker does not abort an otherwise successful batch
- The repo-local skill stays procedural and does not duplicate application business logic
- `--ticker-file` supports plain text, CSV/TSV, JSON lists, and JSON sector maps
- `--watchlist` resolves named universes from `config/watchlists/` or an explicit path
- `--sectors` filters sector-tagged CSV/TSV/JSON universes and intentionally rejects plain-text ticker files
- Margin deterioration now requires a broad or material decline, not tiny dual-margin noise
- AkShare share-capital values are normalized by a share-count multiplier so A-share valuation ratios are on the right scale
- Thesis text avoids unit-specific free-cash-flow wording because provider scales are not normalized to one display unit

## How to run
Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the full test suite:

```powershell
python -m pytest
```

Run one US stock through Yahoo Finance:

```powershell
python -m src.orchestration.run_analysis --ticker MSFT --provider live --output-root outputs
```

Run one China A-share through AkShare:

```powershell
python -m src.orchestration.run_analysis --ticker 600519 --provider akshare --output-root outputs/china_akshare
```

Run a watchlist with live Yahoo Finance data:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_us_watchlist --provider live --output-root outputs/live_watchlist
```

Run a China watchlist with AkShare:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist china_consumer_watchlist --provider akshare --output-root outputs/china_batch
```

Run a deterministic watchlist batch with top-N reports:

```powershell
python -m src.orchestration.run_batch_analysis --watchlist sample_us_watchlist --provider json-directory --provider-data-dir data/fixtures --top-n-reports 1 --output-root outputs/watchlist_batch
```

## Generated outputs
Batch summary files:
- `outputs/batch_summary.csv`
- `outputs/batch_summary.json`
- `outputs/batch_summary.md`
- `outputs/live_batch/batch_summary.csv`
- `outputs/live_batch/batch_summary.json`
- `outputs/live_batch/batch_summary.md`
- `outputs/watchlist_batch/batch_summary.csv`
- `outputs/watchlist_batch/batch_summary.json`
- `outputs/watchlist_batch/batch_summary.md`

Per-stock files:
- `outputs/stocks/<ticker>/reports/<ticker>_analysis_report.md`
- `outputs/stocks/<ticker>/charts/`
- `outputs/stocks/<ticker>/scorecards/`
- `outputs/live_batch/stocks/<ticker>/reports/<ticker>_analysis_report.md`
- `outputs/live_batch/stocks/<ticker>/charts/`
- `outputs/live_batch/stocks/<ticker>/scorecards/`
- `outputs/watchlist_batch/stocks/<ticker>/reports/<ticker>_analysis_report.md`
- `outputs/watchlist_batch/stocks/<ticker>/charts/`
- `outputs/watchlist_batch/stocks/<ticker>/scorecards/`
- `outputs/china_akshare/reports/600519_analysis_report.md`
- `outputs/china_akshare/charts/`
- `outputs/china_akshare/scorecards/`

Repo-local skill:
- `.agents/skills/batch-stock-analysis/SKILL.md`

Watchlist directory:
- `config/watchlists/README.md`
- `config/watchlists/sample_us_watchlist.csv`
- `config/watchlists/sample_sector_watchlist.json`
- `config/watchlists/china_consumer_watchlist.csv`

## Validation
- `python -m pytest` passes with 37 tests
- `python -m src.orchestration.run_analysis --ticker MSFT --provider live --output-root outputs` completed successfully
- `python -m src.orchestration.run_batch_analysis --ticker-file data/fixtures/sample_sector_universe.csv --provider live --output-root outputs/live_batch` completed successfully
- `python -m src.orchestration.run_batch_analysis --watchlist sample_us_watchlist --provider json-directory --provider-data-dir data/fixtures --top-n-reports 1 --output-root outputs/watchlist_batch` completed successfully
- `python -m src.orchestration.run_analysis --ticker 600519 --provider akshare --output-root outputs/china_akshare` completed successfully`r`n- `python -m src.orchestration.run_batch_analysis --watchlist china_consumer_watchlist --provider akshare --output-root outputs/china_batch` is implemented but the live validation attempt was blocked by upstream `RemoteDisconnected` responses from an AkShare source endpoint in this environment
- `quick_validate.py` reports the batch skill is valid

## Current sample results
Live US batch:
- `MSFT`: `good business, too expensive`, score `75.44`, red flags `1`
- `TSLA`: `value trap / governance trap`, score `50.60`, red flags `1`

Deterministic watchlist batch with top-1 reporting:
- `MSFT`: `good business, too expensive`, score `77.04`, red flags `0`, full report generated
- `TSLA`: `good business, too expensive`, score `74.84`, red flags `3`, report skipped by `--top-n-reports 1`

Live China A-share single-stock run:
- `600519` / `贵州茅台`: `high-quality compounder`, score `87.36`, red flags `1`

## Known issues
- The Yahoo Finance path depends on Yahoo response shape and network availability.
- The AkShare backend currently targets Shanghai and Shenzhen A-shares, not a full HK/ADR/Beijing exchange universe.
- Peer comparison support remains simple and provider-dependent; AkShare peer multiples now work for explicit or batch-inferred peer lists, but live China runs still depend on upstream AkShare source stability.
- The repo-local skill was validated structurally, but not forward-tested through subagents because no explicit delegation request was made.

## Next steps
1. Add peer-multiple support for AkShare-backed China analysis.
2. Harden live-provider normalization against ticker-specific AkShare and Yahoo Finance gaps.
3. Add ranking presets or score cutoffs on top of `--top-n-reports`.
4. Add one more live provider backend behind `src/providers/` for redundancy.

