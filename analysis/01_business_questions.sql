-- Business-question analysis for the E-Commerce DuckDB dataset.


-- =============================================================================
-- 01. How is revenue trending over time?
-- =============================================================================
-- Method:
-- - Aggregate raw_order_items to order grain before joining raw_orders.
-- - Exclude cancelled and refunded orders from recognized revenue.
-- - Roll revenue up by order month to show the revenue trend.

COPY (
    WITH order_revenue AS (
        SELECT
            oi.order_id,
            SUM(oi.total_price) AS order_revenue
        FROM raw_order_items AS oi
        GROUP BY
            oi.order_id
    )

    SELECT
        DATE_TRUNC('month', o.order_date) AS revenue_month,
        SUM(orv.order_revenue) AS revenue
    FROM raw_orders AS o
    LEFT JOIN order_revenue AS orv
        ON o.id = orv.order_id
    WHERE o.status NOT IN ('cancelled', 'refunded')
    GROUP BY
        DATE_TRUNC('month', o.order_date)
    ORDER BY
        revenue_month
) TO 'analysis/exports/CSVs/01_01_revenue_over_time.csv'
WITH (HEADER, DELIMITER ',');


-- =============================================================================
-- 02. How are order volume and active customers trending over time?
-- =============================================================================
-- Method:
-- - Use raw_orders as the order-level fact table.
-- - Count total orders and distinct ordering customers by order month.
-- - Sort chronologically to compare order demand and customer reach over time.

COPY (
    SELECT
        DATE_TRUNC('month', order_date) AS order_month,
        COUNT(*) AS total_orders,
        COUNT(DISTINCT user_id) AS unique_customers
    FROM raw_orders
    GROUP BY
        DATE_TRUNC('month', order_date)
    ORDER BY
        order_month
) TO 'analysis/exports/CSVs/01_02_orders_over_time.csv'
WITH (HEADER, DELIMITER ',');


-- =============================================================================
-- 03. How is average order value trending over time?
-- =============================================================================
-- Method:
-- - Join raw_orders to raw_order_items and aggregate line-item value to order grain.
-- - Calculate monthly order count, total revenue, and average order value.
-- - Sort chronologically to compare basket-size changes over time.

COPY (
    WITH order_revenue AS (
        SELECT
            o.id AS order_id,
            o.order_date,
            o.status,
            SUM(oi.total_price) AS order_value
        FROM raw_orders AS o
        LEFT JOIN raw_order_items AS oi
            ON o.id = oi.order_id
        GROUP BY
            o.id,
            o.order_date,
            o.status
    )

    SELECT
        DATE_TRUNC('month', order_date) AS order_month,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(order_value) AS total_revenue,
        AVG(order_value) AS average_order_value
    FROM order_revenue
    GROUP BY
        DATE_TRUNC('month', order_date)
    ORDER BY
        order_month
) TO 'analysis/exports/CSVs/01_03_order_value_over_time.csv'
WITH (HEADER, DELIMITER ',');


-- =============================================================================
-- 04. Which countries, regions, and cities generate the most revenue?
-- =============================================================================
-- Method:
-- - Aggregate raw_payments to order grain before joining order and customer data.
-- - Group by customer geography to compare orders, customers, revenue, and AOV.
-- - Rank markets by total revenue to identify the largest geographic opportunities.

COPY (
    WITH order_revenue AS (
        SELECT
            order_id,
            SUM(amount) AS revenue
        FROM raw_payments
        GROUP BY order_id
    )

    SELECT
        c.country,
        c.region,
        c.city,
        COUNT(DISTINCT o.id) AS total_orders,
        COUNT(DISTINCT c.id) AS total_customers,
        SUM(orv.revenue) AS total_revenue,
        AVG(orv.revenue) AS avg_order_value
    FROM raw_orders AS o
    INNER JOIN raw_customers AS c
        ON o.user_id = c.id
    LEFT JOIN order_revenue AS orv
        ON o.id = orv.order_id
    GROUP BY
        c.country,
        c.region,
        c.city
    ORDER BY
        total_revenue DESC
) TO 'analysis/exports/CSVs/01_04_geography_revenue.csv'
WITH (HEADER, DELIMITER ',');


-- =============================================================================
-- 05. Which countries have the largest customer bases?
-- =============================================================================
-- Method:
-- - Use raw_customers as the customer-level dimension table.
-- - Count customer records by country.
-- - Rank countries by customer count to identify the largest customer markets.

