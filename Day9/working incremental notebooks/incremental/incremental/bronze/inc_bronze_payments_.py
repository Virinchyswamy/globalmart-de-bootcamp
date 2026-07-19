# Databricks notebook source
# MAGIC %md
# MAGIC # Practice — Incremental Load into bronze.payments
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC Goal: drop `payments_050626.csv` into the `payments/` source folder and
# MAGIC confirm Autoloader picks up *only* the new file (via checkpoint), not the
# MAGIC earlier `payments_0{1-4}0626.csv` files already processed.
# MAGIC
# MAGIC Same Autoloader configuration as `03_bronze_payments_autoloader.ipynb` —
# MAGIC this notebook continues that same stream, it doesn't start a new one.
# MAGIC
# MAGIC **No schema evolution in this file** — `payments_050626.csv` has the
# MAGIC exact same columns as the original. It contains 2 rows: `PAY-900001` and
# MAGIC `PAY-900002`, matching the `OR-900001`/`OR-900002` orders added earlier —
# MAGIC this is what fills in the `Payment_ID` that was showing `NULL` in
# MAGIC `fact_sales` for those two orders.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup
# MAGIC Same paths as the original Bronze payments ingestion notebook.

# COMMAND ----------

from pyspark.sql.functions import col, current_timestamp

# ─── Same values as the customers notebook — reused, not re-mounted ───────────
MOUNT_POINT = "/mnt/virinchy_gbmart_data"
CATALOG = "harsh_kumar01_npmentorskool_onmicrosoft_com"
SCHEMA = "bronze"

# No raw-data / raw-demo-data suffix -- source folders live directly under the mount
MOUNT_BASE = MOUNT_POINT

# Table-specific values
SOURCE_FOLDER = "payments"
TABLE = "payments"

TARGET_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

SOURCE_PATH = f"{MOUNT_BASE}/{SOURCE_FOLDER}/"
CHECKPOINT_PATH = f"{MOUNT_BASE}/_checkpoints/{TABLE}/"
SCHEMA_PATH = f"{MOUNT_BASE}/_schemas/{TABLE}/"

# Fail fast with a clear message instead of a confusing downstream error if
# the mount from the customers notebook isn't active in this session.
mount_exists = any(m.mountPoint == MOUNT_POINT for m in dbutils.fs.mounts())
if not mount_exists:
    raise RuntimeError(
        f"{MOUNT_POINT} is not mounted in this session. "
        f"Run the customers notebook's mount cell first."
    )

print(f"Mount point : {MOUNT_POINT} (confirmed mounted)")
print(f"Mount base  : {MOUNT_BASE}")
print(f"Source      : {SOURCE_PATH}")
print(f"Target table: {TARGET_TABLE}")
print(f"Checkpoint  : {CHECKPOINT_PATH}")
print(f"Schema path : {SCHEMA_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — List Files in the Source Folder
# MAGIC Confirm `payments_050626.csv` actually landed (uploaded manually to
# MAGIC ADLS) before running anything.

# COMMAND ----------

files = dbutils.fs.ls(SOURCE_PATH)
print(f"Files found in {SOURCE_FOLDER}/:\n")
for f in files:
    print(f"  {f.name}  ({f.size / 1024:.1f} KB)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Baseline Check
# MAGIC Confirm the current row count in `gbmart.bronze.payments` **before**
# MAGIC running the incremental load, so the before/after comparison in Step 7 is
# MAGIC meaningful.

# COMMAND ----------

# MAGIC %sql
# MAGIC select count(*) from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.payments;

# COMMAND ----------

payments_inc_df = (
    spark.read
         .option("header", "true")
         .option("inferSchema", "true")
         .csv(f"{SOURCE_PATH}payments_040626.csv")
)

payments_inc_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Define the Incremental Read (Autoloader)
# MAGIC
# MAGIC Identical options to `03_bronze_payments_autoloader.ipynb` — `cloudFiles`
# MAGIC source + `CHECKPOINT_PATH` together mean only files **not already
# MAGIC recorded in the checkpoint** get read. Whichever `payments_*.csv` files
# MAGIC were already processed in an earlier run get skipped automatically; this
# MAGIC resolves to just `payments_050626.csv`.
# MAGIC
# MAGIC This cell only **defines** the streaming DataFrame — nothing is read or
# MAGIC written yet.

# COMMAND ----------

payments_df = spark.readStream\
        .format("cloudFiles")\
        .option("cloudFiles.format",              "csv")\
        .option("cloudFiles.schemaLocation",      SCHEMA_PATH)\
        .option("cloudFiles.inferColumnTypes",    "true")\
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")\
        .option("header",                         "true")\
        .load(SOURCE_PATH)\
        .withColumn("_source_file", col("_metadata.file_path"))\
        .withColumn("_ingested_at", current_timestamp())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Preview Before Writing
# MAGIC
# MAGIC `.display()` on a streaming DataFrame triggers a quick preview run
# MAGIC without writing anywhere — confirms only the 2 new rows (`PAY-900001`,
# MAGIC `PAY-900002`) are about to be picked up, and that no unexpected columns
# MAGIC show up (no schema evolution expected this time).

# COMMAND ----------

payments_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Write the Incremental Batch
# MAGIC
# MAGIC `trigger(availableNow=True)` processes whatever's currently new, then
# MAGIC stops. `outputMode("append")` + `checkpointLocation` together make this
# MAGIC safe to re-run later — re-running this exact cell again won't re-process
# MAGIC `payments_040626.csv` a second time.

# COMMAND ----------

payments_df.writeStream\
        .format("delta")\
        .outputMode("append")\
        .option("checkpointLocation", CHECKPOINT_PATH)\
        .option("mergeSchema",        "true")\
        .trigger(availableNow=True)\
        .toTable(TARGET_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7 — Verify the Result
# MAGIC
# MAGIC Check, in order:
# MAGIC 1. **Row count** — should be old total + 2.
# MAGIC 2. **The 2 new rows** — `PAY-900001`/`PAY-900002`, matched to
# MAGIC    `OR-900001`/`OR-900002`.
# MAGIC 3. **No duplicates** — re-running Step 6 again right now should add 0
# MAGIC    rows (checkpoint already marked the file as processed).

# COMMAND ----------

df = spark.table(TARGET_TABLE)
print(f"Total rows : {df.count()}")

df.filter(col("OrderID").isin(["OR-900001", "OR-900002"])) \
  .select("PaymentID", "OrderID", "PaymentDate", "PaymentMethodID", "_ingested_at") \
  .show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8 — Confirm via Delta History
# MAGIC `DESCRIBE HISTORY` shows a new version corresponding to this run,
# MAGIC separate from the versions created by the earlier `payments_*.csv` loads.

# COMMAND ----------

# MAGIC %sql
# MAGIC describe history harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.payments;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Step
# MAGIC
# MAGIC Once confirmed, re-run the **Silver `payments` notebook**
# MAGIC (`06_payments_data_cleaning_dq_checks.ipynb`) — its `MERGE INTO` (Step 7)
# MAGIC will upsert these 2 new rows into `silver.payments`. After that, the
# MAGIC `OR-900001`/`OR-900002` rows in `fact_sales` will get a real `Payment_ID`
# MAGIC instead of `NULL` the next time the Gold notebook is rebuilt.