"""Chart generation for the MVP pipeline."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def generate_charts(financials: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Generate core revenue, cash-flow, and margin charts."""

    output_dir.mkdir(parents=True, exist_ok=True)
    prepared = financials.sort_values("fiscal_year").reset_index(drop=True)

    revenue_chart_path = output_dir / "revenue_and_operating_cash_flow.png"
    _generate_revenue_cashflow_chart(prepared, revenue_chart_path)

    margin_chart_path = output_dir / "margin_profile.png"
    _generate_margin_chart(prepared, margin_chart_path)

    return [revenue_chart_path, margin_chart_path]


def _generate_revenue_cashflow_chart(financials: pd.DataFrame, output_path: Path) -> None:
    years = financials["fiscal_year"]

    figure, axis = plt.subplots(figsize=(9, 5))
    axis.bar(years - 0.15, financials["revenue"], width=0.3, label="Revenue")
    axis.bar(years + 0.15, financials["operating_cash_flow"], width=0.3, label="Operating cash flow")
    axis.set_title("Revenue vs Operating Cash Flow")
    axis.set_xlabel("Fiscal year")
    axis.set_ylabel("USD millions")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def _generate_margin_chart(financials: pd.DataFrame, output_path: Path) -> None:
    years = financials["fiscal_year"]
    gross_margin = financials["gross_profit"].div(financials["revenue"])
    ebit_margin = financials["operating_income"].div(financials["revenue"])
    net_margin = financials["net_income"].div(financials["revenue"])

    figure, axis = plt.subplots(figsize=(9, 5))
    axis.plot(years, gross_margin, marker="o", label="Gross margin")
    axis.plot(years, ebit_margin, marker="o", label="EBIT margin")
    axis.plot(years, net_margin, marker="o", label="Net margin")
    axis.set_title("Margin Profile")
    axis.set_xlabel("Fiscal year")
    axis.set_ylabel("Margin")
    axis.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.0%}"))
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
