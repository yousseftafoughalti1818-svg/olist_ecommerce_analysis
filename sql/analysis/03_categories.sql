-- Revenue by product category with cumulative share (Pareto)
WITH cat AS (
    SELECT category,
           COUNT(*)              AS items_sold,
           SUM(price)            AS revenue,
           AVG(price)            AS avg_price
    FROM v_items
    WHERE order_status = 'delivered'
      AND purchase_ts >= :start AND purchase_ts < :end
    GROUP BY category
)
SELECT
    category,
    items_sold,
    ROUND(revenue, 0)                                                      AS revenue,
    ROUND(avg_price, 2)                                                    AS avg_price,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 2)                       AS revenue_share_pct,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC
                 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
          / SUM(revenue) OVER (), 1)                                       AS cumulative_share_pct
FROM cat
ORDER BY revenue DESC;
