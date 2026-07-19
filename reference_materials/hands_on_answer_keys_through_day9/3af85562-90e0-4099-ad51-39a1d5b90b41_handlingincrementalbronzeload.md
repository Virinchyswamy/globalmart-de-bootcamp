# Handling Incremental Bronze Load 
## Content Type
Scenario

## Overview
Load the next batch of GlobalMart data into the Bronze layer using Autoloader for ADLS sources and Lakeflow Connect for Postgres, without reprocessing data already ingested.

## Learning Objectives
- Trigger Autoloader to pick up only new incremental files from ADLS without reprocessing the initial load.
- Run a SQL script in Supabase to push new orders and status updates through the Lakeflow Connect CDC pipeline.
- Verify each Bronze table received a new Delta version and inspect the incremental rows using table_changes().

## Prerequisites
- Bronze layer fully built — all 8 tables loaded from the initial dataset
- Autoloader pipelines for customers, payments, and products already configured with checkpoint and schema paths in place
- Lakeflow Connect Ingestion Pipeline for orders and order_items already configured and run successfully

## Duration of Completion
60 minutes

## Level
Intermediate

## Industries
- e-commerce

## Tags
- batch-etl (skill)
- data-storage (skill)
- databricks (tool)
- azure (tool)

#### Overview
Load the next batch of GlobalMart data into the Bronze layer using Autoloader for ADLS sources and Lakeflow Connect for Postgres, without reprocessing data already ingested.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- batch-etl (skill)
- data-storage (skill)
- databricks (tool)
- azure (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!IMPORTANT]
> Change Data Feed (CDF) must be enabled on all Bronze Delta tables **before** any incremental data is loaded. If CDF is enabled after data already exists, it only captures changes from that point forward — earlier versions will not be accessible via `table_changes()`.

Verify and enable CDF on all Bronze tables before proceeding:
```python
CATALOG = "<your-catalog>"
SCHEMA  = "bronze"

BRONZE_TABLES = [
     "customers", "addresses", "payments", "payment_methods",
    "products", "returns", "orders", "order_items"]


 for table in BRONZE_TABLES:
     full_name = f"{CATALOG}.{SCHEMA}.{table}"
     spark.sql(f"""
        ALTER TABLE {full_name}
        SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
    """)
     print(f"CDF enabled: {full_name}")
 ```

 Then run `DESCRIBE HISTORY <your-catalog>.bronze.<table>` for each table and **note the latest version number**. You will need this in the next activity.

**Tags**


##### Input 2
**Type:** Text

<p style="text-align:justify;">
GlobalMart's initial pipeline run loaded the full historical dataset into the Medallion architecture. The business is now live.
<p style="text-align:justify;">

<p style="text-align:justify;">
New orders are being placed, customers are updating their profiles, and product prices are being revised. The pipeline cannot stop and reload everything from scratch each time data arrives, it must be able to pick up only what is new, leave existing data untouched, and keep the Bronze layer current without duplication.
<p style="text-align:justify;">

<p style="text-align:justify;">
This activity covers exactly that: ingesting the next batch of data into Bronze incrementally, across all five active source tables, using the ingestion patterns already configured.
<p style="text-align:justify;">

**Tags**


##### Input 3
**Type:** Text

### Task 1 — Incremental Load from ADLS (Customers, Payments, Products)
<br/>

**Source:** ADLS `/raw-data/` — three new incremental files
**Target:** `<your-catalog>.bronze.customers`, `bronze.payments`, `bronze.products`

>[!NOTE]
> You will receive multiple files per source table. Upload **only the mentioned file** listed below. The initial load files are already in ADLS, adding them again will create duplicates in Bronze.

 For **products**, one file is already loaded from the initial pipeline run. The incremental file adds this week's price revisions and new SKUs.
<br/>

| Source | Incremental File | Upload To |
|---|---|---|
| Customers | `customers_inc_040626.csv` | ADLS → `/raw-data/customers/` |
| Payments | `payments_020626.csv` | ADLS → `/raw-data/payments/` |
| Products | `products_020626.json` | ADLS → `/raw-data/products/` |
<br/>

