---
Content Type: Project
Overview: In this hands-on exercise, you will set up Azure Data Lake Storage Gen2 from scratch, upload a real customer dataset, connect your Databricks workspace to ADLS using a storage access key, and then explore the data using PySpark and Spark SQL. By the end, you will have a cleaned Bronze Delta table ready for further processing.
Learning Objectives:
  - Create an Azure Storage Account with ADLS Gen2 (Hierarchical Namespace) enabled
  - Upload a CSV dataset to a structured folder hierarchy in ADLS
  - Connect Azure Databricks to ADLS using a storage access key
  - Explore and transform a DataFrame using PySpark and Spark SQL
  - Write a cleaned DataFrame to a Bronze Delta table
Prerequisites:
  - Access to an Azure subscription (provided by your instructor)
  - A Databricks workspace already created (provided by your instructor)
  - Completed Day 1 ILT 4 — Intro to Databricks + PySpark & Spark SQL
Duration: 60 minutes
Level: Beginner
Industries: e-commerce
Tags: azure, adls, databricks, pyspark, spark-sql, data-wrangling, delta-lake, bronze-layer
---

## Dataset

**File:** customers_010626.csv
**Description:** GlobalMart customer records — 6,666 rows, 8 columns
**Columns:** CustomerID, FirstName, LastName, Email, PhoneNumber, DateOfBirth, RegistrationDate, PreferredPaymentMethodID

[Download customers_010626.csv — attach file here]

---

## Scenario 1: Working with Azure

**Overview:** Before you can use data in Databricks, it needs to live somewhere in the cloud. In this scenario, you will create your own Azure Data Lake Storage Gen2 account, set up the folder structure GlobalMart uses, and upload the customer dataset.

**Outcome:** A storage account with `customers_010626.csv` sitting at `amazon-data/raw/customers/`, ready to be read by Databricks.

---

### Input 1 — Create Your Azure Storage Account

**Instructions:**

Follow these steps carefully. This is your first time setting up cloud storage, so read each step before clicking.

1. Go to [https://portal.azure.com](https://portal.azure.com) and sign in with the Azure credentials provided by your instructor.

2. In the **search bar at the top**, type `Storage accounts` and click the result.

3. Click **+ Create** (top-left button).

4. Fill in the **Basics** tab:
   - **Subscription:** select the subscription provided to you
   - **Resource group:** click *Create new* → name it `globalmart-rg` → click OK
   - **Storage account name:** choose a unique all-lowercase name. Example: `globalmartfirstname` (no spaces, no special characters, 3–24 characters)
   - **Region:** East US (or the region your instructor specifies)
   - **Performance:** Standard
   - **Redundancy:** Locally-redundant storage (LRS)

5. Click the **Advanced** tab at the top of the form.

6. Under **Data Lake Storage Gen2**, check the box next to **Enable hierarchical namespace**.
   > This is the key step that turns a regular Blob storage account into ADLS Gen2. Without it, Databricks cannot use the `abfss://` protocol.

7. Leave all other settings as default.

8. Click **Review + Create** → then **Create**.

9. Wait for the deployment to complete (usually 30–60 seconds). You will see a green tick and "Your deployment is complete."

10. Click **Go to resource**.

**Question:** What is the exact name of the storage account you created?

**Answer type:** Short text

---

### Input 2 — Create Container and Upload the Dataset

**Instructions:**

You are now inside your storage account. Follow these steps to create the folder structure and upload the file.

1. In the left menu, click **Containers** (under the *Data storage* section).

2. Click **+ Container**.
   - Name: `amazon-data`
   - Public access level: *Private (no anonymous access)*
   - Click **Create**

3. Click on the **amazon-data** container to open it.

4. Click **+ Add Directory** → type `raw` → click **Save**.

5. Click on the **raw** folder to open it.

6. Click **+ Add Directory** → type `customers` → click **Save**.

7. You are now inside `amazon-data/raw/customers/`. This is where your file will land.

8. Click the **⬆ Upload** button.
   - Click *Browse for files* and select `customers_010626.csv` from your computer
   - Click **Upload**

9. Wait for the upload to complete. You should see `customers_010626.csv` listed in the folder.

**Question:** Take a screenshot of the Azure Storage Browser showing `customers_010626.csv` inside the `raw/customers/` folder. Upload your screenshot here.

**Answer type:** File upload (image)

---

### Input 3 — Find Your Storage Access Key

**Instructions:**

To connect Databricks to your storage account, you need the Storage Account Access Key. Here is how to find it:

1. In your storage account, look at the **left-side menu**.

2. Scroll down to the **Security + networking** section.

3. Click **Access keys**.

4. You will see **key1** and **key2**. Click **Show** next to *key1*.

5. Copy the key value — you will paste it into your Databricks notebook in Scenario 2.

> ⚠️ **Important:** Never share this key publicly or commit it to GitHub. It gives full access to your storage account. Treat it like a password.

**Question:** Where exactly in the Azure Portal did you find the storage access key? Describe the navigation path (e.g. "Left menu → Security + networking → Access keys").

**Answer type:** Short text

---

### Input 4 — Screenshot: Access Keys Page

**Question:** Take a screenshot of the Access Keys page. **Before uploading, blur or cover the actual key value** — do not share your real key. We just want to confirm you found the right page.

**Answer type:** File upload (image)

---

### Input 5 — Knowledge Check: ADLS Protocol

**Question:** Which protocol does Databricks use to read files from ADLS Gen2?

- a) `wasbs://` — Windows Azure Storage Blob Secure
- b) `abfss://` — Azure Blob File System Secure ✓
- c) `https://` — Standard web protocol
- d) `hdfs://` — Hadoop Distributed File System

