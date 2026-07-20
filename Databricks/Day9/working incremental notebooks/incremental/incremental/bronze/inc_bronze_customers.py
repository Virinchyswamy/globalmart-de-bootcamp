# Databricks notebook source
from pyspark.sql.functions import col, current_timestamp

# ─── Same values as the customers notebook — reused, not re-mounted ───────────
MOUNT_POINT = "/mnt/virinchy_gbmart_data"
CATALOG = "harsh_kumar01_npmentorskool_onmicrosoft_com"
SCHEMA = "bronze"

# No raw-data / raw-demo-data suffix -- source folders live directly under the mount
MOUNT_BASE = MOUNT_POINT

# Table-specific values
SOURCE_FOLDER = "customers"
TABLE = "customers"

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
# MAGIC # Practice — Schema Evolution on bronze.customers
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC Goal: demonstrate Autoloader's `addNewColumns` schema evolution mechanism
# MAGIC end-to-end — a new file lands with columns the target table doesn't have
# MAGIC yet, and Autoloader automatically adds them on write.
# MAGIC
# MAGIC > **Note on the example file:** `customer_consent_040626.csv` is being used
# MAGIC > here purely to demonstrate the *mechanism* (new columns appearing,
# MAGIC > getting merged in automatically). In a real production pipeline, consent
# MAGIC > data would more typically live in its own table (`bronze.customer_consent`)
# MAGIC > rather than being merged into `customers`, since it's a different kind of
# MAGIC > record, not a new attribute of an existing customer. Worth keeping in mind
# MAGIC > when applying this pattern elsewhere — but for seeing how
# MAGIC > `addNewColumns` + `mergeSchema` actually behave, this works fine.
# MAGIC
# MAGIC ## Step 1 — Checking the Path
# MAGIC Same setup as the original Bronze customers ingestion notebook —
# MAGIC confirms `SOURCE_PATH`, `CHECKPOINT_PATH`, `SCHEMA_PATH` before doing
# MAGIC anything else.

# COMMAND ----------

files = dbutils.fs.ls(SOURCE_PATH)
print(f"Files found in {SOURCE_FOLDER}/:\n")
for f in files:
    print(f"  {f.name}  ({f.size / 1024:.1f} KB)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Checking the New File
# MAGIC
# MAGIC `customer_consent_040626.csv` is new — it has both new **rows** and new
# MAGIC **columns** compared to what's already in `bronze.customers`. This is the
# MAGIC file we'll use to trigger schema evolution.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Reading the New File Directly
# MAGIC
# MAGIC A one-off batch read (not Autoloader) just to **see** the new file's
# MAGIC actual columns before doing anything with it.

# COMMAND ----------

customers_inc_df = (
    spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(f"{SOURCE_PATH}customer_consent_040626.csv")
)

display(customers_inc_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Confirming bronze.customers Doesn't Have These Columns Yet
# MAGIC
# MAGIC **We don't have the above columns in the Bronze table.** Run the query
# MAGIC below to confirm — `bronze.customers` only has the original customer
# MAGIC fields, none of the consent-related columns shown in Step 3.
# MAGIC
# MAGIC This is the gap schema evolution closes: the new file has columns the
# MAGIC table doesn't, and rather than failing or dropping them, we want Autoloader
# MAGIC to **merge** them in automatically.

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.customers;

# COMMAND ----------

from pyspark.sql.functions import *

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Autoloader Reads the New Data and Evolves the Schema
# MAGIC
# MAGIC Same stream definition as the original ingestion notebook. With
# MAGIC `cloudFiles.schemaEvolutionMode = "addNewColumns"` set, Autoloader will
# MAGIC automatically detect the consent file's extra columns and add them to the
# MAGIC schema being read — no manual schema editing required.
# MAGIC
# MAGIC This cell only **defines** the streaming DataFrame — nothing is read or
# MAGIC written yet.

# COMMAND ----------

customers_df = spark.readStream\
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

customers_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Writing the Data: Columns Get Merged
# MAGIC
# MAGIC Once this write completes, the new columns will show up as real columns
# MAGIC on `harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.customers` — existing rows will show `NULL` for them,
# MAGIC the consent file's rows will have them populated.
# MAGIC
# MAGIC **The important detail:** `mergeSchema = "true"` on the write side.
# MAGIC `addNewColumns` on the read side only controls what Autoloader is willing
# MAGIC to *read*; without `mergeSchema = "true"` here, Delta will still reject
# MAGIC the write because the incoming data has columns the table doesn't have
# MAGIC yet. Both settings are required together for schema evolution to actually
# MAGIC take effect.

# COMMAND ----------

customers_df.writeStream\
        .format("delta")\
        .outputMode("append")\
        .option("checkpointLocation", CHECKPOINT_PATH)\
        .option("mergeSchema",        "true")\
        .trigger(availableNow=True)\
        .toTable(TARGET_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7 — Verify: Columns Merged, History Updated
# MAGIC
# MAGIC `SELECT *` should now show the new consent-related columns on
# MAGIC `bronze.customers` — `NULL` for the original rows, populated for the rows
# MAGIC that came from `customer_consent_040626.csv`.
# MAGIC
# MAGIC `DESCRIBE HISTORY` shows a new version for this write, separate from the
# MAGIC versions created by the earlier `customers_*.csv` loads — confirms this
# MAGIC was a genuine schema-evolving append, not a no-op.

# COMMAND ----------

# MAGIC %sql
# MAGIC select count(*) from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.customers;

# COMMAND ----------

# MAGIC %sql
# MAGIC describe history harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.customers;

# COMMAND ----------

