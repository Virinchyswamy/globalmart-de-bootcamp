# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer — Suppliers Data Cleaning & Quality Checks
# MAGIC **GlobalMart Assessment 1 | Tredence DE Advanced**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `gbmart.bronze_as.suppliers` (ADLS Gen2 via Autoloader) |
# MAGIC | **Target** | `gbmart.silver_as.suppliers` |
# MAGIC | **SCD Type** | SCD1 — supplier records are updated in place |
# MAGIC
# MAGIC ### What this notebook does
# MAGIC | Step | Action |
# MAGIC |---|---|
# MAGIC | 1 | Setup |
# MAGIC | 2 | Read Bronze + inspect schema |
# MAGIC | 3 | Investigate email format issues |
# MAGIC | 4 | Investigate city alias inconsistency |
# MAGIC | 5 | Investigate ContactPhone format |
# MAGIC | 6 | Investigate IsActive mixed values |
# MAGIC | 7 | Investigate OfficeAddress — embedded data + newline |
# MAGIC | 8 | DQ scan summary |
# MAGIC | 9 | Transform + write to Silver |
# MAGIC | 10 | Verify |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *

CATALOG       = "gbmart"
BRONZE_TABLE  = "gbmart.bronze_as.suppliers"
SILVER_TABLE  = "gbmart.silver_as.suppliers"

