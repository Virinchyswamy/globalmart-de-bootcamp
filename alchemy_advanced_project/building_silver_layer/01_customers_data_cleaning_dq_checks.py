# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer — Customer Data Cleaning & Quality Checks
# MAGIC **GlobalMart | Tredence DE Advanced Training**
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Source** | `gbmart.bronze.customers` |
# MAGIC | **Target** | `gbmart.silver.customers` |
# MAGIC | **Quarantine** | `gbmart.silver.customers_quarantine` |
# MAGIC
# MAGIC ### What this notebook does
# MAGIC | Step | Action |
# MAGIC |---|---|
# MAGIC | 1 | Read full Bronze table |
# MAGIC | 2 | First DQ scan — observe all issues |
# MAGIC | 3 | Investigate + fix emails (spaces, apostrophe) |
# MAGIC | 4 | Investigate + fix phone numbers (country code) |
# MAGIC | 5 | Investigate under-18 registrations — quarantine decision |
# MAGIC | 6 | Final DQ check on fully remediated data — split clean vs quarantine |
# MAGIC | 7 | Deduplicate by CustomerID |
# MAGIC | 8 | Transform — cast types, derive columns |
# MAGIC | 9 | Add SCD2 columns |
# MAGIC | 10 | Write to `silver.customers` + `silver.customers_quarantine` |
# MAGIC | 11 | Verify |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import DateType
from pyspark.sql.window import Window

# PhoneNumber is stored as BIGINT in bronze.
# Disabling ANSI mode prevents Spark from forcing the formatted string back to BIGINT.
spark.conf.set("spark.sql.ansi.enabled", "false")

CATALOG          = "gbmart"
BRONZE_TABLE     = "gbmart.bronze.customers"
SILVER_TABLE     = "gbmart.silver.customers"
QUARANTINE_TABLE = "gbmart.silver.customers_quarantine"

