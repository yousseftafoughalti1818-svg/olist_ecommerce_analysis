-- One row per order with delivery, value and review information.
-- Revenue = sum of product prices (freight excluded).
DROP VIEW IF EXISTS v_orders;
CREATE VIEW v_orders AS
SELECT
    o.order_id,
    c.customer_unique_id,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp                                   AS purchase_ts,
    strftime('%Y-%m', o.order_purchase_timestamp)                AS purchase_month,
    o.order_delivered_customer_date                              AS delivered_ts,
    o.order_estimated_delivery_date                              AS estimated_ts,
    julianday(o.order_delivered_customer_date)
        - julianday(o.order_purchase_timestamp)                  AS delivery_days,
    julianday(date(o.order_delivered_customer_date))
        - julianday(date(o.order_estimated_delivery_date))       AS delay_days,
    CASE
        WHEN o.order_delivered_customer_date IS NULL THEN NULL
        WHEN date(o.order_delivered_customer_date) > date(o.order_estimated_delivery_date) THEN 1
        ELSE 0
    END                                                          AS is_late,
    i.n_items,
    i.items_value,
    i.freight_value,
    r.review_score
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
LEFT JOIN (
    SELECT order_id, COUNT(*) AS n_items, SUM(price) AS items_value, SUM(freight_value) AS freight_value
    FROM order_items
    GROUP BY order_id
) i ON i.order_id = o.order_id
LEFT JOIN (
    -- a few orders have several reviews: keep the average
    SELECT order_id, AVG(review_score) AS review_score
    FROM order_reviews
    GROUP BY order_id
) r ON r.order_id = o.order_id;

-- Delivered orders inside the analysis period (filtered with :start / :end in each query)
DROP VIEW IF EXISTS v_items;
CREATE VIEW v_items AS
SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    oi.price,
    oi.freight_value,
    COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
    v.purchase_ts,
    v.order_status,
    v.customer_state
FROM order_items oi
JOIN v_orders v ON v.order_id = oi.order_id
LEFT JOIN products p ON p.product_id = oi.product_id
LEFT JOIN category_translation t ON t.product_category_name = p.product_category_name;