print(f"Reading from : {BRONZE_TABLE}")
print(f"Writing to   : {SILVER_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Read Bronze + Inspect Schema

# COMMAND ----------

bronze_df = spark.table(BRONZE_TABLE)
print(f"Total records: {bronze_df.count()}")
bronze_df.printSchema()

# COMMAND ----------

bronze_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Investigate: Email Format Issues
# MAGIC
# MAGIC The procurement team sends purchase orders to supplier emails — an invalid address means the PO never arrives and the order is delayed.
# MAGIC Two rows have issues: one is missing the `@` symbol entirely, one is blank.

# COMMAND ----------

email_check = bronze_df.withColumn("_email_issue",
    when(col("SupplierEmail").isNull() | (col("SupplierEmail") == ""), "MISSING_EMAIL")
    .when(~col("SupplierEmail").contains("@"), "INVALID_FORMAT")
    .otherwise(None)
)

email_check.filter(col("_email_issue").isNotNull()) \
    .select("SupplierID", "SupplierName", "SupplierEmail", "_email_issue").display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:**
# MAGIC - `SUP-03`: `supportthompsonent.com` — missing `@`, should be `support@thompsonent.com`
# MAGIC - `SUP-06`: blank email
# MAGIC
# MAGIC **Decision:** Fix `SUP-03` (correct value is derivable). Leave `SUP-06` as NULL — we cannot guess the email.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Investigate: City Alias Inconsistency
# MAGIC
# MAGIC The city field feeds into the carrier-routing logic — the system assigns carriers by city.
# MAGIC If the same city appears under two different names, some shipments will fail to match a carrier.

# COMMAND ----------

bronze_df.groupBy("City").count().orderBy("City").display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:** `Bangalore` (SUP-03) and `Bengaluru` (SUP-10) refer to the same city.
# MAGIC The canonical name used by India Post and most logistics APIs is `Bengaluru`.
# MAGIC
# MAGIC **Decision:** Standardize all `Bangalore` → `Bengaluru`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Investigate: ContactPhone Format
# MAGIC
# MAGIC The operations team uses these numbers for shipment follow-up calls.
# MAGIC Non-standard formats cannot be auto-dialed from the logistics system.

# COMMAND ----------

bronze_df.select("SupplierID", "ContactPhone") \
    .withColumn("_phone_len",
        length(regexp_replace(col("ContactPhone"), r"[^0-9]", ""))) \
    .display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:**
# MAGIC - `SUP-01`, `SUP-08`: NULL — acceptable, ContactPhone is optional
# MAGIC - `SUP-04`: `+91 123 456` — only 7 digits after country code, clearly invalid
# MAGIC - All others: valid `+91-XXXXXXXXXX` format with spaces instead of hyphens in some
# MAGIC
# MAGIC **Decision:** Normalize separators to hyphen. Flag SUP-04 as invalid (cannot guess correct number).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Investigate: IsActive Mixed Values
# MAGIC
# MAGIC `IsActive` controls whether a supplier is eligible for new purchase orders.
# MAGIC Mixed formats (`Y`/`N` and `True`/`False`) will cause filter logic to break downstream.

# COMMAND ----------

bronze_df.groupBy("IsActive").count().display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:** 4 distinct values — `Y`, `N`, `True`, `False`. Must be cast to a uniform boolean.
# MAGIC
# MAGIC **Decision:** `Y` / `True` → `True`, `N` / `False` → `False`.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7 — Investigate: OfficeAddress Embedded Data
# MAGIC
# MAGIC The logistics team uses `OfficeAddress` for physical supplier inspections.
# MAGIC Two types of issues are present:
# MAGIC - **Embedded city + pincode** at the end of the address string (e.g. `45, BKC Complex, Mumbai 400051`)
# MAGIC - **Embedded newline** splitting the street and city across two lines (SUP-05)
# MAGIC
# MAGIC Both pollute the street address with data that already exists in the `City` column.

# COMMAND ----------

bronze_df.select("SupplierID", "OfficeAddress", "City").display()

# COMMAND ----------

# Check how many rows have embedded pincode (6-digit number at end)
bronze_df.withColumn("_has_pincode",
    col("OfficeAddress").rlike(r"\d{6}\s*$")
).groupBy("_has_pincode").count().display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Finding:**
# MAGIC - 6 rows have a 6-digit pincode embedded at the end of the address
# MAGIC - 1 row (SUP-05) has an actual newline character inside the field
# MAGIC
# MAGIC **Decision:** Strip everything from the embedded newline onwards, then strip the trailing `, City PINCODE` pattern.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8 — DQ Scan Summary

# COMMAND ----------

dq_scan = bronze_df.withColumn("_dq_flag",
    when(col("SupplierEmail").isNull() | (col("SupplierEmail") == ""), "MISSING_EMAIL")
    .when(~col("SupplierEmail").contains("@"), "INVALID_EMAIL_FORMAT")
    .when(col("SupplierID").isNull(), "MISSING_SUPPLIER_ID")
    .when(~col("ContactPhone").rlike(r"^\+91[- ]\d{3}[- ]\d{3}$") & col("ContactPhone").isNotNull()
         & ~col("ContactPhone").rlike(r"^\+91-\d{10}$"), "INVALID_PHONE")
    .otherwise(None)
)

print("DQ Summary:")
dq_scan.groupBy("_dq_flag").count().display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 9 — Transform + Write to Silver

# COMMAND ----------

silver_df = bronze_df \
    .withColumn("SupplierEmail",
        when(col("SupplierID") == "SUP-03", "support@thompsonent.com")
        .when(col("SupplierEmail") == "", None)
        .otherwise(col("SupplierEmail"))
    ) \
    .withColumn("City",
        when(col("City") == "Bangalore", "Bengaluru")
        .otherwise(col("City"))
    ) \
    .withColumn("IsActive",
        when(col("IsActive").isin("Y", "True"), lit(True))
        .when(col("IsActive").isin("N", "False"), lit(False))
        .otherwise(lit(None).cast(BooleanType()))
    ) \
    .withColumn("OfficeAddress",
        # Remove newline and everything after it
        regexp_replace(col("OfficeAddress"), r"\n.*", "")
    ) \
    .withColumn("OfficeAddress",
        # Remove trailing ", City PINCODE" pattern
        trim(regexp_replace(col("OfficeAddress"), r",\s*[A-Za-z\s]+\d{6}\s*$", ""))
    ) \
    .withColumnRenamed("SupplierID",    "supplier_id") \
    .withColumnRenamed("SupplierName",  "supplier_name") \
    .withColumnRenamed("SupplierEmail", "supplier_email") \
    .withColumnRenamed("City",          "city") \
    .withColumnRenamed("ContactPhone",  "contact_phone") \
    .withColumnRenamed("SupplierType",  "supplier_type") \
    .withColumnRenamed("IsActive",      "is_active") \
    .withColumnRenamed("OfficeAddress", "office_address") \
    .withColumn("_silver_updated_at", current_timestamp()) \
    .select("supplier_id", "supplier_name", "supplier_email", "city",
            "contact_phone", "supplier_type", "is_active", "office_address",
            "_source_file", "_silver_updated_at")

silver_df.display()

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.silver_as")

silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(SILVER_TABLE)

print(f"Written {spark.table(SILVER_TABLE).count()} rows to {SILVER_TABLE}")

# COMMAND ----------

spark.sql(f"ALTER TABLE {SILVER_TABLE} ADD CONSTRAINT pk_supplier_id NOT NULL (supplier_id)")
print("Constraint added: supplier_id NOT NULL")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 10 — Verify

# COMMAND ----------

df = spark.table(SILVER_TABLE)
print(f"Row count: {df.count()}")
df.printSchema()
df.display()

# COMMAND ----------

# Confirm city alias resolved
df.groupBy("city").count().orderBy("city").display()

# Confirm IsActive is boolean
df.groupBy("is_active").count().display()

# Confirm OfficeAddress no longer has embedded pincodes
df.withColumn("_has_pincode", col("office_address").rlike(r"\d{6}")).groupBy("_has_pincode").count().display()