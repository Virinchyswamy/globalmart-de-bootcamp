# Gold Layer - Dimensional Model, Fact Table & Pre-Aggregated Facts
## Content Type
Scenario

## Overview
Build the GlobalMart Gold layer, dimension tables, a fact table, and pre-aggregated views so downstream teams can query clean, analytics-ready data without writing complex joins every time.

## Learning Objectives
- Build dimension tables and a fact table following a star schema design.
- Create pre-aggregated views on top of the fact table for common business queries.

## Prerequisites
- Silver Layer is built
- Familarity with dimensional modelling & medallion architecture

## Duration of Completion
120 minutes

## Level
Intermediate

## Industries
- e-commerce

## Tags
- data-modelling (skill)
- batch-etl (skill)
- data-wrangling (skill)
- databricks (tool)
- spark (tool)
- sql (tool)

#### Overview
Build the GlobalMart Gold layer, dimension tables, a fact table, and pre-aggregated views so downstream teams can query clean, analytics-ready data without writing complex joins every time.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- data-modelling (skill)
- batch-etl (skill)
- data-wrangling (skill)
- databricks (tool)
- spark (tool)
- sql (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!IMPORTANT]
> All tables must follow the three-level namespace: `<your-catalog>.gold.<table_name>`

GlobalMart's Silver layer holds clean, quality-checked data, but it is not shaped for business consumption. Every analytics question requires writing multi-table joins from scratch, and different teams derive the same metrics slightly differently each time.

The Gold layer solves this once. Data is organised into a **star schema**, a central fact table holding what happened and how much, surrounded by dimension tables that answer who, what, where, when, and how. Downstream consumers, dashboards, Genie, and notebooks, query the Gold layer directly without touching Silver.


**Tags**


##### Input 2
**Type:** Text

**Goal**

Build the GlobalMart Gold layer, dimension tables, a fact table, and pre-aggregated views, following the star schema design shared with you during the dimensional modelling session.

**Outcomes**

By completing this activity, you will have:

- Created all dimension tables in `<your-catalog>.gold`, each with a stable surrogate key
- Built `fact_sales` in `<your-catalog>.gold`, one row per order line item, joined to all 5 dimensions via surrogate keys
- Created two pre-aggregated views on top of `fact_sales` for regional and category-level reporting
- Verified row counts and joins at each step before moving forward



**Tags**


##### Input 3
**Type:** Text

### Part 1 — Dimension Tables

Build the following dimension tables, reading from their respective Silver sources. Use `sha2` hashing to generate a stable surrogate key for each dimension — do not use `monotonically_increasing_id()`.
<br/>
| Dimension Table | Source |
|---|---|
| `dim_customer` | `silver.customers` |
| `dim_product` | `silver.products` |
| `dim_date` | Generated from `silver.orders` date range |
| `dim_address` | `silver.address` |
| `dim_payment_method` | `silver.payment_methods` |
<br/>

- For `dim_date`: generate one continuous row per calendar day from `min(order_date)` to `max(actual_delivery_date)` in `silver.orders`. Derive `year`, `quarter`, `month`, `month_name`, `week_of_year`, `day_of_week`, `day_name`, `is_weekend` for each row.

- For `dim_customer` and `dim_product`: both Silver tables already have SCD2 columns (`is_current`, `effective_start_date`, `effective_end_date`). Carry these forward — the fact table will join to the version of a record that was active at the time of the order.

**Tags**


##### Input 4
**Type:** Choice

**Question:** Your team builds `dim_customer` on Day 1. `CUST-001` is assigned surrogate key `8589934592` using `monotonically_increasing_id()`. The `fact_sales` table stores `8589934592` as the foreign key for all of CUST-001's orders.

On Day 2, a team member drops and rebuilds `dim_customer` to fix a schema issue. This time, `CUST-001` gets assigned `17179869184`. When the BI team runs a report joining `fact_sales` to `dim_customer`, CUST-001's orders return NULL for every customer attribute — name, city, segment — silently dropping them from all aggregations.

Which surrogate key approach prevents this?

**Options:** 
- Continue using `monotonically_increasing_id()` but never drop and rebuild dimension tables

- Use `sha2(customer_id, 256)` — same input always produces the same hash, so the key is identical across every pipeline run

- Use `uuid()` to generate a globally unique key per row

- Use `row_number()` over an `ORDER BY customer_id` window — this produces a consistent sequence

**Correct Options:** 
- Use `sha2(customer_id, 256)` — same input always produces the same hash, so the key is identical across every pipeline run

**Tags**
- data-modelling / dimensional-modelling / dimension-table-design (skill)

