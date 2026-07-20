# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Incremental — Payments (SCD1 via CDF + MERGE)
# MAGIC **GlobalMart | Tredence DE Advanced Training | Day 12 Pattern**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.payments` — CDF enabled (ADLS via Autoloader) |
# MAGIC | **Target** | `harsh_kumar01_npmentorskool_onmicrosoft_com.silver.payments` |
# MAGIC | **SCD Type** | SCD1 — a payment record has one truth; new payments are inserts |
# MAGIC
# MAGIC ### Context
# MAGIC `payments_050626.csv` (2 new rows, `PAY-900001`/`PAY-900002`) was loaded into
# MAGIC Bronze via Autoloader during the incremental Bronze activity. This notebook
# MAGIC reads only those new rows via CDF and merges them into `silver.payments`
# MAGIC using SCD1 — no history needed for payments, just upsert the latest truth.
# MAGIC
# MAGIC ### The flow
# MAGIC | Step | What it does |
# MAGIC |---|---|
# MAGIC | 1 | Baseline row count |
# MAGIC | 2 | Inspect Bronze history — confirm the new file version |
# MAGIC | 3 | CDF read — only the 2 new payment rows |
# MAGIC | 4 | Apply same transforms as the full-load notebook |
# MAGIC | 5 | SCD1 MERGE into silver.payments |
# MAGIC | 6 | Verify |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup + Baseline

# COMMAND ----------

from pyspark.sql.functions import *
from delta.tables import DeltaTable

BRONZE_TABLE = "harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.payments"
SILVER_TABLE = "harsh_kumar01_npmentorskool_onmicrosoft_com.silver.payments"

baseline_count = spark.table(SILVER_TABLE).count()
print(f"silver.payments before this run : {baseline_count:,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Inspect Bronze History
# MAGIC The initial Autoloader runs for `payments_010626.csv` through `payments_040626.csv`
# MAGIC created several Bronze versions already consumed by the full-load notebook.
# MAGIC `payments_050626.csv` (2 new rows) landed as a later version — that's the one to
# MAGIC read from.

# COMMAND ----------

spark.sql(f"DESCRIBE HISTORY {BRONZE_TABLE}") \
    .select("version", "timestamp", "operation", "operationMetrics") \
    .orderBy("version") \
    .display()

# COMMAND ----------

# Check the DESCRIBE HISTORY output above.
# Find the version number for the initial full load (the last version Silver consumed).
# payments_050626.csv landed as the NEXT version after that — set this accordingly.
LAST_PROCESSED_VERSION = 2   # <-- update from history output above

print(f"Silver built from Bronze version : {LAST_PROCESSED_VERSION}")
print(f"CDF will start from version      : {LAST_PROCESSED_VERSION + 1}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — CDF Read: Only the New Payment Rows
# MAGIC Unlike orders (which uses Lakeflow CDC and can have UPDATEs), payments from Autoloader
# MAGIC are append-only. The `_change_type` here will always be `insert` — but we filter
# MAGIC consistently with the other incremental notebooks.

# COMMAND ----------

cdf_df = (
    spark.read.format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", LAST_PROCESSED_VERSION + 1)
        .table(BRONZE_TABLE)
        .filter("_change_type != 'update_preimage'")
)

print(f"Changed rows via CDF: {cdf_df.count():,}")
cdf_df.select("PaymentID", "OrderID", "PaymentDate", "PaymentMethodID", "_change_type", "_commit_version").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Apply Same Transforms as Full-Load Notebook
# MAGIC Identical to `06_payments_data_cleaning_dq_checks.ipynb` Step 6.
# MAGIC No DQ scan needed here — we confirmed in the full-load notebook that this source is
# MAGIC clean; a spot-check is sufficient for incremental.

# COMMAND ----------

# Quick spot-check before writing
print("Null check on incremental rows:")
cdf_df.select(
    count(when(col("PaymentID").isNull(), 1)).alias("null_payment_id"),
    count(when(col("OrderID").isNull(), 1)).alias("null_order_id"),
    count(when(col("PaymentDate").isNull(), 1)).alias("null_payment_date")
).display()

# COMMAND ----------

silver_df = cdf_df \
    .withColumn("used_any_discount",
        (col("GiftCardUsage") == "Yes") | (col("CouponUsage") == "Yes")
    ) \
    .withColumnRenamed("PaymentID",       "payment_id") \
    .withColumnRenamed("OrderID",         "order_id") \
    .withColumnRenamed("PaymentDate",     "payment_date") \
    .withColumnRenamed("GiftCardUsage",   "gift_card_usage") \
    .withColumnRenamed("GiftCardAmount",  "gift_card_amount") \
    .withColumnRenamed("CouponUsage",     "coupon_usage") \
    .withColumnRenamed("CouponAmount",    "coupon_amount") \
    .withColumnRenamed("PaymentMethodID", "payment_method_id") \
    .withColumn("_silver_updated_at", current_timestamp()) \
    .select(
        "payment_id", "order_id", "payment_date", "payment_method_id",
        "gift_card_usage", "gift_card_amount", "coupon_usage", "coupon_amount",
        "used_any_discount",
        "_source_file", "_silver_updated_at"
    )

print(f"Silver-ready rows: {silver_df.count():,}")
silver_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — SCD1 MERGE into silver.payments
# MAGIC
# MAGIC - **Matched** `payment_id` → update all columns (covers edge case where a payment record was corrected)
# MAGIC - **Not matched** → insert as a new row (the normal case for new orders)
# MAGIC
# MAGIC After this runs, `PAY-900001` and `PAY-900002` exist in Silver. The next time
# MAGIC `fact_sales` is rebuilt or incrementally refreshed, those orders will get
# MAGIC a real `Payment_ID` instead of `NULL`.

# COMMAND ----------

silver_table = DeltaTable.forName(spark, SILVER_TABLE)

(silver_table.alias("tgt")
    .merge(silver_df.alias("src"), "tgt.payment_id = src.payment_id")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)

print(f"MERGE complete")
print(f"silver.payments after this run: {spark.table(SILVER_TABLE).count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Verify

# COMMAND ----------

df = spark.table(SILVER_TABLE)
after_count = df.count()
print(f"silver.payments row count : {after_count:,}  (was {baseline_count:,} before run)")
print(f"Net new rows              : {after_count - baseline_count:,}  (expected 2)")

# Show the newly merged payment rows
print("\n--- Sample from incremental batch (PAY-900001, PAY-900002) ---")
df.filter(col("payment_id").isin("PAY-900001", "PAY-900002")) \
  .select("payment_id", "order_id", "payment_date", "payment_method_id", "used_any_discount") \
  .orderBy("payment_id") \
  .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reset (if needed)

# COMMAND ----------

# spark.sql("DELETE FROM harsh_kumar01_npmentorskool_onmicrosoft_com.silver.payments WHERE payment_id IN ('PAY-900001','PAY-900002')")
# print("New payment rows removed")