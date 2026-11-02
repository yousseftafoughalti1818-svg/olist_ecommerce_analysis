-- Revenue concentration among sellers (deciles: 1 = best sellers)
WITH s AS (
    SELECT seller_id, SUM(price) AS revenue
    FROM v_items
    WHERE order_status = 'delivered'
      AND purchase_ts >= :start AND purchase_ts < :end
    GROUP BY seller_id
), ranked AS (
    SELECT seller_id, revenue, NTILE(10) OVER (ORDER BY revenue DESC) AS decile
    FROM s
)
SELECT
    decile,
    COUNT(*)                                                  AS sellers,
    ROUND(SUM(revenue), 0)                                    AS revenue,
    ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS revenue_share_pct
FROM ranked
GROUP BY decile
ORDER BY decile;
