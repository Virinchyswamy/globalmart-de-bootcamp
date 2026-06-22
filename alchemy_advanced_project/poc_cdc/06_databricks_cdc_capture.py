# Databricks notebook source
# MAGIC %md
# MAGIC # Step 6 — CDC Capture
# MAGIC
# MAGIC Read the `poc_orders_slot` replication slot via JDBC -> see the 50 "Day 2" inserts as CDC events.
# MAGIC
# MAGIC `pg_logical_slot_get_changes()` is a regular SQL function, so Spark JDBC can call it like any other query. Each call **drains** the slot up to the current WAL position -- run it again afterwards and you'll get an empty result until the next change happens.

# COMMAND ----------

jdbc_url = "jdbc:postgresql://aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require"

connection_props = {
    "user": "postgres.isqcnhvlfnjszllicxqi",
    "password": "A1qaZ@Vfr$2#3",
    "driver": "org.postgresql.Driver",
}

# COMMAND ----------

cdc_query = (
    "(SELECT * FROM pg_logical_slot_get_changes('poc_orders_slot', NULL, NULL)) AS cdc_changes"
)

# COMMAND ----------

cdc_raw_df = spark.read.jdbc(url=jdbc_url, table=cdc_query, properties=connection_props)

# COMMAND ----------

print("CDC events captured:", cdc_raw_df.count())

# COMMAND ----------

cdc_raw_df.display()

# COMMAND ----------

cdc_raw_df = spark.read.jdbc(url=jdbc_url, table=cdc_query, properties=connection_props).cache()

# COMMAND ----------

print("CDC events captured:", cdc_raw_df.count())

# COMMAND ----------

display(cdc_raw_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Each row's `data` column looks like:
# MAGIC
# MAGIC ```
# MAGIC table public.poc_orders: INSERT: order_id[character varying]:'OR-10009' customer_id[...]:'CUST-13976' ...
# MAGIC ```
# MAGIC
# MAGIC For this POC, just confirm you see ~50 INSERT lines, one per Day-2 order. In a real pipeline you'd parse this text (or switch to the `wal2json` plugin for structured JSON output) and `MERGE` the parsed rows into `bronze.poc_orders`.