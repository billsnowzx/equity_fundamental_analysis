# Codex Phase 3 Prompt

Read these files first:
- `AGENTS.md`
- `project_spec.md`
- `implement.md`
- `documentation.md`
- `codex_phase_1_prompt.md`
- `codex_phase_2_prompt.md`

Repo root:
`D:\AI\equity_fundamental_analysis`

Use relevant repo skills automatically when helpful.

Build the MVP as a single-agent implementation.

Use `TESLA` as the example company for analysis.

Assume Phases 1 and 2 are already complete. Build only Phase 3.

Phase 3 scope:
1. Implement:
   - `valuation.py`
   - `red_flags.py`
   - `scoring.py`
   - `thesis_builder.py`
   - `charts.py`
   - `report_generator.py`
   - `run_analysis.py`
2. Wire the modules into a runnable pipeline for one example company using normalized annual data.
3. Generate scorecard outputs and markdown reporting outputs under `outputs/`.
4. Add or extend tests for valuation, red flags, scoring, and orchestration-critical behavior where practical.
5. Add a smoke test for the runnable pipeline.
6. Update `README.md` and `documentation.md` with the final MVP status, decisions, and how to run the pipeline.

Constraints:
- Keep the architecture modular and provider-agnostic.
- Use Python 3.11+.
- Use `pathlib` for file paths.
- Use annual structured financial data only.
- Do not implement vendor-specific APIs yet.
- Do not implement transcript or annual report parsing in MVP.
- Keep formulas readable and auditable.
- Handle missing data explicitly and log warnings where appropriate.
- Save outputs under `outputs/`.
- Keep diffs scoped to this phase only.
- Run validation after completing this phase.

Validation for Phase 3:
- `pytest` passes
- a smoke test for `run_analysis.py` passes
- path handling works with Windows paths
- outputs are written under `outputs/`
- the markdown report is generated

Phase 3 is done when:
- valuation, red flags, scoring, and reporting are wired into a runnable pipeline
- charts are saved to `outputs/charts`
- scorecards are saved to `outputs/scorecards`
- a markdown report is generated under `outputs/reports`
- tests run successfully
- `documentation.md` is updated with status, decisions, how to run, known issues, and next steps

Do not expand beyond the MVP.
