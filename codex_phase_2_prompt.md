# Codex Phase 2 Prompt

Read these files first:
- `AGENTS.md`
- `project_spec.md`
- `implement.md`
- `documentation.md`
- `codex_phase_1_prompt.md`

Repo root:
`D:\AI\equity_fundamental_analysis`

Use relevant repo skills automatically when helpful.

Build the MVP as a single-agent implementation.

Use `TESLA` as the example company for analysis.

Assume Phase 1 is already complete. Build only Phase 2.

Phase 2 scope:
1. Implement the normalization layer for annual financial data only.
2. Define the normalized annual financial dataframe contract clearly in code and tests.
3. Implement these analysis modules:
   - `revenue_analysis.py`
   - `profitability.py`
   - `returns.py`
   - `balance_sheet.py`
   - `cashflow.py`
4. Add deterministic fixture data for Tesla-like annual financial statements.
5. Add pytest coverage for every metric-computing module added in this phase.
6. Update `documentation.md` with Phase 2 progress, decisions, known issues, and how to run the tests.

Constraints:
- Keep the architecture modular and provider-agnostic.
- Use Python 3.11+.
- Use `pathlib` for file paths.
- Use annual structured financial data only.
- Do not implement vendor-specific APIs yet.
- Do not implement transcript or annual report parsing in MVP.
- Handle missing data explicitly and log warnings where appropriate.
- Do not silently mix currencies.
- Do not silently mix annual and quarterly data.
- Keep formulas readable and auditable.
- Keep diffs scoped to this phase only.
- Run validation after completing this phase.

Validation for Phase 2:
- `pytest` passes
- imports succeed for the new modules
- metric modules operate on normalized annual data
- fixture-driven tests are deterministic

Phase 2 is done when:
- the normalization layer exists and is tested
- normalized annual financial analysis modules exist
- revenue, profitability, returns, balance sheet, and cash flow metrics are implemented
- tests for those modules pass
- `documentation.md` reflects completed milestones and current status

Do not start Phase 3 work yet.
