# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer — Addresses Ingestion via Autoloader
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | ADLS Gen2 → External Location → `addresses/` |
# MAGIC | **External Location** | `abfss://ecom-gbmart-data@ecomadlsdata.dfs.core.windows.net/raw-data` |
# MAGIC | **Target** | `gbmart.bronze.addresses` (Managed Delta Table) |
# MAGIC | **Auth** | Unity Catalog External Location — no keys in code |
# MAGIC | **Note** | `AddressLine1` has embedded newlines — `multiLine=true` handles this |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Configuration
# MAGIC
# MAGIC > **No `spark.conf.set` or secret scope needed for storage access.**  
# MAGIC > Unity Catalog External Location handles authentication automatically.  
# MAGIC > As long as your cluster has access to the `gbmart` catalog, ADLS reads just work.

# COMMAND ----------

from pyspark.sql.functions import input_file_name, current_timestamp

EXTERNAL_LOCATION = "abfss://ecom-gbmart-data@ecomadlsdata.dfs.core.windows.net/raw-data"

SOURCE_FOLDER   = "addresses"
CATALOG         = "gbmart"
SCHEMA          = "bronze"
TABLE           = "addresses"
TARGET_TABLE    = f"{CATALOG}.{SCHEMA}.{TABLE}"

SOURCE_PATH     = f"{EXTERNAL_LOCATION}/{SOURCE_FOLDER}/"
CHECKPOINT_PATH = f"{EXTERNAL_LOCATION}/_checkpoints/{TABLE}/"
SCHEMA_PATH     = f"{EXTERNAL_LOCATION}/_schemas/{TABLE}/"

print(f"Source      : {SOURCE_PATH}")
print(f"Target table: {TARGET_TABLE}")
print(f"Checkpoint  : {CHECKPOINT_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Verify Files in ADLS

# COMMAND ----------

files = dbutils.fs.ls(SOURCE_PATH)
print(f"Files found in {SOURCE_FOLDER}/:\n")
for f in files:
    print(f"  {f.name}  ({f.size / 1024:.1f} KB)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Create Catalog & Schema (if not exists)

# COMMAND ----------

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
print(f"Catalog '{CATALOG}' and schema '{SCHEMA}' are ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Autoloader Ingestion
# MAGIC
# MAGIC | Option | Value | Why |
# MAGIC |---|---|---|
# MAGIC | `cloudFiles.format` | `csv` | source file format |
# MAGIC | `cloudFiles.schemaLocation` | `SCHEMA_PATH` | saves inferred schema — reused on next run |
# MAGIC | `cloudFiles.inferColumnTypes` | `true` | infers proper types instead of all string |
# MAGIC | `cloudFiles.schemaEvolutionMode` | `addNewColumns` | new columns in future files added automatically |
# MAGIC | `multiLine` | `true` | handles embedded newlines in `AddressLine1` field |
# MAGIC | `mergeSchema` | `true` | Delta write-side schema merge |
# MAGIC | `trigger(availableNow)` | — | batch-style: process all new files then stop |

# COMMAND ----------

from pyspark.sql.functions import *

# COMMAND ----------

addresses_df = spark.readStream\
        .format("cloudFiles")\
        .option("cloudFiles.format",              "csv")\
        .option("cloudFiles.schemaLocation",      SCHEMA_PATH)\
        .option("cloudFiles.inferColumnTypes",    "true")\
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")\
        .option("header",                         "true")\
        .option("multiLine",                      "true")\
        .option("escape",                         '"')\
        .load(SOURCE_PATH)\
        .withColumn("_source_file", col("_metadata.file_path"))\
        .withColumn("_ingested_at", current_timestamp())

# COMMAND ----------

addresses_df.writeStream\
        .format("delta")\
        .outputMode("append")\
        .option("checkpointLocation", CHECKPOINT_PATH)\
        .option("mergeSchema",        "true")\
        .trigger(availableNow=True)\
        .toTable(TARGET_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Verify Data in Bronze Table

# COMMAND ----------

df = spark.table(TARGET_TABLE)
print(f"Total rows : {df.count()}")
print(f"Columns    : {df.columns}")
df.display()

# COMMAND ----------

df.groupBy("_source_file").count().orderBy("_source_file").display(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Test Incremental Load
# MAGIC
# MAGIC 1. Upload Day 1 files to `addresses/` in ADLS
# MAGIC 2. Run Step 4 → **~10,000 rows** land in Bronze
# MAGIC 3. Upload `addresses_020626.csv` to ADLS
# MAGIC 4. **Re-run Step 4** — Autoloader skips already-processed files via checkpoint, picks up only the new file
# MAGIC 5. Row count → **~30,000** with no duplicates

# COMMAND ----------

df = spark.table(TARGET_TABLE)
print(f"Total rows : {df.count()}")
print(f"Columns    : {df.columns}")
df.display(5, truncate=False)

# COMMAND ----------

# Run after uploading addresses_030626.csv
spark.table(TARGET_TABLE).groupBy("_source_file").count().orderBy("_source_file").display(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reset (if needed)
# MAGIC Only run this to start fresh — clears checkpoint, schema, and drops the table.

# COMMAND ----------

# dbutils.fs.rm(CHECKPOINT_PATH, recurse=True)
# dbutils.fs.rm(SCHEMA_PATH, recurse=True)
# spark.sql(f"DROP TABLE IF EXISTS {TARGET_TABLE}")
# print("Reset complete — re-run Step 4 for a clean ingestion")