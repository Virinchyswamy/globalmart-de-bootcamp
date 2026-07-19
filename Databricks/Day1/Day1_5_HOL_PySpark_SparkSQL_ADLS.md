---
name: Day 1 HOL — PySpark & Spark SQL with Databricks Volumes
content_type: Project
overview: GlobalMart is a fast-growing e-commerce company that needs a reliable data platform to power its analytics. In this hands-on exercise, you will upload real GlobalMart customer, order, and product data into a Databricks Volume, read it into a notebook, and explore it using PySpark and Spark SQL. By the end, you will have cleaned Bronze Delta tables ready for further processing — and you will have done it without ever touching a storage account key.
learning_objectives:
  - Upload CSV datasets into a Databricks Unity Catalog Volume
  - Read files directly from a Volume path in a notebook — no external storage connection needed
  - Explore and join multiple DataFrames using PySpark and Spark SQL
  - Apply PySpark transformations, including filtering, derived columns, and conditional classification
  - Identify and quantify a real data quality issue
  - Write cleaned DataFrames to Bronze Delta tables
prerequisites:
  - A Databricks workspace already created (provided by your instructor)
  - Completed Day 1 ILT 4 — Intro to Databricks + PySpark & Spark SQL
duration: 60 minutes
level: Beginner
industries:
  - e-commerce
tags:
  - data-wrangling (skill)
  - data-quality (skill)
  - databricks (tool)
  - spark (tool)
---

---

## Scenario 1 — Working with Databricks Volumes

**Overview:** Before you can use data in Databricks, it needs to live somewhere the cluster can read it. Instead of setting up cloud storage from scratch, you will use a **Databricks Volume** — a Unity Catalog-managed storage location you can upload files into directly from the Databricks UI. No storage account, no container, no access key. In this scenario you will upload three real GlobalMart datasets — customers, orders, and products — into your own Volume.

**Outcome:** Three CSV files sitting inside a Volume, organized into `customers/`, `orders/`, and `products/` folders, ready to be read by a notebook with zero credentials.

---

## Input 1

**Type:** Text

>[!IMPORTANT]
>Ensure you download all three datasets below before proceeding with the hands-on.

**Datasets:**
- `ex_customers.csv` — 337 GlobalMart customer records, 6 columns: `customer_id`, `customer_email`, `customer_name`, `segment`, `postal_code`, `joining_date`
  Download from here: https://cdn.enqurious.com/documents/952b52f7-c480-4ada-a0a9-313679bf0486_excustomers.csv
- `ex_orders.csv` — 4,910 GlobalMart orders, 10 columns: `order_id`, `customer_id`, `partner_id`, `ship_mode`, `order_status`, `order_purchase_date`, `order_approved_at`, `order_dispatched_date`, `order_delivered_date`, `order_estimated_delivery_date`
  Download from here: https://cdn.enqurious.com/documents/4b40a04c-65da-4936-9268-74ecb38364bd_exorders.csv
- `ex_products.csv` — 1,779 GlobalMart catalog products, 11 columns: `product_id`, `product_name`, `colors`, `category`, `sub_category`, `date_added`, `manufacturer`, `sizes`, `upc`, `weight`, `product_photos_qty`
  Download from here: https://cdn.enqurious.com/documents/d5ac744f-01de-4b3d-b5c1-a0382ecba404_exproducts.csv

---

## Input 2

**Type:** Text

### Instructions: Create a Unity Catalog Volume

A **Volume** is a Unity Catalog object that represents a folder of raw files (not tables) — the modern, keyless replacement for "go set up a storage account." Follow these steps:

1. In your Databricks workspace, click **Catalog** in the left sidebar.

2. Navigate to the catalog your instructor has given you access to (commonly `workspace`), then into a schema you can write to. If you have permission to create your own schema, do this instead:
   - Click **Create** → **Schema**
   - **Catalog:** the catalog your instructor gave you
   - **Schema name:** your own name in lowercase, e.g. `virinchy` (no spaces)
   - Click **Create**

3. Inside your schema, click **Create** → **Volume**.
   - **Volume name:** `raw_data`
   - **Volume type:** Managed
   - Click **Create**

4. You now have a Volume at the path `/Volumes/<catalog>/<your_schema>/raw_data/` — this is your keyless landing zone. Anyone in the workspace with permission can read it; nobody needs a password to do so.

