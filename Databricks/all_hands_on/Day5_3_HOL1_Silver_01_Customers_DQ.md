---
name: Day 5 HOL 1 — Silver Layer Customer Data Cleaning & Quality Checks
content_type: Scenario
overview: GlobalMart's Bronze customers table has never been quality-checked — 20,000 raw registration records straight from the source system, with no guarantee any of it is clean. In this hands-on, you will scan the full table for multiple possible data quality issues at once, investigate each issue found, decide whether it is recoverable (fix it) or not (quarantine it), deduplicate append-only Bronze data, derive reusable business columns, and add SCD Type 2 tracking columns before writing the result to a practice Silver table.
learning_objectives:
  - Scan a real Bronze table for multiple data quality issues at once, tagging each row by its first failing rule
  - Decide when to fix a data quality issue versus quarantine it, and articulate why
  - Use regex-based string cleaning to repair a known, recoverable formatting mistake
  - Deduplicate append-only Bronze data using a window function, keeping only the latest record per key
  - Derive reusable business columns in Silver so Gold and BI never have to repeat the same calculation
  - Add SCD Type 2 tracking columns to a dimension table on its initial load
prerequisites:
  - A Databricks workspace with read access to the shared bronze.customers table and a schema you can write to
  - Completed Day 5 ILT 1 (Transformation Patterns) and ILT 2 (Data Quality Constraints & Validation)
duration: 90 minutes
level: Intermediate
industries:
  - e-commerce
tags:
  - databricks (tool)
  - spark (tool)
  - data-quality (skill)
  - data-wrangling (skill)
---

---

## Scenario 1 — Read Bronze and Run a Full DQ Scan

**Overview:** GlobalMart's Bronze `customers` table holds 20,000 raw registration records, straight from the source system with no quality checks applied yet. Rather than jumping straight to fixes, you will first read the full table and scan every row for several possible issues at once — missing required fields, invalid email format, and registrations that appear to be from under-18 customers — tagging each row with its first failing rule. This gives you a complete picture of what needs attention before you decide what to do about each issue.

**Outcome:** A full DQ scan of all 20,000 Bronze customer records, with every row tagged by its first failing rule (or none), ready to investigate one issue at a time.

---

## Input 1

**Type:** Text

### Setup

>[!IMPORTANT]
>Never write directly to the shared `silver.customers` table — only the first person in the whole cohort to run this notebook would see real behavior, and everyone after (including you, rehearsing) would see a broken-looking exercise. Clone into your own practice schema instead.

```python
from pyspark.sql.functions import *
from pyspark.sql.types import DateType
from pyspark.sql.window import Window

# PhoneNumber is stored as BIGINT in bronze. Disabling ANSI mode prevents Spark
# from forcing our reformatted string back to BIGINT.
spark.conf.set("spark.sql.ansi.enabled", "false")

# ─── Personal practice schema — never write directly to shared tables ─────────
# HOW TO GET YOUR CATALOG NAME: ask your instructor, or check Catalog Explorer
# for the catalog you have access to.
PRACTICE_SCHEMA  = "main.YOUR_SCHEMA"   # ← replace with a schema you own
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {PRACTICE_SCHEMA}")

BRONZE_TABLE     = f"{PRACTICE_SCHEMA}.bronze_customers_practice"
SILVER_TABLE     = f"{PRACTICE_SCHEMA}.silver_customers_practice"
QUARANTINE_TABLE = f"{PRACTICE_SCHEMA}.silver_customers_quarantine_practice"

# SHALLOW CLONE: same real data as the shared bronze.customers table right now,
# but your own independent transaction log — safe to write to repeatedly.
spark.sql(f"CREATE OR REPLACE TABLE {BRONZE_TABLE} SHALLOW CLONE YOUR_CATALOG.bronze.customers")
```

---

## Input 2

**Type:** Text

### Read the raw data

```python
bronze_df = spark.table(BRONZE_TABLE)
print(f"Total records in Bronze: {bronze_df.count():,}")
```