**Correct answer:** b) `abfss://`

**Explanation:** ADLS Gen2 uses the Azure Blob File System (ABFS) driver. The `abfss://` (secure version) protocol is the standard way Databricks connects to ADLS Gen2. The path format is: `abfss://CONTAINER@STORAGEACCOUNT.dfs.core.windows.net/FOLDER/`

**Answer type:** Choice (single correct)

---

### Input 6 — Write Your ADLS Path

**Instructions:**

The `abfss://` path follows this exact format:

```
abfss://CONTAINER@STORAGEACCOUNT.dfs.core.windows.net/FOLDER/SUBFOLDER/
```

For GlobalMart's setup:
- Container = `amazon-data`
- Storage account = whatever you named yours in Input 1
- Folder path = `raw/customers/`

**Example** (if your storage account is called `globalmartvirincy`):
```
abfss://amazon-data@globalmartvirincy.dfs.core.windows.net/raw/customers/
```

**Question:** Write the full `abfss://` path to your `raw/customers/` folder using your own storage account name.

**Answer type:** Short text

---

### Input 7 — Connect Databricks to ADLS

**Instructions:**

1. Open your **Databricks workspace** and create a new notebook. Name it `Day1_HOL_PySpark_SparkSQL`.

2. Make sure your **cluster is running**. If it is not, click the cluster name at the top of the notebook and start it. Wait for the green dot before continuing.

3. In the first cell of your notebook, paste and run this setup code (replace the two placeholder values):

```python
# ─── ADLS Connection Setup ─────────────────────────────────────────────────
storage_account_name = "YOUR_STORAGE_ACCOUNT_NAME"   # ← replace with your storage account name
container_name       = "amazon-data"
storage_account_key  = "YOUR_STORAGE_ACCOUNT_KEY"    # ← replace with the key you copied

spark.conf.set(
    f"fs.azure.account.key.{storage_account_name}.dfs.core.windows.net",
    storage_account_key
)

base_path    = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net"
raw_path     = f"{base_path}/raw/customers"
bronze_path  = f"{base_path}/bronze/customers"

print("Connection successful!")
print(f"Raw path:    {raw_path}")
print(f"Bronze path: {bronze_path}")
```

4. Press **Shift + Enter** to run the cell.

5. If you see `Connection successful!` printed below the cell, you are ready to continue.

**Question:** Take a screenshot of your Databricks notebook showing the setup cell output with "Connection successful!" Upload it here.

**Answer type:** File upload (image)

---

## Scenario 2: Data Wrangling with PySpark & Spark SQL

**Overview:** With the customer data now in ADLS and Databricks connected, you will explore the dataset, answer business questions using Spark SQL, apply PySpark transformations, and finally write a clean version of the data to a Bronze Delta table.

**Outcome:** A cleaned Bronze Delta table at `bronze/customers/` with correct data types, trimmed strings, and a new `LoyaltyTier` column.

> **Tip:** Continue working in the same notebook you created in Scenario 1. Add new cells below the setup cell for each question.

---

### Phase A — Understand the Data

---

### Input 8 — Read the CSV and Explore

**Instructions:**

