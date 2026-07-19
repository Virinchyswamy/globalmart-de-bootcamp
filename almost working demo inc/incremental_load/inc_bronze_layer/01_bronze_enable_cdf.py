# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer — Enable Change Data Feed (CDF)
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC > **Run this only after the Bronze layer's full load is complete** — once
# MAGIC > every Bronze table (`customers`, `orders`, `order_items`, `products`,
# MAGIC > `addresses`, `payments`, `payment_methods`, `returns`) has been created
# MAGIC > and populated via Lakeflow Connect / Autoloader. CDF needs to be enabled
# MAGIC > on each table *before* Silver starts reading incremental changes from
# MAGIC > it — enabling it after Silver has already started reading would mean
# MAGIC > missing whatever changes happened in between.
# MAGIC
# MAGIC ## Why CDF?
# MAGIC Without CDF, Silver's incremental notebooks would have to **full-scan**
# MAGIC Bronze every run to find new/changed rows. With CDF enabled, Silver reads
# MAGIC **only the changes** since its last run.
# MAGIC
# MAGIC ```
# MAGIC Without CDF:  Silver reads 126,000 orders every run → slow, expensive
# MAGIC With CDF:     Silver reads 800 new orders since last run → fast, cheap
# MAGIC ```
# MAGIC
# MAGIC ## What CDF tracks
# MAGIC Every INSERT / UPDATE / DELETE on a Bronze table is recorded with:
# MAGIC
# MAGIC | Column | Description |
# MAGIC |---|---|
# MAGIC | `_change_type` | `insert`, `update_preimage`, `update_postimage`, `delete` |
# MAGIC | `_commit_version` | Delta table version when the change happened |
# MAGIC | `_commit_timestamp` | When the change was committed |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Enable CDF on All Bronze Tables
# MAGIC Table list matches what was actually built in this program's Bronze layer.

# COMMAND ----------

CATALOG = "gbmart"
SCHEMA  = "bronze"

BRONZE_TABLES = [
    "customers", "orders", "order_items", "products",
    "addresses", "payments", "payment_methods", "returns"
]

for table in BRONZE_TABLES:
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
# MAGIC %md
# MAGIC ## Step 2 — Verify CDF is enabled

# COMMAND ----------

# MAGIC %sql
# MAGIC describe history gbmart.bronze.customers;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ```
# MAGIC Bronze Delta Tables (CDF enabled)
# MAGIC   gbmart.bronze.customers          <- CDF ON
# MAGIC   gbmart.bronze.orders             <- skipped, Lakeflow Connect Streaming Table (pipeline-owned) — uses updated_at cursor instead
# MAGIC   gbmart.bronze.order_items        <- skipped, Lakeflow Connect Streaming Table (pipeline-owned) — uses updated_at cursor instead
# MAGIC   gbmart.bronze.products           <- CDF ON
# MAGIC   gbmart.bronze.addresses          <- CDF ON
# MAGIC   gbmart.bronze.payments           <- CDF ON
# MAGIC   gbmart.bronze.payment_methods    <- CDF ON
# MAGIC   gbmart.bronze.returns            <- CDF ON
# MAGIC        |
# MAGIC        |  Silver reads via:
# MAGIC        |  spark.read.format("delta")
# MAGIC        |      .option("readChangeFeed", "true")
# MAGIC        |      .option("startingVersion", last_version)
# MAGIC        v
# MAGIC   gbmart.silver.*  (next layer)
# MAGIC ```
# MAGIC
# MAGIC **Bronze layer CDF is enabled. Next: run the Silver layer's own CDF
# MAGIC notebook after the Silver full load is complete.**