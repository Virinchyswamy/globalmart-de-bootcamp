# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer — Dimension Tables
# MAGIC **GlobalMart Assessment 1 | Tredence DE Advanced**
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## What is the Gold Layer?
# MAGIC
# MAGIC The Gold layer contains **business-ready, query-optimised data** modelled as a **Star Schema**.
# MAGIC Everything here is built for analysts, BI tools, and reporting — not for raw debugging.
# MAGIC
# MAGIC In a Star Schema:
# MAGIC - **Dimension tables** describe *who*, *what*, and *where* — the context of each event
# MAGIC - **Fact tables** record *what happened* — the measurable events (shipments, orders, payments)
# MAGIC
# MAGIC This notebook builds the **3 dimension tables** for the Supply Chain domain:
# MAGIC
# MAGIC | Dimension | Source | Grain | Business Role |
# MAGIC |---|---|---|---|
# MAGIC | `dim_supplier` | `silver_as.suppliers` | One row per supplier | Who supplied the goods? |
# MAGIC | `dim_carrier` | `silver_as.carriers` | One row per carrier | Who delivered the shipment? |
# MAGIC | `dim_shipping_tier` | `silver_as.shipping_tier` | One row per tier | What delivery speed was chosen? |
# MAGIC
# MAGIC ### Surrogate Keys
# MAGIC Each dimension gets a **surrogate key** — a system-generated integer that uniquely identifies
# MAGIC a dimension member regardless of changes to the natural key in the source system.
# MAGIC The fact table joins to dimensions using surrogate keys, not natural keys.
# MAGIC
# MAGIC ```
# MAGIC dim_supplier    → supplier_key (integer)
# MAGIC dim_carrier     → carrier_key (integer)
# MAGIC dim_shipping_tier → shipping_tier_key (integer)
# MAGIC ```
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

CATALOG = "gbmart"

# Sources
SILVER_SUPPLIERS     = "gbmart.silver_as.suppliers"
SILVER_CARRIERS      = "gbmart.silver_as.carriers"
SILVER_SHIPPING_TIER = "gbmart.silver_as.shipping_tier"

