"""Investment thesis builder for the MVP report."""

from __future__ import annotations

from collections.abc import Mapping


def build_investment_thesis(sections: Mapping[str, object]) -> str:
    """Assemble a markdown thesis summary from pipeline sections."""

    company_name = str(sections.get("company_name", "Unknown company"))
    ticker = str(sections.get("ticker", "N/A"))
    label = str(sections.get("label", "watchlist only"))
    overall_score = float(sections.get("overall_score", 0.0))
    valuation_view = str(sections.get("valuation_view", "Valuation view unavailable."))
    positives = list(sections.get("positives", []))
    concerns = list(sections.get("concerns", []))
    red_flags = list(sections.get("red_flags", []))

    positive_lines = "\n".join(f"- {item}" for item in positives) or "- No clear strengths were generated."
    concern_lines = "\n".join(f"- {item}" for item in concerns) or "- No immediate concerns were generated."
    red_flag_lines = "\n".join(f"- {item}" for item in red_flags) or "- No red flags triggered."

    return f"""## Investment Thesis

**{company_name} ({ticker})** currently screens as **{label}** with an overall score of **{overall_score:.1f}/100**.

### Positives
{positive_lines}

### Concerns
{concern_lines}

### Valuation View
- {valuation_view}

### Triggered Red Flags
{red_flag_lines}
"""
