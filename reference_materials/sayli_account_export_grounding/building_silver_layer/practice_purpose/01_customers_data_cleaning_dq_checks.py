# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer — Customers
# MAGIC ## What are we doing here?
# MAGIC We are taking raw customer data from the Bronze layer, fixing data issues, 
# MAGIC adding useful columns, and saving clean data to the Silver layer.
# MAGIC
# MAGIC Any bad records that cannot be fixed will go to a separate Quarantine table 
# MAGIC so nothing is lost.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Setup
# MAGIC Define which tables we are reading from and writing to.
# MAGIC

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import DateType
from pyspark.sql.window import Window

CATALOG          = "gbmart"
BRONZE_TABLE     = "gbmart.bronze.customers"
SILVER_TABLE     = "gbmart.silver.customers"
QUARANTINE_TABLE = "gbmart.silver.customers_quarantine"

print(f"Reading from : {BRONZE_TABLE}")
print(f"Writing to   : {SILVER_TABLE}")


# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Read Raw Data from Bronze
# MAGIC Load all customer records from the Bronze layer as-is. 
# MAGIC No changes at this step — just reading.
# MAGIC

# COMMAND ----------

bronze_df = spark.table(BRONZE_TABLE)
print(f"Total records in Bronze: {bronze_df.count():,}")
bronze_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Check What's Wrong (First DQ Scan)
# MAGIC Before fixing anything, run DQ checks to see what issues exist in the data.
# MAGIC This tells us exactly what needs to be fixed and how many records are affected.
# MAGIC

# COMMAND ----------

EMAIL_REGEX = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'

dq_df = bronze_df \
    .withColumn("_dob_temp", to_date(col("DateOfBirth"),      "yyyy-MM-dd")) \
    .withColumn("_reg_temp", to_date(col("RegistrationDate"), "yyyy-MM-dd")) \
    .withColumn("_age_at_reg", floor(datediff(col("_reg_temp"), col("_dob_temp")) / 365.25)) \
    .withColumn("_dq_issue",
        when(col("CustomerID").isNull(),                               lit("NULL_CUSTOMER_ID"))
        .when(col("FirstName").isNull() | (trim(col("FirstName")) == ""), lit("NULL_FIRST_NAME"))
        .when(col("LastName").isNull()  | (trim(col("LastName"))  == ""), lit("NULL_LAST_NAME"))
        .when(col("Email").isNull(),                                   lit("NULL_EMAIL"))
        .when(~col("Email").rlike(EMAIL_REGEX),                        lit("INVALID_EMAIL_FORMAT"))
        .when(col("DateOfBirth").isNull(),                             lit("NULL_DATE_OF_BIRTH"))
        .when(col("RegistrationDate").isNull(),                        lit("NULL_REGISTRATION_DATE"))
        .when(col("_age_at_reg") < 18,                                lit("REGISTERED_UNDER_18"))
        .otherwise(lit(None))
    )

print("=== DQ Issues Found ===")
dq_df.groupBy("_dq_issue").count().orderBy("count", ascending=False).display()


# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Investigate Each Issue
# MAGIC
# MAGIC From the DQ scan above we found INVALID_EMAIL_FORMAT issues.
# MAGIC Let us look at the actual bad emails to understand the pattern before fixing.
# MAGIC

# COMMAND ----------

# Look at what invalid emails actually look like
dq_df.filter(col("_dq_issue") == "INVALID_EMAIL_FORMAT") \
    .select("CustomerID", "Email") \
    .display()


# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Investigate Invalid Emails
# MAGIC
# MAGIC We found 318 emails with invalid format. 
# MAGIC Before writing any fix, let us look at the actual emails to understand the pattern.
# MAGIC

# COMMAND ----------

# Look at actual invalid emails — find the pattern yourself
dq_df.filter(col("_dq_issue") == "INVALID_EMAIL_FORMAT") \
    .select("CustomerID", "Email") \
    .distinct() \
    .display()


# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Root Cause & Fix Strategy: Invalid Emails
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
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Business Decision — Fix, don't quarantine
# MAGIC Both are recoverable errors. Quarantining them means losing real customers.  
# MAGIC After applying both fixes, we re-validate — any remaining invalids go to quarantine.
# MAGIC

# COMMAND ----------

# Fix both patterns, then re-validate

remediated_df = bronze_df.withColumn(
    "Email",
    regexp_replace(
        regexp_replace(
            trim(lower(col("Email"))),
            " ", ""          # Pattern 1: remove spaces
        ),
        "'", ""              # Pattern 2: remove apostrophe (d'Souza → dSouza)
    )
)

# Re-run email validation on remediated data
EMAIL_REGEX = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
remediated_df \
    .filter(~col("Email").rlike(EMAIL_REGEX) & col("Email").isNotNull()) \
    .select("CustomerID", "Email") \
    .display()
# Goal: 0 rows (all 318 should be recovered)


# COMMAND ----------

remediated_df = bronze_df.withColumn(
    "Email",
    regexp_replace(
        regexp_replace(
            trim(lower(col("Email"))),
            " ", ""                      # Pattern 1: remove spaces
        ),
        "d['\u2019\u2018]", ""           # Pattern 2: d + any apostrophe variant (ASCII + Unicode)
    )
)

# Re-run validation — should now show 0 rows
EMAIL_REGEX = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
remediated_df \
    .filter(~col("Email").rlike(EMAIL_REGEX) & col("Email").isNotNull()) \
    .select("CustomerID", "Email") \
    .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — REGISTERED_UNDER_18: Root Cause & Decision
# MAGIC
# MAGIC ##### Business Rule
# MAGIC GlobalMart requires **18+** to register — legal compliance, payment authorization, and Terms of Service.
# MAGIC
# MAGIC ##### Why did these 77 get in?
# MAGIC The registration form had **no age validation** at the time. Source system gap — not a data entry mistake.
# MAGIC
# MAGIC ##### Why we can't fix it (unlike email spaces)
# MAGIC Email spaces — we knew the correct email, just cleaned the format.  
# MAGIC Age — we **cannot assume** the DOB is wrong. The customer may genuinely have been under 18.
# MAGIC
# MAGIC ##### Decision → Quarantine
# MAGIC These 77 records go to quarantine with reason `REGISTERED_UNDER_18`.  
# MAGIC Business team will decide: verify DOB, deactivate account, or flag for legal review.
# MAGIC
# MAGIC **Silver layer will not include these records.**
# MAGIC

# COMMAND ----------

# Final DQ check — on remediated email data, including age rule

EMAIL_REGEX = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'

dq_df = remediated_df \
    .withColumn("_dob_temp",    to_date(col("DateOfBirth"),      "yyyy-MM-dd")) \
    .withColumn("_reg_temp",    to_date(col("RegistrationDate"), "yyyy-MM-dd")) \
    .withColumn("_age_at_reg",  floor(datediff(col("_reg_temp"), col("_dob_temp")) / 365.25)) \
    .withColumn("_dq_issue",
        when(col("CustomerID").isNull(),                               lit("NULL_CUSTOMER_ID"))
        .when(col("FirstName").isNull() | (trim(col("FirstName")) == ""), lit("NULL_FIRST_NAME"))
        .when(col("LastName").isNull()  | (trim(col("LastName"))  == ""), lit("NULL_LAST_NAME"))
        .when(col("Email").isNull(),                                   lit("NULL_EMAIL"))
        .when(~col("Email").rlike(EMAIL_REGEX),                        lit("INVALID_EMAIL_FORMAT"))
        .when(col("DateOfBirth").isNull(),                             lit("NULL_DATE_OF_BIRTH"))
        .when(col("RegistrationDate").isNull(),                        lit("NULL_REGISTRATION_DATE"))
        .when(col("_age_at_reg") < 18,                                 lit("REGISTERED_UNDER_18"))
        .otherwise(lit(None))
    )

# COMMAND ----------

dq_df.display()

# COMMAND ----------

clean_df      = dq_df.filter(col("_dq_issue").isNull()) \
                     .drop("_dq_issue", "_dob_temp", "_reg_temp", "_age_at_reg")
