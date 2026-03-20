# AGENTS.md

## Project goal
Build a modular Python engine for listed-company fundamental analysis.

## Repo root
Treat the current working directory as the repository root:
D:\AI\equity_fundamental_analysis

## Working rules
- Keep ingestion, processing, analysis, scoring, and reporting separate.
- Use Python 3.11+.
- Use pandas for tabular financial outputs.
- Use pathlib for file paths.
- Add type hints and docstrings.
- Add pytest tests for any module that computes metrics.
- Handle missing data explicitly and log warnings where appropriate.
- Do not hardcode ticker-specific logic.
- Do not silently mix currencies.
- Do not silently mix annual and quarterly data.
- Keep formulas readable and auditable.
- Prefer small composable functions over large scripts.
- Keep diffs scoped to the current milestone.
- Update documentation.md after each milestone.

## MVP priorities
1. Repo scaffold
2. Shared schemas and provider interfaces
3. Normalized annual financial dataframe
4. Revenue analysis
5. Profitability analysis
6. Return-ratio analysis
7. Balance-sheet analysis
8. Cash-flow analysis
9. Valuation
10. Red flags
11. Scoring
12. Markdown report
13. Runnable orchestration entry point

## Non-goals for MVP
- Transcript NLP
- Annual report PDF parsing
- Market-specific ownership integrations
- Advanced industry-cycle modeling
- Dashboard UI
- Multi-agent orchestration

## Testing and validation
- Use pytest.
- Add deterministic fixture data under tests/fixtures or data/fixtures.
- Run tests after each milestone.
- Keep interfaces clean and provider-agnostic.
- Use pathlib for any filesystem operations.

## Documentation
Update documentation.md with:
- current status
- milestones completed
- decisions made
- how to run
- known issues
- next steps
