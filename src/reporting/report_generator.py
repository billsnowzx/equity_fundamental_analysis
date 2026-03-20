"""Markdown report generation for the MVP pipeline."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from string import Template

from src.shared.schemas import AnalysisRequest


REPORT_TEMPLATE = Template(
    """# $company_name ($ticker) Fundamental Analysis

Generated from the configured MVP analysis pipeline.

## Summary
- Exchange: $exchange
- Reporting currency: $currency
- Overall label: $label
- Overall score: $overall_score

## Key Metrics
$key_metrics_markdown

## Scorecard
$scorecard_markdown

## Red Flags
$red_flags_markdown

$thesis_markdown

## Charts
$chart_list_markdown

## Output Files
- Scorecard CSV: `$scorecard_csv`
- Scorecard JSON: `$scorecard_json`
- Red Flags CSV: `$red_flags_csv`
- Metric Snapshot CSV: `$metric_snapshot_csv`
- Report: `$report_path`
"""
)


def generate_markdown_report(
    request: AnalysisRequest,
    output_dir: Path,
    context: Mapping[str, object] | None = None,
) -> Path:
    """Generate the markdown report for one analysis run."""

    output_dir.mkdir(parents=True, exist_ok=True)
    context = dict(context or {})
    report_path = output_dir / f"{request.company.ticker.lower()}_analysis_report.md"

    content = REPORT_TEMPLATE.substitute(
        company_name=request.company.company_name,
        ticker=request.company.ticker,
        exchange=request.company.exchange,
        currency=request.company.reporting_currency,
        label=context.get("label", "watchlist only"),
        overall_score=context.get("overall_score", "n/a"),
        key_metrics_markdown=context.get("key_metrics_markdown", "No key metrics available."),
        scorecard_markdown=context.get("scorecard_markdown", "No scorecard available."),
        red_flags_markdown=context.get("red_flags_markdown", "No red flag analysis available."),
        thesis_markdown=context.get("thesis_markdown", "No thesis available."),
        chart_list_markdown=context.get("chart_list_markdown", "No charts generated."),
        scorecard_csv=context.get("scorecard_csv", "n/a"),
        scorecard_json=context.get("scorecard_json", "n/a"),
        red_flags_csv=context.get("red_flags_csv", "n/a"),
        metric_snapshot_csv=context.get("metric_snapshot_csv", "n/a"),
        report_path=report_path,
    )
    report_path.write_text(content)
    return report_path