##### Input 5
**Type:** File Upload

**Question:** Upload your completed dimension tables notebook.

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-modelling / dimensional-modelling / dimension-table-design (skill)

##### Input 6
**Type:** File Upload

**Question:** Before building the fact table, submit your dimensional model design.

Your submission should include all dimension tables and the fact table (`fact_sales`), showing column names, primary keys, foreign keys, and the relationship between the fact and dimensions.

Upload your dimensional model design (Excel, Visio, or any diagram tool export).

**Max No. of Files:** 1

**Max File Size:** 100

**Allowed File Types:** ANY

**Tags**
- data-modelling / dimensional-modelling / dimension-table-design (skill)

##### Input 7
**Type:** Text

### Part 2 — Fact Table

**Goal**

Build `fact_sales` in `<your-catalog>.gold`, the central table of the star schema. Every downstream query for revenue, quantity, and order volume runs against this table.

**Grain:** One row per order line item (`order_item_id`)

**Outcomes**

- `fact_sales` contains one row per order line item, joined to all 5 dimension surrogate keys
- `Sales_amount` derived as `Quantity_purchased × Discounted_price`
-  Row count matches `silver.order_items`, no rows dropped during joins

**Fact Table Schema**

<p align="center">
  <img src="https://cdn.enqurious.com/images/2794d5fb-e811-4a7c-b661-7c04c0c2d861_image.webp" alt="fact_sales schema" />
</p>

The fact table joins to dimensions via surrogate keys only, never on the raw operational IDs. `Time_ID` joins to `dim_date.date_key`, `Customer_ID` joins via `dim_customer.customer_id` (then carry `customer_sk`), and so on for the remaining dimensions.


**Tags**


##### Input 8
**Type:** File Upload

**Question:** Upload your completed `fact_sales` notebook.

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-modelling / dimensional-modelling / slowly-changing-dimensions (skill)
- data-wrangling / join (skill)
- batch-etl / batch-processing (skill)
- batch-etl / medallion-architecture (skill)

##### Input 9
**Type:** Text

### Part 3 — Pre-Aggregated Views

**Goal**

Create two pre-aggregated views on top of `fact_sales` to serve the most common reporting queries without re-computing the joins every time.

**Outcomes**

- `vw_monthly_category_sales` — monthly revenue and order volume by product category and sub-category
- `vw_regional_sales` — total revenue, order count, and average order value by state and city

Both should be created as `CREATE OR REPLACE VIEW` in `<your-catalog>.gold` — not as Delta tables. Views recompute from `fact_sales` on every query, which means they always reflect the latest data without a separate refresh step.

`vw_monthly_category_sales` 
 - **columns:** `year`, `month`, `category`, `sub_category`, `total_quantity_sold`, `total_revenue`, `total_orders`, `avg_discount_given`

`vw_regional_sales` 
 - **columns:** `state`, `city`, `total_orders`, `total_customers`, `total_quantity_sold`, `total_revenue`, `avg_order_value`

**Tags**


##### Input 10
**Type:** File Upload

**Question:** Upload your completed pre-aggregated views notebook.

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- batch-etl / medallion-architecture (skill)

##### Input 11
**Type:** Code

**Question:** **Business Requirement:** The finance team wants to identify which
product category has generated the most revenue across all time to
prioritise investment and inventory planning. Write SQL query


**Language:** sql

**Snippet:** 

**Tags**


##### Input 12
**Type:** Choice

**Question:** Query `gbmart.gold.vw_monthly_category_sales` to find
which product category has the highest total revenue.

**Options:** 
- Electronics

- Appliances

- Fashion

- Home & Furniture

**Correct Options:** 
- Electronics

**Tags**
- data-wrangling / join (skill)
- data-wrangling / group (skill)
- sql (tool)

##### Input 13
**Type:** Code

**Question:** **Business Requirement:** The regional sales team wants to identify
which state contributes the most to GlobalMart's overall revenue to
prioritise warehouse expansion and logistics investment.

**Language:** sql

**Snippet:** 

**Tags**


##### Input 14
**Type:** Choice

**Question:** Query `gbmart.gold.vw_regional_sales` to find which
state has generated the highest total revenue


**Options:** 
- Uttar Pradesh

- West Bengal

- Maharashtra

- Bihar

**Correct Options:** 
- Uttar Pradesh

**Tags**
- data-wrangling / join (skill)
- data-wrangling / group (skill)
- data-wrangling / filter (skill)

##### Input 15
**Type:** Text

>[!CAUTION]
> Please ensure `fact_sales` and both views are created and verified before moving forward.

**Tags**


