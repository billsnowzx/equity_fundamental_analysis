# Codex Phase 1 Prompt

Read these files first:
- `AGENTS.md`
- `project_spec.md`
- `implement.md`
- `documentation.md`

Repo root:
`D:\AI\equity_fundamental_analysis`

Use relevant repo skills automatically when helpful.

Build the MVP as a single-agent implementation.

Use `TESLA` as the example company for analysis.

Phase 1 scope:
1. Scaffold the repository structure.
2. Add `pyproject.toml`, `requirements.txt`, and `README.md`.
3. Define shared schemas and abstract provider interfaces.
4. Create placeholder modules in `src/` for ingestion, processing, analysis, reporting, and orchestration.
5. Set up `pytest` and test fixture directories.
6. Update `documentation.md` with the Phase 1 status, decisions, and how to run.

Constraints:
- Keep the architecture modular and provider-agnostic.
- Use Python 3.11+.
- Use `pathlib` for file paths.
- Do not implement vendor-specific APIs yet.
- Do not implement transcript or annual report parsing in MVP.
- Keep diffs scoped to the current milestone.
- Run validation after the phase is complete.
- Add tests only if they are needed for scaffold or setup verification in this phase.

Phase 1 is done when:
- `src/`, `tests/`, `config/`, `outputs/`, and `data/` folders exist
- `pyproject.toml`, `requirements.txt`, and `README.md` were created
- provider interfaces and shared schemas were added
- placeholder modules exist
- `documentation.md` was updated
- `pytest` setup works

Do not start Phase 2 work yet.