# Targets
DIM_SUPPLIER      = "gbmart.gold_as.dim_supplier"
DIM_CARRIER       = "gbmart.gold_as.dim_carrier"
DIM_SHIPPING_TIER = "gbmart.gold_as.dim_shipping_tier"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.gold_as")
print("Gold schema ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Dimension 1 — `dim_supplier`
# MAGIC
# MAGIC **Business role:** Every shipment originates from a supplier warehouse.
# MAGIC Analysts need to answer: *Which supplier types generate the most shipments?
# MAGIC Are deactivated suppliers still appearing in new orders?*
# MAGIC
# MAGIC **Columns kept:** Only descriptive attributes that help slice and filter shipments.
# MAGIC Operational columns (`office_address`, `contact_phone`) are excluded from the Gold dim —
# MAGIC they belong in operational systems, not in the analytical layer.
# MAGIC

# COMMAND ----------

suppliers_df = spark.table(SILVER_SUPPLIERS)
print(f"Source rows: {suppliers_df.count()}")
suppliers_df.printSchema()

# COMMAND ----------

# Surrogate key: row_number ordered by supplier_id for deterministic assignment
w = Window.orderBy("supplier_id")

dim_supplier = suppliers_df     .withColumn("supplier_key", row_number().over(w))     .select(
        col("supplier_key"),
        col("supplier_id"),
        col("supplier_name"),
        col("city")         .alias("supplier_city"),
        col("supplier_type"),
        col("is_active"),
        current_timestamp() .alias("_gold_updated_at")
    )

dim_supplier.display()

# COMMAND ----------

dim_supplier.write     .format("delta")     .mode("overwrite")     .option("overwriteSchema", "true")     .saveAsTable(DIM_SUPPLIER)

print(f"Written {spark.table(DIM_SUPPLIER).count()} rows to {DIM_SUPPLIER}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Dimension 2 — `dim_carrier`
# MAGIC
# MAGIC **Business role:** Carrier performance is a key operational metric —
# MAGIC on-time delivery rates, cost efficiency, and regional coverage all vary by carrier.
# MAGIC Analysts need: *Which carrier has the best on-time rate? Which regions are underserved?*
# MAGIC
# MAGIC **Note on orphaned carriers:** The Silver layer flagged 3 shipments referencing `CAR-99`
# MAGIC (a carrier that does not exist in our system). `CAR-99` is deliberately excluded from
# MAGIC `dim_carrier` — it will appear as a NULL `carrier_key` in the fact table, which is
# MAGIC the correct way to signal an unresolvable reference in a Star Schema.
# MAGIC

# COMMAND ----------

carriers_df = spark.table(SILVER_CARRIERS)
print(f"Source rows: {carriers_df.count()}")
carriers_df.printSchema()

# COMMAND ----------

w = Window.orderBy("carrier_id")

dim_carrier = carriers_df     .withColumn("carrier_key", row_number().over(w))     .select(
        col("carrier_key"),
        col("carrier_id"),
        col("carrier_name"),
        col("carrier_type"),
        col("service_region"),
        col("is_active"),
        current_timestamp().alias("_gold_updated_at")
    )

dim_carrier.display()

# COMMAND ----------

dim_carrier.write     .format("delta")     .mode("overwrite")     .option("overwriteSchema", "true")     .saveAsTable(DIM_CARRIER)

print(f"Written {spark.table(DIM_CARRIER).count()} rows to {DIM_CARRIER}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Dimension 3 — `dim_shipping_tier`
# MAGIC
# MAGIC **Business role:** GlobalMart offers multiple delivery speeds at different price points.
# MAGIC The shipping tier dimension lets analysts answer: *Does faster delivery actually cost more?
# MAGIC Which tier is most popular? Are premium tiers available online?*
# MAGIC
# MAGIC This is a **small lookup dimension** (5 rows) but critical for cost and SLA analysis.
# MAGIC

# COMMAND ----------

tier_df = spark.table(SILVER_SHIPPING_TIER)
print(f"Source rows: {tier_df.count()}")
tier_df.display()

# COMMAND ----------

w = Window.orderBy("shipping_tier_id")

dim_shipping_tier = tier_df     .withColumn("shipping_tier_key", row_number().over(w))     .select(
        col("shipping_tier_key"),
        col("shipping_tier_id"),
        col("tier_name"),
        col("cost_inr")             .alias("tier_cost_inr"),
        col("max_delivery_days"),
        col("is_available_online"),
        current_timestamp()         .alias("_gold_updated_at")
    )

dim_shipping_tier.display()

# COMMAND ----------

dim_shipping_tier.write     .format("delta")     .mode("overwrite")     .option("overwriteSchema", "true")     .saveAsTable(DIM_SHIPPING_TIER)

print(f"Written {spark.table(DIM_SHIPPING_TIER).count()} rows to {DIM_SHIPPING_TIER}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Final Verification — All Dimensions
# MAGIC

# COMMAND ----------

dims = {
    "dim_supplier"      : DIM_SUPPLIER,
    "dim_carrier"       : DIM_CARRIER,
    "dim_shipping_tier" : DIM_SHIPPING_TIER
}

for name, table in dims.items():
    df = spark.table(table)
    print(f"{table}: {df.count()} rows")

# COMMAND ----------

# Confirm surrogate keys are unique in each dim
for name, table in dims.items():
    df = spark.table(table)
    key_col = [c for c in df.columns if c.endswith("_key")][0]
    total = df.count()
    unique = df.select(key_col).distinct().count()
    print(f"{name}.{key_col}: {total} total, {unique} unique — {'OK' if total == unique else 'DUPLICATE KEYS FOUND'}") 