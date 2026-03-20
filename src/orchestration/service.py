"""Shared orchestration helpers for single-stock and batch analysis."""

from __future__ import annotations

import socket
from pathlib import Path
from typing import Any

import pandas as pd

from src.analysis.balance_sheet import analyze_balance_sheet
from src.analysis.cashflow import analyze_cashflow
from src.analysis.profitability import analyze_profitability
from src.analysis.red_flags import analyze_red_flags
from src.analysis.revenue_analysis import analyze_revenue
from src.analysis.returns import analyze_returns
from src.analysis.scoring import score_company
from src.analysis.thesis_builder import build_investment_thesis
from src.analysis.valuation import analyze_valuation
from src.processing.normalize_financials import normalize_annual_financials
from src.providers.errors import ProviderConfigurationError, ProviderDataError, ProviderError
from src.providers.factory import ProviderRuntime
from src.reporting.charts import generate_charts
from src.reporting.report_generator import generate_markdown_report
from src.shared.schemas import AnalysisRequest, CompanyDataBundle, CompanyProfile


def resolve_company_profile(
    ticker: str,
    provider_runtime: ProviderRuntime | None = None,
    *,
    company_name: str | None = None,
    exchange: str | None = None,
    currency: str | None = None,
) -> CompanyProfile:
    """Resolve company metadata from overrides and optional provider defaults."""

    defaults: dict[str, Any] = {}
    if provider_runtime is not None and provider_runtime.company_profile_resolver is not None:
        defaults = provider_runtime.company_profile_resolver.resolve_profile_defaults(ticker)

    return CompanyProfile(
        ticker=ticker.upper(),
        company_name=company_name or defaults.get("company_name") or ticker.upper(),
        exchange=exchange or defaults.get("exchange") or "UNKNOWN",
        reporting_currency=currency or defaults.get("reporting_currency") or "USD",
        peer_list=defaults.get("peer_list", []),
    )


def load_company_data(company: CompanyProfile, provider_runtime: ProviderRuntime) -> CompanyDataBundle:
    """Load provider-backed company inputs into the shared runtime bundle."""

    financial_statements = list(
        provider_runtime.financial_statements_provider.get_annual_financial_statements(company)
    )
    if not financial_statements:
        raise ProviderDataError(f"No annual financial statements available for {company.ticker}.")

    market_prices = list(provider_runtime.market_data_provider.get_historical_prices(company))
    shares_outstanding = list(provider_runtime.shares_outstanding_provider.get_shares_outstanding(company))
    peer_multiples = list(provider_runtime.peer_multiples_provider.get_peer_multiples(company))

    resolved_currency = company.reporting_currency or financial_statements[0].currency
    resolved_company = CompanyProfile(
        ticker=company.ticker,
        company_name=company.company_name,
        exchange=company.exchange,
        reporting_currency=resolved_currency,
        peer_list=company.peer_list or [record.ticker for record in peer_multiples],
    )
    return CompanyDataBundle(
        company=resolved_company,
        financial_statements=financial_statements,
        market_prices=market_prices,
        shares_outstanding=shares_outstanding,
        peer_multiples=peer_multiples,
    )


