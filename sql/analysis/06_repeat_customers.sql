-- How many customers come back?
WITH per_customer AS (
    SELECT customer_unique_id, COUNT(*) AS n_orders, SUM(items_value) AS revenue
    FROM v_orders
    WHERE order_status = 'delivered'
      AND purchase_ts >= :start AND purchase_ts < :end
    GROUP BY customer_unique_id
)
SELECT
    CASE WHEN n_orders = 1 THEN '1 order' WHEN n_orders = 2 THEN '2 orders' ELSE '3+ orders' END AS segment,
    COUNT(*)                                              AS customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)    AS customers_pct,
    ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 2) AS revenue_pct
FROM per_customer
GROUP BY segment
ORDER BY segment;
