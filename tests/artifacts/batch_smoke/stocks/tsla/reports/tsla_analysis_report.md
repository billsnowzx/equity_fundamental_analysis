# Tesla, Inc. (TSLA) Fundamental Analysis

Generated from the configured MVP analysis pipeline.

## Summary
- Exchange: NASDAQ
- Reporting currency: USD
- Overall label: good business, too expensive
- Overall score: 74.8/100

## Key Metrics
| category | metric | value |
| --- | --- | --- |
| revenue | revenue | 105000.0000 |
| revenue | revenue_yoy_growth | 0.0850 |
| revenue | revenue_cagr_3y | 0.2495 |
| revenue | revenue_cagr_5y | 0.3370 |
| profitability | gross_margin | 0.1743 |
| profitability | ebitda_margin | 0.1457 |
| profitability | ebit_margin | 0.0876 |
| profitability | net_margin | 0.0771 |
| returns | roe | 0.1240 |
| returns | roa | 0.0721 |
| returns | roce | 0.1147 |
| returns | asset_turnover | 0.9349 |

## Scorecard
| category | score | weight | summary |
| --- | --- | --- | --- |
| revenue | 85.0000 | 0.1600 | Strong multi-year growth receives the highest weight in the model. |
| profitability | 68.0000 | 0.1600 | Margins measure structural business quality and pricing power. |
| returns | 79.0000 | 0.1600 | Return ratios reward efficient use of capital and assets. |
| balance_sheet | 100.0000 | 0.1600 | Leverage and liquidity determine resilience through weaker cycles. |
| cashflow | 92.0000 | 0.1600 | Cash conversion and free cash flow anchor the quality check. |
| valuation | 5.0000 | 0.1000 | Valuation is intentionally harsh on expensive equities. |
| red_flags | 65.0000 | 0.1000 | Triggered red flags reduce confidence in the headline metrics. |
| overall | 74.8400 | 1.0000 | good business, too expensive |

## Red Flags
| flag | triggered | severity | detail |
| --- | --- | --- | --- |
| receivables_growth_faster_than_revenue | False | medium | Receivables growth 7.0% versus revenue growth 8.5%. |
| inventory_growth_faster_than_revenue | True | low | Inventory growth 10.1% versus revenue growth 8.5%. |
| cfo_below_net_income_for_two_years | False | high | Operating cash flow is below net income in each of the last two fiscal years. |
| rising_leverage | False | medium | Debt-to-equity has risen for three consecutive annual observations. |
| share_dilution | True | low | Shares outstanding changed by 8.1% versus 2021-12-31. |
| margin_deterioration_despite_sales_growth | True | medium | Revenue growth 8.5%; gross margin moved from 18.2% to 17.4%; net margin moved from 15.5% to 7.7%. |

## Investment Thesis

**Tesla, Inc. (TSLA)** currently screens as **good business, too expensive** with an overall score of **74.8/100**.

### Positives
- Three-year revenue CAGR remains strong at 25.0%.
- Leverage is conservative with debt-to-equity at 0.08x.
- Free cash flow remains positive in the latest fiscal year.

### Concerns
- The equity screens as expensive at 98.8x earnings.
- Enterprise value to sales remains elevated at 7.4x.
- Triggered red flags: inventory_growth_faster_than_revenue, share_dilution, margin_deterioration_despite_sales_growth.

### Valuation View
- Latest valuation implies 98.8x earnings, 7.4x EV/sales, and an FCF yield of 0.7%.

### Triggered Red Flags
- inventory_growth_faster_than_revenue
- share_dilution
- margin_deterioration_despite_sales_growth


## Charts
- `revenue_and_operating_cash_flow.png`
- `margin_profile.png`

## Output Files
- Scorecard CSV: `D:\AI\equity_fundamental_analysis\tests\artifacts\batch_smoke\stocks\tsla\scorecards\tsla_scorecard.csv`
- Scorecard JSON: `D:\AI\equity_fundamental_analysis\tests\artifacts\batch_smoke\stocks\tsla\scorecards\tsla_scorecard.json`
- Report: `D:\AI\equity_fundamental_analysis\tests\artifacts\batch_smoke\stocks\tsla\reports\tsla_analysis_report.md`