def prepare_company_analysis(
    request: AnalysisRequest,
    provider_runtime: ProviderRuntime,
) -> dict[str, Any]:
    """Load inputs and compute analysis frames without writing output artifacts."""

    company_data = load_company_data(request.company, provider_runtime)
    financials = normalize_annual_financials(company_data.financial_statements)
    market_data = pd.DataFrame([_model_to_dict(item) for item in company_data.market_prices])
    shares_outstanding = pd.DataFrame([_model_to_dict(item) for item in company_data.shares_outstanding])
    peer_multiples = pd.DataFrame([_model_to_dict(item) for item in company_data.peer_multiples])

    revenue = analyze_revenue(financials)
    profitability = analyze_profitability(financials)
    returns = analyze_returns(financials)
    balance_sheet = analyze_balance_sheet(financials)
    cashflow = analyze_cashflow(financials)
    valuation = analyze_valuation(financials, market_data, shares_outstanding, peer_multiples)
    red_flags = analyze_red_flags(financials, shares_outstanding)

    metric_frames: dict[str, pd.DataFrame] = {
        "revenue": revenue,
        "profitability": profitability,
        "returns": returns,
        "balance_sheet": balance_sheet,
        "cashflow": cashflow,
        "valuation": valuation,
    }
    scorecard = score_company(metric_frames, red_flags)
    metric_snapshot = _build_metric_snapshot(metric_frames)

    overall_row = scorecard.loc[scorecard["category"] == "overall"].iloc[0]
    valuation_row = valuation.iloc[0]
    thesis = build_investment_thesis(
        {
            "company_name": request.company.company_name,
            "ticker": request.company.ticker,
            "label": overall_row["summary"],
            "overall_score": overall_row["score"],
            "valuation_view": _build_valuation_view(valuation_row),
            "positives": _build_positives(metric_frames),
            "concerns": _build_concerns(metric_frames, red_flags),
            "red_flags": red_flags.loc[red_flags["triggered"], "flag"].tolist(),
        }
    )

    return {
        "financials": financials,
        "metric_frames": metric_frames,
        "scorecard": scorecard,
        "red_flags": red_flags,
        "metric_snapshot": metric_snapshot,
        "overall_row": overall_row,
        "valuation_row": valuation_row,
        "thesis": thesis,
    }


def summarize_company_analysis(
    request: AnalysisRequest,
    analysis_context: dict[str, Any],
) -> dict[str, Any]:
    """Build the summary payload returned by single-stock and batch analysis."""

    overall_row = analysis_context["overall_row"]
    valuation_row = analysis_context["valuation_row"]
    red_flags = analysis_context["red_flags"]
    red_flag_count = int(red_flags["triggered"].sum())

    return {
        "ticker": request.company.ticker,
        "company_name": request.company.company_name,
        "status": "success",
        "failure_category": None,
        "overall_label": overall_row["summary"],
        "overall_score": float(overall_row["score"]),
        "red_flag_count": red_flag_count,
        "share_price": float(valuation_row["share_price"]),
        "price_to_earnings": _optional_float(valuation_row.get("price_to_earnings")),
        "ev_to_sales": _optional_float(valuation_row.get("ev_to_sales")),
        "fcf_yield": _optional_float(valuation_row.get("fcf_yield")),
        "screen_rank": None,
        "report_eligible": True,
        "report_generated": False,
        "report_skip_reason": None,
        "artifact_root": None,
        "report_path": None,
        "scorecard_csv": None,
        "scorecard_json": None,
        "red_flags_csv": None,
        "metric_snapshot_csv": None,
        "charts_dir": None,
        "report_dir": None,
        "scorecard_dir": None,
        "error": None,
    }


def persist_company_analysis_outputs(
    request: AnalysisRequest,
    analysis_context: dict[str, Any],
) -> dict[str, Path]:
    """Persist charts, scorecards, and markdown reports for one analysis result."""

    output_root = Path(request.output_root)
    report_dir = output_root / "reports"
    chart_dir = output_root / "charts"
    scorecard_dir = output_root / "scorecards"
    report_dir.mkdir(parents=True, exist_ok=True)
    chart_dir.mkdir(parents=True, exist_ok=True)
    scorecard_dir.mkdir(parents=True, exist_ok=True)

    financials = analysis_context["financials"]
    scorecard = analysis_context["scorecard"]
    red_flags = analysis_context["red_flags"]
    metric_snapshot = analysis_context["metric_snapshot"]
    overall_row = analysis_context["overall_row"]
    chart_paths = generate_charts(financials, chart_dir)

    ticker_slug = request.company.ticker.lower()
    scorecard_csv = scorecard_dir / f"{ticker_slug}_scorecard.csv"
    scorecard_json = scorecard_dir / f"{ticker_slug}_scorecard.json"
    red_flags_csv = scorecard_dir / f"{ticker_slug}_red_flags.csv"
    metric_snapshot_csv = scorecard_dir / f"{ticker_slug}_metric_snapshot.csv"

    scorecard.to_csv(scorecard_csv, index=False)
    scorecard.to_json(scorecard_json, orient="records", indent=2)
    red_flags.to_csv(red_flags_csv, index=False)
    metric_snapshot.to_csv(metric_snapshot_csv, index=False)

    report_path = generate_markdown_report(
        request,
        report_dir,
        {
            "label": overall_row["summary"],
            "overall_score": f"{overall_row['score']:.1f}/100",
            "key_metrics_markdown": _markdown_table(metric_snapshot.head(12)),
            "scorecard_markdown": _markdown_table(scorecard[["category", "score", "weight", "summary"]]),
            "red_flags_markdown": _markdown_table(red_flags[["flag", "triggered", "severity", "detail"]]),
            "thesis_markdown": analysis_context["thesis"],
            "chart_list_markdown": "\n".join(f"- `{path.name}`" for path in chart_paths),
            "scorecard_csv": scorecard_csv,
            "scorecard_json": scorecard_json,
            "red_flags_csv": red_flags_csv,
            "metric_snapshot_csv": metric_snapshot_csv,
        },
    )

    return {
        "artifact_root": output_root,
        "report_path": report_path,
        "scorecard_csv": scorecard_csv,
        "scorecard_json": scorecard_json,
        "red_flags_csv": red_flags_csv,
        "metric_snapshot_csv": metric_snapshot_csv,
        "charts_dir": chart_dir,
        "report_dir": report_dir,
        "scorecard_dir": scorecard_dir,
    }


