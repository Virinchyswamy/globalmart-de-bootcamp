# Data Cleaning and Enrichment - Silver Layer
## Content Type
Scenario

## Overview
Clean, enrich, and enforce quality constraints on all 8 GlobalMart source tables to produce a trusted Silver layer ready for dimensional modelling.

## Learning Objectives
- Identify, investigate, and remediate data quality issues across structured and semi-structured datasets.
- Apply fix-in-place vs quarantine decisions based on root cause analysis and downstream impact.
- Add SCD2 scaffold columns to dimension tables in preparation for incremental history tracking.
- Enforce Delta constraints and use Delta Time Travel to verify Silver table versions.

## Prerequisites
- Building the Bronze Layer activity completed — all 8 Bronze tables populated and verified
- Familiarity with Databricks & Pyspark
- Familiarity with data quality issue & data cleaning

## Duration of Completion
180 minutes

## Level
Intermediate

## Industries
- e-commerce

## Tags
- approach (skill)
- quality (skill)
- data-understanding (skill)
- data-quality (skill)
- batch-etl (skill)
- data-wrangling (skill)
- databricks (tool)
- spark (tool)

#### Overview
Clean, enrich, and enforce quality constraints on all 8 GlobalMart source tables to produce a trusted Silver layer ready for dimensional modelling.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- approach (skill)
- quality (skill)
- data-understanding (skill)
- data-quality (skill)
- batch-etl (skill)
- data-wrangling (skill)
- databricks (tool)
- spark (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!NOTE]
> The solution to the previous activity can be downloaded here.
>
> - [Building the Bronze Layer — Solution](PLACEHOLDER)

>[!IMPORTANT]
> All tables built in this activity must follow the three-level namespace:
> `<your-catalog>.silver.<table_name>`

**Tags**


##### Input 2
**Type:** Text

The Silver layer is the most critical layer in the Medallion Architecture, not the most visible, but the most consequential.

Bronze accepts everything the source sends. Gold serves what the business queries. Silver is the layer in between that determines whether those queries return numbers that can be trusted or numbers that will be questioned in a meeting.

Every data quality issue that is not caught and resolved here will silently flow into the Gold layer and eventually surface as a wrong total in a dashboard, a broken foreign key in a report, or a metric that no one can explain. By the time it is visible in Gold, the damage is already done.

This layer demands more than writing code; it demands investigation. Some patterns that look like errors are valid business rules. Some that look clean are silently broken. The decisions made here, fix, flag, or quarantine- directly define what GlobalMart can and cannot report on.

>[!IMPORTANT]
> Investigate before you decide. Every table has its own patterns; do not assume that what is clean in one table is clean in another.

**Follow this approach for every dataset in this activity:**

- Read all records from the corresponding Bronze table
- Run a DQ scan, tag each row with its first failing rule to get a complete picture of all issues
- Investigate each flagged category before making any decision, understand the root cause first
- Fix what can be corrected programmatically; quarantine what cannot be recovered
- Apply transformations - cast types, derive columns, standardize column naming to snake_case
- Write clean records to Silver

 

**Tags**


##### Input 3
**Type:** Text

### Task 1: customers
<br/>

**Source:** `<your-catalog>.bronze.customers`
**Target:** `<your-catalog>.silver.customers`
<br/>

| Issue | What to Do |
|---|---|
| Phone numbers are stored without a standard international format | GlobalMart's support team uses these for order follow-ups — non-standard numbers cannot be dialed from CRM systems. Identify the exact format pattern and correct it. |
| Email addresses contain invalid characters | Invalid formats cause marketing emails to bounce. Find all character patterns causing failures and fix them. |
| Date columns have incorrect data types | Age calculations and customer segmentation queries fail when date fields are stored as strings. Cast each date column to the correct type. |
| ID columns contain null values | Records without a `CustomerID` cannot be joined to orders, payments, or any downstream table. These must not pass through to Silver. |
| Customers registered under 18 years of age | GlobalMart requires customers to be 18 or older for payment authorization and legal compliance. Records below this threshold must be moved to a quarantine table. |
| Customer profiles change over time | GlobalMart's analytics team needs to track both the previous and current version of a customer record. Add SCD2 columns to support this. |
| Enforce data quality at the table level | After writing to Silver, add NOT NULL constraints on `customer_id` and `email` so no future write can insert records with missing values on these critical columns. |
<br/>

