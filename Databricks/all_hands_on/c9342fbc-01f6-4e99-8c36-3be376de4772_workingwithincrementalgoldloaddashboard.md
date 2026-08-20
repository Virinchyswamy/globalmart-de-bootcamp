# Working with Incremental Gold Load & Dashboard
## Content Type
Scenario

## Overview
Propagate Silver incremental changes up to the Gold layer refresh dimension tables, update fact_sales, rebuild the aggregated regional summary, and publish a live dashboard.

## Learning Objectives
- Refresh SCD2 Gold dimension tables after Silver adds new versioned rows.
- Read only new fact rows from Silver using CDF and merge them into fact_sales.
- Build a pre-aggregated Gold table suitable for dashboard consumption.
- Connect a Gold table to a Databricks AI/BI Dashboard and add visualizations.

## Prerequisites
- Silver incremental load completed — all Silver tables reflect the new batch
- Gold full load already built — all dim tables and fact_sales exist
- regional_sales_summary does not yet exist — this activity creates it for the first time

## Duration of Completion
60 minutes

## Level
Intermediate

## Industries
- e-commerce

## Tags
- approach (skill)
- data-understanding (skill)
- data-storage (skill)
- data-wrangling (skill)
- batch-etl (skill)
- databricks (tool)
- spark (tool)

#### Overview
Propagate Silver incremental changes up to the Gold layer refresh dimension tables, update fact_sales, rebuild the aggregated regional summary, and publish a live dashboard.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- approach (skill)
- data-understanding (skill)
- data-storage (skill)
- data-wrangling (skill)
- batch-etl (skill)
- databricks (tool)
- spark (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!IMPORTANT]
> Run notebooks in the following order. Each step depends on the one before it:

1. **Dim refresh** — Silver SCD2 must be complete before dims are refreshed
2. **fact_sales incremental** — Silver order_items and payments must be merged before fact rows are built
3. **Aggregated table** — fact_sales must be updated before the regional summary is rebuilt
4. **Dashboard** — regional_sales_summary must exist before connecting to the dashboard

> Running out of order will result in stale or incomplete data at each layer.

**Tags**


##### Input 2
**Type:** Text

Silver has been updated with the latest incremental batch, new customer versions, updated product prices, new orders, and new payments are all in Silver. Gold, however, still reflects the state from the initial full load.

The Gold layer is what dashboards and business teams read from. Until Gold is refreshed, downstream consumers are working with stale data, missing new orders, old prices, and incomplete dimension history.

This activity completes the incremental pipeline by propagating Silver changes upward through three steps: refreshing the dimensions that changed, merging new fact rows, and rebuilding the aggregated summary table. The final step connects that table to a live dashboard.

**Tags**


##### Input 3
**Type:** Text

### Task 1 — Refresh Dimension Tables

After a Silver incremental run, some dimension tables in Gold may be stale — Silver has added new versioned rows that Gold does not yet reflect.

**Goals:**
- Check which Gold dims have Silver rows not yet present
- Overwrite those dims from Silver so the latest versions are in Gold

**Outcome:**
- Gold dim tables reflect the full version history from Silver — old versions and new versions both present, with exactly one active version per business key

>[!NOTE]
> Not every dim needs refreshing on every run. Check which Silver tables actually received new versions in this batch — only those dims need to be overwritten. Dims that did not change in Silver can be skipped.

**Hint — how to refresh a dim from Silver:**
Read from the Silver table, select the columns needed in Gold, and overwrite the dim table. For example, this is how `dim_customer` was refreshed from `silver.customers`:

```python
dim_df = spark.table("gbmart.silver.customers").select(
     "customer_sk", "customer_id", "full_name", "email", "phone_number",
     "is_current", "effective_start_date", "effective_end_date"
 )

 dim_df.write.format("delta").mode("overwrite").saveAsTable("gbmart.gold.dim_customer")
 ```

 Apply the same pattern for each dim that needs refreshing, read from the relevant Silver table, select the required columns, overwrite the Gold dim.