print(f"Reading from : {BRONZE_TABLE}")
print(f"Writing to   : {SILVER_TABLE}")
print(f"Quarantine   : {QUARANTINE_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Read Raw Data from Bronze
# MAGIC Load all customer records as-is. No changes at this step — just reading.

# COMMAND ----------

bronze_df = spark.table(BRONZE_TABLE)
print(f"Total records in Bronze: {bronze_df.count():,}")
bronze_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — First DQ Scan
# MAGIC Before fixing anything, scan all rows and tag each one with its first failing rule.
# MAGIC This gives us a complete picture of what needs to be fixed.

# COMMAND ----------

EMAIL_REGEX = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'

dq_scan_df = bronze_df \
    .withColumn("_dob_temp",    to_date(col("DateOfBirth"),      "yyyy-MM-dd")) \
    .withColumn("_reg_temp",    to_date(col("RegistrationDate"), "yyyy-MM-dd")) \
    .withColumn("_age_at_reg",  floor(datediff(col("_reg_temp"), col("_dob_temp")) / 365.25)) \
    .withColumn("_dq_issue",
        when(col("CustomerID").isNull(),                                lit("NULL_CUSTOMER_ID"))
        .when(col("FirstName").isNull() | (trim(col("FirstName")) == ""), lit("NULL_FIRST_NAME"))
        .when(col("LastName").isNull()  | (trim(col("LastName"))  == ""), lit("NULL_LAST_NAME"))
        .when(col("Email").isNull(),                                    lit("NULL_EMAIL"))
        .when(~col("Email").rlike(EMAIL_REGEX),                         lit("INVALID_EMAIL_FORMAT"))
        .when(col("DateOfBirth").isNull(),                              lit("NULL_DATE_OF_BIRTH"))
        .when(col("RegistrationDate").isNull(),                         lit("NULL_REGISTRATION_DATE"))
        .when(col("_age_at_reg") < 18,                                  lit("REGISTERED_UNDER_18"))
        .otherwise(lit(None))
    )

print("=== DQ Issues Found ===")
dq_scan_df.groupBy("_dq_issue").count().orderBy("count", ascending=False).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Investigate: Invalid Emails
# MAGIC Before writing any fix, look at the actual bad emails to understand the pattern.

# COMMAND ----------

dq_scan_df.filter(col("_dq_issue") == "INVALID_EMAIL_FORMAT") \
    .select("CustomerID", "Email") \
    .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Root Cause & Fix: Invalid Emails
# MAGIC
# MAGIC ### Pattern 1 — Accidental Space in email
# MAGIC
# MAGIC | Customer | Invalid Email |
# MAGIC |---|---|
# MAGIC | CUST-09525 | `swaminathaninaaya 482@outlook.com` |
# MAGIC | CUST-14348 | `inaaya _739@yahoo.com` |
# MAGIC
# MAGIC **Why it happens:** Mobile keyboard autocorrect inserts a space after a long name, splitting the local part of the email.  
# MAGIC **Fix:** Remove all spaces → `swaminathaninaaya482@outlook.com` ✓
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Pattern 2 — Apostrophe (d') in name-based email
# MAGIC
# MAGIC | Customer | Invalid Email |
# MAGIC |---|---|
# MAGIC | CUST-07081 | `taran.d'alia307@hotmail.com` |
# MAGIC
# MAGIC **Why it happens:** Surnames like D'Souza, D'Silva, D'Cruz contain `d'` as a prefix.  
# MAGIC Customers include it when creating their email — most providers strip it, but the form accepted it.  
# MAGIC **Fix:** Remove the `d'` pattern → `taran.alia307@hotmail.com` ✓
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Business Decision — Fix, don't quarantine
# MAGIC Both are recoverable errors. Quarantining them means losing real customers.  
# MAGIC After applying both fixes, we re-validate — any remaining invalids go to quarantine.

# COMMAND ----------

# Apply email fixes
remediated_df = bronze_df.withColumn(
    "Email",
    regexp_replace(
        regexp_replace(
            trim(lower(col("Email"))),
            " ", ""                       # Pattern 1: remove spaces
        ),
        "d['\u2019\u2018]", ""             # Pattern 2: d + any apostrophe variant
    )
)

# Re-validate — should show 0 rows
EMAIL_REGEX = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
still_invalid = remediated_df \
    .filter(~col("Email").rlike(EMAIL_REGEX) & col("Email").isNotNull()) \
    .count()

print(f"Remaining invalid emails after fix: {still_invalid}")
# Expected: 0

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Investigate: Phone Number Format

# COMMAND ----------

# Check phone number length distribution
remediated_df \
    .withColumn("_phone_len", length(col("PhoneNumber").cast("string"))) \
    .groupBy("_phone_len").count() \
    .orderBy("_phone_len") \
    .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7 — Root Cause & Fix: Phone Number Format
# MAGIC
# MAGIC ### What we found
# MAGIC All phone numbers are 12 digits — every record has the `91` India country code prepended.
# MAGIC
# MAGIC | CustomerID | PhoneNumber (raw) | Expected |
# MAGIC |---|---|---|
# MAGIC | CUST-xxxxx | `917584314890` | `+91-7584314890` |
# MAGIC
# MAGIC ### Why it happened
# MAGIC GlobalMart's registration form auto-appended the `+91` country code but stored it **without the `+`**,  
# MAGIC resulting in `91XXXXXXXXXX` (12 digits) instead of the standard `+91-XXXXXXXXXX` format.
# MAGIC
# MAGIC ### Fix
# MAGIC Strip the raw `91` prefix and reformat into standard international format: `+91-XXXXXXXXXX`  
# MAGIC `917584314890` → `+91-7584314890`
# MAGIC
# MAGIC > **Note:** PhoneNumber is stored as BIGINT in Bronze. We cast to STRING first before formatting.

# COMMAND ----------

# Apply phone fix — cast to string first, then reformat
remediated_df = remediated_df \
    .withColumn("PhoneNumber", col("PhoneNumber").cast("string")) \
    .withColumn(
        "PhoneNumber",
        when(
            (length(col("PhoneNumber")) == 12) & col("PhoneNumber").startswith("91"),
            concat(lit("+91-"), col("PhoneNumber").substr(3, 10))
        ).otherwise(col("PhoneNumber"))
    )

# Verify
remediated_df.select("CustomerID", "PhoneNumber").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8 — Investigate: REGISTERED_UNDER_18
# MAGIC The DQ scan flagged 77 customers whose RegistrationDate is less than 18 years after their DateOfBirth.  
# MAGIC Before deciding, look at the actual data.

# COMMAND ----------

remediated_df \
    .withColumn("_dob",      to_date(col("DateOfBirth"),      "yyyy-MM-dd")) \
    .withColumn("_reg",      to_date(col("RegistrationDate"), "yyyy-MM-dd")) \
    .withColumn("_age_at_reg", floor(datediff(col("_reg"), col("_dob")) / 365.25).cast("int")) \
    .filter(col("_age_at_reg") < 18) \
    .select("CustomerID", "DateOfBirth", "RegistrationDate", "_age_at_reg") \
    .orderBy("_age_at_reg") \
    .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8 — Root Cause & Decision: REGISTERED_UNDER_18
# MAGIC
# MAGIC ### Business Rule
# MAGIC GlobalMart requires **18+** to register — legal compliance, payment authorization, and Terms of Service.
# MAGIC
# MAGIC ### Why did these 77 get in?
# MAGIC The registration form had **no age validation** at the time. Source system gap — not a data entry mistake.
# MAGIC
# MAGIC ### Why we can't fix it (unlike email spaces)
# MAGIC Email spaces — we knew the correct email, just cleaned the format.  
# MAGIC Age — we **cannot assume** the DOB is wrong. The customer may genuinely have been under 18.
# MAGIC
# MAGIC ### Decision → Quarantine
# MAGIC These 77 records go to quarantine with reason `REGISTERED_UNDER_18`.  
# MAGIC Business team will decide: verify DOB, deactivate account, or flag for legal review.
# MAGIC
# MAGIC **Silver layer will not include these records.**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 9 — Final DQ Check + Split
# MAGIC All remediations are applied. Now run the full DQ check on `remediated_df` and split into clean + quarantine.

# COMMAND ----------

EMAIL_REGEX = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'

dq_df = remediated_df \
    .withColumn("_dob_temp",   to_date(col("DateOfBirth"),      "yyyy-MM-dd")) \
    .withColumn("_reg_temp",   to_date(col("RegistrationDate"), "yyyy-MM-dd")) \
    .withColumn("_age_at_reg", floor(datediff(col("_reg_temp"), col("_dob_temp")) / 365.25)) \
    .withColumn("_dq_issue",
        when(col("CustomerID").isNull(),                                lit("NULL_CUSTOMER_ID"))
        .when(col("FirstName").isNull() | (trim(col("FirstName")) == ""), lit("NULL_FIRST_NAME"))
        .when(col("LastName").isNull()  | (trim(col("LastName"))  == ""), lit("NULL_LAST_NAME"))
        .when(col("Email").isNull(),                                    lit("NULL_EMAIL"))
        .when(~col("Email").rlike(EMAIL_REGEX),                         lit("INVALID_EMAIL_FORMAT"))
        .when(col("DateOfBirth").isNull(),                              lit("NULL_DATE_OF_BIRTH"))
        .when(col("RegistrationDate").isNull(),                         lit("NULL_REGISTRATION_DATE"))
        .when(col("_age_at_reg") < 18,                                  lit("REGISTERED_UNDER_18"))
        .otherwise(lit(None))
    )

clean_df      = dq_df.filter(col("_dq_issue").isNull()) \
                     .drop("_dq_issue", "_dob_temp", "_reg_temp", "_age_at_reg")
quarantine_df = dq_df.filter(col("_dq_issue").isNotNull()) \
                     .drop("_dob_temp", "_reg_temp", "_age_at_reg")

print(f"Total rows  : {bronze_df.count():,}")
print(f"Clean rows  : {clean_df.count():,}")
print(f"Quarantine  : {quarantine_df.count():,}")

# COMMAND ----------

# Quarantine breakdown
quarantine_df.groupBy("_dq_issue").count().orderBy("count", ascending=False).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 10 — Deduplicate by CustomerID
# MAGIC Bronze is append-only — the same customer can appear across multiple files.  
# MAGIC Keep the latest record per CustomerID based on `_ingested_at`.

# COMMAND ----------

window_latest = Window.partitionBy("CustomerID").orderBy(col("_ingested_at").desc())

deduped_df = (
    clean_df
    .withColumn("_row_num", row_number().over(window_latest))
    .filter(col("_row_num") == 1)
    .drop("_row_num")
)

print(f"After dedup : {deduped_df.count():,} unique customers")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 11 — Transform
# MAGIC
# MAGIC | Column | Transformation |
# MAGIC |---|---|
# MAGIC | `DateOfBirth` | Cast string → DateType |
# MAGIC | `RegistrationDate` | Cast string → DateType |
# MAGIC | `FirstName` / `LastName` | Trim whitespace |
# MAGIC | `full_name` | Derived: `FirstName + ' ' + LastName` |
# MAGIC | `age` | Derived: `floor(datediff(today, DOB) / 365.25)` |
# MAGIC | `customer_tenure_days` | Derived: `datediff(today, RegistrationDate)` |

# COMMAND ----------

# MAGIC %md
# MAGIC ### Why `customer_tenure_days`?
# MAGIC - This is a pre-computed business metric — how many days this customer has been with GlobalMart since registration.
# MAGIC  
# MAGIC - Gold layer and BI tools will constantly need customer segmentation like:
# MAGIC     - tenure < 90 days    → New Customer
# MAGIC     - tenure 90–365 days  → Regular Customer
# MAGIC     - tenure > 365 days   → Loyal Customer
# MAGIC
# MAGIC
# MAGIC - If we skip this in Silver, every Gold query and report has to repeat `datediff(current_date, registration_date)` — duplicated logic across fact tables, dashboards, and Genie queries.
# MAGIC
# MAGIC **Rule:** If multiple Gold tables need the same derived value, compute it once in Silver.

# COMMAND ----------

transformed_df = (
    deduped_df
    .withColumn("DateOfBirth",      to_date(col("DateOfBirth"),      "yyyy-MM-dd"))
    .withColumn("RegistrationDate", to_date(col("RegistrationDate"), "yyyy-MM-dd"))
    .withColumn("FirstName",        trim(col("FirstName")))
    .withColumn("LastName",         trim(col("LastName")))
    .withColumn("full_name",            concat_ws(" ", col("FirstName"), col("LastName")))
    .withColumn("age",                  floor(datediff(current_date(), col("DateOfBirth")) / 365.25).cast("int"))
    .withColumn("customer_tenure_days", datediff(current_date(), col("RegistrationDate")).cast("int"))

    # Standardise to snake_case
    .withColumnRenamed("CustomerID",               "customer_id")
    .withColumnRenamed("FirstName",                "first_name")
    .withColumnRenamed("LastName",                 "last_name")
    .withColumnRenamed("Email",                    "email")
    .withColumnRenamed("PhoneNumber",              "phone_number")
    .withColumnRenamed("DateOfBirth",              "date_of_birth")
    .withColumnRenamed("RegistrationDate",         "registration_date")
    .withColumnRenamed("PreferredPaymentMethodID", "preferred_payment_method_id")
)

transformed_df.select(
    "customer_id", "full_name", "email", "phone_number",
    "date_of_birth", "age", "registration_date", "customer_tenure_days"
).display()


# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 12 — Add SCD2 Columns
# MAGIC
# MAGIC Initial load — every customer starts as `is_current = true`.  
# MAGIC In Phase 2 (incremental), when Email or PhoneNumber changes, the old row is expired and a new version is inserted.
# MAGIC
# MAGIC | Column | Value (initial load) |
# MAGIC |---|---|
# MAGIC | `customer_sk` | `sha2(CustomerID + effective_start_date, 256)` — stable surrogate key |
# MAGIC | `is_current` | `true` |
# MAGIC | `effective_start_date` | `RegistrationDate` |
# MAGIC | `effective_end_date` | `null` |

# COMMAND ----------

silver_df = (
    transformed_df
    .withColumn("effective_start_date", col("registration_date"))
    .withColumn("effective_end_date",   lit(None).cast(DateType()))
    .withColumn("is_current",           lit(True))
    .withColumn(
        "customer_sk",
        sha2(concat_ws("|", col("customer_id"), col("effective_start_date").cast("string")), 256)
    )
    .withColumn("_silver_updated_at", current_timestamp())
    .select(
        "customer_sk",
        "customer_id",
        "first_name", "last_name", "full_name",
        "email", "phone_number",
        "date_of_birth", "age",
        "registration_date", "customer_tenure_days",
        "preferred_payment_method_id",
        "is_current", "effective_start_date", "effective_end_date",
        "_source_file", "_silver_updated_at"
    )
)

print(f"Silver rows : {silver_df.count():,}")
silver_df.display()


# COMMAND ----------

# MAGIC %md
# MAGIC ### Why create `customer_sk` in Silver?
# MAGIC
# MAGIC | Reason | Explanation |
# MAGIC |---|---|
# MAGIC | **SCD2 support** | When email/phone changes, a new row with a new `customer_sk` is inserted. `fact_orders` links to the key active at order time — preserving history. |
# MAGIC | **Decouple Gold from source** | Gold tables join on `customer_sk`, not `CustomerID`. Source system changes don't break downstream. |
# MAGIC | **Generate once, use everywhere** | All Gold tables read `customer_sk` directly from Silver — no duplication of key generation logic. |
# MAGIC
# MAGIC > **Rule:** Natural key (`CustomerID`) comes from the source. Surrogate key (`customer_sk`) is owned by the warehouse — created once in Silver, used everywhere in Gold.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 13 — Write to Silver Layer

# COMMAND ----------

# Create schema if not exists
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.silver")
print("Schema 'silver' ready.")

# COMMAND ----------

# Write clean records to silver.customers
silver_df.write \
    .format("delta") \
    .mode("append") \
    .saveAsTable(SILVER_TABLE)

print(f"Written to {SILVER_TABLE}: {spark.table(SILVER_TABLE).count():,} rows")

# COMMAND ----------

# Write quarantine records
quarantine_df \
    .withColumn("_quarantine_ts", current_timestamp()) \
    .write \
    .format("delta") \
    .mode("append") \
    .option("overwriteSchema", "true") \
    .saveAsTable(QUARANTINE_TABLE)

print(f"Quarantine  : {spark.table(QUARANTINE_TABLE).count():,} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 14 — Verify

# COMMAND ----------

df = spark.table(SILVER_TABLE)

print(f"silver.customers rows : {df.count():,}")
print(f"Columns               : {df.columns}")

# SCD2 check — all initial records should be is_current = true
df.groupBy("is_current").count().display()

# Age sanity check
df.select(
    min("age").alias("min_age"),
    max("age").alias("max_age"),
    avg("age").alias("avg_age")
).display()

# Phone format check
df.select("customer_id", "phone_number").limit(5).display()

# COMMAND ----------

# Schema + Delta history
df.printSchema()
spark.sql(f"DESCRIBE HISTORY {SILVER_TABLE}") \
    .select("version", "timestamp", "operation") \
    .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reset (if needed)

# COMMAND ----------

# spark.sql(f"DROP TABLE IF EXISTS {SILVER_TABLE}")
# spark.sql(f"DROP TABLE IF EXISTS {QUARANTINE_TABLE}")
# print("Reset complete")