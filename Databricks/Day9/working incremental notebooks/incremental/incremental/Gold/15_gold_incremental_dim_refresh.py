# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Incremental — Dimension Refresh (dim_customer + dim_product)
# MAGIC **GlobalMart | Tredence DE Advanced Training | Day 12 Pattern**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `gbmart.silver.customers`, `gbmart.silver.products` — SCD2 columns (`is_current`, `effective_start_date`, `effective_end_date`, surrogate key) |
# MAGIC | **Target** | `gbmart.gold.dim_customer`, `gbmart.gold.dim_product` |
# MAGIC | **Strategy** | Full overwrite — Silver is the source of truth for versioning; Gold just re-publishes it |
# MAGIC
# MAGIC ### Why run this after the Silver SCD2 notebooks?
# MAGIC
# MAGIC Notebooks `10_products_incremental_scd2_merge.ipynb` and
# MAGIC `11_customers_incremental_scd2_merge.ipynb` ran SCD2 MERGEs on Silver:
# MAGIC - Old version rows got `is_current = false` + `effective_end_date` stamped
# MAGIC - New version rows were inserted with a **new surrogate key** + `is_current = true`
# MAGIC
# MAGIC Gold's `dim_customer` and `dim_product` are now stale — they were built from
# MAGIC Silver's state before those SCD2 MERGEs ran. This notebook refreshes them.
# MAGIC
# MAGIC ### Why overwrite, not MERGE?
# MAGIC
# MAGIC All SCD2 decision-making (closing old rows, inserting new versions) happened in
# MAGIC Silver. By the time Gold reads Silver, the rows are already correctly versioned.
# MAGIC A MERGE on `customer_sk` would match each row to itself — no actual decision left
# MAGIC to make. A full overwrite re-publishes the complete versioned set cleanly.
# MAGIC
# MAGIC ### Which dims need refreshing?
# MAGIC
# MAGIC | Dim | Refresh needed? | Why |
# MAGIC |---|---|---|
# MAGIC | `dim_customer` | **Yes** | SCD2 — new email triggered new version in notebook 11 |
# MAGIC | `dim_product` | **Yes** | SCD2 — price change triggered new version in notebook 10 |
# MAGIC | `dim_date` | No | Static generated calendar — no incremental changes |
# MAGIC | `dim_address` | No | SCD1 — not updated in this incremental scenario |
# MAGIC | `dim_payment_method` | No | SCD1 lookup (5 rows, unchanged) |
# MAGIC | `dim_orders` | No | SCD1 — `silver.orders` MERGE already handled in notebook 12 |
# MAGIC
# MAGIC ### The flow
# MAGIC | Step | What it does |
# MAGIC |---|---|
# MAGIC | 1 | Setup + baseline row counts |
# MAGIC | 2 | Inspect Silver — show new SCD2 versions not yet in Gold |
# MAGIC | 3 | Overwrite `dim_customer` from Silver |
# MAGIC | 4 | Overwrite `dim_product` from Silver |
# MAGIC | 5 | Verify — confirm new versions present, history preserved |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup + Baseline

# COMMAND ----------

from pyspark.sql.functions import *

CATALOG = "harsh_kumar01_npmentorskool_onmicrosoft_com"

# Baseline counts before the refresh
base_dim_customer = spark.table(f"{CATALOG}.gold.dim_customer").count()
base_dim_product  = spark.table(f"{CATALOG}.gold.dim_product").count()

