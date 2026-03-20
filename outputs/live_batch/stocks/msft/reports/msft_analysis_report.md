# Microsoft Corporation (MSFT) Fundamental Analysis

Generated from the configured MVP analysis pipeline.

## Summary
- Exchange: NMS
- Reporting currency: USD
- Overall label: good business, too expensive
- Overall score: 75.4/100

## Key Metrics
| category | metric | value |
| --- | --- | --- |
| revenue | revenue | 281724000000.0000 |
| revenue | revenue_yoy_growth | 0.1493 |
| revenue | revenue_cagr_3y | 0.1242 |
| revenue | revenue_cagr_5y | n/a |
| profitability | gross_margin | 0.6882 |
| profitability | ebitda_margin | 0.5685 |
| profitability | ebit_margin | 0.4562 |
| profitability | net_margin | 0.3615 |
| returns | roe | 0.3328 |
| returns | roa | 0.1800 |
| returns | roce | 0.2973 |
| returns | asset_turnover | 0.4981 |

## Scorecard
| category | score | weight | summary |
| --- | --- | --- | --- |
| revenue | 55.0000 | 0.1600 | Strong multi-year growth receives the highest weight in the model. |
| profitability | 100.0000 | 0.1600 | Margins measure structural business quality and pricing power. |
| returns | 80.0000 | 0.1600 | Return ratios reward efficient use of capital and assets. |
| balance_sheet | 89.0000 | 0.1600 | Leverage and liquidity determine resilience through weaker cycles. |
| cashflow | 80.0000 | 0.1600 | Cash conversion and free cash flow anchor the quality check. |
| valuation | 23.0000 | 0.1000 | Valuation is intentionally harsh on expensive equities. |
| red_flags | 85.0000 | 0.1000 | Triggered red flags reduce confidence in the headline metrics. |
| overall | 75.4400 | 1.0000 | good business, too expensive |

## Red Flags
| flag | triggered | severity | detail |
| --- | --- | --- | --- |
| receivables_growth_faster_than_revenue | True | medium | Receivables growth 22.8% versus revenue growth 14.9%. |
| inventory_growth_faster_than_revenue | False | low | Inventory growth -24.7% versus revenue growth 14.9%. |
| cfo_below_net_income_for_two_years | False | high | Operating cash flow is below net income in each of the last two fiscal years. |
| rising_leverage | False | medium | Debt-to-equity has risen for three consecutive annual observations. |
| share_dilution | False | low | Shares outstanding changed by 0.0% versus 2023-12-27. |
| margin_deterioration_despite_sales_growth | False | medium | Revenue growth 14.9%; gross margin moved from 69.8% to 68.8%; net margin moved from 36.0% to 36.1%. |

## Investment Thesis

**Microsoft Corporation (MSFT)** currently screens as **good business, too expensive** with an overall score of **75.4/100**.

### Positives
- ROCE remains healthy at 29.7%.
- Leverage is conservative with debt-to-equity at 0.18x.
- Free cash flow remains positive in the latest fiscal year.

### Concerns
- Enterprise value to sales remains elevated at 10.4x.
- Triggered red flags: receivables_growth_faster_than_revenue.

### Valuation View
- Latest valuation implies 28.6x earnings, 10.4x EV/sales, and an FCF yield of 2.5%.

### Triggered Red Flags
- receivables_growth_faster_than_revenue


## Charts
- `revenue_and_operating_cash_flow.png`
- `margin_profile.png`

## Output Files
- Scorecard CSV: `outputs\live_batch\stocks\msft\scorecards\msft_scorecard.csv`
- Scorecard JSON: `outputs\live_batch\stocks\msft\scorecards\msft_scorecard.json`
- Report: `outputs\live_batch\stocks\msft\reports\msft_analysis_report.md`
