# Microsoft Corporation (MSFT) Fundamental Analysis

Generated from the configured MVP analysis pipeline.

## Summary
- Exchange: NASDAQ
- Reporting currency: USD
- Overall label: good business, too expensive
- Overall score: 77.0/100

## Key Metrics
| category | metric | value |
| --- | --- | --- |
| revenue | revenue | 232000.0000 |
| revenue | revenue_yoy_growth | 0.0948 |
| revenue | revenue_cagr_3y | 0.1134 |
| revenue | revenue_cagr_5y | 0.1301 |
| profitability | gross_margin | 0.6897 |
| profitability | ebitda_margin | 0.5302 |
| profitability | ebit_margin | 0.4310 |
| profitability | net_margin | 0.3448 |
| returns | roe | 0.3668 |
| returns | roa | 0.1900 |
| returns | roce | 0.3181 |
| returns | asset_turnover | 0.5511 |

## Scorecard
| category | score | weight | summary |
| --- | --- | --- | --- |
| revenue | 50.0000 | 0.1600 | Strong multi-year growth receives the highest weight in the model. |
| profitability | 100.0000 | 0.1600 | Margins measure structural business quality and pricing power. |
| returns | 88.0000 | 0.1600 | Return ratios reward efficient use of capital and assets. |
| balance_sheet | 90.0000 | 0.1600 | Leverage and liquidity determine resilience through weaker cycles. |
| cashflow | 86.0000 | 0.1600 | Cash conversion and free cash flow anchor the quality check. |
| valuation | 8.0000 | 0.1000 | Valuation is intentionally harsh on expensive equities. |
| red_flags | 100.0000 | 0.1000 | Triggered red flags reduce confidence in the headline metrics. |
| overall | 77.0400 | 1.0000 | good business, too expensive |

## Red Flags
| flag | triggered | severity | detail |
| --- | --- | --- | --- |
| receivables_growth_faster_than_revenue | False | medium | Receivables growth 6.8% versus revenue growth 9.5%. |
| inventory_growth_faster_than_revenue | False | low | Inventory growth -4.0% versus revenue growth 9.5%. |
| cfo_below_net_income_for_two_years | False | high | Operating cash flow is below net income in each of the last two fiscal years. |
| rising_leverage | False | medium | Debt-to-equity has risen for three consecutive annual observations. |
| share_dilution | False | low | Shares outstanding changed by -2.0% versus 2021-06-30. |
| margin_deterioration_despite_sales_growth | False | medium | Revenue growth 9.5%; gross margin moved from 68.9% to 69.0%; net margin moved from 34.1% to 34.5%. |

## Investment Thesis

**Microsoft Corporation (MSFT)** currently screens as **good business, too expensive** with an overall score of **77.0/100**.

### Positives
- ROCE remains healthy at 31.8%.
- Free cash flow remains positive in the latest fiscal year.

### Concerns
- The equity screens as expensive at 41.8x earnings.
- Enterprise value to sales remains elevated at 14.1x.

### Valuation View
- Latest valuation implies 41.8x earnings, 14.1x EV/sales, and an FCF yield of 2.0%.

### Triggered Red Flags
- No red flags triggered.


## Charts
- `revenue_and_operating_cash_flow.png`
- `margin_profile.png`

## Output Files
- Scorecard CSV: `D:\AI\equity_fundamental_analysis\tests\artifacts\batch_top_n\stocks\msft\scorecards\msft_scorecard.csv`
- Scorecard JSON: `D:\AI\equity_fundamental_analysis\tests\artifacts\batch_top_n\stocks\msft\scorecards\msft_scorecard.json`
- Report: `D:\AI\equity_fundamental_analysis\tests\artifacts\batch_top_n\stocks\msft\reports\msft_analysis_report.md`