**Outcome:**

- SCD2 logic added — both historical and current customer records can coexist in the table
- All data quality issues resolved and clean records stored in `<your-catalog>.silver.customers`
- Records violating the age rule stored in `<your-catalog>.silver.customers_quarantine`
- NOT NULL constraints enforced on `customer_id` and `email`

**Tags**


##### Input 4
**Type:** Short Answer

**Question:** Did you discover any data quality issues in this dataset beyond the ones listed above? For each, describe what you found, how you investigated it, and the action you took.

**Template:** null

**Tags**
- batch-etl / batch-processing (skill)

##### Input 5
**Type:** File Upload

**Question:** Upload your completed customer Silver notebook and a screenshot showing five sample rows from table

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-wrangling / text-processing (skill)
- data-wrangling / date-processing (skill)
- data-wrangling / dataframe-processing (skill)
- batch-etl / batch-processing (skill)
- data-quality / integrity (skill)

##### Input 6
**Type:** Text

### Task 2: orders
<br/>

**Source:** `<your-catalog>.bronze.orders`
**Target:** `<your-catalog>.silver.orders`
<br/>

| Observation | What to Investigate |
|---|---|
| Column names are all lowercase in Bronze | Lakeflow Connect lowercases all column names during ingestion — `OrderID` becomes `orderid`, `CustomerID` becomes `customerid`. These lowercase names are your final column schema in Silver. |
| Some orders show delivery date earlier than shipping date | Check how many records are affected and whether the gap is consistent or random. If all gaps are exactly 1 day, investigate whether a timezone difference between source systems could cause the date labels to flip — that would make the records valid, not erroneous. |
| NULL values in shipping and delivery date columns | An order that has not shipped yet will naturally have a NULL shipping date. Understand what each NULL means in the order lifecycle before treating it as a missing value. |
| Enforce data quality at the table level | After writing to Silver, add NOT NULL constraints on `order_id` and `customer_id` to prevent any future write from inserting orders without a valid identifier or owner. |
<br/>

**Outcome:**

- All 126,036 orders retained in `silver.orders` — no records are removed or flagged
- NOT NULL constraints enforced on `order_id` and `customer_id`

**Tags**


##### Input 7
**Type:** Short Answer

**Question:** Did you discover any data quality issues in this dataset beyond the ones listed above? For each, describe what you found, how you investigated it, and the action you took.

**Template:** null

**Tags**
- approach / concept-clarity (skill)

##### Input 8
**Type:** File Upload

**Question:** Upload your completed `orders` Silver notebook, and a screenshot showing five sample rows from table

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-quality / data-consistency (skill)
- data-wrangling / filter (skill)
- data-wrangling / date-processing (skill)
- batch-etl / batch-processing (skill)
- data-wrangling / dataframe-processing (skill)

##### Input 9
**Type:** Text

### Task 3: products
<br/>

**Source:** `<your-catalog>.bronze.products`
**Target:** `<your-catalog>.silver.products`
<br/>

| Issue | What to Do |
|---|---|
| `specs` and `supplier_info` are nested struct columns | BI tools and the Gold layer cannot query nested fields directly. Flatten both to top-level columns before running any DQ checks. |
| `tags` and `color_options` are array columns | Decide how to handle them without breaking the one-row-per-product grain. |
| `_rescued_data` column may contain non-null values | Any non-null value means a field arrived in the source that Autoloader could not map to the inferred schema. Check across all rows before proceeding. |
| `material` is null for some products | Before treating this as a data gap, investigate: electronics and personal care products genuinely do not have a material attribute. Check whether the nulls follow a category-specific pattern. |
| Add a derived column `discount_pct` | The sales team needs to report on promotion depth across categories. Derive it from the existing price columns using: `((actual_price_inr - discounted_price_inr) / actual_price_inr) * 100` |
| Product prices change over time | The finance team needs the price of a product at the time each order was placed, not just the current price. Add SCD2 scaffold columns to support historical price tracking. |
<br/>

**Outcome:**

- SCD2 logic added — historical and current product versions can coexist in the table
- `silver.products` is fully flattened with `discount_pct` pre-computed for all 500 products
- `_rescued_data` confirmed as 0 non-null rows

