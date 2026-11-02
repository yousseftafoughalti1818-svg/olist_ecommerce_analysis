-- Sales and logistics by customer state
SELECT
    customer_state                                         AS state,
    COUNT(*)                                               AS orders,
    ROUND(SUM(items_value), 0)                             AS revenue,
    ROUND(AVG(items_value), 2)                             AS avg_order_value,
    ROUND(100.0 * SUM(freight_value) / SUM(items_value), 1) AS freight_pct_of_price,
    ROUND(AVG(delivery_days), 1)                           AS avg_delivery_days,
    ROUND(100.0 * AVG(is_late), 1)                         AS late_pct,
    ROUND(AVG(review_score), 2)                            AS avg_review_score
FROM v_orders
WHERE order_status = 'delivered'
  AND purchase_ts >= :start AND purchase_ts < :end
GROUP BY customer_state
ORDER BY revenue DESC;
