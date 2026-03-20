# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project uses semantic version tags.

## [Unreleased]

### Added
- Batch screening filters for `--minimum-score`, `--max-red-flags`, and `--report-labels`.
- Stable failure categories in batch summaries and single-stock CLI exits.
- Expanded artifact metadata in batch summaries, including artifact-root and scorecard path fields.

### Changed
- Batch report generation now applies `--top-n-reports` after report eligibility filters instead of before them.
- Markdown reports now list red-flag and metric-snapshot artifact files alongside the report and scorecard outputs.
- README and operator documentation now include report-gating workflows and common failure guidance.

## [v0.1.0] - 2026-03-20

### Added
- Modular Python project structure for ingestion, processing, analysis, scoring, reporting, and orchestration.
- Shared schemas and provider-agnostic runtime interfaces.
- Normalized annual financial processing and core metric analysis modules.
- Valuation, red-flag detection, scoring, thesis generation, charting, and markdown reporting.
- Runnable single-stock and batch CLI entrypoints.
- Deterministic fixture-backed provider mode for development and tests.
- Yahoo Finance live provider support for US-listed stocks.
- AkShare live provider support for mainland China A-shares.
- Batch watchlists, sector filtering, and top-N report generation.
- Repo-local Codex batch analysis skill.
- Pytest coverage for metrics, providers, pipelines, and batch workflows.

### Changed
- README tightened for external use and clearer operator workflows.
- Git tracking updated to ignore generated outputs and transient test artifacts.

### Notes
- `v0.1.0` is the first tagged release baseline for future incremental changes.
