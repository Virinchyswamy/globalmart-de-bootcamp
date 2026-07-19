# Databricks notebook source
# MAGIC %md
# MAGIC # Practice — Incremental Load into bronze.products
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC Goal: drop `products_020626.json` into the `products/` source folder and
# MAGIC confirm Autoloader picks up *only* the new file (via checkpoint), not
# MAGIC `products_010626.json` which was already processed.
# MAGIC
# MAGIC Same Autoloader configuration as `04_bronze_products_autoloader.ipynb` —
# MAGIC this notebook continues that same stream, it doesn't start a new one.
# MAGIC
# MAGIC **No schema evolution in this file** — `products_020626.json` has the
# MAGIC exact same fields as the original. It demonstrates a price change on 2
# MAGIC existing products (the SCD2 scenario) plus 1 brand-new product.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup
# MAGIC Same paths as the original Bronze products ingestion notebook.

# COMMAND ----------

from pyspark.sql.functions import *

EXTERNAL_LOCATION = "abfss://ecom-gbmart-data@ecomadlsdata.dfs.core.windows.net/raw-data"

SOURCE_FOLDER   = "products"
CATALOG         = "gbmart"
SCHEMA          = "bronze"
TABLE           = "products"
TARGET_TABLE    = f"{CATALOG}.{SCHEMA}.{TABLE}"

SOURCE_PATH     = f"{EXTERNAL_LOCATION}/{SOURCE_FOLDER}/"
CHECKPOINT_PATH = f"{EXTERNAL_LOCATION}/_checkpoints/{TABLE}/"
SCHEMA_PATH     = f"{EXTERNAL_LOCATION}/_schemas/{TABLE}/"

print(f"Source      : {SOURCE_PATH}")
print(f"Target table: {TARGET_TABLE}")
print(f"Checkpoint  : {CHECKPOINT_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — List Files in the Source Folder
# MAGIC Confirm `products_020626.json` actually landed (uploaded manually to ADLS)
# MAGIC alongside `products_010626.json`, before running anything.

# COMMAND ----------

files = dbutils.fs.ls(SOURCE_PATH)
print(f"Files found in {SOURCE_FOLDER}/:\n")
for f in files:
    print(f"  {f.name}  ({f.size / 1024:.1f} KB)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Baseline Check
# MAGIC Confirm the current row count in `gbmart.bronze.products` **before** running
# MAGIC the incremental load, so the before/after comparison in Step 7 is
# MAGIC meaningful. Should show 500 rows.

# COMMAND ----------

# MAGIC %sql
# MAGIC select count(*) from gbmart.bronze.products;

# COMMAND ----------

products_inc_df = (
    spark.read\
         .option("multiLine","true")\
         .json("abfss://ecom-gbmart-data@ecomadlsdata.dfs.core.windows.net/raw-data/products/products_020626.json")
)

# COMMAND ----------

products_inc_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Define the Incremental Read (Autoloader)
# MAGIC
# MAGIC Identical options to `04_bronze_products_autoloader.ipynb` — `cloudFiles`
# MAGIC source + `CHECKPOINT_PATH` together mean only files **not already recorded
# MAGIC in the checkpoint** get read. `products_010626.json` was already processed
# MAGIC in an earlier run, so this resolves to just `products_020626.json`.
# MAGIC
# MAGIC `multiLine = true` is required here (not needed for the customers CSV
# MAGIC notebook) because the JSON file is a single array spanning multiple lines.
# MAGIC
# MAGIC This cell only **defines** the streaming DataFrame — nothing is read or
# MAGIC written yet.

# COMMAND ----------

products_df = spark.readStream\
        .format("cloudFiles")\
        .option("cloudFiles.format",              "json")\
        .option("cloudFiles.schemaLocation",      SCHEMA_PATH)\
        .option("cloudFiles.inferColumnTypes",    "true")\
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")\
        .option("multiLine",                      "true")\
        .load(SOURCE_PATH)\
        .withColumn("_source_file", col("_metadata.file_path"))\
        .withColumn("_ingested_at", current_timestamp())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Preview Before Writing
# MAGIC
# MAGIC `.display()` on a streaming DataFrame triggers a quick preview run without
# MAGIC writing anywhere — confirms only the 3 new rows (2 price changes + 1 new
# MAGIC product) are about to be picked up, and that no unexpected fields show up
# MAGIC (no schema evolution expected this time).

# COMMAND ----------

products_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Write the Incremental Batch
# MAGIC
# MAGIC `trigger(availableNow=True)` processes whatever's currently new, then
# MAGIC stops. `outputMode("append")` + `checkpointLocation` together make this
# MAGIC safe to re-run later — re-running this exact cell again won't re-process
# MAGIC `products_020626.json` a second time.

# COMMAND ----------

products_df.writeStream\
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
# MAGIC 1. **Row count** — should be `500 + 3 = 503`.
# MAGIC 2. **The 2 changed `product_id`s** — should now show **2 rows each**, old
# MAGIC    price and new price, distinguished by `_ingested_at`.
# MAGIC 3. **No duplicates** — re-running Step 6 again right now should add 0 rows
# MAGIC    (checkpoint already marked the file as processed).

# COMMAND ----------

df = spark.table(TARGET_TABLE)
print(f"Total rows : {df.count()}")

df.filter(col("product_id").isin(["PRD-00001", "PRD-00002"])) \
  .select("product_id", "product_name", "discounted_price_inr", "_ingested_at") \
  .orderBy("product_id", "_ingested_at") \
  .show(truncate=False)

df.filter(col("product_id") == "PRD-00501") \
  .select("product_id", "product_name", "category", "discounted_price_inr") \
  .show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8 — Confirm via Delta History
# MAGIC `DESCRIBE HISTORY` shows a new version with `operation = STREAMING UPDATE`
# MAGIC corresponding to this run, separate from the version created by the
# MAGIC original `products_010626.json` load.

# COMMAND ----------

# MAGIC %sql
# MAGIC describe history gbmart.bronze.products;