# Databricks notebook source
from pyspark.sql.functions import input_file_name, current_timestamp

# External Location base path — set once, reuse everywhere
EXTERNAL_LOCATION = "abfss://ecom-gbmart-data@ecomadlsdata.dfs.core.windows.net/raw-data"

SOURCE_FOLDER   = "customers_exp"
CATALOG         = "harsh_kumar01_npmentorskool_onmicrosoft_com"
SCHEMA          = "bronze_practice"
TABLE           = "customers_exp"
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

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
print(f"Catalog '{CATALOG}' and schema '{SCHEMA}' are ready.")

# COMMAND ----------

from pyspark.sql.functions import *

# COMMAND ----------

# MAGIC %md
# MAGIC #### First Load

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

customers_df.writeStream\
        .format("delta")\
        .outputMode("append")\
        .option("checkpointLocation", CHECKPOINT_PATH)\
        .trigger(availableNow=True)\
        .toTable(TARGET_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Second Load
# MAGIC - Uploading new file to ADLS with new schema

# COMMAND ----------

files = dbutils.fs.ls(SOURCE_PATH)
print(f"Files found in {SOURCE_FOLDER}/:\n")
for f in files:
    print(f"  {f.name}  ({f.size / 1024:.1f} KB)")

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze_practice.customers_exp;

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
        .trigger(availableNow=True)\
        .toTable(TARGET_TABLE)

# COMMAND ----------

customers_df.writeStream\
        .format("delta")\
        .outputMode("append")\
        .option("checkpointLocation", CHECKPOINT_PATH)\
        .trigger(availableNow=True)\
        .toTable(TARGET_TABLE)

# COMMAND ----------

# MAGIC %md
# MAGIC ### rescue mode

# COMMAND ----------

customers_df = spark.readStream\
        .format("cloudFiles")\
        .option("cloudFiles.format",              "csv")\
        .option("cloudFiles.schemaLocation",      SCHEMA_PATH)\
        .option("cloudFiles.inferColumnTypes",    "true")\
        .option("cloudFiles.schemaEvolutionMode", "rescue")\
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
        .option("mergeschema", "true")\
        .trigger(availableNow=True)\
        .toTable(TARGET_TABLE)

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze_practice.customers_exp;

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from harsh_kumar01_npmentorskool_onmicrosoft_com.bronze_practice.customers_exp
# MAGIC where third_party_data_sharing is not null;