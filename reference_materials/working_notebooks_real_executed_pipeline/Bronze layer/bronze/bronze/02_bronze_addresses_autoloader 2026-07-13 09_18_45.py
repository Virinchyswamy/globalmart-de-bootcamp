# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer — Addresses Ingestion via Autoloader
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | Blob Storage, mounted via `dbutils.fs.mount()` → `addresses/` |
# MAGIC | **Mount** | Reused — no new mount created here. Same `MOUNT_POINT` as the customers notebook. |
# MAGIC | **Target** | `harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.addresses` (Managed Delta Table) |
# MAGIC | **Auth** | Storage account access key, set once at mount time — no Unity Catalog External Location involved |
# MAGIC | **Note** | `AddressLine1` has embedded newlines — `multiLine=true` handles this |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Configuration
# MAGIC
# MAGIC > **No new mount is created here — this reuses the mount already set up in the customers notebook.**
# MAGIC > `dbutils.fs.mounts()` is checked first; if `MOUNT_POINT` isn't already mounted in this session, the cell fails fast with a clear message instead of a confusing downstream error.

# COMMAND ----------

from pyspark.sql.functions import col, current_timestamp

# ─── Same values as the customers notebook — reused, not re-mounted ───────────
MOUNT_POINT = "/mnt/virinchy_gbmart_data"
CATALOG = "harsh_kumar01_npmentorskool_onmicrosoft_com"   # ← different catalog than gbmart
SCHEMA = "bronze"

# No raw-data / raw-demo-data suffix -- source folders live directly under the mount
MOUNT_BASE  = MOUNT_POINT

# Fail fast with a clear message instead of a confusing downstream error if
# the mount from the customers notebook isn't active in this session.
mount_exists = any(m.mountPoint == MOUNT_POINT for m in dbutils.fs.mounts())
if not mount_exists:
    raise RuntimeError(
        f"{MOUNT_POINT} is not mounted in this session. "
        f"Run the customers notebook's mount cell first."
    )

print(f"Mount point : {MOUNT_POINT}  (confirmed mounted)")
print(f"Mount base  : {MOUNT_BASE}")
print(f"Catalog     : {CATALOG}")
print(f"Schema      : {SCHEMA}")

# ─── Addresses-specific paths, built from the shared mount config above ───────
# Same shared-root checkpoint/schema structure as the other mounting notebooks:
# _checkpoints/<table>/ and _schemas/<table>/ live directly under MOUNT_BASE.
SOURCE_FOLDER   = "addresses"
TABLE           = "addresses"
TARGET_TABLE    = f"{CATALOG}.{SCHEMA}.{TABLE}"

SOURCE_PATH     = f"{MOUNT_BASE}/{SOURCE_FOLDER}/"
CHECKPOINT_PATH = f"{MOUNT_BASE}/_checkpoints/{TABLE}/"
SCHEMA_PATH     = f"{MOUNT_BASE}/_schemas/{TABLE}/"

print(f"Source      : {SOURCE_PATH}")
print(f"Target table: {TARGET_TABLE}")
print(f"Checkpoint  : {CHECKPOINT_PATH}")
print(f"Schema      : {SCHEMA_PATH}")

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.addresses;
# MAGIC

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

# COMMAND ----------

