# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Incremental — Customers (SCD2 via CDF + MERGE)
# MAGIC **GlobalMart | Tredence DE Advanced Training | Day 12 Pattern**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.customers` — CDF enabled |
# MAGIC | **Target** | `harsh_kumar01_npmentorskool_onmicrosoft_com.silver.customers` |
# MAGIC | **SCD Type** | SCD2 — an attribute change (e.g. `email`) creates a new version, old version closed out |
# MAGIC
# MAGIC Same 6-step flow as `10_products_incremental_scd2_merge.ipynb`, applied
# MAGIC to `customers`. Change detection here keys off `email` (the attribute
# MAGIC that actually changes in our scenario), the same way `products` keyed off
# MAGIC `discounted_price_inr`.
# MAGIC
# MAGIC | Step | What it does |
# MAGIC |---|---|
# MAGIC | 1 | Read all data — current full state of Bronze |
# MAGIC | 2 | Show what changed in Bronze — inspect Delta history |
# MAGIC | 3 | Take **only** the changes — CDF read |
# MAGIC | 4 | Process those rows — same cleaning logic as the full-load notebook, scoped down |
# MAGIC | 5 | Load into Silver — SCD2 `MERGE` (close out old version) + insert (new version / new customer) |
# MAGIC | 6 | Verify |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Read All Data (Current Full State of Bronze)

# COMMAND ----------

from pyspark.sql.functions import *
from delta.tables import DeltaTable

CATALOG      = "harsh_kumar01_npmentorskool_onmicrosoft_com"
BRONZE_TABLE = "harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.customers"
SILVER_TABLE = "harsh_kumar01_npmentorskool_onmicrosoft_com.silver.customers"