> **Why this replaces a storage account + key:** a Volume is already inside Unity Catalog, so it is governed the same way as every table you will build later in this course — permissions, audit logs, and lineage all apply automatically. There is no key to leak, rotate, or accidentally commit to GitHub.

---

## Input 3

**Type:** Short Answer

**Question:** What is the full path to the Volume you created? (Format: `/Volumes/<catalog>/<schema>/<volume_name>/`)

**Template:** null

**Tags**
- databricks (tool)
- data-storage (skill)

---

## Input 4

**Type:** Text

### Instructions: Create Folders and Upload the Datasets

You are now inside your Volume. Create one folder per dataset and upload each file into its own folder.

1. Click **Create** → **Folder**, name it `customers`, click **Create**.
2. Click into the `customers` folder, click **Upload to this volume**, select `ex_customers.csv` from your computer, and upload it.
3. Go back to the Volume root. Repeat step 1 with the folder name `orders`, and upload `ex_orders.csv` into it.
4. Go back to the Volume root. Repeat step 1 with the folder name `products`, and upload `ex_products.csv` into it.
5. You should now see three folders inside your Volume, each containing exactly one CSV file.

---

## Input 5

**Type:** File Upload

**Question:** Take a screenshot of the Volume browser showing all three folders (`customers`, `orders`, `products`), each containing its file. Upload your screenshot here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)

---

## Input 6

**Type:** Choice

**Question:** What is the correct path format for a file inside a Unity Catalog Volume?

**Options:**
- `abfss://<container>@<account>.dfs.core.windows.net/<path>`
- `/Volumes/<catalog>/<schema>/<volume_name>/<path>`
- `dbfs:/mnt/<mount_name>/<path>`
- `s3://<bucket>/<path>`

**Correct Options:**
- `/Volumes/<catalog>/<schema>/<volume_name>/<path>`

**Solution:**
Unity Catalog Volumes are always addressed as `/Volumes/<catalog>/<schema>/<volume_name>/<path>` — the same three-level namespace (catalog.schema.object) used for tables, just for files instead of rows and columns. `abfss://` is the ADLS Gen2 protocol used when connecting to external storage directly with a key — a Volume never needs it.

**Tags**
- databricks (tool)
- data-storage (skill)

---

## Input 7

**Type:** Text

### Instructions: Read the Volume From a Notebook

1. Open your **Databricks workspace** and create a new notebook. Name it `Day1_HOL_PySpark_SparkSQL`.

2. Make sure your **cluster is running**. If it is not, click the cluster name at the top of the notebook and start it. Wait for the green dot before continuing.

3. In the first cell of your notebook, paste and run this setup code. Replace the placeholder with your own catalog/schema:

```python
# ─── Volume Setup ───────────────────────────────────────────────────────────
# HOW TO GET THIS VALUE: Catalog (left sidebar) → your catalog → your schema
# → raw_data volume → the path is shown at the top of the Volume browser, or
# copy it from Input 3 above.
# No key, no spark.conf.set(), no storage account -- Unity Catalog already
# knows who you are and what you're allowed to read.
volume_path = "/Volumes/YOUR_CATALOG/YOUR_SCHEMA/raw_data"   # ← replace with your path

customers_path = f"{volume_path}/customers/ex_customers.csv"
orders_path    = f"{volume_path}/orders/ex_orders.csv"
products_path  = f"{volume_path}/products/ex_products.csv"

# List what's actually in the volume -- a quick sanity check before reading
display(dbutils.fs.ls(volume_path))
```

4. Press **Shift + Enter** to run the cell.

5. If you see your three folders (`customers`, `orders`, `products`) listed below the cell, you are ready for Scenario 2.

---

## Input 8

**Type:** File Upload

**Question:** Take a screenshot of your Databricks notebook showing the `dbutils.fs.ls()` output with your three folders listed. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)

---

## Scenario 2 — Data Wrangling with PySpark & Spark SQL

**Overview:** With customers, orders, and products sitting in your Volume, you will load all three into DataFrames, query and join them with Spark SQL, apply PySpark transformations, catch a genuine data quality gap in the product catalog, and write cleaned Bronze Delta tables.

