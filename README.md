# Data Analyst Case Study: E-Commerce Dataset

## Overview

This repository contains a SQL-first analysis of the fictional direct-to-consumer e-commerce DuckDB dataset provided in `datasets/ecommerce.duckdb`. The work focuses on repeatable schema exploration, prioritized business questions, exported analysis tables, and a small set of Python-generated visual outputs for a short walkthrough.

## Deliverable

The current submission includes:

- A one-page-style business-questions summary in this README.
- Repeatable DuckDB SQL scripts:
  - `analysis/00_schema_exploration.sql` for table inventory, column metadata, row counts, and activity-date ranges.
  - `analysis/01_business_questions.sql` for the business-question analysis extracts.
- Exported CSV outputs in `analysis/exports/CSVs/` for schema checks and analysis results.
- Exported chart images in `analysis/exports/Charts/` for the primary trend visuals.
- Python charting scripts in `analysis/py/` that read the CSV exports and generate visualizations.
- Walkthrough-ready notes in this README. The actual video recording/link is not stored in the repository yet.

## Steps I Took

1. Reviewed `TASKS.md` to identify the required business-questions document, SQL analysis, visualizations, and walkthrough video.
2. Chose the provided e-commerce DuckDB dataset because it supports business-relevant analysis across customers, orders, products, payments, marketing, support, web sessions, subscriptions, and abandoned carts.
3. Created `analysis/00_schema_exploration.sql` as the repeatable schema-profiling script.
4. Added table inventory queries to validate that the expected 17 raw tables are present.
5. Added column metadata, row-count checks, and date-range checks to compare actual table coverage against the task prompt and understand the analysis window.
6. Created `analysis/01_business_questions.sql` with reusable queries for revenue trends, demand trends, average order value, geography, payment mix, best sellers, abandoned-cart recovery, and product quality/revenue tradeoffs.
7. Exported SQL outputs to `analysis/exports/CSVs/` so results can be inspected without rerunning the database locally.
8. Created Python plotting scripts in `analysis/py/` (`analysis\py`) for the primary visuals.
9. Organized exported CSV and chart outputs in `analysis/exports/` (`analysis\exports`) so results can be reviewed without rerunning the full workflow.
10. Summarized the main findings, recommended decisions, and next-step analysis below for use in the walkthrough.

## Prioritized Business Questions

### 1. How are revenue, orders, active customers, and average order value trending over time?

- **Why it matters:** This is the core business-health view. It informs whether growth is being driven by more customers, higher purchase frequency, or larger baskets.
- **Approach:** Use `raw_orders` as the order-level fact table, aggregate `raw_order_items` to order/month grain for merchandise revenue, exclude cancelled/refunded orders from recognized revenue where appropriate, and calculate monthly revenue, order count, unique ordering customers, and AOV.
- **Current finding:** The order window runs from January 2023 through September 2025. Recognized item revenue totals about **$966.5K**, with the highest revenue and order-volume month in **August 2025**. Overall AOV is about **$51.79**, with peak monthly AOV in **October 2024**.

### 2. Which geographies should the business prioritize for growth or operational focus?

- **Why it matters:** Geography analysis can guide localized campaigns, shipping/logistics investments, and market expansion decisions.
- **Approach:** Join `raw_orders` to `raw_customers`, aggregate `raw_payments` to order grain, and rank country/region/city combinations by orders, customers, revenue, and AOV. Separately, count the customer base by country.
- **Current finding:** The largest customer base is in the **USA** by a wide margin, while top revenue city/region combinations include **Vancouver, Montreal, Tokyo, Berlin, and Edinburgh**.

### 3. Which products are the best sellers, and are high-revenue products also healthy from a quality/support perspective?

- **Why it matters:** Product assortment, inventory planning, merchandising, and quality investments should account for both commercial performance and customer experience.
- **Approach:** Aggregate `raw_order_items` by product, join product/category metadata from `raw_products` and `raw_categories`, then layer in review metrics from `raw_reviews` and support-ticket signals from `raw_customer_support`.
- **Current finding:** **Jaffle Storage Containers** leads by units sold, while **Premium Jaffle Maker** leads by revenue. Several high-revenue products also show support-ticket rates around or above 10%, suggesting a quality or post-purchase experience opportunity.

### 4. How effective is abandoned-cart recovery, and where is the largest unrecovered revenue opportunity?

- **Why it matters:** Cart recovery is a direct revenue-leakage and lifecycle-marketing opportunity. Improving recovery can increase revenue without requiring entirely new demand generation.
- **Approach:** Aggregate `raw_abandoned_carts` to cart grain, join `raw_user_sessions` for traffic source, segment by cart-value band, and calculate abandoned value, recovered value proxy, unrecovered value opportunity, recovery rate, and average hours to recovery.
- **Current finding:** Across **6,558** abandoned carts, recovery is about **5.0%**. The largest unrecovered opportunities are concentrated in the **$100-$199** cart-value band across referral, email, paid, direct, and organic sources.

### 5. How does revenue mix vary by payment method over time?

- **Why it matters:** Payment mix informs checkout optimization, processing-cost management, fraud/risk monitoring, and customer payment preferences.
- **Approach:** Join `raw_payments` to `raw_orders` for order-month context and aggregate payment amount by month and payment method.
- **Current finding:** Credit card payments dominate recorded payment revenue, followed by bank transfer, gift card, and coupon activity.