print(f"dim_customer before refresh : {base_dim_customer:,} rows")
print(f"dim_product  before refresh : {base_dim_product:,} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Inspect Silver: What's New Since the Last Gold Build?
# MAGIC
# MAGIC Find surrogate keys that exist in Silver but are **not yet** in Gold.
# MAGIC These are the new version rows inserted by the SCD2 MERGE.
# MAGIC
# MAGIC If the count is > 0 here, the dims are stale and must be refreshed.
# MAGIC If the count is 0, Gold is already up to date — but we'll still run the
# MAGIC overwrite (idempotent — overwrites with the same data, which is harmless).

# COMMAND ----------

# --- dim_customer ---
silver_customers = spark.table(f"{CATALOG}.silver.customers").select("customer_sk", "customer_id", "is_current")
gold_customers   = spark.table(f"{CATALOG}.gold.dim_customer").select("customer_sk")

new_customer_versions = silver_customers.join(gold_customers, "customer_sk", "left_anti")
print(f"New customer_sk rows in Silver not yet in Gold dim: {new_customer_versions.count():,}")
if new_customer_versions.count() > 0:
    new_customer_versions.display()

# --- dim_product ---
silver_products = spark.table(f"{CATALOG}.silver.products").select("product_sk", "product_id", "is_current")
gold_products   = spark.table(f"{CATALOG}.gold.dim_product").select("product_sk")

new_product_versions = silver_products.join(gold_products, "product_sk", "left_anti")
print(f"New product_sk rows in Silver not yet in Gold dim: {new_product_versions.count():,}")
if new_product_versions.count() > 0:
    new_product_versions.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Refresh dim_customer
# MAGIC
# MAGIC Identical select to the full-load notebook (Step 2 of `01_build_dimension_tables.ipynb`).
# MAGIC Now Silver has both the old version (`is_current = false`) and the new version
# MAGIC (`is_current = true`) — both land in the overwrite.

# COMMAND ----------

dim_customer_df = spark.table(f"{CATALOG}.silver.customers").select(
    "customer_sk", "customer_id", "full_name", "email", "phone_number",
    "is_current", "effective_start_date", "effective_end_date"
)

dim_customer_df.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.gold.dim_customer")
print(f"dim_customer after refresh : {spark.table(f'{CATALOG}.gold.dim_customer').count():,} rows  (was {base_dim_customer:,})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Refresh dim_product
# MAGIC
# MAGIC Identical select to the full-load notebook (Step 3 of `01_build_dimension_tables.ipynb`).
# MAGIC The new product version (new `product_sk`, updated `discounted_price_inr`, `is_current = true`)
# MAGIC is now included alongside the old version (`is_current = false`).

# COMMAND ----------

dim_product_df = spark.table(f"{CATALOG}.silver.products").select(
    "product_sk", "product_id", "product_name", "category", "sub_category",
    "discounted_price_inr", "is_current", "effective_start_date", "effective_end_date"
)

dim_product_df.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.gold.dim_product")
print(f"dim_product after refresh  : {spark.table(f'{CATALOG}.gold.dim_product').count():,} rows  (was {base_dim_product:,})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Verify
# MAGIC
# MAGIC Three things to confirm:
# MAGIC 1. Row counts increased (new SCD2 versions added)
# MAGIC 2. Exactly one `is_current = true` row exists per business key
# MAGIC 3. Old versions still present with `is_current = false` (history preserved)

# COMMAND ----------

# --- dim_customer check ---
dim_cust = spark.table(f"{CATALOG}.gold.dim_customer")

print(f"dim_customer row count : {dim_cust.count():,}  (was {base_dim_customer:,} before refresh)")
print(f"  is_current = true  : {dim_cust.filter('is_current = true').count():,}")
print(f"  is_current = false : {dim_cust.filter('is_current = false').count():,}")

# Confirm only 1 current version per customer
dup_current = (
    dim_cust.filter("is_current = true")
            .groupBy("customer_id")
            .count()
            .filter("count > 1")
)
print(f"  customer_ids with more than 1 current version : {dup_current.count():,}  (expected 0)")

# Show a customer who got consent update — should have 2 rows (pre-consent + post-consent)
print("\n--- CUST-10941 (both versions: no consent → with consent) ---")
dim_cust.filter(col("customer_id") == "CUST-10941") \
    .select("customer_id", "email", "customer_sk", "is_current", "effective_start_date", "effective_end_date") \
    .orderBy("effective_start_date") \
    .display()

# COMMAND ----------

# --- dim_product check ---
dim_prod = spark.table(f"{CATALOG}.gold.dim_product")

print(f"dim_product row count  : {dim_prod.count():,}  (was {base_dim_product:,} before refresh)")
print(f"  is_current = true  : {dim_prod.filter('is_current = true').count():,}")
print(f"  is_current = false : {dim_prod.filter('is_current = false').count():,}")

dup_current = (
    dim_prod.filter("is_current = true")
            .groupBy("product_id")
            .count()
            .filter("count > 1")
)
print(f"  product_ids with more than 1 current version : {dup_current.count():,}  (expected 0)")

# Show the product whose price changed — should have 2 rows (old price + new price)
print("\n--- Product with updated price (both versions should appear) ---")
dim_prod.filter(col("product_id") == "PRD-00001") \
    .select("product_id", "product_name", "discounted_price_inr", "product_sk", "is_current", "effective_start_date", "effective_end_date") \
    .orderBy("effective_start_date") \
    .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Note — Denormalized Prices in fact_sales
# MAGIC
# MAGIC `fact_sales` stores `Actual_price` and `Discounted_price` copied from Silver at
# MAGIC write time. Existing fact rows keep the price that was current when they were
# MAGIC written — they do **not** automatically update when a product's price changes.
# MAGIC
# MAGIC | Scenario | What happens |
# MAGIC |---|---|
# MAGIC | New order_items written **after** the price change | Pick up the new price (via `is_current = true` join) |
# MAGIC | Existing order_items written **before** the price change | Keep the old price (correct — reflects actual transaction price) |
# MAGIC
# MAGIC This is the intended behaviour for a fact table: facts record what was true at
# MAGIC the time of the transaction. If the business needs point-in-time price lookups
# MAGIC against the SCD2 `product_sk`, they can join `fact_sales → silver.products` on
# MAGIC `Product_ID` where `is_current = false` and the effective date range covers
# MAGIC the `order_date`. That's what the SCD2 dimension is designed to support.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reset (if needed)

# COMMAND ----------

# To restore to pre-refresh state, use Delta Time Travel:
# spark.sql("RESTORE TABLE gbmart.gold.dim_customer TO VERSION AS OF <version_before_refresh>")
# spark.sql("RESTORE TABLE gbmart.gold.dim_product  TO VERSION AS OF <version_before_refresh>")
# print("Dims restored to pre-refresh state")