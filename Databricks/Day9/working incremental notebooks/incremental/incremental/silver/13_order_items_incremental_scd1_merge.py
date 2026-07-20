# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Incremental — Order Items (SCD1 via CDF + MERGE)
# MAGIC **GlobalMart | Tredence DE Advanced Training | Day 12 Pattern**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.order_items` — CDF enabled (Lakeflow Connect CDC) |
# MAGIC | **Target** | `harsh_kumar01_npmentorskool_onmicrosoft_com.silver.order_items` |
# MAGIC | **SCD Type** | SCD1 — line items are immutable transactional facts; new lines are inserts only |
# MAGIC
# MAGIC ### Dependency
# MAGIC Run `12_orders_incremental_scd1_merge.ipynb` **before** this notebook.
# MAGIC `OR-900001` and `OR-900002` must exist in `silver.orders` before order_items for
# MAGIC those orders can pass referential integrity.
# MAGIC
# MAGIC ### The flow
# MAGIC | Step | What it does |
# MAGIC |---|---|
# MAGIC | 1 | Baseline row count |
# MAGIC | 2 | Inspect Bronze history — find the version to read from |
# MAGIC | 3 | CDF read — only the new/changed order_item rows |
# MAGIC | 4 | Referential integrity check (new items must have a parent order + product in Silver) |
# MAGIC | 5 | SCD1 MERGE into silver.order_items |
# MAGIC | 6 | Verify |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup + Baseline

# COMMAND ----------

from pyspark.sql.functions import *
from delta.tables import DeltaTable

BRONZE_TABLE = "harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.order_items"
SILVER_TABLE = "harsh_kumar01_npmentorskool_onmicrosoft_com.silver.order_items"

baseline_count = spark.table(SILVER_TABLE).count()
print(f"silver.order_items before this run : {baseline_count:,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Inspect Bronze History
# MAGIC Find the version the initial full-load notebook already consumed.
# MAGIC CDF reads everything strictly **after** `LAST_PROCESSED_VERSION`.

# COMMAND ----------

spark.sql(f"DESCRIBE HISTORY {BRONZE_TABLE}") \
    .select("version", "timestamp", "operation", "operationMetrics") \
    .orderBy("version") \
    .display()

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM table_changes(
# MAGIC   'harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.order_items',
# MAGIC   0,
# MAGIC   10
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Version 1
# MAGIC SELECT *
# MAGIC FROM table_changes(
# MAGIC   'harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.order_items',
# MAGIC   1
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Version 2
# MAGIC SELECT *
# MAGIC FROM table_changes(
# MAGIC   'harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.order_items',
# MAGIC   2
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Version 3
# MAGIC SELECT *
# MAGIC FROM table_changes(
# MAGIC   'harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.order_items',
# MAGIC   3
# MAGIC );

# COMMAND ----------

LAST_PROCESSED_VERSION = 3   # <-- update from history output above

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — CDF Read: Only the Changes
# MAGIC For the Day 12 scenario: if `05_make_order_changes_for_incremental.sql` included the
# MAGIC optional `INSERT INTO order_items` block, new line items for `OR-900001`/`OR-900002`
# MAGIC land here via Lakeflow. If not, this CDF read returns 0 rows — that's correct.

# COMMAND ----------

cdf_df = (
    spark.read.format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", LAST_PROCESSED_VERSION + 1)
        .table(BRONZE_TABLE)
        .filter(col("_change_type").isin(["insert", "update_postimage"]))
)

changed_count = cdf_df.count()
print(f"Changed rows via CDF: {changed_count:,}")

if changed_count > 0:
    cdf_df.select("orderitemid", "orderid", "productid", "quantity", "_change_type", "_commit_version").display()
else:
    print("No new order_items in this batch — nothing to merge.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Referential Integrity Check
# MAGIC New order_items must have a parent order in `silver.orders` and a valid product in
# MAGIC `silver.products`. If `notebook 12` ran first, `OR-900001`/`OR-900002` should already
# MAGIC be there.

# COMMAND ----------

if changed_count > 0:
    silver_orders   = spark.table("harsh_kumar01_npmentorskool_onmicrosoft_com.silver.orders").select("order_id")
    silver_products = spark.table("harsh_kumar01_npmentorskool_onmicrosoft_com.silver.products").select("product_id").distinct()

    orphan_orders   = cdf_df.join(silver_orders,   cdf_df.OrderID   == silver_orders.order_id,   "left_anti")
    orphan_products = cdf_df.join(silver_products, cdf_df.ProductID == silver_products.product_id, "left_anti")

    print(f"order_items with no matching silver.order   : {orphan_orders.count():,}  (expected 0)")
    print(f"order_items with no matching silver.product : {orphan_products.count():,}  (expected 0)")

    if orphan_orders.count() > 0:
        print("\n[WARNING] Orphaned orders — run notebook 12 first, then re-run this notebook")
        orphan_orders.select("orderitemid", "orderid").display()
else:
    print("Skipped — no rows to check.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Transform + SCD1 MERGE into silver.order_items
# MAGIC Same minimal transform as the full-load notebook — rename to snake_case, add audit
# MAGIC column. Line-item amounts are not computed here; `fact_sales` derives them at Gold
# MAGIC by joining to `silver.products`.

# COMMAND ----------

if changed_count > 0:
    silver_df = cdf_df \
        .withColumnRenamed("orderitemid", "order_item_id") \
        .withColumnRenamed("orderid",     "order_id") \
        .withColumnRenamed("productid",   "product_id") \
        .withColumn("_silver_updated_at", current_timestamp()) \
        .select("order_item_id", "order_id", "product_id", "quantity", "updated_at", "_silver_updated_at")

    silver_table = DeltaTable.forName(spark, SILVER_TABLE)

    (silver_table.alias("tgt")
        .merge(silver_df.alias("src"), "tgt.order_item_id = src.order_item_id")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

    print(f"MERGE complete")
    print(f"silver.order_items after this run: {spark.table(SILVER_TABLE).count():,}")
else:
    print("No rows to merge — silver.order_items unchanged.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Verify

# COMMAND ----------

df = spark.table(SILVER_TABLE)
print(f"silver.order_items row count : {df.count():,}  (was {baseline_count:,} before run)")

# Check if new order_items for OR-900001 / OR-900002 landed
new_items = df.filter(col("order_id").isin(["OR-900001", "OR-900002"]))
print(f"\norder_items for OR-900001/OR-900002 : {new_items.count():,} rows")
if new_items.count() > 0:
    new_items.select("order_item_id", "order_id", "product_id", "quantity").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reset (if needed)

# COMMAND ----------

# spark.sql("DELETE FROM harsh_kumar01_npmentorskool_onmicrosoft_com.silver.order_items WHERE order_id IN ('OR-900001','OR-900002')")
# print("New order_items removed")