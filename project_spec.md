# Project Spec

## Project Name

Listed Company Fundamental Analysis Engine

## Objective

Build a modular Python research engine for listed-company analysis.

The system should:
- ingest structured financial and market data
- normalize annual company financials
- compute revenue, profitability, return, balance sheet, cash flow, and valuation metrics
- detect red flags
- produce a weighted scorecard
- generate charts and a markdown investment memo
- support later extension into filings, transcripts, ownership, and monitoring

## Initial Scope

Single-agent implementation only.

## Repository Root

`D:\AI\equity_fundamental_analysis`

## Example Company for MVP

Use Tesla as the canonical example company for fixtures, examples, and smoke tests.

Baseline example assumptions:
- ticker: `TSLA`
- company name: `Tesla, Inc.`
- exchange / market: `NASDAQ`
- reporting currency: `USD`
- period scope: annual data only

Tesla usage rules for MVP:
- use Tesla-shaped fixture data for tests and examples
- keep logic ticker-agnostic even when Tesla is the reference company
- do not hardcode Tesla-specific formulas, thresholds, or narrative output

## Inputs

- ticker
- company name
- exchange / market
- reporting currency
- optional peer list
- annual financial statements
- historical market price data
- shares outstanding data if available

## Outputs

- processed company dataset
- normalized annual financial dataframe
- metrics dataframe
- scorecard csv/json
- chart images
- markdown report
- test suite

## MVP Modules

### Ingestion

- `src/ingestion/base.py`
- `src/ingestion/financials.py`
- `src/ingestion/market_data.py`

### Processing

- `src/processing/normalize_financials.py`

### Analysis

- `src/analysis/revenue_analysis.py`
- `src/analysis/profitability.py`
- `src/analysis/returns.py`
- `src/analysis/balance_sheet.py`
- `src/analysis/cashflow.py`
- `src/analysis/valuation.py`
- `src/analysis/red_flags.py`
- `src/analysis/scoring.py`
- `src/analysis/thesis_builder.py`

### Reporting

- `src/reporting/charts.py`
- `src/reporting/report_generator.py`

### Orchestration

- `src/orchestration/run_analysis.py`

## Suggested Repo Structure

- `config/`
- `data/raw/`
- `data/processed/`
- `data/cache/`
- `data/fixtures/`
- `outputs/reports/`
- `outputs/charts/`
- `outputs/scorecards/`
- `src/`
- `tests/`
- `notebooks/`

## Phase Boundaries

### Phase 1

Phase 1 establishes the scaffold and contracts only.

Deliverables:
- repository folder structure
- `pyproject.toml`
- `requirements.txt`
- `README.md`
- shared schemas
- abstract provider interfaces
- placeholder modules in `src/`
- pytest configuration and fixture directories
- `documentation.md` updated for Phase 1

Out of scope:
- real financial metric implementations
- report generation
- runnable end-to-end analysis pipeline

### Phase 2

Phase 2 implements normalized annual financial processing and the core metric modules.

Deliverables:
- normalization layer for annual financial data only
- normalized dataframe contract enforced in code and tests
- deterministic Tesla fixture data
- revenue analysis
- profitability analysis
- return-ratio analysis
- balance-sheet analysis
- cash-flow analysis
- tests for all metric-computing modules added in this phase
- `documentation.md` updated for Phase 2

Out of scope:
- valuation
- red flags
- scoring
- report generation
- full runnable pipeline

### Phase 3

Phase 3 wires the remaining analysis and reporting flow into a runnable MVP pipeline.

Deliverables:
- valuation
- red flags
- scoring
- thesis builder
- charts
- report generator
- orchestration entry point
- smoke test for the pipeline
- output artifacts written under `outputs/`
- `README.md` and `documentation.md` finalized for MVP usage

## Core Analytical Sections

1. Business understanding placeholder
2. Revenue analysis
3. Profitability analysis
4. Return ratios
5. Balance sheet check
6. Cash flow analysis
7. Valuation check
8. Red flags
9. Scorecard
10. Investment thesis summary

## Financial Metrics to Support in MVP

### Revenue Analysis

- YoY revenue growth
- 3Y CAGR where available
- 5Y CAGR where available

### Profitability

- Gross margin
- EBITDA margin
- EBIT margin
- Net margin

### Return Ratios

- ROE
- ROA
- ROCE or ROIC
- Asset turnover

### Balance Sheet

- Debt to equity
- Net debt to EBITDA if possible
- Current ratio
- Interest coverage if possible
- Working capital metrics where possible

### Cash Flow

- Operating cash flow
- Free cash flow
- CFO vs PAT / net income
- Capex trend

### Valuation

- PE
- PB
- EV/EBITDA
- EV/Sales
- FCF yield where possible
- simple peer comparison support

### Red Flags

- receivables growth faster than revenue
- inventory growth faster than revenue
- CFO below PAT for consecutive years
- rising leverage
- share dilution
- margin deterioration despite sales growth

## Scoring Categories

- revenue analysis
- profitability
- returns
- balance sheet
- cash flow
- valuation
- red flags

## Final Labels

- high-quality compounder
- good business, too expensive
- cyclical opportunity
- watchlist only
- value trap / governance trap

## Fixture Expectations

Tesla fixture data should be deterministic and easy to audit.

Minimum expectations:
- annual periods only
- consistent `USD` currency across the fixture
- enough history to exercise YoY and CAGR calculations where possible
- statement coverage for income statement, balance sheet, and cash flow inputs needed by MVP metrics
- market data and shares outstanding fixture inputs sufficient for valuation and reporting in Phase 3

Fixture storage:
- prefer `tests/fixtures/` for test-owned inputs
- `data/fixtures/` is acceptable for reusable sample datasets

## Engineering Requirements

- Python 3.11+
- pandas
- numpy
- pydantic
- matplotlib
- jinja2
- pytest
- pathlib-based file handling
- modular interfaces
- provider-agnostic design

## MVP Constraints

- annual structured financial data only
- no transcript parsing
- no annual report PDF parsing
- no vendor-specific API integrations yet
- no market-specific ownership integrations
- no multi-agent orchestration

## Definition of Done for MVP

- one command runs the pipeline for one ticker
- tests pass
- metrics are computed from normalized annual data
- a markdown report is generated
- red flags are listed
- charts are saved to `outputs/charts`
- scorecard is saved to `outputs/scorecards`
- the implementation remains modular and provider-agnostic