## Outputs

### SQL and CSV Outputs

- `analysis/00_schema_exploration.sql` exports:
  - `analysis/exports/CSVs/00_tables.csv`
  - `analysis/exports/CSVs/00_columns.csv`
  - `analysis/exports/CSVs/00_row_count.csv`
  - `analysis/exports/CSVs/00_date_range.csv`
- `analysis/01_business_questions.sql` exports:
  - `analysis/exports/CSVs/01_01_revenue_over_time.csv`
  - `analysis/exports/CSVs/01_02_orders_over_time.csv`
  - `analysis/exports/CSVs/01_03_order_value_over_time.csv`
  - `analysis/exports/CSVs/01_04_geography_revenue.csv`
  - `analysis/exports/CSVs/01_05_geography_customers.csv`
  - `analysis/exports/CSVs/01_06_payment_method_revenue.csv`
  - `analysis/exports/CSVs/01_07_best_sellers.csv`
  - `analysis/exports/CSVs/01_08_abandoned_cart_recovery.csv`
  - `analysis/exports/CSVs/01_09_product_quality_revenue.csv`

### Chart Gallery

The charts below are exported to `analysis/exports/Charts/` and correspond to the business-question extracts in `analysis/01_business_questions.sql`.

#### 01. Revenue over time

![Revenue over time](analysis/exports/Charts/01_01_revenue_over_time.png)

- **Business question:** How is revenue trending over time?
- **Description:** Monthly recognized revenue, calculated by aggregating `raw_order_items` to order grain, joining to `raw_orders`, excluding cancelled/refunded orders, and rolling revenue up by order month.

#### 02. Orders and active customers over time

![Orders and active customers over time](analysis/exports/Charts/01_02_orders_over_time.png)

- **Business question:** How are order volume and active customers trending over time?
- **Description:** Monthly demand and customer reach, calculated from `raw_orders` by counting total orders and distinct ordering customers by order month.

#### 03. Average order value over time

![Average order value over time](analysis/exports/Charts/01_03_order_value_over_time.png)

- **Business question:** How is average order value trending over time?
- **Description:** Monthly order count, total revenue, and average order value, calculated by joining `raw_orders` to `raw_order_items`, aggregating line-item value to order grain, and comparing basket-size changes over time.

#### 04. Revenue by geography

![Revenue by geography](analysis/exports/Charts/01_04_geography_revenue.png)

- **Business question:** Which countries, regions, and cities generate the most revenue?
- **Description:** Revenue, order, customer, and AOV comparison by customer geography, calculated by aggregating `raw_payments` to order grain, joining order and customer data, and ranking markets by total revenue.

#### 05. Customers by country

![Customers by country](analysis/exports/Charts/01_05_geography_customers.png)

- **Business question:** Which countries have the largest customer bases?
- **Description:** Customer-base size by country, calculated from `raw_customers` by counting customer records and ranking countries by customer count.

#### 06. Payment-method revenue over time

![Payment-method revenue over time](analysis/exports/Charts/01_06_payment_method_revenue.png)

- **Business question:** How does revenue mix vary by payment method over time?
- **Description:** Monthly payment-method contribution, calculated by joining `raw_payments` to `raw_orders` for order-date context and aggregating payment amount by order month and payment method.

#### 07. Best sellers by units and revenue

![Best sellers by units and revenue](analysis/exports/Charts/01_07_best_sellers.png)

- **Business question:** Which products are best sellers by units and revenue?
- **Description:** Product sales performance, calculated from `raw_order_items` joined to product names and order context, then aggregated by product for units, revenue, order count, and average unit price.

#### 08. Abandoned-cart recovery

![Abandoned-cart recovery](analysis/exports/Charts/01_08_abandoned_cart_recovery.png)

- **Business question:** How effective is abandoned-cart recovery, and where is the largest revenue opportunity?
- **Description:** Recovery performance and unrecovered value opportunity by cart-value band and traffic source, calculated from cart-grain `raw_abandoned_carts` with session traffic source, recovered value proxy, recovery rate, and average hours to recovery.

#### 09. Product quality and revenue

![Product quality and revenue](analysis/exports/Charts/01_09_product_quality_revenue.png)

- **Business question:** Which products and categories are driving quality revenue?
- **Description:** Product revenue with quality/support signals, calculated by aggregating order items to product grain, joining category metadata, layering review and support aggregates separately, and flagging high-revenue products with weak quality or support indicators.

### Suggested Walkthrough Structure

1. **Approach:** Start with schema profiling to confirm table coverage, row counts, and date ranges before answering business questions.
2. **Focus areas:** Explain why revenue trends, geography, product performance, cart recovery, and payment mix were prioritized.
3. **Key findings:** Highlight the August 2025 peak, USA customer concentration, top revenue geographies, Jaffle Maker revenue strength, and low abandoned-cart recovery.
4. **Decisions made:** Note the use of order-grain aggregations before joins to avoid double-counting and the separation of review/support aggregates from sales facts.
5. **Next steps:** Add cohort retention/LTV, subscription churn, marketing ROI, promotion effectiveness, and deeper cart-recovery experiments if more time is available.