No changes at this step — just reading. This should show **20,000** records.

---

## Input 3

**Type:** Text

### Scan every row for multiple possible issues at once

```python
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

dq_scan_df.groupBy("_dq_issue").count().orderBy("count", ascending=False).display()
```

---

## Input 4

**Type:** Short Answer

**Question:** Which distinct DQ issue categories did your scan surface, and which one appears to affect the most rows based on your own `groupBy` output?

**Template:** null

**Tags**
- data-quality (skill)

---

## Input 5

**Type:** Choice

**Question:** In a chain like `.when(cond1, valueA).when(cond2, valueB).otherwise(valueC)`, if a single row happens to match both `cond1` and `cond2`, which value does that row get?

**Options:**
- `valueA` — the first matching condition in the chain
- `valueB` — the last matching condition in the chain
- Both values, concatenated
- `valueC`, since a row can't match two conditions

**Correct Options:**
- `valueA` — the first matching condition in the chain

**Solution:**
A `when().when().otherwise()` chain evaluates its conditions in the order they're written and stops at the first match — it does not keep checking later conditions once one has matched. That's why this scan's rule chain (null checks, then email format, then age) tags each row with only its *first* failing rule, even if a row happens to fail more than one.

**Tags**
- data-quality (skill)
- approach (skill)

---

## Scenario 2 — Investigate & Fix: Invalid Email Format

**Overview:** GlobalMart's Bronze `customers` table has 20,000 raw registration records, and the DQ scan in Scenario 1 flagged some of them for `INVALID_EMAIL_FORMAT`. Before writing any fix, you will look at the actual bad emails to understand the pattern behind them — two specific, recoverable mistakes caused by GlobalMart's registration form: an autocorrect-inserted space, and an unstripped apostrophe in surnames like D'Souza. Because the correct email can be confidently reconstructed in both cases, the decision is to fix these rows rather than quarantine them.

**Outcome:** All invalid emails cleaned via two targeted regex fixes, re-validated to zero remaining invalid emails.

---

## Input 6

**Type:** Text

### Investigate the pattern before fixing anything

```python
dq_scan_df.filter(col("_dq_issue") == "INVALID_EMAIL_FORMAT") \
    .select("CustomerID", "Email") \
    .display()
```

Two recurring patterns emerge:

**Pattern 1 — accidental space**, e.g. `swaminathaninaaya 482@outlook.com` — mobile keyboard autocorrect inserts a space after a long name, splitting the local part of the email.

**Pattern 2 — apostrophe in a surname-based email**, e.g. `taran.d'alia307@hotmail.com` — surnames like D'Souza, D'Silva, D'Cruz contain `d'` as a prefix, and the registration form accepted the apostrophe even though most mail providers would strip it.

**Business decision:** both are recoverable errors — quarantining them would mean losing real customers, so both get fixed, then re-validated; only genuinely un-fixable emails would go to quarantine.

---

## Input 7

**Type:** Text

### Apply both fixes and re-validate

```python
remediated_df = bronze_df.withColumn(
    "Email",
    regexp_replace(
        regexp_replace(
            trim(lower(col("Email"))),
            " ", ""                       # Pattern 1: remove spaces
        ),
        "d['’‘]", ""             # Pattern 2: d + any apostrophe variant
    )
)

still_invalid = remediated_df \
    .filter(~col("Email").rlike(EMAIL_REGEX) & col("Email").isNotNull()) \
    .count()

