# Databricks notebook source
# MAGIC %md
# MAGIC # Assessment 1 — Bronze Layer: Autoloader Ingestion
# MAGIC **Source:** ADLS Gen2 container `assessment-raw-data`  
# MAGIC **Tables:** `suppliers` | `shipping_tier` | `carriers`  
# MAGIC **Target:** `gbmart.bronze_as.*`

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
# MAGIC ## Table 1: `suppliers`
# MAGIC **Source path:** `assessment-raw-data/suppliers/`
# MAGIC
# MAGIC ### Step 1 — Read without `multiLine` to observe the issue

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

# MAGIC %md
# MAGIC ### Step 2 — Fix with `multiLine=True` and `escape` options
# MAGIC
# MAGIC `SUP-05` has an actual newline embedded inside the `OfficeAddress` field. Without `multiLine`, Spark splits that row into two records at the newline. Adding `multiLine=True` and `escape='"'` tells Spark to treat the quoted field as a single value regardless of embedded newlines.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 3 — Autoloader ingestion with fix applied

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

# MAGIC %md
# MAGIC ---
# MAGIC ## Table 2: `shipping_tier`
# MAGIC **Source path:** `assessment-raw-data/shipping-tier/`
# MAGIC
# MAGIC ### Heads-up: column name issue
# MAGIC
# MAGIC Run the cell below first — it will intentionally fail. Read the error carefully before moving to the fix.

# COMMAND ----------

spark.table(f"{catalog}.{schema}.suppliers").display()

# COMMAND ----------

# MAGIC %md
# MAGIC **What happened?**
# MAGIC
# MAGIC The CSV has a column named `Cost (Rs)`. Delta Lake does not accept column names with spaces or special characters — the parentheses and space cause the write to fail with an `AnalysisException`.
# MAGIC
# MAGIC **Fix:** Rename the column using `.withColumnRenamed("Cost (Rs)", "cost_inr")` before writing to Delta.

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

# MAGIC %md
# MAGIC ---
# MAGIC ## Table 3: `carriers`
# MAGIC **Source path:** `assessment-raw-data/carriers/`

# COMMAND ----------

spark.table(f"{catalog}.{schema}.shipping_tier").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Table 3: 
# MAGIC **Source path:** 

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Table 4: `shipments` — Lakeflow Connect (UI)
# MAGIC
# MAGIC The `shipments` table is ingested via **Lakeflow Connect Ingestion Pipeline** configured in the Databricks UI — no notebook code required for ingestion.
# MAGIC
# MAGIC Once the pipeline completes its initial load, run the cell below to verify.

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
# MAGIC ## Final Verification — Row Counts
# MAGIC
# MAGIC | Table | Source | Expected Rows |
# MAGIC |---|---|---|
# MAGIC | `gbmart.bronze_as.suppliers` | ADLS / Autoloader | 10 |
# MAGIC | `gbmart.bronze_as.shipping_tier` | ADLS / Autoloader | 5 |
# MAGIC | `gbmart.bronze_as.carriers` | ADLS / Autoloader | 10 |
# MAGIC | `gbmart.bronze_as.shipments` | Postgres / Lakeflow Connect | 120 |

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