**Outcome:** Three cleaned Bronze Delta tables — `bronze/customers`, `bronze/orders`, `bronze/products` — plus seven real GlobalMart business questions answered directly in code, and a documented, quantified data quality gap in the product catalog.

> Continue working in the same notebook you created in Scenario 1. Add new cells below the setup cell for each question.

---

## Input 9

**Type:** Text

### Phase A — Understand the Data

In a new cell, load all three datasets and explore their structure:

```python
customers_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(customers_path)
)

orders_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(orders_path)
)

products_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(products_path)
)

for name, df in [("customers", customers_df), ("orders", orders_df), ("products", products_df)]:
    print(f"--- {name} ---")
    print(f"Rows: {df.count()}")
    df.printSchema()
```

---

## Input 10

**Type:** Short Answer

**Question:** How many rows are in each of the three DataFrames? Name one column in `orders_df` that Spark inferred as a date/timestamp type, and one column it inferred as a string.

**Template:** null

**Tags**
- data-understanding (skill)

---

## Input 11

**Type:** Choice

**Question:** What does `.option("inferSchema", "true")` do when reading a CSV file?

**Options:**
- It reads the first row as column headers
- It automatically detects the data type of each column
- It removes rows with null values
- It converts all columns to String type

**Correct Options:**
- It automatically detects the data type of each column

**Solution:**
Without inferSchema, Spark reads every column as a String. With inferSchema=True, Spark scans the file and assigns the most appropriate type (StringType, DateType, IntegerType, etc.) to each column. In production you would define the schema explicitly for performance and safety — but for exploration, inferSchema is convenient.

**Tags**
- data-understanding (skill)
- approach (skill)

---

## Input 12

**Type:** Text

### Phase B — Spark SQL

Register all three DataFrames as temporary SQL views so each one can be queried directly with Spark SQL:

```python
customers_df.createOrReplaceTempView("customers")
orders_df.createOrReplaceTempView("orders")
products_df.createOrReplaceTempView("products")
print("All three temp views registered.")
```

Run one quick sanity check to confirm the views are working before moving on to the real business questions:

```sql
SELECT COUNT(*) AS customer_count FROM customers
```

---

## Input 13

**Type:** Code

**Question:** GlobalMart's leadership wants a breakdown of the customer base by segment for an upcoming board presentation. Using Spark SQL, write a query that shows how many customers fall into each segment, sorted from most to least. State which segment has the most customers and how many.

**Language:** sql

**Snippet:**

**Solution:**
```sql
SELECT segment,
       COUNT(*) AS customer_count
FROM customers
GROUP BY segment
ORDER BY customer_count DESC
```
Grouping `customers` by `segment` and sorting the counts descending shows **Consumer** as the largest segment with **177** customers, followed by Corporate (105) and Home Office (55) — out of 337 customers total.

**Tags**
- sql (tool)
- data-wrangling / group-by-aggregate (skill)
- data-wrangling / sort (skill)

---

## Input 14

**Type:** Code

**Question:** GlobalMart's operations team wants to understand how orders are distributed across fulfillment statuses so they can spot bottlenecks. Using Spark SQL, write a query that counts orders by their status, sorted from most common to least common. State which status is most common and roughly what percentage of all orders it represents.

**Language:** sql

**Snippet:**

**Solution:**
```sql
SELECT order_status,
       COUNT(*) AS order_count
FROM orders
GROUP BY order_status
ORDER BY order_count DESC
```
`delivered` is by far the most common status, with 4,762 of the 4,910 total orders — about **97.0%**. The remaining statuses (shipped=63, canceled=28, unavailable=26, processing=18, invoiced=12, created=1) together make up the last 3%.

**Tags**
- sql (tool)
- data-wrangling / group-by-aggregate (skill)
- data-wrangling / sort (skill)

---

## Input 15

**Type:** Code

**Question:** GlobalMart's marketing team wants to send a "we miss you" email to every customer who has never placed a single order — but first they need the actual list. Using Spark SQL, write a query that finds every customer who has never placed a single order. State how many there are and list their customer_id values.

**Language:** sql

**Snippet:**

**Solution:**
```sql
SELECT c.customer_id, c.customer_name, c.segment
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
```
A `LEFT JOIN` from `customers` to `orders` keeps every customer row regardless of whether a matching order exists; filtering to rows where `o.order_id IS NULL` isolates the customers with no matching order at all. There are **5** such customers: `GB-10000`, `LU-10002`, `PX-10004`, `SQ-10003`, `UL-10001`.

