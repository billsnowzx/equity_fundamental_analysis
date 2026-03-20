# Tesla, Inc. (TSLA) Fundamental Analysis

Generated from the configured MVP analysis pipeline.

## Summary
- Exchange: NMS
- Reporting currency: USD
- Overall label: value trap / governance trap
- Overall score: 50.6/100

## Key Metrics
| category | metric | value |
| --- | --- | --- |
| revenue | revenue | 94827000000.0000 |
| revenue | revenue_yoy_growth | -0.0293 |
| revenue | revenue_cagr_3y | 0.0519 |
| revenue | revenue_cagr_5y | n/a |
| profitability | gross_margin | 0.1803 |
| profitability | ebitda_margin | 0.1241 |
| profitability | ebit_margin | 0.0511 |
| profitability | net_margin | 0.0400 |
| returns | roe | 0.0489 |
| returns | roa | 0.0292 |
| returns | roce | 0.0487 |
| returns | asset_turnover | 0.7298 |

## Scorecard
| category | score | weight | summary |
| --- | --- | --- | --- |
| revenue | 10.0000 | 0.1600 | Strong multi-year growth receives the highest weight in the model. |
| profitability | 44.0000 | 0.1600 | Margins measure structural business quality and pricing power. |
| returns | 14.0000 | 0.1600 | Return ratios reward efficient use of capital and assets. |
| balance_sheet | 100.0000 | 0.1600 | Leverage and liquidity determine resilience through weaker cycles. |
| cashflow | 92.0000 | 0.1600 | Cash conversion and free cash flow anchor the quality check. |
| valuation | 0.0000 | 0.1000 | Valuation is intentionally harsh on expensive equities. |
| red_flags | 90.0000 | 0.1000 | Triggered red flags reduce confidence in the headline metrics. |
| overall | 50.6000 | 1.0000 | value trap / governance trap |

## Red Flags
| flag | triggered | severity | detail |
| --- | --- | --- | --- |
| receivables_growth_faster_than_revenue | False | medium | Receivables growth 3.6% versus revenue growth -2.9%. |
| inventory_growth_faster_than_revenue | False | low | Inventory growth 3.1% versus revenue growth -2.9%. |
| cfo_below_net_income_for_two_years | False | high | Operating cash flow is below net income in each of the last two fiscal years. |
| rising_leverage | False | medium | Debt-to-equity has risen for three consecutive annual observations. |
| share_dilution | True | low | Shares outstanding changed by 18.0% versus 2023-12-30. |
| margin_deterioration_despite_sales_growth | False | medium | Revenue growth -2.9%; gross margin moved from 17.9% to 18.0%; net margin moved from 7.3% to 4.0%. |

## Investment Thesis

**Tesla, Inc. (TSLA)** currently screens as **value trap / governance trap** with an overall score of **50.6/100**.

### Positives
- Leverage is conservative with debt-to-equity at 0.18x.
- Free cash flow remains positive in the latest fiscal year.

### Concerns
- The equity screens as expensive at 388.5x earnings.
- Enterprise value to sales remains elevated at 15.5x.
- Triggered red flags: share_dilution.

### Valuation View
- Latest valuation implies 388.5x earnings, 15.5x EV/sales, and an FCF yield of 0.4%.

### Triggered Red Flags
- share_dilution


## Charts
- `revenue_and_operating_cash_flow.png`
- `margin_profile.png`

## Output Files
- Scorecard CSV: `outputs\live_watchlist\stocks\tsla\scorecards\tsla_scorecard.csv`
- Scorecard JSON: `outputs\live_watchlist\stocks\tsla\scorecards\tsla_scorecard.json`
- Report: `outputs\live_watchlist\stocks\tsla\reports\tsla_analysis_report.md`
