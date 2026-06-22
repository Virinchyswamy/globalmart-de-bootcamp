# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer — Products Ingestion via Autoloader (JSON)
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | ADLS Gen2 -> External Location -> `products/*.json` |
# MAGIC | **External Location** | `abfss://ecom-gbmart-data@ecomadlsdata.dfs.core.windows.net/raw-data` |
# MAGIC | **Target** | `gbmart.bronze.products` (Managed Delta Table) |
# MAGIC | **Auth** | Unity Catalog External Location — no keys in code |
# MAGIC | **Schema** | Flat fields + nested `specs` struct + `tags` array + `supplier_info` struct |
# MAGIC
# MAGIC **Nested JSON in Bronze — Silver will flatten and explode the nested fields.**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Configuration
# MAGIC
# MAGIC > **No `spark.conf.set` or secret scope needed for storage access.**  
# MAGIC > Unity Catalog External Location handles authentication automatically.

# COMMAND ----------

from pyspark.sql.functions import input_file_name, current_timestamp

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
# MAGIC | `cloudFiles.format` | `json` | source file format |
# MAGIC | `cloudFiles.schemaLocation` | `SCHEMA_PATH` | saves inferred schema — reused on next run |
# MAGIC | `cloudFiles.inferColumnTypes` | `true` | infers proper types (numbers stay numeric) |
# MAGIC | `cloudFiles.schemaEvolutionMode` | `addNewColumns` | new fields in future files added automatically |
# MAGIC | `multiLine` | `true` | JSON array spread across multiple lines |
# MAGIC | `mergeSchema` | `true` | Delta write-side schema merge |
# MAGIC | `trigger(availableNow)` | — | batch-style: process all new files then stop |
# MAGIC
# MAGIC **Nested fields preserved in Bronze:**
# MAGIC ```json
# MAGIC {
# MAGIC   "product_id": "PRD-00001",
# MAGIC   "specs": { "warranty_months": 24, "color_options": ["Blue", "Black"] },
# MAGIC   "tags": ["electronics", "gadget"],
# MAGIC   "supplier_info": { "supplier_id": "SUP-02", "name": "Greenwood Supplies" }
# MAGIC }
# MAGIC ```
# MAGIC Silver will use `specs.warranty_months`, `EXPLODE(tags)` etc.

# COMMAND ----------

from pyspark.sql.functions import *

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

products_df.display()

# COMMAND ----------

products_df.writeStream\
        .format("delta")\
        .outputMode("append")\
        .option("checkpointLocation", CHECKPOINT_PATH)\
        .option("mergeSchema",        "true")\
        .trigger(availableNow=True)\
        .toTable(TARGET_TABLE)

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from gbmart.bronze.products;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Verify Data in Bronze Table

# COMMAND ----------

df = spark.table(TARGET_TABLE)
print(f"Total rows : {df.count()}")
print(f"Columns    : {df.columns}")
df.display(5, truncate=False)

# COMMAND ----------

df.groupBy("_source_file").count().orderBy("_source_file").display(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Explore Nested Schema

# COMMAND ----------

# Nested structs are preserved as-is in Bronze
df.printSchema()

# COMMAND ----------

# Access nested fields directly
df.select(
    "product_id",
    "product_name",
    "specs.warranty_months",
    "specs.color_options",
    "supplier_info.name"
).display()

# COMMAND ----------

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