**Tags**
- sql (tool)
- data-wrangling / joins (skill)
- data-wrangling / filter (skill)

---

## Input 16

**Type:** Code

**Question:** GlobalMart wants to see how order volume has grown year over year. Using Spark SQL, write a query that counts how many orders were placed in each year. Sort from most recent year to oldest. State which year had the most orders and how many.

**Language:** sql

**Snippet:**

**Solution:**
```sql
SELECT YEAR(order_purchase_date) AS order_year,
       COUNT(*) AS order_count
FROM orders
GROUP BY order_year
ORDER BY order_year DESC
```
Extracting the year from `order_purchase_date` and grouping by it shows order volume growing sharply over time: 2016 had 17 orders, 2017 had 2,196, and 2018 had the most with **2,697** orders — out of 4,910 total.

**Tags**
- sql (tool)
- data-wrangling / date-processing (skill)
- data-wrangling / group-by-aggregate (skill)

---

## Input 17

**Type:** Text

### Phase C — PySpark Transformations

Filter `orders_df` down to only delivered orders, then add a `delivery_days` column measuring the gap between purchase and delivery:

```python
from pyspark.sql.functions import col, datediff, when, trim, avg

delivered_orders = orders_df.filter(col("order_status") == "delivered")

delivered_with_days = delivered_orders.withColumn(
    "delivery_days",
    datediff(col("order_delivered_date"), col("order_purchase_date"))
)

print(f"Delivered orders: {delivered_with_days.count()}")
```

---

## Input 18

**Type:** Code

**Question:** Using PySpark, write code that computes the average delivery time, in days, across all delivered orders using the `delivery_days` column you just derived.

**Language:** python

**Snippet:**

**Solution:**
```python
delivered_with_days.agg(
    avg("delivery_days").alias("avg_delivery_days")
).show()
```
Averaging `delivery_days` across all 4,762 delivered orders gives an average delivery time of **12.37 days**.

**Tags**
- spark (tool)
- data-wrangling / aggregate (skill)
- data-wrangling / math-calculations (skill)

---

## Input 19

**Type:** Code

**Question:** GlobalMart's customer experience team wants to understand how delivery speed actually feels to customers, not just the average. Using PySpark, add a column that classifies each delivered order's speed into three tiers based on `delivery_days`: 3 days or fewer, 4 to 7 days, and more than 7 days. Then report how many orders fall into each tier.

**Language:** python

**Snippet:**

**Solution:**
```python
orders_with_speed = delivered_with_days.withColumn(
    "delivery_speed",
    when(col("delivery_days") <= 3, "Fast")
    .when(col("delivery_days") <= 7, "Normal")
    .otherwise("Slow")
)

orders_with_speed.groupBy("delivery_speed").count().orderBy("delivery_speed").show()
```
Chaining `when/otherwise` builds the three-tier label column, and `groupBy("delivery_speed").count()` tallies each tier: **Fast** (≤3 days) = 370 orders, **Normal** (4–7 days) = 1,189 orders, **Slow** (>7 days) = 3,203 orders — out of 4,762 delivered orders. Most delivered orders actually take longer than a week, even though the average of 12.37 days looks reasonable on its own.

**Tags**
- spark (tool)
- data-wrangling / conditional-logic (skill)
- data-wrangling / derived-column (skill)
- data-wrangling / group-by-aggregate (skill)

---

## Input 20

**Type:** Text

### Phase D — Data Quality Check

Real product catalogs are rarely complete. Check how much of the `products` data is missing a `manufacturer` value:

```python
total_products = products_df.count()
missing_manufacturer = products_df.filter(
    col("manufacturer").isNull() | (trim(col("manufacturer")) == "")
).count()

pct_missing = round(100 * missing_manufacturer / total_products, 1)
print(f"Products missing manufacturer: {missing_manufacturer} / {total_products} ({pct_missing}%)")

products_df.groupBy("category").count().orderBy(col("count").desc()).show()
```

Running this shows **1,047** of the **1,779** products (**58.9%**) are missing a manufacturer value — a significant gap in the catalog.

---

## Input 21

**Type:** Code