**Tags**


##### Input 4
**Type:** Text

### Task 2 — Incremental fact_sales Load

New line items have landed in `silver.order_items`. These must be built into fact rows and merged into `fact_sales` — using the same join chain as the full load (order header, product prices, date, address, payments).

**Goals:**
- Read only the new order_item rows from Silver using CDF
- Build complete fact rows by joining to the relevant Silver and Gold dim tables
- MERGE into fact_sales — insert new rows, update existing ones if re-run

**Outcome:**
- fact_sales contains new rows for the new orders with all foreign keys populated and no NULL Payment_IDs

>[!NOTE]
> fact_sales stores prices at the time of the transaction — `Actual_price` and `Discounted_price` are copied from Silver at write time. Existing fact rows are not updated when a product's price changes later. Only new fact rows written after a price change pick up the new price.

**Tags**


##### Input 5
**Type:** Text

### Task 3 — Pre-Aggregated Regional Sales Table

`vw_regional_sales` recomputes from the full fact_sales on every query. As the fact table grows, this becomes slow for dashboards that need to refresh frequently. A pre-aggregated table solves this by storing the rolled-up result — dashboards query a small fast table instead of the full fact.

**Goals:**
- Aggregate fact_sales by state and city — total orders, total customers, total quantity, total revenue, avg order value
- Write the result to `gold.regional_sales_summary` using overwrite mode

**Outcome:**
- `regional_sales_summary` exists as a Gold Delta table — one row per city, ready for dashboard consumption

**Tags**


##### Input 6
**Type:** Text

### Task 4 — Dashboard

Connect `regional_sales_summary` to a Databricks AI/BI Dashboard and build a regional performance view for business stakeholders.

**Goals:**
- Create a new AI/BI Dashboard and connect `regional_sales_summary` as the dataset
- Use Genie Code to generate visualizations — revenue by state (bar chart), top cities (table), total revenue and total orders (KPI tiles)
- Publish the dashboard

**Outcome:**
- A live published dashboard backed by `regional_sales_summary` showing regional revenue, order volumes, and average order value

>[!NOTE]
> Use the **Genie Code** prompt box on the dashboard canvas to generate charts. Example prompt:
>
> *"Create a bar chart showing total revenue by state from @regional_sales_summary, sorted highest first, top 10 states only"*
>
> Use `@` to reference your dataset by name inside the prompt.


**Tags**


##### Input 7
**Type:** File Upload

**Question:** Upload the following screenshots:

1. A sample dimension table row showing **two SCD2 versions** for the same business key — one with `is_current = false` (old version) and one with `is_current = true` (new version)
2. fact_sales row count **before and after** the incremental run, plus a spot-check of the new fact rows showing all foreign keys populated and `NULL Payment_ID = 0`
3. `regional_sales_summary` — top 10 cities output
4. Published Databricks AI/BI Dashboard showing at least one visualization connected to `regional_sales_summary`

**Max No. of Files:** 15

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- batch-etl / batch-incremental-load (skill)

##### Input 8
**Type:** File Upload

**Question:** Upload all notebooks created for the Gold incremental load, dim refresh, fact_sales incremental, and regional sales aggregation.

**Max No. of Files:** 10

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- batch-etl / batch-incremental-load (skill)

##### Input 9
**Type:** Short Answer

**Question:** The dim refresh notebook uses `mode("overwrite")` instead of a MERGE. Why is overwrite the correct approach here, even though fact_sales uses MERGE?

**Template:** null

**Tags**
- batch-etl / batch-incremental-load (skill)

##### Input 10
**Type:** Short Answer

**Question:** `vw_regional_sales` is a view that always reads live from fact_sales. `regional_sales_summary` is a pre-aggregated Delta table. What is the trade-off between the two and when would you choose one over the other?

**Template:** null

**Tags**
- batch-etl / batch-incremental-load (skill)

