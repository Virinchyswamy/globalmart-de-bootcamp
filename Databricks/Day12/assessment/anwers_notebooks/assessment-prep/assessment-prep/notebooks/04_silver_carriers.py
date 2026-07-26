# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer — Carriers Data Cleaning & Quality Checks
# MAGIC **GlobalMart Assessment 1 | Tredence DE Advanced**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `gbmart.bronze_as.carriers` (ADLS Gen2 via Autoloader) |
# MAGIC | **Target** | `gbmart.silver_as.carriers` |
# MAGIC | **SCD Type** | SCD1 — carrier records updated in place |
# MAGIC
# MAGIC ### What this notebook does
# MAGIC | Step | Action |
# MAGIC |---|---|
# MAGIC | 1 | Setup |
# MAGIC | 2 | Read Bronze + inspect |
# MAGIC | 3 | Investigate CarrierType casing |
# MAGIC | 4 | Investigate ServiceRegion formatting |
# MAGIC | 5 | Transform + write to Silver |
# MAGIC | 6 | Verify |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *

CATALOG       = "gbmart"
BRONZE_TABLE  = "gbmart.bronze_as.carriers"
SILVER_TABLE  = "gbmart.silver_as.carriers"

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
# MAGIC ## Step 3 — Investigate: CarrierType Casing
# MAGIC
# MAGIC `CarrierType` is used to filter eligible carriers by package weight and destination.
# MAGIC Air carriers handle time-sensitive or long-distance shipments; Road and Local handle bulk or nearby deliveries.
# MAGIC If the same type appears as `Air`, `air`, and `AIR`, filters will silently miss records.

# COMMAND ----------

bronze_df.groupBy("CarrierType").count().orderBy("CarrierType").display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:** 5 distinct values for what should be 3 — `Air`, `air`, `AIR`, `Road`, `road`, `Local`.
# MAGIC
# MAGIC **Decision:** Standardize to Title Case using `initcap()` — `Air`, `Road`, `Local`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Investigate: ServiceRegion Formatting
# MAGIC
# MAGIC `ServiceRegion` gates which carrier is assigned based on the delivery address.
# MAGIC `South` and `South India` are the same region — inconsistency means some southern orders
# MAGIC will fail to match any eligible carrier.

# COMMAND ----------

bronze_df.select("CarrierID", "CarrierName", "CarrierType", "ServiceRegion").display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:**
# MAGIC - `CAR-06`: `South` → should be `South India`
# MAGIC - `CAR-07`: `west india` → should be `West India`
# MAGIC - `CAR-10`: `North` → should be `North India`
# MAGIC - Others: already correct
# MAGIC
# MAGIC **Decision:** Map incomplete/lowercase region names to their canonical form.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Transform + Write to Silver

# COMMAND ----------

silver_df = bronze_df \
    .withColumn("CarrierType", initcap(col("CarrierType"))) \
    .withColumn("ServiceRegion",
        when(lower(col("ServiceRegion")) == "south", "South India")
        .when(lower(col("ServiceRegion")) == "west india", "West India")
        .when(lower(col("ServiceRegion")) == "north", "North India")
        .otherwise(col("ServiceRegion"))
    ) \
    .withColumn("IsActive",
        when(col("IsActive") == "Y", lit(True))
        .when(col("IsActive") == "N", lit(False))
        .otherwise(lit(None).cast(BooleanType()))
    ) \
    .withColumnRenamed("CarrierID",     "carrier_id") \
    .withColumnRenamed("CarrierName",   "carrier_name") \
    .withColumnRenamed("CarrierType",   "carrier_type") \
    .withColumnRenamed("ServiceRegion", "service_region") \
    .withColumnRenamed("ContactEmail",  "contact_email") \
    .withColumnRenamed("IsActive",      "is_active") \
    .withColumn("_silver_updated_at", current_timestamp()) \
    .select("carrier_id", "carrier_name", "carrier_type",
            "service_region", "contact_email", "is_active",
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

# Confirm CarrierType standardized
df.groupBy("carrier_type").count().display()

# Confirm ServiceRegion standardized
df.groupBy("service_region").count().orderBy("service_region").display()