# Databricks notebook source
from pyspark.sql.functions import input_file_name, current_timestamp

# External Location base path — set once, reuse everywhere
EXTERNAL_LOCATION = "abfss://ecom-gbmart-data@ecomadlsdata.dfs.core.windows.net/raw-data"

SOURCE_FOLDER   = "customers"
CATALOG         = "gbmart"
SCHEMA          = "bronze"
TABLE           = "customers"
TARGET_TABLE    = f"{CATALOG}.{SCHEMA}.{TABLE}"

SOURCE_PATH     = f"{EXTERNAL_LOCATION}/{SOURCE_FOLDER}/"
CHECKPOINT_PATH = f"{EXTERNAL_LOCATION}/_checkpoints/{TABLE}/"
SCHEMA_PATH     = f"{EXTERNAL_LOCATION}/_schemas/{TABLE}/"

print(f"Source      : {SOURCE_PATH}")
print(f"Target table: {TARGET_TABLE}")
print(f"Checkpoint  : {CHECKPOINT_PATH}")

# COMMAND ----------

files = dbutils.fs.ls(SOURCE_PATH)
print(f"Files found in {SOURCE_FOLDER}/:\n")
for f in files:
    print(f"  {f.name}  ({f.size / 1024:.1f} KB)")

# COMMAND ----------

customers_inc_df = (
    spark.read
         .option("header", "true")
         .option("inferSchema", "true")
         .csv("abfss://ecom-gbmart-data@ecomadlsdata.dfs.core.windows.net/raw-data/customers/customer_consent_040626.csv")
)

display(customers_inc_df)

# COMMAND ----------

# MAGIC %md
# MAGIC We don't have above columns in bronze table

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from gbmart.bronze.customers;

# COMMAND ----------

from pyspark.sql.functions import *

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

customers_df.writeStream\
        .format("delta")\
        .outputMode("append")\
        .option("checkpointLocation", CHECKPOINT_PATH)\
        .option("mergeSchema",        "true")\
        .trigger(availableNow=True)\
        .toTable(TARGET_TABLE)

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from gbmart.bronze.customers;

# COMMAND ----------

# MAGIC %sql
# MAGIC describe history gbmart.bronze.customers;