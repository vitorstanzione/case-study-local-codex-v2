# Data Analyst Case Study

## Overview

Welcome! This case study is designed to give you the opportunity to demonstrate your analytical skills in a realistic, open-ended scenario. You'll work with a real-world dataset of your choosing, explore the data, identify meaningful business questions, and deliver both written analysis and visual outputs.

There is no single "right answer." We're interested in how you think, how you communicate, and the quality of the work you produce. You are free to use any tools you're comfortable with — including AI assistants, BI platforms, Python, SQL, dbt, or any combination.

**A note on tooling:** We have a preference for well-orchestrated, repeatable approaches — dbt is a good example, because it makes analysis reproducible and easy to review. If you're already comfortable with dbt, please use it. If you're not, don't try to learn it on the clock — use whatever you already know best. We care more about clear thinking than tool choice.

**Time expectation:** 4 hours. Don't over-polish — we'd rather see clear thinking and solid fundamentals than a perfect deliverable.

---

## Choosen Dataset

A self-contained DuckDB database file in the `datasets/` directory. 

| Dataset | Domain | Tables | Approx. Total Rows | Example Angles |
|---|---|---|---|---|
| E-Commerce | DTC retail: customers, orders, marketing, support | 17 | ~195K | LTV, cohorts, attribution, churn, cart recovery |

---

### Option: E-Commerce
**File:** `datasets/ecommerce.duckdb`

A complete online retail dataset from a fictional direct-to-consumer brand, including customer records, orders, payments, product catalog, reviews, marketing campaigns, support tickets, shipping, subscriptions, web sessions, and abandoned carts.

| Table | Description | Rows |
|---|---|---|
| `raw_customers` | Customer profiles with location data | ~17.4K |
| `raw_orders` | Order records with status | ~18.5K |
| `raw_order_items` | Line-item detail per order | ~37.2K |
| `raw_payments` | Payment transactions by method | ~18.5K |
| `raw_products` | Product catalog with pricing | 15 |
| `raw_categories` | Product category hierarchy | 5 |
| `raw_reviews` | Customer product reviews with ratings | ~5.5K |
| `raw_marketing` | Marketing campaign performance | 64 |
| `raw_customer_support` | Support tickets with resolution data | ~1.9K |
| `raw_shipping` | Shipping and delivery tracking | ~15.7K |
| `raw_subscriptions` | Subscription plans and status | ~2.5K |
| `raw_user_sessions` | Website session activity and conversion | ~68.7K |
| `raw_abandoned_carts` | Cart abandonment with recovery data | ~6.5K |
| `raw_inventory` | Current inventory levels | 15 |
| `raw_promotions` | Promotion definitions and usage | 10 |
| `raw_order_promotions` | Promotion applications to orders | 15 |
| `raw_product_variants` | Product variant details and SKUs | 15 |

**Possible angles:** Customer lifetime value, cohort analysis, marketing attribution, subscription churn, cart abandonment recovery, product performance, support ticket drivers.

---

## Getting Started

### Prerequisites

You need [DuckDB](https://duckdb.org/docs/installation/) installed. You can use:
- The DuckDB CLI
- Python with the `duckdb` package
- Any tool that supports DuckDB (DBeaver, DataGrip, Evidence, etc.)

### Quick Start

```bash
# Open your chosen dataset
duckdb datasets/ecommerce.duckdb

# Explore the tables
SHOW TABLES;

# Preview a table
SELECT * FROM raw_orders LIMIT 10;

# Check the schema
DESCRIBE raw_orders;
```

If you prefer Python:

```python
import duckdb

con = duckdb.connect("datasets/ecommerce.duckdb", read_only=True)
con.sql("SHOW TABLES").show()
con.sql("SELECT * FROM raw_orders LIMIT 10").show()
```

---

## What to Deliver

### 1. Business Questions Document (1 page max)

After exploring the data, write up 3–5 prioritized business questions you'd investigate. For each question, briefly explain:
- **Why it matters** — what business decision does it inform?
- **How you'd approach it** — what tables/joins/metrics would you use?

This is your chance to show you can think like an analyst, not just a query writer.

### 2. SQL Analysis

Write SQL queries that answer your business questions. These should be:
- **Well-organized** — use CTEs, meaningful aliases, and comments where helpful
- **Correct** — results should be validated and make sense
- **Readable** — someone else on the team should be able to follow your logic

You may deliver this as `.sql` files, a Jupyter/Python notebook, or within a dbt project — your choice.

### 3. Visualizations

Create 2–4 visualizations that communicate your findings. Use any tool you want:
- BI tools (Tableau, Power BI, Metabase, Preset, Looker, Hashboard, Evidence, Hex, etc.)
- Python (matplotlib, seaborn, plotly, altair, etc.)
- Any other tool you prefer

Include the visualizations as screenshots, exported files, or live links. Each visualization should have a clear title, labels, and a brief annotation or caption explaining the insight.

### 4. Walkthrough Video (Required)

Record a short video walkthrough — **longer than 2 minutes and shorter than 10 minutes.** Use Loom, a screen recording, or any tool you prefer. Walk us through:
- **Your approach** — how you explored the data and decided what to focus on
- **Key findings** — the most important insights from your analysis
- **Decisions you made** — why you chose certain metrics, joins, or visualizations
- **What you'd do next** — given more time, what would you investigate further?

Aim for the 5-minute range. We'd rather see a tight 4-minute walkthrough than a padded 9-minute one.

---

## How to Submit

Package your deliverables in a GitHub repo or zip file:

```
your-submission/
├── README.md               # Your business questions document
├── analysis/
│   ├── queries.sql          # or a notebook, dbt project, etc.
│   └── ...
├── visualizations/
│   ├── chart_1.png          # or links to live dashboards
│   └── ...
└── walkthrough_video.md     # link to your video walkthrough
```

---

## Tips

- **Explore first.** Spend time understanding the data before writing queries. Look at distributions, nulls, cardinality, and relationships between tables.
- **Quality over quantity.** Two well-reasoned insights are better than five surface-level observations.
- **Show your work.** We care about your process as much as your output. Leave comments, explain your thinking, document assumptions.
- **Use what you know.** There's no required tool or language — use whatever lets you do your best work.
- **Ask questions.** If something about the data is ambiguous, document your assumption and proceed. That's exactly what we'd expect on the job.
- **AI is welcome.** You're free to use AI assistants. What matters is that you can explain and stand behind your work.

---

## Technical Notes

- All datasets are [DuckDB](https://duckdb.org/) database files (`.duckdb`). DuckDB is a fast, embedded analytical database — no server setup required.
- Datasets are read-only snapshots. You won't break anything by exploring.
- DuckDB supports standard SQL with extensions for analytics (window functions, CTEs, QUALIFY, etc.). See the [DuckDB SQL reference](https://duckdb.org/docs/sql/introduction).