**Tags**


##### Input 10
**Type:** File Upload

**Question:** Upload your completed `products` Silver notebook, and a screenshot showing five sample rows from table

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-wrangling / text-processing (skill)
- data-wrangling / dataframe-processing (skill)
- batch-etl / batch-processing (skill)

##### Input 11
**Type:** Text

### Task 4: addresses
<br/>

**Source:** `<your-catalog>.bronze.addresses`
**Target:** `<your-catalog>.silver.address`
<br/>

| Issue | What to Do |
|---|---|
| `PinCode` values are shorter than 6 digits for some records | Autoloader inferred a numeric type and stripped leading zeros at ingestion — e.g. `082130` became `82130`. India's postal system uses 6-digit PINs and truncated values would cause package routing failures. Find the true value from within the same dataset and recover it. |
| `AddressLine1` contains embedded city and PinCode values | Delivery systems read `AddressLine1` as the street address only. The embedded data would be misread as part of the street name — e.g. `"61/96, Chauhan Road\nHaldia 060162"` should be cleaned to `"61/96, Chauhan Road"`. Identify and remove the duplicate portion. |
| `State` and `AddressType` use underscores instead of spaces | e.g. `Tamil_Nadu` should be `Tamil Nadu`, `Andhra_Pradesh` should be `Andhra Pradesh`. Standardize the formatting across all rows. |
<br/>

**Outcome:**

- All `pincode` values in `silver.address` are exactly 6 characters — no truncated PINs remain
- `address_line1` contains only the street address portion
- Consistent formatting across `state` and `address_type`

**Tags**


##### Input 12
**Type:** Short Answer

**Question:** Did you discover any data quality issues in this dataset beyond the ones listed above? For each, describe what you found, how you investigated it, and the action you took.

**Template:** null

**Tags**
- approach / concept-clarity (skill)

##### Input 13
**Type:** File Upload

**Question:** Upload your completed `addresses` Silver notebook, and a screenshot showing five sample rows from table

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-wrangling / text-processing (skill)
- data-wrangling / dataframe-processing (skill)

##### Input 14
**Type:** Text

### Task 5: order_items
<br/>

**Source:** `<your-catalog>.bronze.order_items`
**Target:** `<your-catalog>.silver.order_items`
<br/>

| Issue | What to Do |
|---|---|
| Column names are all lowercase in Bronze | Lakeflow Connect lowercases all column names during ingestion — `OrderItemID` becomes `orderitemid`. These lowercase names are your final column schema in Silver. |
| Referential integrity against parent tables | Every `order_id` must match a record in `silver.orders` and every `product_id` must match a record in `silver.products`. Orphaned line items would create revenue figures in Gold that reference orders or products which do not exist, making totals irreconcilable. |
<br/>

**Outcome:**

- `silver.order_items` contains all 377,866 rows with 0 orphaned records

**Tags**


##### Input 15
**Type:** Short Answer

**Question:** Did you discover any data quality issues in this dataset beyond the ones listed above? For each, describe what you found, how you investigated it, and the action you took.

**Template:** null

**Tags**
- approach / concept-clarity (skill)

##### Input 16
**Type:** File Upload

**Question:** Upload your completed `order_items` Silver notebook, and a screenshot showing five sample rows from table

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-quality / integrity (skill)
- data-wrangling / dataframe-processing (skill)

##### Input 17
**Type:** Text

### Task 6: payments
<br/>

**Source:** `<your-catalog>.bronze.payments`
**Target:** `<your-catalog>.silver.payments`
<br/>

| Issue | What to Do |
|---|---|
| `GiftCardAmount` and `CouponAmount` are NULL for many rows | Check whether the NULL follows a pattern — when `GiftCardUsage = 'No'`, is `GiftCardAmount` always NULL? When `GiftCardUsage = 'Yes'`, is it always populated? If the pattern holds in both directions, it is a business rule, not a data quality issue. |
| Derive a `used_any_discount` column | The marketing team needs a simple true/false flag to identify which payments had any discount applied. Derive it as: `used_any_discount = True if GiftCardUsage = 'Yes' OR CouponUsage = 'Yes'` |
| Referential integrity against `silver.orders` | A payment with no matching order cannot be attributed to any revenue event in Gold. |
<br/>

