# Power BI dashboard

The Python pipeline exports a **star schema** into `powerbi/data/`. This guide explains how the
dashboard `olist_dashboard.pbix` is built from these files.

```bash
python scripts/download_data.py
python -m olist_analysis.pipeline     # creates powerbi/data/*.csv
```

## 1. Data model

| Table | Grain | Key columns |
|---|---|---|
| `fact_orders` | 1 row per order | order_id, customer_unique_id, order_date, revenue, freight, delivery_days, delay_days, is_late, review_score, main_payment_type |
| `fact_order_items` | 1 row per product sold | order_id, product_id, seller_id, order_date, price, freight |
| `dim_date` | 1 row per day (2017-01-01 → 2018-08-31) | date, year, month, quarter, weekday |
| `dim_customers` | 1 row per customer | customer_unique_id, city, state |
| `dim_products` | 1 row per product | product_id, category (English) |
| `dim_sellers` | 1 row per seller | seller_id, city, state |

Relationships (all *many-to-one*, single direction):

```
dim_date[date]                       1 ─── * fact_orders[order_date]
dim_date[date]                       1 ─── * fact_order_items[order_date]
dim_customers[customer_unique_id]    1 ─── * fact_orders[customer_unique_id]
dim_products[product_id]             1 ─── * fact_order_items[product_id]
dim_sellers[seller_id]               1 ─── * fact_order_items[seller_id]
```

Mark `dim_date` as the date table (*Table tools → Mark as date table → date*).

> **Import tip (French Windows):** the CSV files use a dot as decimal separator. Before importing,
> set *File → Options → Current file → Regional settings → Locale for import* to
> **English (United States)**, otherwise `125.12` can be read as `12512`.

## 2. DAX measures

```dax
Revenue =
CALCULATE ( SUM ( fact_orders[revenue] ), fact_orders[order_status] = "delivered" )

Orders =
CALCULATE ( DISTINCTCOUNT ( fact_orders[order_id] ), fact_orders[order_status] = "delivered" )

Customers =
CALCULATE ( DISTINCTCOUNT ( fact_orders[customer_unique_id] ), fact_orders[order_status] = "delivered" )

Average Basket = DIVIDE ( [Revenue], [Orders] )

Revenue Previous Month =
CALCULATE ( [Revenue], DATEADD ( dim_date[date], -1, MONTH ) )

Revenue MoM % = DIVIDE ( [Revenue] - [Revenue Previous Month], [Revenue Previous Month] )

Late Delivery % =
DIVIDE (
    CALCULATE ( COUNTROWS ( fact_orders ), fact_orders[is_late] = 1 ),
    CALCULATE ( COUNTROWS ( fact_orders ), NOT ISBLANK ( fact_orders[is_late] ) )
)

Average Review = AVERAGE ( fact_orders[review_score] )

Item Revenue =
CALCULATE ( SUM ( fact_order_items[price] ), fact_order_items[order_status] = "delivered" )
```

Calculated column in `fact_orders` (used on the delivery page):

```dax
Delay Bucket =
SWITCH (
    TRUE (),
    ISBLANK ( fact_orders[delay_days] ), BLANK (),
    fact_orders[delay_days] <= 0, "1. On time",
    fact_orders[delay_days] <= 3, "2. 1-3 days late",
    fact_orders[delay_days] <= 7, "3. 4-7 days late",
    fact_orders[delay_days] <= 14, "4. 8-14 days late",
    "5. 15+ days late"
)
```

> Use `[Item Revenue]` (not `[Revenue]`) in visuals split by category or seller, because those
> dimensions are linked to `fact_order_items`.

## 3. Report pages

**Page 1 – Overview**
- Cards: Revenue, Orders, Customers, Average Basket, Late Delivery %, Average Review
- Line chart: Revenue by `dim_date[month]`
- Filled map or bar chart: Revenue by `dim_customers[state]`
- Slicers: year, quarter, state

**Page 2 – Products & sellers**
- Bar chart: top 15 `dim_products[category]` by Item Revenue
- Table: top 10 sellers (seller_id, state, Item Revenue)
- Donut: orders by `main_payment_type`

**Page 3 – Delivery & satisfaction**
- Column chart: Average Review by Delay Bucket
- Bar chart: Late Delivery % and average `delivery_days` by state
- Line chart: Late Delivery % by month (peaks after Black Friday 2017 and in Feb–Mar 2018)

Save the file as `powerbi/olist_dashboard.pbix` and add screenshots of each page in
`powerbi/screenshots/`.