quarantine_df = dq_df.filter(col("_dq_issue").isNotNull()) \
                     .drop("_dob_temp", "_reg_temp", "_age_at_reg")

# COMMAND ----------

quarantine_df.display()

# COMMAND ----------

clean_df.display()

# COMMAND ----------

print(f"Total rows    : {bronze_df.count():,}")
print(f"Clean rows    : {clean_df.count():,}")
print(f"Quarantine    : {quarantine_df.count():,}")

quarantine_df.groupBy("_dq_issue").count().orderBy("count", ascending=False).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7 — Root Cause & Fix: Phone Number Format
# MAGIC
# MAGIC ### What we found
# MAGIC All 19,920 phone numbers are 12 digits — every record has the `91` India country code prepended.
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
# MAGIC

# COMMAND ----------

# Check phone number length distribution

clean_df \
    .withColumn("_phone_len", length(col("PhoneNumber"))) \
    .groupBy("_phone_len").count() \
    .orderBy("_phone_len") \
    .display()


# COMMAND ----------

# Show records where phone is NOT 10 digits
clean_df \
    .withColumn("_phone_len", length(col("PhoneNumber"))) \
    .filter(col("_phone_len") != 10) \
    .select("CustomerID", "PhoneNumber", "_phone_len") \
    .display()


# COMMAND ----------

remediated_df = remediated_df.withColumn(
    "PhoneNumber",
    when(
        (length(col("PhoneNumber")) == 12) & col("PhoneNumber").startswith("91"),
        concat(lit("+91-"), col("PhoneNumber").substr(3, 10))
    ).otherwise(col("PhoneNumber"))
)

# Verify
remediated_df.select("CustomerID", "PhoneNumber").display()


# COMMAND ----------

remediated_df = remediated_df.withColumn(
    "PhoneNumber",
    when(
        (length(col("PhoneNumber").cast("string")) == 12) &
        col("PhoneNumber").cast("string").startswith("91"),
        concat(lit("+91-"), col("PhoneNumber").cast("string").substr(3, 10))
    ).otherwise(col("PhoneNumber").cast("string"))
)

# Verify
remediated_df.select("CustomerID", "PhoneNumber").display()


# COMMAND ----------

# Step 1 — break the BIGINT lineage
remediated_df = remediated_df.withColumn("PhoneNumber", col("PhoneNumber").cast("string"))


# COMMAND ----------

# Step 2 — now PhoneNumber is STRING, no type conflict
remediated_df = remediated_df.withColumn(
    "PhoneNumber",
    when(
        (length(col("PhoneNumber")) == 12) & col("PhoneNumber").startswith("91"),
        concat(lit("+91-"), col("PhoneNumber").substr(3, 10))
    ).otherwise(col("PhoneNumber"))
)

# COMMAND ----------


remediated_df.select("CustomerID", "PhoneNumber").display()

# COMMAND ----------

remediated_df = (
    remediated_df
    .withColumn(
        "phone_clean",
        when(
            (length(col("PhoneNumber").cast("string")) == 12) &
            col("PhoneNumber").cast("string").startswith("91"),
            concat(lit("+91-"), col("PhoneNumber").cast("string").substr(3, 10))
        ).otherwise(col("PhoneNumber").cast("string"))
    )
    .drop("PhoneNumber")
    .withColumnRenamed("phone_clean", "PhoneNumber")
)

remediated_df.select("CustomerID", "PhoneNumber").display()


# COMMAND ----------

spark.conf.set("spark.sql.ansi.enabled", "false")

# COMMAND ----------

remediated_df = remediated_df.withColumn(
    "PhoneNumber",
    when(
        (length(col("PhoneNumber").cast("string")) == 12) &
        col("PhoneNumber").cast("string").startswith("91"),
        concat(lit("+91-"), col("PhoneNumber").cast("string").substr(3, 10))
    ).otherwise(col("PhoneNumber").cast("string"))
)


# COMMAND ----------

remediated_df.select("CustomerID", "PhoneNumber").display()