bronze_df = spark.table(BRONZE_TABLE)
print(f"Total rows currently in Bronze: {bronze_df.count():,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Show What Changed in Bronze
# MAGIC Find the version right before the incremental file landed — CDF will
# MAGIC read everything **after** it.
# MAGIC
# MAGIC > If `customer_consent_*.csv` also landed in this same source folder, its
# MAGIC > rows will show up in Bronze history too (and in the CDF read below) —
# MAGIC > that file is a different entity, not part of this customer-attribute
# MAGIC > SCD2 flow. Filter it out in Step 3/4 if needed (e.g. by checking which
# MAGIC > expected customer columns are non-null), rather than processing it here.

# COMMAND ----------

spark.sql(f"DESCRIBE HISTORY {BRONZE_TABLE}") \
    .select("version", "timestamp", "operation", "operationMetrics") \
    .orderBy("version") \
    .display()

# COMMAND ----------

LAST_PROCESSED_VERSION = 3   # <-- set this from the history output above

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Take Only the Changes (CDF, Not a Full Re-Scan)

# COMMAND ----------

cdf_changes_df = (
    spark.read.format("delta")
        .option("readChangeFeed", "true")
        .option("startingVersion", LAST_PROCESSED_VERSION + 1)
        .table(BRONZE_TABLE)
        .filter("_change_type != 'update_preimage'")
)

print(f"Changed rows via CDF: {cdf_changes_df.count():,}")
cdf_changes_df.select("CustomerID", "Email", "_change_type", "_commit_version").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Process Only These Changed Rows
# MAGIC Same cleaning/transform logic as the full-load notebook (`full_name`,
# MAGIC `age`, `customer_tenure_days`), scoped to just the CDF result. If
# MAGIC `customer_consent` rows are present (per the note in Step 2), filter them
# MAGIC out here by requiring the core customer fields to be non-null.

# COMMAND ----------

processed_df = cdf_changes_df \
    .filter(col("CustomerID").isNotNull() & col("Email").isNotNull())  \
    .withColumn("DateOfBirth", to_date(col("DateOfBirth"), "yyyy-MM-dd")) \
    .withColumn("RegistrationDate", to_date(col("RegistrationDate"), "yyyy-MM-dd")) \
    .withColumn("FirstName", trim(col("FirstName"))) \
    .withColumn("LastName", trim(col("LastName"))) \
    .withColumn("full_name", concat_ws(" ", col("FirstName"), col("LastName"))) \
    .withColumn("age", floor(datediff(current_date(), col("DateOfBirth")) / 365.25).cast("int")) \
    .withColumn("customer_tenure_days", datediff(current_date(), col("RegistrationDate")).cast("int")) \
    .withColumnRenamed("CustomerID", "customer_id") \
    .withColumnRenamed("Email", "email") \
    .withColumnRenamed("PhoneNumber", "phone_number") \
    .withColumnRenamed("DateOfBirth", "date_of_birth") \
    .withColumnRenamed("RegistrationDate", "registration_date") \
    .withColumnRenamed("PreferredPaymentMethodID", "preferred_payment_method_id") \
    .select(
        "customer_id", "full_name", "email", "phone_number",
        "date_of_birth", "age", "registration_date", "customer_tenure_days",
        "preferred_payment_method_id"
    )

processed_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Load into Silver: SCD2 (Close Old Version + Insert New)
# MAGIC
# MAGIC **5a.** Close out the old version — for any `customer_id` already
# MAGIC `is_current = true` in Silver where the incoming `email` differs, flip
# MAGIC `is_current` to `false` and stamp `effective_end_date`.
# MAGIC
# MAGIC **5b.** Insert the new version — every row in `processed_df` becomes a
# MAGIC fresh Silver row with a new `customer_sk`. Covers both a changed customer
# MAGIC (new email version) and a brand-new customer (5a simply won't match it).

# COMMAND ----------

# 5a — close out old versions where email actually changed
silver_table = DeltaTable.forName(spark, SILVER_TABLE)

(silver_table.alias("tgt")
    .merge(
        processed_df.alias("src"),
        "tgt.customer_id = src.customer_id AND tgt.is_current = true "
        "AND tgt.email <> src.email"
    )
    .whenMatchedUpdate(set={
        "is_current": "false",
        "effective_end_date": "current_date()"
    })
    .execute()
)

print("Step 5a complete — old versions closed out where email changed")

# COMMAND ----------

spark.table(SILVER_TABLE).printSchema()

# COMMAND ----------

# 5b — insert new versions (email changes) + brand-new customers
new_versions_df = processed_df \
    .withColumn("phone_number", col("phone_number").cast("string")) \
    .withColumn("effective_start_date", current_date()) \
    .withColumn("effective_end_date", lit(None).cast("date")) \
    .withColumn("is_current", lit(True)) \
    .withColumn(
        "customer_sk",
        sha2(
            concat_ws("|", col("customer_id"), col("effective_start_date").cast("string")),
            256
        )
    ) \
    .withColumn("_silver_updated_at", current_timestamp()) \
    .select(
        "customer_sk",
        "customer_id",
        "full_name",
        "email",
        "phone_number",
        "date_of_birth",
        "age",
        "registration_date",
        "customer_tenure_days",
        "preferred_payment_method_id",
        "is_current",
        "effective_start_date",
        "effective_end_date",
        "_silver_updated_at"
    )

new_versions_df.write \
    .format("delta") \
    .option("mergeSchema", "true") \
    .mode("append") \
    .saveAsTable(SILVER_TABLE)

print(f"Step 5b complete — {new_versions_df.count()} new version row(s) inserted")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Verify
# MAGIC Each changed `customer_id` should now show **2 rows** — old version
# MAGIC (`is_current=false`, `effective_end_date` set) and new version
# MAGIC (`is_current=true`). Brand-new customers show a single `is_current=true`
# MAGIC row.

# COMMAND ----------

df = spark.table(SILVER_TABLE)
print(f"silver.customers rows : {df.count():,}")

changed_ids = [row.customer_id for row in processed_df.select("customer_id").distinct().collect()]
df.filter(col("customer_id").isin(changed_ids)) \
  .select("customer_sk", "customer_id", "email", "is_current",
          "effective_start_date", "effective_end_date") \
  .orderBy("customer_id", "effective_start_date") \
  .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reset (if needed)

# COMMAND ----------

# spark.sql(f"DELETE FROM {SILVER_TABLE} WHERE effective_start_date = current_date()")
# print("Incremental rows removed — re-run the full-load notebook to restore baseline")