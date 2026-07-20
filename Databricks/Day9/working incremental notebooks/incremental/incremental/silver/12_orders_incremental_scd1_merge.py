# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Incremental — Orders (SCD1 via CDF + MERGE)
# MAGIC **GlobalMart | Tredence DE Advanced Training | Day 12 Pattern**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders` — CDF enabled (Lakeflow Connect CDC) |
# MAGIC | **Target** | `harsh_kumar01_npmentorskool_onmicrosoft_com.silver.orders` |
# MAGIC | **SCD Type** | SCD1 — orders are transactional facts; the latest state overwrites the previous |
# MAGIC
# MAGIC ### Why SCD1 for orders?
# MAGIC An order has **one current truth** — its current status, current delivery date. When
# MAGIC Lakeflow CDC tells us `OR-000478` moved from `Shipped` to `Delivered`, we overwrite
# MAGIC the row, not keep both versions. That is SCD1.
# MAGIC
# MAGIC ### The flow
# MAGIC | Step | What it does |
# MAGIC |---|---|
# MAGIC | 1 | Baseline — row counts before the run |
# MAGIC | 2 | Inspect Bronze history — identify the version to read from |
# MAGIC | 3 | CDF read — only the changed rows, not the full 126k+ table |
# MAGIC | 4 | Apply the same transforms as the full-load notebook |
# MAGIC | 5 | SCD1 MERGE into silver.orders |
# MAGIC | 6 | Verify — confirm the update + new inserts landed correctly |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup + Baseline

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import DateType
from delta.tables import DeltaTable

BRONZE_TABLE = "harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders"
SILVER_TABLE = "harsh_kumar01_npmentorskool_onmicrosoft_com.silver.orders"
VALID_CHANNELS = ["Online", "Retail PoS"]