print(f"Remaining invalid emails after fix: {still_invalid}")
```

---

## Input 8

**Type:** Choice

**Question:** Why does GlobalMart's team choose to fix these malformed emails instead of quarantining them?

**Options:**
- Because email issues are more common than other issues, so fixing is faster
- Because the correct email can be confidently reconstructed from a known formatting mistake, unlike the under-18 case later in this notebook
- Because emails cannot legally be quarantined
- Because `Email` is stored as a numeric type

**Correct Options:**
- Because the correct email can be confidently reconstructed from a known formatting mistake, unlike the under-18 case later in this notebook

**Solution:**
Both email patterns are recoverable: the space and the apostrophe are known formatting artifacts, and removing them reconstructs the email the customer actually intended. Quarantining a fixable issue would mean losing a real customer's data for no reason. The under-18 case in Scenario 4 is different precisely because there is no equivalent way to confidently reconstruct a "correct" value.

**Tags**
- approach (skill)

---

## Input 9

**Type:** Choice

**Question:** After applying both email fixes and re-running the same validation check, how many invalid emails should remain?

**Options:**
- 0
- 2
- 20,000
- The same number as before the fix

**Correct Options:**
- 0

**Solution:**
Both known bad patterns (a stray space, an unstripped `d'` apostrophe) are removed by the two chained `regexp_replace` calls, and every email in this dataset matches one of those two patterns — so re-running the same `EMAIL_REGEX` validation afterward should show zero remaining invalid emails.

**Tags**
- data-wrangling / regex (skill)

---

## Scenario 3 — Investigate & Fix: Phone Number Format

**Overview:** GlobalMart's Bronze `customers` table stores `PhoneNumber` as a BIGINT, and every record turns out to have the same structural problem: the registration form auto-appended India's `+91` country code but stored it without the `+`, resulting in a 12-digit number like `917584314890` instead of the standard `+91-7584314890` format GlobalMart expects.

**Outcome:** All phone numbers reformatted to the standard `+91-XXXXXXXXXX` string format.

---

## Input 10

**Type:** Text

### Investigate the phone number format

```python
remediated_df \
    .withColumn("_phone_len", length(col("PhoneNumber").cast("string"))) \
    .groupBy("_phone_len").count() \
    .orderBy("_phone_len") \
    .display()
```

Every phone number is 12 digits — the `91` India country code prepended, with no `+` and no separator.

---

## Input 11

**Type:** Text

### Fix — cast to string, then reformat

```python
remediated_df = remediated_df \
    .withColumn("PhoneNumber", col("PhoneNumber").cast("string")) \
    .withColumn(
        "PhoneNumber",
        when(
            (length(col("PhoneNumber")) == 12) & col("PhoneNumber").startswith("91"),
            concat(lit("+91-"), col("PhoneNumber").substr(3, 10))
        ).otherwise(col("PhoneNumber"))
    )
```

---

## Input 12

**Type:** Choice

**Question:** Why must `PhoneNumber` be cast to a string type before it can be reformatted into `+91-XXXXXXXXXX`, instead of reformatting it while it's still a BIGINT?

**Options:**
- BIGINT values are always too large to hold a phone number
- A numeric type cannot represent formatting characters like `+` and `-`, or a prefix that's been stripped and reassembled into a display string
- Casting to string is required before any `length()` call in Spark
- BIGINT columns cannot be filtered with `when()`

**Correct Options:**
- A numeric type cannot represent formatting characters like `+` and `-`, or a prefix that's been stripped and reassembled into a display string

**Solution:**
`+91-7584314890` is not a valid number — the `+` and `-` are text characters, and leading content like the reconstructed `+91-` prefix isn't something a numeric type can hold at all. Casting to string first is what makes this a text-formatting operation rather than an arithmetic one.

**Tags**
- data-wrangling / text-processing (skill)

---

## Scenario 4 — Investigate & Decide: Under-18 Registrations

**Overview:** GlobalMart requires customers to be 18 or older to register — a legal compliance, payment-authorization, and Terms-of-Service requirement. The Scenario 1 DQ scan flagged registrations where `RegistrationDate` is less than 18 years after `DateOfBirth`, and investigation shows GlobalMart's registration form simply had no age validation at the time these 77 accounts were created — a source-system gap, not a one-off data entry mistake.

**Outcome:** A deliberate decision to quarantine every under-18 registration rather than attempt to fix it, since — unlike the email and phone issues — there is no way to confidently determine what the "correct" data should have been.

---

## Input 13

**Type:** Text

