-- Headline KPIs for delivered orders
SELECT
    COUNT(*)                                   AS orders,
    COUNT(DISTINCT customer_unique_id)         AS customers,
    ROUND(SUM(items_value), 0)                 AS revenue,
    ROUND(AVG(items_value), 2)                 AS avg_order_value,
    ROUND(AVG(delivery_days), 1)               AS avg_delivery_days,
    ROUND(100.0 * AVG(is_late), 1)             AS late_pct,
    ROUND(AVG(review_score), 2)                AS avg_review_score,
    ROUND(100.0 * AVG(review_score <= 2), 1)   AS low_review_pct
FROM v_orders
WHERE order_status = 'delivered'
  AND purchase_ts >= :start AND purchase_ts < :end;