baseline_count = spark.table(SILVER_TABLE).count()
print(f"silver.orders before this run : {baseline_count:,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Inspect Bronze History
# MAGIC Find the version the initial full-load notebook (`02_orders_data_cleaning_dq_checks.ipynb`)
# MAGIC already consumed. Set `LAST_PROCESSED_VERSION` to that version number — CDF reads
# MAGIC everything **strictly after** it, which is only the Lakeflow-delivered changes.

# COMMAND ----------

spark.sql(f"DESCRIBE HISTORY {BRONZE_TABLE}") \
    .select("version", "timestamp", "operation", "operationMetrics") \
    .orderBy("version") \
    .display()

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Version 0
# MAGIC SELECT *
# MAGIC FROM harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders
# MAGIC VERSION AS OF 0;
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM table_changes(
# MAGIC   'harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders',
# MAGIC   0,
# MAGIC   10
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Version 1
# MAGIC SELECT *
# MAGIC FROM table_changes(
# MAGIC   'harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders',
# MAGIC   1
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Version 2
# MAGIC SELECT *
# MAGIC FROM table_changes(
# MAGIC   'harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders',
# MAGIC   2
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Version 3
# MAGIC SELECT *
# MAGIC FROM table_changes(
# MAGIC   'harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders',
# MAGIC   3
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Version 4
# MAGIC SELECT *
# MAGIC FROM table_changes(
# MAGIC   'harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders',
# MAGIC   4
# MAGIC );

# COMMAND ----------

# Set to the version number of the initial full load (already consumed by silver full-load notebook)
LAST_PROCESSED_VERSION = 3   # <-- update from history output above

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — CDF Read: Only the Changes
# MAGIC `readChangeFeed` + `startingVersion` returns only rows that changed after
# MAGIC `LAST_PROCESSED_VERSION`. `update_preimage` (the before-snapshot of an update) is
# MAGIC dropped — we only want the final state: `insert` and `update_postimage`.
# MAGIC
# MAGIC For the Day 12 scenario:
# MAGIC - `OR-000001`, `OR-000002`, `OR-000003` — Lakeflow CDC UPDATEs (`ActualDeliveryDate` filled)
# MAGIC - `OR-900001`, `OR-900002` — new inserts from Postgres via Lakeflow

# COMMAND ----------

cdf_df = (
    spark.read.format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", LAST_PROCESSED_VERSION + 1)
        .table(BRONZE_TABLE)
)

print(f"Changed rows via CDF: {cdf_df.count():,}")
cdf_df.select("orderid", "actualdeliverydate", "_change_type", "_commit_version").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Apply Same Transforms as Full-Load Notebook
# MAGIC Identical logic to `02_orders_data_cleaning_dq_checks.ipynb` Step 9 —
# MAGIC date casts, derived KPI columns, `_data_note` for timezone-artifact rows.
# MAGIC Scoped to the small CDF result instead of all 126k+ rows.

# COMMAND ----------

transformed_df = (
    cdf_df
    .withColumn("orderdate",            col("orderdate").cast(DateType()))
    .withColumn("shippingdate",         col("shippingdate").cast(DateType()))
    .withColumn("expecteddeliverydate", col("expecteddeliverydate").cast(DateType()))
    .withColumn("actualdeliverydate",   col("actualdeliverydate").cast(DateType()))
    .withColumn("order_to_ship_days",
        when(col("shippingdate").isNotNull(),
             datediff(col("shippingdate"), col("orderdate"))
        ).otherwise(lit(None).cast("int"))
    )
    .withColumn("ship_to_delivery_days",
        when(col("actualdeliverydate").isNotNull() & col("shippingdate").isNotNull(),
             datediff(col("actualdeliverydate"), col("shippingdate"))
        ).otherwise(lit(None).cast("int"))
    )
    .withColumn("delivery_delay_days",
        when(col("actualdeliverydate").isNotNull() & col("expecteddeliverydate").isNotNull(),
             datediff(col("actualdeliverydate"), col("expecteddeliverydate"))
        ).otherwise(lit(None).cast("int"))
    )
    .withColumn("is_delivered", col("actualdeliverydate").isNotNull())
    .withColumn("is_late",
        when(
            col("actualdeliverydate").isNotNull() & col("expecteddeliverydate").isNotNull(),
            col("actualdeliverydate") > col("expecteddeliverydate")
        ).otherwise(lit(None).cast("boolean"))
    )
    .withColumn("order_status",
        when(col("actualdeliverydate").isNotNull(), lit("Delivered"))
        .when(col("shippingdate").isNotNull(),      lit("Shipped"))
        .otherwise(                                  lit("Pending"))
    )
    .withColumn("_data_note",
        when(
            col("actualdeliverydate").isNotNull() & col("shippingdate").isNotNull() &
            (col("actualdeliverydate") < col("shippingdate")),
            lit("POSSIBLE_TIMEZONE_OFFSET_1DAY")
        ).otherwise(lit(None).cast("string"))
    )
    .withColumnRenamed("orderid",              "order_id")
    .withColumnRenamed("customerid",           "customer_id")
    .withColumnRenamed("orderdate",            "order_date")
    .withColumnRenamed("shippingdate",         "shipping_date")
    .withColumnRenamed("expecteddeliverydate", "expected_delivery_date")
    .withColumnRenamed("actualdeliverydate",   "actual_delivery_date")
    .withColumnRenamed("shippingtierid",       "shipping_tier_id")
    .withColumnRenamed("supplierid",           "supplier_id")
    .withColumnRenamed("orderchannel",         "order_channel")
    .withColumn("_silver_updated_at", current_timestamp())
    .select(
        "order_id", "customer_id", "order_date", "order_channel", "order_status",
        "shipping_tier_id", "supplier_id",
        "shipping_date", "expected_delivery_date", "actual_delivery_date",
        "order_to_ship_days", "ship_to_delivery_days", "delivery_delay_days",
        "is_delivered", "is_late", "_data_note", "updated_at", "_silver_updated_at"
    )
)

print(f"Rows to merge: {transformed_df.count():,}")
transformed_df.select("order_id", "order_status", "actual_delivery_date", "_change_type" if "_change_type" in transformed_df.columns else lit(None)).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — SCD1 MERGE into silver.orders
# MAGIC
# MAGIC - **Matched** `order_id` → update all columns (overwrite — SCD1, no history kept)
# MAGIC - **Not matched** → insert as a new row (new order placed since last run)
# MAGIC
# MAGIC This is safe to re-run. Running it twice on the same CDF batch produces the same
# MAGIC result — the second run matches and overwrites with identical data.

# COMMAND ----------

silver_table = DeltaTable.forName(spark, SILVER_TABLE)

(silver_table.alias("tgt")
    .merge(transformed_df.alias("src"), "tgt.order_id = src.order_id")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)

print(f"MERGE complete")
print(f"silver.orders after this run: {spark.table(SILVER_TABLE).count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Verify
# MAGIC
# MAGIC Three things to confirm:
# MAGIC 1. `OR-000001`, `OR-000002`, `OR-000003` now show `order_status = Delivered` with `actual_delivery_date` populated
# MAGIC 2. `OR-900001` and `OR-900002` exist as new rows with `order_status = Pending`
# MAGIC 3. Row count = baseline + 2 (the 2 new orders)

# COMMAND ----------

df = spark.table(SILVER_TABLE)
print(f"silver.orders row count : {df.count():,}  (was {baseline_count:,} before run)")

# Check the 3 updated orders — ActualDeliveryDate should now be filled, status = Delivered
print("\n--- OR-000001 / OR-000002 / OR-000003 (should be Delivered) ---")
df.filter(col("order_id").isin(["OR-000001", "OR-000002", "OR-000003"])) \
  .select("order_id", "order_status", "actual_delivery_date", "delivery_delay_days", "_silver_updated_at") \
  .display()

# Check the 2 new orders
print("\n--- OR-900001 / OR-900002 (should exist as new rows, status = Pending) ---")
df.filter(col("order_id").isin(["OR-900001", "OR-900002"])) \
  .select("order_id", "customer_id", "order_date", "order_channel", "order_status") \
  .display()

# COMMAND ----------

# Delta history — should show a new MERGE version
spark.sql(f"DESCRIBE HISTORY {SILVER_TABLE}") \
    .select("version", "timestamp", "operation", "operationMetrics") \
    .orderBy(desc("version")).limit(3).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reset (if needed)

# COMMAND ----------

# Undo only the 2 new inserts. OR-000478 update is harder to roll back — use Time Travel if needed.
# spark.sql("DELETE FROM harsh_kumar01_npmentorskool_onmicrosoft_com.silver.orders WHERE order_id IN ('OR-900001','OR-900002')")
# print("New orders removed — OR-000478 still shows updated state; use Time Travel to restore if needed")