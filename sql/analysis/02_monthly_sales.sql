-- Monthly revenue, orders and average basket
SELECT
    purchase_month                         AS month,
    COUNT(*)                               AS orders,
    ROUND(SUM(items_value), 0)             AS revenue,
    ROUND(AVG(items_value), 2)             AS avg_order_value,
    ROUND(100.0 * AVG(is_late), 1)         AS late_pct
FROM v_orders
WHERE order_status = 'delivered'
  AND purchase_ts >= :start AND purchase_ts < :end
GROUP BY purchase_month
ORDER BY purchase_month;
