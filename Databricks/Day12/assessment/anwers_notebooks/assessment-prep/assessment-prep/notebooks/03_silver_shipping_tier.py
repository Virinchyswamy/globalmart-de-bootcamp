# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer — Shipping Tier Data Cleaning & Quality Checks
# MAGIC **GlobalMart Assessment 1 | Tredence DE Advanced**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `gbmart.bronze_as.shipping_tier` (ADLS Gen2 via Autoloader) |
# MAGIC | **Target** | `gbmart.silver_as.shipping_tier` |
# MAGIC | **SCD Type** | SCD1 — lookup table, updated in place |
# MAGIC
# MAGIC ### What this notebook does
# MAGIC | Step | Action |
# MAGIC |---|---|
# MAGIC | 1 | Setup |
# MAGIC | 2 | Read Bronze + inspect |
# MAGIC | 3 | Investigate TierName casing |
# MAGIC | 4 | Investigate IsAvailableOnline mixed values |
# MAGIC | 5 | Transform + write to Silver |
# MAGIC | 6 | Verify |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *

CATALOG       = "gbmart"
BRONZE_TABLE  = "gbmart.bronze_as.shipping_tier"
SILVER_TABLE  = "gbmart.silver_as.shipping_tier"

print(f"Reading from : {BRONZE_TABLE}")
print(f"Writing to   : {SILVER_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Read Bronze + Inspect

# COMMAND ----------

bronze_df = spark.table(BRONZE_TABLE)
print(f"Total records: {bronze_df.count()}")
bronze_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Investigate: TierName Casing
# MAGIC
# MAGIC `TierName` appears in customer-facing order confirmation emails and the checkout page.
# MAGIC Inconsistent casing (`EXPRESS`, `overnight`) would display incorrectly to customers.

# COMMAND ----------

bronze_df.select("ShippingTierID", "TierName").display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:**
# MAGIC - `SHP-002`: `EXPRESS` — all uppercase, should be `Express`
# MAGIC - `SHP-003`: `overnight` — all lowercase, should be `Overnight`
# MAGIC - Others: already in correct Title Case
# MAGIC
# MAGIC **Decision:** Apply `initcap()` to standardize all TierName values.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Investigate: IsAvailableOnline Mixed Values
# MAGIC
# MAGIC `IsAvailableOnline` controls which shipping tiers appear on the checkout page.
# MAGIC Mixed `Yes`/`No` and `1`/`0` values will break any boolean filter downstream.

# COMMAND ----------

bronze_df.select("ShippingTierID", "TierName", "IsAvailableOnline").display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:** Two formats present — `Yes`/`No` (rows 1–3) and `1`/`0` (rows 4–5).
# MAGIC
# MAGIC **Decision:** Cast all to boolean — `Yes`/`1` → `True`, `No`/`0` → `False`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Transform + Write to Silver

# COMMAND ----------

silver_df = bronze_df \
    .withColumn("TierName", initcap(col("TierName"))) \
    .withColumn("IsAvailableOnline",
        when(col("IsAvailableOnline").isin("Yes", "1"), lit(True))
        .when(col("IsAvailableOnline").isin("No", "0"), lit(False))
        .otherwise(lit(None).cast(BooleanType()))
    ) \
    .withColumnRenamed("ShippingTierID",     "shipping_tier_id") \
    .withColumnRenamed("TierName",           "tier_name") \
    .withColumnRenamed("cost_inr",           "cost_inr") \
    .withColumnRenamed("MaxDeliveryDays",    "max_delivery_days") \
    .withColumnRenamed("IsAvailableOnline",  "is_available_online") \
    .withColumn("_silver_updated_at", current_timestamp()) \
    .select("shipping_tier_id", "tier_name", "cost_inr",
            "max_delivery_days", "is_available_online",
            "_source_file", "_silver_updated_at")

silver_df.display()

# COMMAND ----------

silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(SILVER_TABLE)

print(f"Written {spark.table(SILVER_TABLE).count()} rows to {SILVER_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Verify

# COMMAND ----------

df = spark.table(SILVER_TABLE)
df.display()

# Confirm TierName is title case
df.select("tier_name").distinct().display()

# Confirm is_available_online is boolean
df.select("tier_name", "is_available_online").display()