COPY (
    SELECT
        country,
        COUNT(*) AS number_of_customers
    FROM raw_customers
    GROUP BY country
    ORDER BY number_of_customers DESC
) TO 'analysis/exports/CSVs/01_05_geography_customers.csv'
WITH (HEADER, DELIMITER ',');

-- =============================================================================
-- 06. How does revenue mix vary by payment method over time?
-- =============================================================================
-- Method:
-- - Join raw_payments to raw_orders to add order-date context to each payment.
-- - Aggregate payment amount by order month and payment method.
-- - Sort by month and revenue to compare payment-method contribution over time.

COPY (
    SELECT
        DATE_TRUNC('month', o.order_date) AS order_month,
        p.payment_method,
        SUM(p.amount) AS revenue
    FROM raw_payments AS p
    INNER JOIN raw_orders AS o
        ON p.order_id = o.id
    GROUP BY
        DATE_TRUNC('month', o.order_date),
        p.payment_method
    ORDER BY
        order_month,
        revenue DESC
) TO 'analysis/exports/CSVs/01_06_payment_method_revenue.csv'
WITH (HEADER, DELIMITER ',');

-- =============================================================================
-- 07. Which products are best sellers by units and revenue?
-- =============================================================================
-- Method:
-- - Use raw_order_items as the product-level sales fact table.
-- - Join raw_products for product names and raw_orders for order context.
-- - Aggregate units, revenue, order count, and average unit price by product.

COPY (
    SELECT
        p.id AS product_id,
        p.product_name,
        SUM(oi.quantity) AS total_units_sold,
        SUM(oi.total_price) AS total_revenue,
        COUNT(DISTINCT oi.order_id) AS number_of_orders,
        AVG(oi.unit_price) AS average_unit_price
    FROM raw_order_items AS oi
    INNER JOIN raw_products AS p
        ON oi.product_id = p.id
    INNER JOIN raw_orders AS o
        ON oi.order_id = o.id
    GROUP BY
        p.id,
        p.product_name
    ORDER BY
        total_units_sold DESC,
        total_revenue DESC
) TO 'analysis/exports/CSVs/01_07_best_sellers.csv'
WITH (HEADER, DELIMITER ',');


-- =============================================================================
-- 08. How effective is abandoned-cart recovery, and where is the largest revenue
--    opportunity?
-- =============================================================================
-- Method:
-- - Use raw_abandoned_carts at cart grain.
-- - Bring in session traffic source when available.
-- - Segment by cart-value band and traffic source to compare recovery rates,
--   recovered value proxy, unrecovered opportunity, and recovery speed.

COPY (
    WITH cart_summary AS (
        SELECT
            ac.cart_id,
            ac.customer_id,
            ac.session_id,
            SUM(ac.total_price) AS cart_value,
            MIN(ac.added_at) AS created_at,
            ac.recovered,
            ac.recovery_date AS recovered_at
        FROM raw_abandoned_carts AS ac
        GROUP BY
            ac.cart_id,
            ac.customer_id,
            ac.session_id,
            ac.recovered,
            ac.recovery_date
    ), carts AS (
        SELECT
            cs.cart_id,
            cs.customer_id,
            cs.session_id,
            cs.cart_value,
            cs.created_at,
            cs.recovered,
            cs.recovered_at,
            COALESCE(us.traffic_source, 'unknown') AS traffic_source,
            CASE
                WHEN cs.cart_value < 50 THEN '<$50'
                WHEN cs.cart_value < 100 THEN '$50-$99'
                WHEN cs.cart_value < 200 THEN '$100-$199'
                WHEN cs.cart_value < 500 THEN '$200-$499'
                ELSE '$500+'
            END AS cart_value_band
        FROM cart_summary AS cs
        LEFT JOIN raw_user_sessions AS us
            ON cs.session_id = us.session_id
    ), cart_rollup AS (
        SELECT
            traffic_source,
            cart_value_band,
            COUNT(*) AS abandoned_carts,
            COUNT(DISTINCT customer_id) AS customers_with_abandoned_carts,
            SUM(cart_value) AS abandoned_cart_value,
            SUM(CASE WHEN recovered THEN 1 ELSE 0 END) AS recovered_carts,
            SUM(CASE WHEN recovered THEN cart_value ELSE 0 END) AS recovered_value_proxy,
            SUM(CASE WHEN recovered THEN 0 ELSE cart_value END) AS unrecovered_value_opportunity,
            AVG(CASE WHEN recovered THEN DATE_DIFF('hour', created_at, recovered_at) END) AS avg_hours_to_recovery
        FROM carts
        GROUP BY
            traffic_source,
            cart_value_band
    )
    SELECT
        traffic_source,
        cart_value_band,
        abandoned_carts,
        customers_with_abandoned_carts,
        abandoned_cart_value,
        recovered_carts,
        recovered_value_proxy,
        unrecovered_value_opportunity,
        ROUND(100.0 * recovered_carts / NULLIF(abandoned_carts, 0), 2) AS cart_recovery_rate,
        ROUND(recovered_value_proxy / NULLIF(recovered_carts, 0), 2) AS avg_recovered_cart_value,
        avg_hours_to_recovery
    FROM cart_rollup
    ORDER BY
        unrecovered_value_opportunity DESC,
        abandoned_cart_value DESC
) TO 'analysis/exports/CSVs/01_08_abandoned_cart_recovery.csv'
WITH (HEADER, DELIMITER ',');