**Outcome:**

- `silver.payments` confirmed clean — NULL amount pattern validated as an expected business rule
- `used_any_discount` flag present on all rows

**Tags**


##### Input 18
**Type:** Short Answer

**Question:** Did you discover any data quality issues in this dataset beyond the ones listed above? For each, describe what you found, how you investigated it, and the action you took.

**Template:** null

**Tags**
- approach / concept-clarity (skill)

##### Input 19
**Type:** File Upload

**Question:** Upload your completed `payments` Silver notebook, and a screenshot showing five sample rows from table

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-wrangling / derived-column (skill)
- data-wrangling / text-processing (skill)
- data-quality / integrity (skill)

##### Input 20
**Type:** Text

### Task 7: payment_methods
<br/>

**Source:** `<your-catalog>.bronze.payment_methods`
**Target:** `<your-catalog>.silver.payment_methods`
<br/>

| Issue | What to Do |
|---|---|
| 5-row lookup table | Validate the values and load as-is — this table maps payment method IDs to their names and is used as a dimension in Gold. |
<br/>

**Outcome:**

- `silver.payment_methods` contains all 5 payment method records with clean values

**Tags**


##### Input 21
**Type:** Short Answer

**Question:** Did you discover any data quality issues in this dataset beyond the ones listed above? For each, describe what you found, how you investigated it, and the action you took.

**Template:** null

**Tags**
- approach / concept-clarity (skill)

##### Input 22
**Type:** File Upload

**Question:** Upload your completed `payment_methods` Silver notebook, and a screenshot showing five sample rows from table

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-wrangling / dataframe-processing (skill)
- batch-etl / batch-processing (skill)

##### Input 23
**Type:** Text

### Task 8: returns
<br/>

**Source:** `<your-catalog>.bronze.returns`
**Target:** `<your-catalog>.silver.returns`
<br/>

| Issue | What to Do |
|---|---|
| `RefundAmount` is `0.0` for some records | Before flagging this, investigate: a Pending return means no refund has been issued yet; a Rejected return means no refund will ever be issued. The finance team uses `RefundAmount` to report on total money returned to customers — the zero values may be intentional and correct. |
| Column names are inconsistently cased in the source | `OrderId` instead of `OrderID`, `Return_reason` instead of `ReturnReason`. Standardize all to snake_case to prevent join failures when used alongside other Silver tables. |
| `ReturnMethod` uses underscores in place of spaces | `Store_Drop` instead of `Store Drop`. Standardize the formatting. |
| Referential integrity against parent tables | Verify every `order_id` and `product_id` has a matching record in `silver.orders` and `silver.products`. |
<br/>

**Outcome:**

- `silver.returns` confirmed clean — zero-refund pattern validated as expected business behavior
- Consistent snake_case column naming and clean formatting throughout

**Tags**


##### Input 24
**Type:** Short Answer

**Question:** Did you discover any data quality issues in this dataset beyond the ones listed above? For each, describe what you found, how you investigated it, and the action you took.

**Template:** null

**Tags**
- approach / concept-clarity (skill)

##### Input 25
**Type:** File Upload

**Question:** Upload your completed `returns` Silver notebook, and a screenshot showing five sample rows from table

**Max No. of Files:** 4

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**
- data-quality / data-consistency (skill)
- data-quality / integrity (skill)
- data-wrangling / text-processing (skill)

##### Input 26
**Type:** Text

>[!CAUTION]
> Please ensure all 8 Silver tables are created and verified before moving forward. You will not be able to return to this activity.

>[!IMPORTANT] 
> Enable Change Data Feed (CDF) on all Bronze tables before proceeding. CDF allows the Silver layer to track only the rows that changed since the last run, inserts, updates, and deletes, so that future incremental loads do not need to rescan the entire Bronze table.

```
CATALOG = "<your-catalog>"
SCHEMA  = "silver"

BRONZE_TABLES = [
    "customers", "addresses", "payments", "payment_methods",
    "products", "returns", "orders", "order_items"
]

for table in BRONZE_TABLES:
    full_name = f"{CATALOG}.{SCHEMA}.{table}"
    spark.sql(f"""
        ALTER TABLE {full_name}
        SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
    """)
    print(f"CDF enabled: {full_name}")
```

**Tags**