def run_company_analysis(
    request: AnalysisRequest,
    provider_runtime: ProviderRuntime,
    *,
    persist_outputs: bool = True,
) -> dict[str, Any]:
    """Run the full analysis pipeline for one company from provider-backed inputs."""

    analysis_context = prepare_company_analysis(request, provider_runtime)
    result = summarize_company_analysis(request, analysis_context)
    if persist_outputs:
        result.update(persist_company_analysis_outputs(request, analysis_context))
        result["report_generated"] = True
    return result


def build_batch_summary_rows(results: list[dict[str, Any]]) -> pd.DataFrame:
    """Build a ranked batch summary dataframe from per-ticker results."""

    dataframe = pd.DataFrame(results)
    if dataframe.empty:
        return dataframe
    successful = dataframe.loc[dataframe["status"] == "success"].copy()
    failed = dataframe.loc[dataframe["status"] != "success"].copy()
    if not successful.empty:
        successful = successful.sort_values(["overall_score", "ticker"], ascending=[False, True])
    if not failed.empty:
        failed = failed.sort_values("ticker")
    return pd.concat([successful, failed], ignore_index=True)


def render_batch_summary_markdown(summary: pd.DataFrame) -> str:
    """Render a markdown batch summary table."""

    columns = [
        "screen_rank",
        "ticker",
        "status",
        "overall_label",
        "overall_score",
        "price_to_earnings",
        "ev_to_sales",
        "fcf_yield",
        "red_flag_count",
        "report_eligible",
        "report_generated",
        "report_skip_reason",
        "artifact_root",
        "report_path",
        "scorecard_csv",
        "red_flags_csv",
        "failure_category",
        "error",
    ]
    existing_columns = [column for column in columns if column in summary.columns]
    return _markdown_table(summary[existing_columns])


def classify_runtime_failure(exc: Exception) -> tuple[str, str]:
    """Convert runtime exceptions into stable categories and operator-facing messages."""

    if isinstance(exc, ProviderConfigurationError):
        return "configuration", str(exc)
    if isinstance(exc, ProviderDataError):
        return "data", str(exc)
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return "network", f"Timed out while loading provider data: {exc}"

    exception_name = type(exc).__name__
    module_name = type(exc).__module__
    message = str(exc)
    message_lower = message.lower()

    if isinstance(exc, ProviderError):
        return "provider", message
    if "remote disconnected" in message_lower:
        return "network", f"Provider connection closed unexpectedly: {message}"
    if "connection" in exception_name.lower() or "connection" in message_lower:
        return "network", f"Provider network error: {message}"
    if "http" in exception_name.lower() or "request" in module_name.lower():
        return "provider", f"Provider request failed: {message}"

    return "unexpected", f"{exception_name}: {message}" if message else exception_name