-- =============================================================================
-- 09. Which products and categories are driving quality revenue?
-- =============================================================================
-- Method:
-- - Aggregate order items to product grain before joining product metadata.
-- - Keep review and support aggregates separate so multiple reviews/support
--   tickets do not multiply line-item revenue.
-- - Flag products that combine high revenue with weak quality or support signals.

COPY (
    WITH product_sales AS (
        SELECT
            oi.product_id,
            COUNT(DISTINCT oi.id) AS orders_with_product,
            COUNT(DISTINCT o.id) AS customers,
            SUM(oi.quantity) AS units_sold,
            SUM(oi.quantity * oi.unit_price) AS item_revenue,
            AVG(oi.unit_price) AS avg_selling_price
        FROM raw_order_items AS oi
        INNER JOIN raw_orders AS o
            ON oi.order_id = o.id
        GROUP BY oi.product_id
    ), product_reviews AS (
        SELECT
            product_id,
            COUNT(*) AS review_count,
            AVG(rating) AS avg_rating
        FROM raw_reviews
        GROUP BY product_id
    ), product_support AS (
        SELECT
            oi.product_id,
            COUNT(DISTINCT cs.ticket_id) AS support_tickets,
            COUNT(DISTINCT oi.order_id) AS supported_orders
        FROM raw_customer_support AS cs
        INNER JOIN raw_order_items AS oi
            ON cs.order_id = oi.order_id
        GROUP BY oi.product_id
    ), product_profile AS (
        SELECT
            p.id AS product_id,
            p.product_name,
            c.category_name,
            COALESCE(ps.orders_with_product, 0) AS orders_with_product,
            COALESCE(ps.customers, 0) AS customers,
            COALESCE(ps.units_sold, 0) AS units_sold,
            COALESCE(ps.item_revenue, 0) AS item_revenue,
            ps.avg_selling_price,
            COALESCE(pr.review_count, 0) AS review_count,
            pr.avg_rating,
            COALESCE(psu.support_tickets, 0) AS support_tickets,
            COALESCE(psu.supported_orders, 0) AS supported_orders
        FROM raw_products AS p
        LEFT JOIN raw_categories AS c
            ON p.category_id = c.id
        LEFT JOIN product_sales AS ps
            ON p.id = ps.product_id
        LEFT JOIN product_reviews AS pr
            ON p.id = pr.product_id
        LEFT JOIN product_support AS psu
            ON p.id = psu.product_id
    )
    SELECT
        product_id,
        product_name,
        category_name,
        orders_with_product,
        customers,
        units_sold,
        item_revenue,
        avg_selling_price,
        review_count,
        avg_rating,
        support_tickets,
        ROUND(100.0 * support_tickets / NULLIF(orders_with_product, 0), 2) AS support_ticket_rate_per_order,
        CASE
            WHEN item_revenue >= QUANTILE_CONT(item_revenue, 0.75) OVER ()
                AND COALESCE(avg_rating, 5) < 3.5 THEN 'high revenue / low rating'
            WHEN item_revenue >= QUANTILE_CONT(item_revenue, 0.75) OVER ()
                AND 100.0 * support_tickets / NULLIF(orders_with_product, 0) >= 10 THEN 'high revenue / high support rate'
            WHEN item_revenue >= QUANTILE_CONT(item_revenue, 0.75) OVER () THEN 'high revenue'
            ELSE 'monitor'
        END AS product_action_flag
    FROM product_profile
    ORDER BY
        item_revenue DESC,
        support_ticket_rate_per_order DESC NULLS LAST
) TO 'analysis/exports/CSVs/01_09_product_quality_revenue.csv'
WITH (HEADER, DELIMITER ',');