**Question:** The overall 58.9% figure hides a lot of detail. Using PySpark, additionally compute what percentage of products are missing a manufacturer value within each product category (not just overall), and report your findings. Then explain why it would be risky to write this data straight into a Bronze table without flagging the gap, even though Bronze is supposed to stay "raw and unmodified."

**Language:** python

**Snippet:**

**Solution:**
```python
from pyspark.sql.functions import col, trim, round

# Total products per category
total_by_category = (
    products_df
    .groupBy("category")
    .count()
    .withColumnRenamed("count", "total")
)

# Products per category that are missing a manufacturer
missing_by_category = (
    products_df
    .filter(col("manufacturer").isNull() | (trim(col("manufacturer")) == ""))
    .groupBy("category")
    .count()
    .withColumnRenamed("count", "missing")
)

# Join the two counts together and compute the percentage
category_gap = (
    missing_by_category
    .join(total_by_category, on="category")
    .withColumn("pct_missing", round(100 * col("missing") / col("total"), 1))
)

category_gap.orderBy(col("pct_missing").desc()).show()
```
This reuses the same three building blocks from earlier in this notebook — `filter()` to isolate the missing rows, `groupBy().count()` to total each category two different ways, and a `join()` to bring both totals onto the same row — instead of introducing a new technique. The result shows the gap is not evenly spread, but it is consistently bad everywhere: **Office Supplies** is missing manufacturer for 625 of 1,043 products (**59.9%**), **Furniture** for 217 of 364 (**59.6%**), and **Technology** for 205 of 372 (**55.1%**) — all close to the 58.9% overall figure, so no single category is masking or hiding the problem.

Writing this straight into Bronze without flagging the gap is risky because "raw and unmodified" describes what happens to the *values* in Bronze — it does not mean staying silent about *known* problems with those values. A Silver or Gold consumer downstream has no way to discover, on their own, that nearly 6 in 10 products have no manufacturer recorded. If that gap isn't surfaced somewhere (a data quality metric, a monitoring check, a documented known-issue note), it will quietly propagate into every manufacturer-based report or join built on top of Bronze, and someone will eventually make a business decision on incomplete data without knowing it.

**Tags**
- spark (tool)
- data-quality / missing-values (skill)
- data-wrangling / group-by-aggregate (skill)
- data-wrangling / conditional-logic (skill)

---

## Input 22

**Type:** Text

### Phase E — Write to Bronze

Write all three cleaned DataFrames to the Bronze layer as Delta tables, inside your own Volume. Use `overwrite` mode so you can safely re-run this cell without creating duplicates:

```python
bronze_path = f"{volume_path}/bronze"

customers_df.write.format("delta").mode("overwrite").save(f"{bronze_path}/customers")
orders_df.write.format("delta").mode("overwrite").save(f"{bronze_path}/orders")
products_df.write.format("delta").mode("overwrite").save(f"{bronze_path}/products")

for name in ["customers", "orders", "products"]:
    bronze_df = spark.read.format("delta").load(f"{bronze_path}/{name}")
    print(f"bronze/{name}: {bronze_df.count()} rows written")
```

---

## Input 23

**Type:** File Upload

**Question:** Take a screenshot of your Databricks notebook showing the Bronze write output with all three row counts. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)
- data-storage (skill)

---

## Input 24

**Type:** Choice

**Question:** GlobalMart's data engineering team wants to add new order records that arrive every day to the Bronze `orders` table, preserving all historical data. Which of the following commands should they use?

**Options:**
- df.write.mode("overwrite").format("delta").save(bronze_path)
- df.write.mode("append").format("delta").save(bronze_path)
- df.write.mode("replace").format("delta").save(bronze_path)
- df.write.mode("insert").format("delta").save(bronze_path)

**Correct Options:**
- df.write.mode("append").format("delta").save(bronze_path)

**Solution:**
`overwrite` deletes everything at the destination path and writes fresh data. `append` adds new rows on top of existing data without touching what is already there. Use `overwrite` for small reference tables that are fully refreshed. Use `append` for tables that grow over time, like new daily order files.

**Tags**
- data-storage (skill)
- approach (skill)

---

## Input 25

**Type:** File Upload

**Question:** Upload your completed Databricks notebook (.ipynb file). Your notebook never contained a storage account key, so there is nothing to redact before submitting.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, JUPYTER_NOTEBOOK

**Tags**
- databricks (tool)