In a new cell in your notebook, paste and run this code:

```python
# Read customers CSV from ADLS
customers_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{raw_path}/customers_010626.csv")
)

# Explore
print(f"Total rows: {customers_df.count()}")
print("\nSchema:")
customers_df.printSchema()

print("\nFirst 5 rows:")
customers_df.show(5, truncate=False)
```

**Question:** How many rows are in the dataset? List all 8 column names and their data types as detected by Spark.

**Answer type:** Short text

---

### Input 9 — Knowledge Check: inferSchema

**Question:** What does `.option("inferSchema", "true")` do when reading a CSV file?

- a) It reads the first row as column headers
- b) It automatically detects the data type of each column ✓
- c) It removes rows with null values
- d) It converts all columns to String type

**Correct answer:** b)

**Explanation:** Without `inferSchema`, Spark reads every column as a String. With `inferSchema=True`, Spark scans the file and assigns the most appropriate type (IntegerType, DateType, StringType, etc.) to each column automatically. In production you would define the schema explicitly for speed and safety.

**Answer type:** Choice (single correct)

---

### Phase B — Spark SQL

---

### Input 10 — Register a Temp View and Query Payment Methods

**Instructions:**

First, register the DataFrame as a temporary SQL view so you can query it using standard SQL:

```python
customers_df.createOrReplaceTempView("customers")
```

Now run this Spark SQL query in a new `%sql` cell (or using `spark.sql()`):

```sql
-- How many customers prefer each payment method?
SELECT PreferredPaymentMethodID,
       COUNT(*) AS customer_count
FROM customers
GROUP BY PreferredPaymentMethodID
ORDER BY customer_count DESC
```

**Question:** Which payment method has the highest number of customers? How many customers prefer it?

**Answer type:** Short text + paste your query output

---

### Input 11 — Customers Registered Per Year

**Instructions:**

Write a Spark SQL query to find how many customers registered in each year. Sort the results from most recent year to oldest.

**Hint:** Use the `YEAR()` function to extract the year from the `RegistrationDate` column.

```sql
-- Your query here
SELECT YEAR(RegistrationDate) AS registration_year,
       COUNT(*) AS customer_count
FROM customers
GROUP BY registration_year
ORDER BY registration_year DESC
```

**Question:** In which year did the most customers register? How many?

**Answer type:** Short text + paste your query output

---

### Input 12 — Customers Born in the 1990s

**Instructions:**

Write a Spark SQL query to find all customers born between 1 January 1990 and 31 December 1999.

**Hint:** Use `WHERE DateOfBirth BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'`

**Question:** How many customers were born in the 1990s? Write the query you used and paste the result.

**Answer type:** Code (SQL) + short text answer

---

### Input 13 — Knowledge Check: YEAR() Function

**Question:** Which Spark SQL function correctly extracts the year from a date column?

- a) `DATE_YEAR(column)`
- b) `TO_YEAR(column)`
- c) `YEAR(column)` ✓
- d) `EXTRACT_YEAR(column)`

**Correct answer:** c) `YEAR(column)`

**Explanation:** `YEAR()` is a standard SQL function supported in both Spark SQL and most SQL databases. It takes a date or timestamp column and returns the integer year value.

**Answer type:** Choice (single correct)

---

### Phase C — PySpark Transformations

---

### Input 14 — Filter + Add Age Column

**Instructions:**

Complete the following tasks in PySpark. Fill in the blanks in the code:

```python
from pyspark.sql.functions import col, year, floor, datediff, current_date, when

# Task 1: Filter customers who registered in 2020 or later
recent_customers = customers_df.filter(year(col("RegistrationDate")) >= 2020)
print(f"Customers registered 2020 or later: {recent_customers.count()}")

# Task 2: Add an 'age' column (calculated from DateOfBirth to today)
customers_with_age = customers_df.withColumn(
    "age",
    floor(datediff(current_date(), col("DateOfBirth")) / 365)
)

# Show age statistics
from pyspark.sql.functions import min as spark_min, max as spark_max, avg
customers_with_age.agg(
    spark_min("age").alias("youngest"),
    spark_max("age").alias("oldest"),
    avg("age").alias("average_age")
).show()
```

**Question:**
1. How many customers registered in 2020 or later?
2. What is the age of the youngest customer? The oldest?

**Answer type:** Short text

---

### Input 15 — Classify Customers into Loyalty Tiers

**Instructions:**