def determine_report_eligibility(
    result: dict[str, Any],
    *,
    minimum_score: float | None = None,
    max_red_flags: int | None = None,
    allowed_labels: set[str] | None = None,
) -> tuple[bool, str | None]:
    """Determine whether a successful screen qualifies for full report generation."""

    if result.get("status") != "success":
        return False, "screen_failed"

    if minimum_score is not None and float(result["overall_score"]) < minimum_score:
        return False, f"score_below_minimum:{minimum_score:g}"

    if max_red_flags is not None and int(result["red_flag_count"]) > max_red_flags:
        return False, f"red_flags_above_maximum:{max_red_flags}"

    if allowed_labels:
        normalized_label = str(result["overall_label"]).strip().lower()
        if normalized_label not in allowed_labels:
            return False, "label_not_selected"

    return True, None


def _build_metric_snapshot(metric_frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for category, frame in metric_frames.items():
        latest = frame.iloc[-1]
        for metric, value in latest.items():
            if metric in {"fiscal_year", "as_of_date", "shares_as_of_date"}:
                continue
            rows.append(
                {
                    "category": category,
                    "metric": metric,
                    "value": _serialize_scalar(value),
                }
            )
    return pd.DataFrame(rows)


def _build_positives(metric_frames: dict[str, pd.DataFrame]) -> list[str]:
    positives: list[str] = []
    revenue_row = metric_frames["revenue"].iloc[-1]
    returns_row = metric_frames["returns"].iloc[-1]
    balance_row = metric_frames["balance_sheet"].iloc[-1]
    cashflow_row = metric_frames["cashflow"].iloc[-1]

    if pd.notna(revenue_row.get("revenue_cagr_3y")) and revenue_row["revenue_cagr_3y"] > 0.20:
        positives.append(f"Three-year revenue CAGR remains strong at {revenue_row['revenue_cagr_3y']:.1%}.")
    if returns_row.get("roce") > 0.15:
        positives.append(f"ROCE remains healthy at {returns_row['roce']:.1%}.")
    if balance_row.get("debt_to_equity") < 0.2:
        positives.append(f"Leverage is conservative with debt-to-equity at {balance_row['debt_to_equity']:.2f}x.")
    if cashflow_row.get("free_cash_flow") > 0:
        positives.append("Free cash flow remains positive in the latest fiscal year.")
    return positives


def _build_concerns(metric_frames: dict[str, pd.DataFrame], red_flags: pd.DataFrame) -> list[str]:
    concerns: list[str] = []
    valuation_row = metric_frames["valuation"].iloc[-1]
    if pd.notna(valuation_row.get("price_to_earnings")) and valuation_row["price_to_earnings"] > 40:
        concerns.append(f"The equity screens as expensive at {valuation_row['price_to_earnings']:.1f}x earnings.")
    if pd.notna(valuation_row.get("ev_to_sales")) and valuation_row["ev_to_sales"] > 6:
        concerns.append(f"Enterprise value to sales remains elevated at {valuation_row['ev_to_sales']:.1f}x.")
    triggered = red_flags.loc[red_flags["triggered"], "flag"].tolist()
    if triggered:
        concerns.append(f"Triggered red flags: {', '.join(triggered)}.")
    return concerns


def _build_valuation_view(valuation_row: pd.Series) -> str:
    pe = valuation_row.get("price_to_earnings")
    ev_sales = valuation_row.get("ev_to_sales")
    fcf_yield = valuation_row.get("fcf_yield")
    return (
        f"Latest valuation implies {pe:.1f}x earnings, {ev_sales:.1f}x EV/sales, "
        f"and an FCF yield of {fcf_yield:.1%}."
    )


def _markdown_table(frame: pd.DataFrame) -> str:
    rows = frame.copy()
    headers = list(rows.columns)
    header_line = "| " + " | ".join(headers) + " |"
    divider_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_lines = []
    for _, row in rows.iterrows():
        body_lines.append(
            "| " + " | ".join(_format_markdown_value(row[column]) for column in headers) + " |"
        )
    return "\n".join([header_line, divider_line, *body_lines])


def _format_markdown_value(value: Any) -> str:
    if pd.isna(value):
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _serialize_scalar(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    return value


def _optional_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def _model_to_dict(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
