-- Schema exploration for the E-Commerce DuckDB dataset.
-- All statements are read-only.

-- 1. Table inventory
COPY (
    SELECT table_name
    FROM duckdb_tables()
    WHERE schema_name = 'main'
    ORDER BY table_name
) TO 'analysis/exports/CSVs/00_tables.csv'
WITH (HEADER, DELIMITER ',');

-- 2. Column metadata
COPY (
    WITH expected_raw_tables(table_name) AS (
        VALUES
            ('raw_customers'),
            ('raw_orders'),
            ('raw_order_items'),
            ('raw_payments'),
            ('raw_products'),
            ('raw_categories'),
            ('raw_reviews'),
            ('raw_marketing'),
            ('raw_customer_support'),
            ('raw_shipping'),
            ('raw_subscriptions'),
            ('raw_user_sessions'),
            ('raw_abandoned_carts'),
            ('raw_inventory'),
            ('raw_promotions'),
            ('raw_order_promotions'),
            ('raw_product_variants')
    )
    SELECT
        c.table_name,
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.ordinal_position
    FROM information_schema.columns AS c
    INNER JOIN expected_raw_tables AS e
        ON c.table_name = e.table_name
    ORDER BY
        c.table_name,
        c.ordinal_position
) TO 'analysis/exports/CSVs/00_columns.csv'
WITH (HEADER, DELIMITER ',');

-- 3. Row-count profiling across all 17 raw tables
COPY (
    SELECT
        'raw_customers' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: ~17.4K rows
    FROM raw_customers
    UNION ALL
    SELECT
        'raw_orders' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: ~18.5K rows
    FROM raw_orders
    UNION ALL
    SELECT
        'raw_order_items' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: ~37.2K rows
    FROM raw_order_items
    UNION ALL
    SELECT
        'raw_payments' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: ~18.5K rows; should broadly align 1:1 with orders
    FROM raw_payments
    UNION ALL
    SELECT
        'raw_products' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: 15 rows; exact small reference table check
    FROM raw_products
    UNION ALL
    SELECT
        'raw_categories' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: 5 rows; exact small reference table check
    FROM raw_categories
    UNION ALL
    SELECT
        'raw_reviews' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: ~5.5K rows
    FROM raw_reviews
    UNION ALL
    SELECT
        'raw_marketing' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: 64 rows; exact campaign-period check
    FROM raw_marketing
    UNION ALL
    SELECT
        'raw_customer_support' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: ~1.9K rows
    FROM raw_customer_support
    UNION ALL
    SELECT
        'raw_shipping' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: ~15.7K rows; fewer than orders if some are pending/cancelled
    FROM raw_shipping
    UNION ALL
    SELECT
        'raw_subscriptions' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: ~2.5K rows
    FROM raw_subscriptions
    UNION ALL
    SELECT
        'raw_user_sessions' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: ~68.7K rows; largest clickstream-style table
    FROM raw_user_sessions
    UNION ALL
    SELECT
        'raw_abandoned_carts' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: ~6.5K rows
    FROM raw_abandoned_carts
    UNION ALL
    SELECT
        'raw_inventory' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: 15 rows; should align with product/SKU grain
    FROM raw_inventory
    UNION ALL
    SELECT
        'raw_promotions' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: 10 rows; exact small reference table check
    FROM raw_promotions
    UNION ALL
    SELECT
        'raw_order_promotions' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: 15 rows; exact promotion-application check
    FROM raw_order_promotions
    UNION ALL
    SELECT
        'raw_product_variants' AS table_name,
        COUNT(*) AS row_count -- TASKS.md: 15 rows; should align with inventory/product variant grain
    FROM raw_product_variants
    ORDER BY table_name
) TO 'analysis/exports/CSVs/00_row_count.csv'
WITH (HEADER, DELIMITER ',');

-- 4. Date-range profiling for timestamp/date-bearing raw tables
COPY (
    SELECT
        'raw_orders' AS table_name,
        COUNT(*) AS row_count,
        MIN(order_date) AS min_activity_at,
        MAX(order_date) AS max_activity_at
    FROM raw_orders
    UNION ALL
    SELECT
        'raw_shipping' AS table_name,
        COUNT(*) AS row_count,
        MIN(shipped_date) AS min_activity_at,
        MAX(COALESCE(delivered_date, shipped_date)) AS max_activity_at
    FROM raw_shipping
    UNION ALL
    SELECT
        'raw_reviews' AS table_name,
        COUNT(*) AS row_count,
        MIN(review_date) AS min_activity_at,
        MAX(review_date) AS max_activity_at
    FROM raw_reviews
    UNION ALL
    SELECT
        'raw_marketing' AS table_name,
        COUNT(*) AS row_count,
        MIN(start_date) AS min_activity_at,
        MAX(end_date) AS max_activity_at
    FROM raw_marketing
    UNION ALL
    SELECT
        'raw_customer_support' AS table_name,
        COUNT(*) AS row_count,
        MIN(created_at) AS min_activity_at,
        MAX(created_at) AS max_activity_at
    FROM raw_customer_support
    UNION ALL
    SELECT
        'raw_subscriptions' AS table_name,
        COUNT(*) AS row_count,
        MIN(start_date) AS min_activity_at,
        MAX(end_date) AS max_activity_at
    FROM raw_subscriptions
    UNION ALL
    SELECT
        'raw_user_sessions' AS table_name,
        COUNT(*) AS row_count,
        MIN(session_start) AS min_activity_at,
        MAX(session_end) AS max_activity_at
    FROM raw_user_sessions
    UNION ALL
    SELECT
        'raw_abandoned_carts' AS table_name,
        COUNT(*) AS row_count,
        MIN(added_at) AS min_activity_at,
        MAX(added_at) AS max_activity_at
    FROM raw_abandoned_carts
    ORDER BY table_name
) TO 'analysis/exports/CSVs/00_date_range.csv'
WITH (HEADER, DELIMITER ',');
