# Data quality report

| Check | Table | Severity | Failing rows | % | Status |
|---|---|---|---|---|---|
| Duplicate order_id | orders | high | 0 | 0.0 | OK |
| Order without customer | orders | high | 0 | 0.0 | OK |
| Item without order | order_items | high | 0 | 0.0 | OK |
| Item without product | order_items | high | 0 | 0.0 | OK |
| Negative or zero price | order_items | high | 0 | 0.0 | OK |
| Delivered order without delivery date | orders | medium | 8 | 0.008 | WARNING |
| Delivered before purchase | orders | medium | 0 | 0.0 | OK |
| Order without items | orders | medium | 775 | 0.779 | WARNING |
| Order with several reviews | order_reviews | low | 547 | 0.554 | WARNING |
| Product without category | products | low | 610 | 1.851 | WARNING |
| Category without English translation | products | low | 2 | 2.74 | WARNING |
| Payment with zero value | order_payments | low | 9 | 0.009 | WARNING |

How the analysis handles these issues:
- only orders with status `delivered` are used for sales KPIs;
- orders without delivery date are excluded from delivery-time metrics;
- orders with several reviews use the average score;
- products without category are grouped as `unknown`.
