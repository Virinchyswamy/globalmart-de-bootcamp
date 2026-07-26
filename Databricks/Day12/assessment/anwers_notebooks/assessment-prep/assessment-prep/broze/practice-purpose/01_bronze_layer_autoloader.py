# Databricks notebook source
# MAGIC %md
# MAGIC # Assessment 1 — Bronze Layer: Autoloader Ingestion
# MAGIC **Source:** ADLS Gen2 container   
# MAGIC **Tables:**  |  |   
# MAGIC **Target:** 

# COMMAND ----------

from pyspark.sql.functions import input_file_name, current_timestamp

catalog          = "gbmart"
schema           = "bronze_as"
mount_point      = "/mnt/assessment-raw-data"
checkpoint_base  = f"{mount_point}/checkpoints"
schema_base      = f"{mount_point}/schema"

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Table 1: 
# MAGIC **Source path:** 

# COMMAND ----------

df = (
    spark.read
    .format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .load("/mnt/assessment-raw-data/suppliers/")
)
display(df)

# COMMAND ----------

suppliers_df = (
    spark.read
    .format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .option("multiLine", "true")
    .option("escape", '"')
    .load("/mnt/assessment-raw-data/suppliers/")
)
display(suppliers_df)

# COMMAND ----------

source = f"{mount_point}/suppliers/"

df_suppliers = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", f"{schema_base}/suppliers")
    .option("header", "true")
    .option("inferSchema", "true")
    .option("multiLine", "true")
    .option("escape", '"')
    .load(source)
    .withColumn("_source_file", input_file_name())
    .withColumn("_ingestion_timestamp", current_timestamp())
)

(
    df_suppliers.writeStream
    .format("delta")
    .option("checkpointLocation", f"{checkpoint_base}/suppliers")
    .trigger(availableNow=True)
    .toTable(f"{catalog}.{schema}.suppliers")
    .awaitTermination()
)

print(f"Done: {catalog}.{schema}.suppliers")

# COMMAND ----------

spark.table(f"{catalog}.{schema}.suppliers").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Table 2: 
# MAGIC **Source path:** 
# MAGIC
# MAGIC ### Heads-up: column name issue
# MAGIC
# MAGIC Run the cell below first — it will intentionally fail. Read the error carefully before moving to the fix.

# COMMAND ----------

# Run this to observe the error — do not skip it
try:
    df_test = (
        spark.read
        .format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load(f"{mount_point}/shipping-tier/")
    )
    print("Schema inferred:")
    df_test.printSchema()
    df_test.write.format("delta").mode("overwrite").saveAsTable(f"{catalog}.{schema}._test_tier")
except Exception as e:
    print(f"ERROR: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC **What happened?**
# MAGIC
# MAGIC The CSV has a column named . Delta Lake does not accept column names with spaces or special characters — the parentheses and space cause the write to fail with an .
# MAGIC
# MAGIC **Fix:** Rename the column using  before writing to Delta.

# COMMAND ----------

source = f"{mount_point}/shipping-tier/"

df_tier = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", f"{schema_base}/shipping_tier")
    .option("header", "true")
    .option("inferSchema", "true")
    .load(source)
    .withColumnRenamed("Cost (Rs)", "cost_inr")   # fix applied at read time
    .withColumn("_source_file", input_file_name())
    .withColumn("_ingestion_timestamp", current_timestamp())
)

(
    df_tier.writeStream
    .format("delta")
    .option("checkpointLocation", f"{checkpoint_base}/shipping_tier")
    .trigger(availableNow=True)
    .toTable(f"{catalog}.{schema}.shipping_tier")
    .awaitTermination()
)

print(f"Done: {catalog}.{schema}.shipping_tier")

# COMMAND ----------

spark.table(f"{catalog}.{schema}.shipping_tier").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Table 3: 
# MAGIC **Source path:** 

# COMMAND ----------

source = f"{mount_point}/carriers/"

df_carriers = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", f"{schema_base}/carriers")
    .option("header", "true")
    .option("inferSchema", "true")
    .load(source)
    .withColumn("_source_file", input_file_name())
    .withColumn("_ingestion_timestamp", current_timestamp())
)

(
    df_carriers.writeStream
    .format("delta")
    .option("checkpointLocation", f"{checkpoint_base}/carriers")
    .trigger(availableNow=True)
    .toTable(f"{catalog}.{schema}.carriers")
    .awaitTermination()
)

print(f"Done: {catalog}.{schema}.carriers")

# COMMAND ----------

spark.table(f"{catalog}.{schema}.carriers").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Table 4:  — Lakeflow Connect (UI)
# MAGIC
# MAGIC The  table is ingested via **Lakeflow Connect Ingestion Pipeline** configured in the Databricks UI — no notebook code required for ingestion.
# MAGIC
# MAGIC Once the pipeline completes its initial load, run the cell below to verify.

# COMMAND ----------

spark.table(f"{catalog}.{schema}.shipments").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Enable Change Data Feed on all Bronze tables
# MAGIC
# MAGIC CDF allows downstream Silver pipelines to read only changed rows — required for incremental loading in Assessment 2.

# COMMAND ----------

for table in ["suppliers", "shipping_tier", "carriers"]:
    spark.sql(f"""
        ALTER TABLE {catalog}.{schema}.{table}
        SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
    """)
    print(f"CDF enabled: {catalog}.{schema}.{table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Final Verification — Row Counts
# MAGIC
# MAGIC | Table | Source | Expected Rows |
# MAGIC |---|---|---|
# MAGIC |  | ADLS / Autoloader | 10 |
# MAGIC |  | ADLS / Autoloader | 5 |
# MAGIC |  | ADLS / Autoloader | 10 |
# MAGIC |  | Postgres / Lakeflow Connect | 120 |

# COMMAND ----------

for table in ["suppliers", "shipping_tier", "carriers", "shipments"]:
    count = spark.table(f"{catalog}.{schema}.{table}").count()
    print(f"{catalog}.{schema}.{table}: {count} rows")