### Investigate before deciding

```python
remediated_df \
    .withColumn("_dob",      to_date(col("DateOfBirth"),      "yyyy-MM-dd")) \
    .withColumn("_reg",      to_date(col("RegistrationDate"), "yyyy-MM-dd")) \
    .withColumn("_age_at_reg", floor(datediff(col("_reg"), col("_dob")) / 365.25).cast("int")) \
    .filter(col("_age_at_reg") < 18) \
    .select("CustomerID", "DateOfBirth", "RegistrationDate", "_age_at_reg") \
    .orderBy("_age_at_reg") \
    .display()
```

The registration form had no age validation at the time — this is a source-system gap, not a data entry mistake. Unlike the email spaces (where the correct email was knowable), there is no way to confidently assume the `DateOfBirth` is wrong: the customer may genuinely have been under 18 when they registered. **Decision: quarantine, don't fix.** These records will not go into Silver — the business team will decide separately whether to verify the DOB, deactivate the account, or flag it for legal review.

---

## Input 14

**Type:** Short Answer

**Question:** In your own words, why can't the under-18 issue be "fixed" the same way the email and phone number issues were?

**Template:** null

**Tags**
- data-quality / business-rule-violation (skill)

---

## Input 15

**Type:** Choice

**Question:** Based on this notebook's investigation, how many customer records get flagged for `REGISTERED_UNDER_18`?

**Options:**
- 0
- 77
- 20,000
- 19,920

**Correct Options:**
- 77

**Solution:**
The investigation in this scenario identifies 77 customers whose `RegistrationDate` is less than 18 years after their `DateOfBirth` — the registration form had no age gate at the time these accounts were created.

**Tags**
- data-quality / business-rule-violation (skill)

---

## Scenario 5 — Final DQ Check, Split, and Deduplicate

**Overview:** GlobalMart's Bronze `customers` table has now had both recoverable issues fixed — the email and phone number formats. The only unresolved issue is the 77 under-18 registrations from Scenario 4, which are being quarantined rather than fixed. Now you will run one final, complete DQ check on this fully remediated data and split it into a clean set (which will go on to Silver) and a quarantine set (which will not), then deduplicate the clean set — Bronze is append-only, so the same customer can appear more than once across different ingestion files.

**Outcome:** A clean DataFrame ready for Silver, a quarantine DataFrame with every remaining issue tagged, and a deduplicated clean set keeping only the latest record per customer.

---

## Input 16

**Type:** Text

### Run the final check and split

```python
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
```

---

## Input 17

**Type:** Short Answer

**Question:** After running this final DQ check, how many rows landed in `clean_df` and how many in `quarantine_df`? Given that only the under-18 issue (77 rows) remained unresolved at this point, does your quarantine count match that number exactly, or is it slightly different — and if different, what might that tell you about this dataset?

**Template:** null

**Tags**
- data-quality (skill)

---

## Input 18

**Type:** Code

**Question:** Bronze is append-only, so the same customer can appear more than once across different ingestion files. Using PySpark, write code that keeps only the single latest record per customer from `clean_df`, based on the `_ingested_at` column.

**Language:** python

**Snippet:**
```python
window_latest = Window.partitionBy("CustomerID").orderBy(col("_ingested_at").desc())

# your deduplication code here
```

**Solution:**
```python
window_latest = Window.partitionBy("CustomerID").orderBy(col("_ingested_at").desc())

deduped_df = (
    clean_df
    .withColumn("_row_num", row_number().over(window_latest))
    .filter(col("_row_num") == 1)
    .drop("_row_num")
)

print(f"After dedup : {deduped_df.count():,} unique customers")
```
`row_number()` over a window partitioned by `CustomerID` and ordered by `_ingested_at` descending numbers each customer's records from most recent (1) to oldest — keeping only `_row_num == 1` keeps exactly the latest one per customer. In this particular dataset, `clean_df` and `deduped_df` come out to the same row count, meaning this run happened not to contain any actual duplicate `CustomerID`s — but the technique is still necessary, because Bronze being append-only means duplicates *can* appear on a different ingestion run even when this one doesn't have any.

