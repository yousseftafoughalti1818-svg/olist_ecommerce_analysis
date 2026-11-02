-- Does late delivery hurt customer satisfaction?
SELECT
    CASE
        WHEN delay_days <= 0  THEN '1. On time or early'
        WHEN delay_days <= 3  THEN '2. 1-3 days late'
        WHEN delay_days <= 7  THEN '3. 4-7 days late'
        WHEN delay_days <= 14 THEN '4. 8-14 days late'
        ELSE                       '5. 15+ days late'
    END                                        AS delay_bucket,
    COUNT(*)                                   AS orders,
    ROUND(AVG(review_score), 2)                AS avg_review_score,
    ROUND(100.0 * AVG(review_score <= 2), 1)   AS low_review_pct
FROM v_orders
WHERE order_status = 'delivered'
  AND delay_days IS NOT NULL
  AND review_score IS NOT NULL
  AND purchase_ts >= :start AND purchase_ts < :end
GROUP BY delay_bucket
ORDER BY delay_bucket;