Add a new column `LoyaltyTier` to classify customers based on how long they have been with GlobalMart:

- Registered **before 2010** → `"Gold"` (loyal long-term customers)
- Registered **2010 to 2019** → `"Silver"`
- Registered **2020 or later** → `"Bronze"` (newest customers)

Use PySpark's `when / otherwise` to create this column:

```python
customers_tiered = customers_with_age.withColumn(
    "LoyaltyTier",
    when(year(col("RegistrationDate")) < 2010, "Gold")
    .when(year(col("RegistrationDate")) < 2020, "Silver")
    .otherwise("Bronze")
)

# Count customers in each tier
customers_tiered.groupBy("LoyaltyTier").count().orderBy("LoyaltyTier").show()
```

**Question:** How many customers fall into each loyalty tier (Gold, Silver, Bronze)?

**Answer type:** Short text + paste your output

---

### Input 16 — Data Quality Fix: Trim Spaces

**Instructions:**

The dataset has a data quality issue — some `FirstName` values have trailing spaces (e.g., `"Ahana "` instead of `"Ahana"`). Fix this using PySpark's `trim()` function:

```python
from pyspark.sql.functions import trim, length

# Find customers where FirstName has extra spaces
dirty = customers_tiered.filter(
    length(col("FirstName")) != length(trim(col("FirstName")))
)
print(f"Rows with trailing/leading spaces in FirstName: {dirty.count()}")

# Fix it — apply trim to FirstName and Email
customers_clean = customers_tiered.withColumn(
    "FirstName", trim(col("FirstName"))
).withColumn(
    "Email", trim(col("Email"))
)

print("Spaces removed. Sample of cleaned data:")
customers_clean.select("CustomerID", "FirstName", "Email").show(5, truncate=False)
```

**Question:** How many rows had trailing or leading spaces in `FirstName`? Why is this important to fix before writing to the Silver layer?

**Answer type:** Short text

---

### Phase D — Write to Bronze

---

### Input 17 — Write to Bronze as Delta

**Instructions:**

Write your cleaned DataFrame to the Bronze layer as a **Delta table**. Use `overwrite` mode so you can safely re-run this cell without creating duplicates.

```python
# Write to Bronze — Delta format, overwrite mode
customers_clean.write \
    .format("delta") \
    .mode("overwrite") \
    .save(bronze_path)

print(f"Written to: {bronze_path}")

# Read it back to verify
bronze_df = spark.read.format("delta").load(bronze_path)
print(f"Bronze row count: {bronze_df.count()}")
bronze_df.show(3, truncate=False)
```

**Question:** What is the row count of your Bronze table? Does it match the source CSV? Take a screenshot of the output and upload it.

**Answer type:** File upload (image) + short text

---

### Input 18 — Knowledge Check: Overwrite vs Append

**Question:** New customer files will arrive tomorrow. You want to ADD the new customers to Bronze without deleting the existing ones. Which write mode should you use?

- a) `overwrite` — replaces everything in the destination with new data
- b) `append` — adds new rows on top of existing data ✓
- c) `merge` — upserts rows matching on a key
- d) `replace` — not a valid Spark write mode

**Correct answer:** b) `append`

**Explanation:** `overwrite` deletes everything at the destination path and writes fresh. `append` adds new rows without touching what is already there. Use `overwrite` for small reference tables that are fully refreshed. Use `append` for tables that grow over time (like new daily customer files).

**Answer type:** Choice (single correct)

---

### Input 19 — Final Submission

**Instructions:**

Before submitting, confirm the following checklist in your notebook. Add a final markdown cell with:

```
## Submission Checklist
- [ ] Storage account created with Hierarchical Namespace (ADLS Gen2) enabled
- [ ] Container 'amazon-data' created with raw/customers/ folder structure
- [ ] customers_010626.csv uploaded and visible in Azure Storage Browser
- [ ] Databricks connected to ADLS — connection cell ran successfully
- [ ] Total row count confirmed: ______
- [ ] Top payment method: ______
- [ ] Year with most new registrations: ______
- [ ] Number of Gold tier customers: ______
- [ ] Bronze Delta table written and row count verified: ______
```

Fill in each blank with your actual answers from the exercise.

**Question:** Upload your completed Databricks notebook (.ipynb file) here. Make sure the access key is removed or replaced with "YOUR_STORAGE_ACCOUNT_KEY" before uploading.

**Answer type:** File upload (.ipynb)