**Tags**
- data-wrangling / window (skill)
- data-quality / duplicates (skill)

---

## Scenario 6 — Transform, Derive Business Columns, and Add SCD2 Tracking

**Overview:** With `clean_df` deduplicated, GlobalMart's Silver layer standard is to apply a few final transformations before writing: proper date types instead of strings, standardized `snake_case` column names, two derived business metrics computed once so Gold and BI never repeat the same calculation, and the SCD Type 2 tracking columns that let Gold detect and preserve history when a customer's email or phone number changes later.

**Outcome:** A fully transformed, Silver-ready DataFrame with `age` and `customer_tenure_days` derived, and initial-load SCD2 values where every customer starts as `is_current = true`.

---

## Input 19

**Type:** Text

### Cast types, trim, and standardize column names

```python
transformed_df = (
    deduped_df
    .withColumn("DateOfBirth",      to_date(col("DateOfBirth"),      "yyyy-MM-dd"))
    .withColumn("RegistrationDate", to_date(col("RegistrationDate"), "yyyy-MM-dd"))
    .withColumn("FirstName",        trim(col("FirstName")))
    .withColumn("LastName",         trim(col("LastName")))
    .withColumn("full_name",        concat_ws(" ", col("FirstName"), col("LastName")))
    # your derived columns go here — see Input 20
    .withColumnRenamed("CustomerID",               "customer_id")
    .withColumnRenamed("FirstName",                "first_name")
    .withColumnRenamed("LastName",                 "last_name")
    .withColumnRenamed("Email",                    "email")
    .withColumnRenamed("PhoneNumber",              "phone_number")
    .withColumnRenamed("DateOfBirth",              "date_of_birth")
    .withColumnRenamed("RegistrationDate",         "registration_date")
    .withColumnRenamed("PreferredPaymentMethodID", "preferred_payment_method_id")
)
```

---

## Input 20

**Type:** Code

**Question:** GlobalMart's Gold layer and BI tools will constantly need to segment customers by how long they've been registered (for example: under 90 days = New Customer, 90–365 days = Regular Customer, over 365 days = Loyal Customer). If this calculation isn't done once in Silver, every downstream Gold table, dashboard, and Genie query would have to repeat it independently. Using PySpark, derive two columns on `transformed_df`: `age` (in whole years, from `date_of_birth` to today) and `customer_tenure_days` (days since `registration_date`, to today).

**Language:** python

**Snippet:**
```python
transformed_df = (
    transformed_df
    # your two derived columns here
)
```

**Solution:**
```python
transformed_df = (
    transformed_df
    .withColumn("age", floor(datediff(current_date(), col("date_of_birth")) / 365.25).cast("int"))
    .withColumn("customer_tenure_days", datediff(current_date(), col("registration_date")).cast("int"))
)
```
`datediff()` gives the gap in days between two dates; dividing by `365.25` and flooring converts a day-gap into whole years for `age`, while `customer_tenure_days` is used directly as days. Computing both here, once, in Silver means every Gold table and dashboard downstream reads a ready-made column instead of repeating this same `datediff()` logic independently.

**Tags**
- data-wrangling / derived-column (skill)
- data-wrangling / date-processing (skill)

---

## Input 21

**Type:** Choice

**Question:** Why compute `age` and `customer_tenure_days` once in Silver, instead of letting each Gold table or BI dashboard compute them independently?

**Options:**
- Because Gold tables cannot use `datediff()`
- Because if multiple Gold tables or dashboards need the same derived value, computing it once in Silver avoids duplicating that logic everywhere it's needed
- Because Silver tables are not allowed to contain raw dates
- Because Gold layer joins run faster without date columns

**Correct Options:**
- Because if multiple Gold tables or dashboards need the same derived value, computing it once in Silver avoids duplicating that logic everywhere it's needed

