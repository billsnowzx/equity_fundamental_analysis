# Codex MVP Prompt

Read these files first:
- `AGENTS.md`
- `project_spec.md`
- `implement.md`
- `documentation.md`

Repo root:
`D:\AI\equity_fundamental_analysis`

Use relevant repo skills automatically when helpful.

Build the MVP as a single-agent implementation.

Tasks:
1. Scaffold the repository structure.
2. Add `pyproject.toml`, `requirements.txt`, and `README.md`.
3. Define shared schemas and abstract provider interfaces.
4. Create placeholder modules in `src/` for ingestion, processing, analysis, reporting, and orchestration.
5. Set up `pytest` and test fixture directories.
6. Implement the MVP modules described in `project_spec.md`.
7. Update `documentation.md` as milestones are completed.

Constraints:
- Keep the architecture modular and provider-agnostic.
- Use Python 3.11+.
- Use `pathlib` for file paths.
- Do not implement vendor-specific APIs yet.
- Do not implement transcript or annual report parsing in MVP.
- Keep diffs scoped to the current milestone.
- Run validation after each milestone.
- Add tests for metric modules.

Done when:
- the repo scaffold is complete
- tests run successfully
- normalized annual financial analysis modules exist
- valuation, red flags, scoring, and reporting are wired into a runnable pipeline
- `documentation.md` is updated with status, decisions, and how to run
