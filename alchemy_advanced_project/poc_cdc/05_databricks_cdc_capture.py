# Databricks notebook source
# MAGIC %md
# MAGIC # Step 5 — CDC Capture
# MAGIC
# MAGIC Read the `cdc_poc_products_slot` replication slot via JDBC -> see the Day-2 INSERT / UPDATE / DELETE as CDC events.
# MAGIC
# MAGIC `pg_logical_slot_get_changes()` is a regular SQL function, so Spark JDBC can call it like any other query. Each call **drains** the slot up to the current WAL position -- run it again afterwards and you'll get an empty result until the next change happens.
# MAGIC
# MAGIC We `.cache()` the result immediately so that `count()` and `display()` both read the same materialized snapshot instead of re-draining the slot twice.

# COMMAND ----------

jdbc_url = "jdbc:postgresql://aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require"

connection_props = {
    "user": "postgres.isqcnhvlfnjszllicxqi",
    "password": "A1qaZ@Vfr$2#3",
    "driver": "org.postgresql.Driver",
}

# COMMAND ----------

cdc_query = (
    "(SELECT * FROM pg_logical_slot_get_changes('cdc_poc_products_slot', NULL, NULL)) AS cdc_changes"
)

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
# MAGIC table cdc_poc.products: INSERT: product_id[text]:'PRD-005' product_name[text]:'Desk Lamp' ...
# MAGIC table cdc_poc.products: UPDATE: product_id[text]:'PRD-001' ... price[numeric]:549.00
# MAGIC table cdc_poc.products: DELETE: product_id[text]:'PRD-004' ...
# MAGIC ```
# MAGIC
# MAGIC Every transaction is wrapped in `BEGIN <xid>` / `COMMIT <xid>` markers, so 1 statement = 3 rows (BEGIN, the change, COMMIT). If you ran all three statements from `04_make_changes.sql` separately, you'll see 3 transactions x 3 rows = 9 rows total here.
# MAGIC
# MAGIC In a real pipeline you'd parse this text (or switch to the `wal2json` plugin for structured JSON output) and `MERGE` the parsed rows into `bronze.cdc_poc_products`.