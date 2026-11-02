-- Payment methods (an order can be paid with several methods)
WITH p AS (
    SELECT p.order_id, p.payment_type, p.payment_value, p.payment_installments
    FROM order_payments p
    JOIN v_orders v ON v.order_id = p.order_id
    WHERE v.order_status = 'delivered'
      AND v.purchase_ts >= :start AND v.purchase_ts < :end
)
SELECT
    payment_type,
    COUNT(DISTINCT order_id)                                                 AS orders,
    ROUND(100.0 * COUNT(DISTINCT order_id) / (SELECT COUNT(DISTINCT order_id) FROM p), 1) AS orders_pct,
    ROUND(SUM(payment_value), 0)                                             AS amount,
    ROUND(AVG(payment_installments), 1)                                      AS avg_installments
FROM p
GROUP BY payment_type
ORDER BY orders DESC;