**Download all files from the Resources section of this activity.**
- [Dataset Link](https://cdn.enqurious.com/others/d7d34c3a-7894-4374-821e-dfdf7b2f0c2d_adlsincdata.7z)
<br/>

Goals:
- Confirm CDF is enabled on bronze.customers, bronze.payments, and bronze.products before uploading any files
- Upload a single file for each source to the correct ADLS folder
- Create a new folder in your workspace and create new Autoloader notebooks in that folder for the incremental load. Let's not disturb previously executed code.
- Ingest the new data into the same Bronze tables created during the initial load; checkpoint and schema paths must match the existing ones
- After each load, run DESCRIBE HISTORY and confirm a new Delta version was created
- Use table_changes(table, <new_version>) or readChangeFeed to inspect what the new version contains; confirm only the incremental rows appear
- Note the latest version number for each table; you will need this in the Silver Incremental Load activity


**Outcome:**

- Autoloader picks up only the new file for each source; the initial load files are not reprocessed
- `DESCRIBE HISTORY` shows a new Delta version for `bronze.customers`, `bronze.payments`, and `bronze.products`
- `table_changes(table, <new_version>)` returns only the rows from the incremental file

**Things to Consider:**

- Autoloader tracks processed files via a checkpoint; think about what would happen to Bronze if that checkpoint were lost before this run
- The incremental customers file contains a mix of new customers and updates to existing ones; consider how Bronze handles this and what it means for Silver
- After uploading, do not change the checkpoint or schema path, your existing pipeline configuration must be reused as-is

**Tags**


##### Input 4
**Type:** File Upload

**Question:** Upload the output of `DESCRIBE HISTORY` and `table_changes(table, <new_version>)` for each of the three ADLS Bronze tables — confirming a new version was created and only the incremental rows are returned.

**Max No. of Files:** 6

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**


##### Input 5
**Type:** Text

### Task 2 — Incremental Load from Postgres (Orders, Order Items)

**Source:** Supabase Postgres → Lakeflow Connect CDC pipeline
**Target:** `<your-catalog>.bronze.orders`, `bronze.order_items`

New orders have been placed and existing orders have had their status updated in Postgres since the initial load. Unlike the CSV sources, you do not upload a file — you run a SQL script in the Supabase SQL Editor and Lakeflow Connect streams the changes into Bronze automatically.

**Download `inc_orders_order_items.sql` from the Resources section of this activity.**

-  [Supabase Script](https://cdn.enqurious.com/others/20794240-4678-4498-bb3b-082ea748c420_incordersorderitems.sql)

The script contains:

- **6 new orders** — ORD-1005 to ORD-1010, all with status `Placed`
- **3 status updates** on existing orders — ORD-1001 to ORD-1003 move to `Shipped` or `Delivered`
- **8 new order items** — linked to the 6 new orders above

Run the script in Supabase, verify the rows were inserted/updated in the Supabase table editor, then check Lakeflow in Databricks and wait for the pipeline run to complete before querying Bronze.

**Outcome:**

- `bronze.orders` has 6 new rows and 3 rows with updated status values
- `bronze.order_items` has 8 new rows
- `DESCRIBE HISTORY` shows a new Delta version for both tables after Lakeflow processes the changes

**Things to Consider:**

- Lakeflow Connect uses SCD1 for Bronze — think about what happens to the rows for ORD-1001, ORD-1002, and ORD-1003 after their status changes. Are both the old and new values visible in Bronze?

**Tags**


##### Input 6
**Type:** File Upload

**Question:** Upload the following for all five Bronze tables:

1. All notebooks created for the incremental load (customers, payments, products)
2. Screenshots showing rows have been added to each Bronze table — a query result or row count output is sufficient for each table (`bronze.customers`, `bronze.payments`, `bronze.products`, `bronze.orders`, `bronze.order_items`)
3. A screenshot of `bronze.customers` schema (output of `printSchema()` or `DESCRIBE TABLE`) showing the 4 new consent columns — `third_party_data_sharing`, `marketing_communication`, `cookies_tracking`, `consent_timestamp` — present alongside the original columns
5. A screenshot of the Lakeflow Connect ingestion pipeline showing a successful run — the upserted row counts for `orders` and `order_items` must be visible in the pipeline UI

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- batch-etl / batch-incremental-load (skill)
- batch-etl / medallion-architecture (skill)
- azure / azure-data-factory / ingestion-and-parsing (tool)

##### Input 7
**Type:** Text

>[!IMPORTANT]
> Before closing this activity, record the latest Bronze version for each table. This becomes `LAST_PROCESSED_VERSION` in the Silver Incremental Load activity — the Silver CDF read will start from `LAST_PROCESSED_VERSION + 1`. If this number is wrong, Silver will either miss the new batch or reprocess data it has already seen.

```python
CATALOG = "<your-catalog>"
SCHEMA  = "bronze"

for table in ["customers", "payments", "products", "orders", "order_items"]:
    latest = spark.sql(f"DESCRIBE HISTORY {CATALOG}.{SCHEMA}.{table}") \
                  .orderBy("version", ascending=False) \
                  .select("version").limit(1).collect()[0][0]
    print(f"{table:20s} → LAST_PROCESSED_VERSION = {latest}")
```


**Tags**


