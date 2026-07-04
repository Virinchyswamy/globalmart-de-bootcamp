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
  - databricks (tool)
  - spark (tool)
  - sql (tool)
  - data-storage (skill)
  - data-wrangling (skill)
  - data-quality (skill)
  - data-understanding (skill)
  - approach (skill)
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
- `ex_customers.csv` — 336 GlobalMart customer records, 6 columns: `customer_id`, `customer_email`, `customer_name`, `segment`, `postal_code`, `joining_date`
- `ex_orders.csv` — 4,909 GlobalMart orders, 10 columns: `order_id`, `customer_id`, `partner_id`, `ship_mode`, `order_status`, `order_purchase_date`, `order_approved_at`, `order_dispatched_date`, `order_delivered_date`, `order_estimated_delivery_date`
- `ex_products.csv` — 1,778 GlobalMart catalog products, 11 columns: `product_id`, `product_name`, `colors`, `category`, `sub_category`, `date_added`, `manufacturer`, `sizes`, `upc`, `weight`, `product_photos_qty`

**Tags**
- data-understanding (skill)

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

**Tags**
- databricks (tool)
- data-storage (skill)

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

**Tags**
- databricks (tool)
- data-storage (skill)

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

**Tags**
- databricks (tool)
- approach (skill)

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

**Overview:** With customers, orders, and products sitting in your Volume, you will load all three into DataFrames, join them to answer real business questions, apply PySpark transformations, catch a genuine data quality gap in the product catalog, and write cleaned Bronze Delta tables.

**Outcome:** Three cleaned Bronze Delta tables — `bronze/customers`, `bronze/orders`, `bronze/products` — plus answers to five real GlobalMart business questions.

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

**Tags**
- spark (tool)
- data-understanding (skill)

---

## Input 10

**Type:** Short Answer

**Question:** How many rows are in each of the three DataFrames? Name one column in `orders_df` that Spark inferred as a date/timestamp type, and one column it inferred as a string.

**Template:** null

**Tags**
- data-understanding (skill)
- data-wrangling (skill)

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

Register all three DataFrames as temporary SQL views:

```python
customers_df.createOrReplaceTempView("customers")
orders_df.createOrReplaceTempView("orders")
products_df.createOrReplaceTempView("products")
print("All three temp views registered.")
```

**Business Question 1 — Customer segments:**

```sql
SELECT segment,
       COUNT(*) AS customer_count
FROM customers
GROUP BY segment
ORDER BY customer_count DESC
```

**Tags**
- sql (tool)
- data-wrangling (skill)

---

## Input 13

**Type:** Short Answer

**Question:** Which customer segment has the most customers? How many? Paste your query output.

**Template:** null

**Tags**
- sql (tool)
- data-wrangling (skill)

---

## Input 14

**Type:** Code

**Question:** Write a Spark SQL query to count orders by `order_status`, sorted from most common to least common status.

**Language:** sql

**Snippet:**

**Tags**
- sql (tool)
- data-wrangling / group-by-aggregate (skill)

---

## Input 15

**Type:** Short Answer

**Question:** Which order status is the most common? Roughly what percentage of all orders does it represent?

**Template:** null

**Tags**
- sql (tool)
- data-wrangling (skill)

---

## Input 16

**Type:** Code

**Question:** GlobalMart's marketing team wants to send a "we miss you" email to any customer who has **never placed a single order**. Write a Spark SQL query using a `LEFT JOIN` between `customers` and `orders` (joined on `customer_id`) that returns only customers with zero orders. Hint: filter on `WHERE order_id IS NULL` after the join.

**Language:** sql

**Snippet:**

**Tags**
- sql (tool)
- data-wrangling / joins (skill)

---

## Input 17

**Type:** Short Answer

**Question:** How many customers have never placed an order? List their `customer_id` values.

**Template:** null

**Tags**
- sql (tool)
- data-wrangling (skill)

---

## Input 18

**Type:** Code

**Question:** Write a Spark SQL query to count orders placed in each year, using `YEAR(order_purchase_date)`. Sort from most recent year to oldest.

**Language:** sql

**Snippet:**

**Tags**
- sql (tool)
- data-wrangling / date-processing (skill)

---

## Input 19

**Type:** Short Answer

**Question:** In which year were the most orders placed? How many orders were placed that year?

**Template:** null

**Tags**
- sql (tool)
- data-wrangling (skill)

---

## Input 20

**Type:** Text

### Phase C — PySpark Transformations

**Task 1 — Calculate delivery time:**

```python
from pyspark.sql.functions import col, datediff, when, trim, avg, count

delivered_orders = orders_df.filter(col("order_status") == "delivered")

delivered_with_days = delivered_orders.withColumn(
    "delivery_days",
    datediff(col("order_delivered_date"), col("order_purchase_date"))
)

delivered_with_days.agg(
    avg("delivery_days").alias("avg_delivery_days")
).show()
```

**Tags**
- spark (tool)
- data-wrangling / date-processing (skill)

---

## Input 21

**Type:** Short Answer

**Question:** What is the average delivery time, in days, for delivered orders?

**Template:** null

**Tags**
- data-wrangling (skill)
- data-wrangling / date-processing (skill)

---

## Input 22

**Type:** Code

**Question:** Using `when / otherwise`, add a `delivery_speed` column to `delivered_with_days` that classifies each order as `"Fast"` (3 days or fewer), `"Normal"` (4–7 days), or `"Slow"` (more than 7 days). Then use `groupBy` to count how many orders fall into each tier.

**Language:** python

**Snippet:**

**Tags**
- data-wrangling (skill)
- data-wrangling / dataframe-processing (skill)
- approach (skill)

---

## Input 23

**Type:** Short Answer

**Question:** How many delivered orders fall into each delivery speed tier (Fast / Normal / Slow)?

**Template:** null

**Tags**
- data-wrangling (skill)

---

## Input 24

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

**Tags**
- data-quality (skill)
- spark (tool)

---

## Input 25

**Type:** Short Answer

**Question:** What percentage of products are missing a `manufacturer` value? Why is it risky to write this straight to a Bronze table without flagging the gap, even though Bronze is supposed to stay "raw and unmodified"?

**Template:** null

**Tags**
- data-quality (skill)
- data-wrangling (skill)

---

## Input 26

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

**Tags**
- data-storage (skill)
- spark (tool)

---

## Input 27

**Type:** File Upload

**Question:** Take a screenshot of your Databricks notebook showing the Bronze write output with all three row counts. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)
- data-storage (skill)

---

## Input 28

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

## Input 29

**Type:** File Upload

**Question:** Upload your completed Databricks notebook (.ipynb file). Your notebook never contained a storage account key, so there is nothing to redact before submitting.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, JUPYTER_NOTEBOOK

**Tags**
- databricks (tool)