**Solution:**
The rule this notebook follows: if multiple Gold tables need the same derived value, compute it once in Silver. Otherwise every Gold query, dashboard, and Genie query built on top of Silver ends up repeating the same `datediff()` expression independently — duplicated logic that has to be kept consistent everywhere it's copied.

**Tags**
- approach (skill)

---

## Input 22

**Type:** Text

### Add SCD2 tracking columns (initial load)

```python
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
)
```

On this initial load, every customer starts as `is_current = true` with no `effective_end_date`. Later, when a customer's email or phone number changes, the old row is expired (`is_current = false`, `effective_end_date` set) and a new version is inserted with a new `customer_sk` — that's Phase 2, incremental SCD2, covered on Day 10.

---

## Input 23

**Type:** Choice

**Question:** Why does Gold join to `customer_sk` (the surrogate key generated here in Silver) instead of joining directly on `customer_id` (the natural key from the source system)?

**Options:**
- `customer_id` cannot be used in a join condition
- `customer_sk` supports SCD2 history (a changed customer gets a new key + new row) and decouples Gold from the source system, so source changes don't break downstream joins
- `customer_sk` is shorter and therefore faster to join on
- There is no difference; either key works identically

**Correct Options:**
- `customer_sk` supports SCD2 history (a changed customer gets a new key + new row) and decouples Gold from the source system, so source changes don't break downstream joins

**Solution:**
When a customer's email or phone changes, a new row with a new `customer_sk` gets inserted rather than overwriting the old one — `fact_orders` can then link to whichever `customer_sk` was active at the time of the order, preserving history. Joining on the natural key (`customer_id`) instead would lose that history and tie every downstream table directly to the source system's own key.

**Tags**
- approach (skill)

---

## Scenario 7 — Write to Silver and Verify

**Overview:** GlobalMart's clean, transformed, deduplicated customer data — with SCD2 tracking columns applied — is ready to land in Silver. To keep this hands-on repeatable for every learner and every rehearsal, you will write to your own practice schema's Silver and quarantine tables rather than the shared workspace tables, then verify the result: row counts, the SCD2 flag, a sanity check on the age range, and the phone number formatting.

**Outcome:** `silver_customers_practice` and `silver_customers_quarantine_practice` populated and verified — correct row counts, every customer `is_current = true`, a sensible age range, and correctly formatted phone numbers.

---

## Input 24

**Type:** Text

### Write clean and quarantine records to your practice schema

```python
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {PRACTICE_SCHEMA}")

silver_df.write \
    .format("delta") \
    .mode("append") \
    .saveAsTable(SILVER_TABLE)

quarantine_df \
    .withColumn("_quarantine_ts", current_timestamp()) \
    .write \
    .format("delta") \
    .mode("append") \
    .option("overwriteSchema", "true") \
    .saveAsTable(QUARANTINE_TABLE)
```

---

## Input 25

**Type:** Text

### Verify

```python
df = spark.table(SILVER_TABLE)

print(f"{SILVER_TABLE} rows : {df.count():,}")

# SCD2 check — all initial records should be is_current = true
df.groupBy("is_current").count().display()

# Age sanity check
df.select(min("age").alias("min_age"), max("age").alias("max_age"), avg("age").alias("avg_age")).display()

# Phone format check
df.select("customer_id", "phone_number").limit(5).display()

spark.sql(f"DESCRIBE HISTORY {SILVER_TABLE}").select("version", "timestamp", "operation").display()
```

---

## Input 26

**Type:** Short Answer

**Question:** After writing to your practice Silver table, confirm: how many rows are in `silver_customers_practice`, does the `is_current` breakdown show every row as `true`, and what does your min/max `age` range look like? Given the under-18 quarantine decision from Scenario 4, would you expect to see anyone under 18 in this age range — why or why not?

**Template:** null

**Tags**
- data-quality (skill)

---

## Input 27

**Type:** File Upload

**Question:** Take a screenshot of your notebook output showing the `DESCRIBE HISTORY` result alongside your row-count and `is_current` verification. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)
