# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer — Enable Change Data Feed (CDF)
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC > **Run this only after the Silver layer's full load is complete** — once
# MAGIC > all 8 Silver tables (`customers`, `orders`, `order_items`, `products`,
# MAGIC > `address`, `payments`, `payment_methods`, `returns`) have been built
# MAGIC > from Bronze. CDF needs to be enabled on each Silver table *before*
# MAGIC > anything starts reading incremental changes out of it — same reasoning
# MAGIC > as Bronze: enabling it late means missing whatever changed in between.
# MAGIC
# MAGIC ## Why CDF on Silver?
# MAGIC This lets a future incremental Gold refresh (or any other downstream
# MAGIC consumer) read only the *changed* Silver rows since last run, instead of
# MAGIC rescanning the full table — the same efficiency reason CDF is enabled on
# MAGIC Bronze for Silver's benefit.
# MAGIC
# MAGIC > **Not required for Gold today.** This program's `dim_*`/`fact_sales`
# MAGIC > tables are built via full overwrite, not incremental `MERGE`, so
# MAGIC > nothing currently reads a Silver change feed. Enabling it here is about
# MAGIC > keeping the option open for later (e.g. if Gold ever needs to move to
# MAGIC > an incremental refresh at larger scale), not because today's Gold
# MAGIC > build depends on it.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Enable CDF on All Silver Tables

# COMMAND ----------

CATALOG = "harsh_kumar01_npmentorskool_onmicrosoft_com"
SCHEMA  = "silver"

SILVER_TABLES = [
    "customers", "orders", "order_items", "products",
    "address", "payments", "payment_methods", "returns"
]

for table in SILVER_TABLES:
    full_name = f"{CATALOG}.{SCHEMA}.{table}"
    try:
        spark.sql(f"""
            ALTER TABLE {full_name}
            SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
        """)
        print(f"  CDF enabled : {full_name}")
    except Exception as e:
        print(f"  SKIPPED     : {full_name} — {str(e)[:60]}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Verify CDF is enabled

# COMMAND ----------

# MAGIC %sql
# MAGIC describe history harsh_kumar01_npmentorskool_onmicrosoft_com.silver.customers;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ```
# MAGIC Silver Delta Tables (CDF enabled)
# MAGIC   gbmart.silver.customers          <- CDF ON
# MAGIC   gbmart.silver.orders             <- CDF ON
# MAGIC   gbmart.silver.order_items        <- CDF ON
# MAGIC   gbmart.silver.products           <- CDF ON
# MAGIC   gbmart.silver.address            <- CDF ON
# MAGIC   gbmart.silver.payments           <- CDF ON
# MAGIC   gbmart.silver.payment_methods    <- CDF ON
# MAGIC   gbmart.silver.returns            <- CDF ON
# MAGIC        |
# MAGIC        |  Available for incremental reads via:
# MAGIC        |  spark.read.format("delta")
# MAGIC        |      .option("readChangeFeed", "true")
# MAGIC        |      .option("startingVersion", last_version)
# MAGIC        v
# MAGIC   Not consumed by Gold today (full overwrite) — kept available
# MAGIC   for the Day 12 incremental SCD1/SCD2 notebooks and any future
# MAGIC   incremental Gold refresh.
# MAGIC ```
# MAGIC
# MAGIC **Silver layer CDF is enabled.**