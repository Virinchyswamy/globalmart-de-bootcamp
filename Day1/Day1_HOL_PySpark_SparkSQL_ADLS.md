---
name: Day 1 HOL — PySpark & Spark SQL with ADLS
content_type: Project
overview: GlobalMart is a fast-growing e-commerce company that needs a reliable data platform to power its analytics. In this hands-on exercise, you will set up Azure Data Lake Storage Gen2 from scratch, upload a real GlobalMart customer dataset, connect your Databricks workspace to ADLS using a storage access key, and explore the data using PySpark and Spark SQL. By the end, you will have a cleaned Bronze Delta table ready for further processing.
learning_objectives:
  - Create an Azure Storage Account with ADLS Gen2 (Hierarchical Namespace) enabled
  - Upload a CSV dataset to a structured folder hierarchy in ADLS
  - Connect Azure Databricks to ADLS using a storage access key
  - Explore and transform a DataFrame using PySpark and Spark SQL
  - Write a cleaned DataFrame to a Bronze Delta table
prerequisites:
  - Access to an Azure subscription (provided by your instructor)
  - A Databricks workspace already created (provided by your instructor)
  - Completed Day 1 ILT 4 — Intro to Databricks + PySpark & Spark SQL
duration: 60 minutes
level: Beginner
industries:
  - e-commerce
tags:
  - azure (tool)
  - databricks (tool)
  - spark (tool)
  - sql (tool)
  - data-storage (skill)
  - data-wrangling (skill)
  - data-quality (skill)
  - approach (skill)
---

---

## Scenario 1 — Working with Azure

**Overview:** Before you can use data in Databricks, it needs to live somewhere in the cloud. In this scenario you will create your own Azure Data Lake Storage Gen2 account, set up the folder structure GlobalMart uses, and upload the customer dataset.

**Outcome:** A storage account with `customers_010626.csv` sitting at `amazon-data/raw/customers/`, ready to be read by Databricks.

---

## Input 1

**Type:** Text

>[!IMPORTANT]
>Ensure you download the dataset below before proceeding with the hands-on.

**Dataset:** customers_010626.csv — 6,666 GlobalMart customer records, 8 columns: CustomerID, FirstName, LastName, Email, PhoneNumber, DateOfBirth, RegistrationDate, PreferredPaymentMethodID

[Download customers_010626.csv — attach file here]

**Tags**

---

## Input 2

**Type:** Text

### Instructions: Create Your Azure Storage Account

Follow these steps carefully. This is your first time setting up cloud storage — read each step before clicking.

1. Go to **https://portal.azure.com** and sign in with the Azure credentials provided by your instructor.

2. In the **search bar at the top**, type `Storage accounts` and click the result.

3. Click **+ Create** (top-left button).

4. Fill in the **Basics** tab:
   - **Subscription:** select the subscription provided to you
   - **Resource group:** click *Create new* → name it `globalmart-rg` → click OK
   - **Storage account name:** choose a unique all-lowercase name, e.g. `globalmartYOURNAME` (no spaces, no special characters, 3–24 characters)
   - **Region:** East US (or the region your instructor specifies)
   - **Performance:** Standard
   - **Redundancy:** Locally-redundant storage (LRS)

5. Click the **Advanced** tab at the top of the form.

6. Under **Data Lake Storage Gen2**, check the box next to **Enable hierarchical namespace**.
   > This is the critical step — it turns a regular Blob storage account into ADLS Gen2. Without it, Databricks cannot use the `abfss://` protocol.

7. Leave all other settings as default.

8. Click **Review + Create** → then **Create**.

9. Wait for the deployment to complete (usually 30–60 seconds). You will see a green tick and "Your deployment is complete."

10. Click **Go to resource**.

**Tags**

---

## Input 3

**Type:** Short Answer

**Question:** What is the exact name of the storage account you created?

**Template:** null

**Tags**
- azure (tool)
- data-storage (skill)

---

## Input 4

**Type:** Text

### Instructions: Create Container, Folder Structure, and Upload the Dataset

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

8. Click the **⬆ Upload** button. Click *Browse for files*, select `customers_010626.csv` from your computer, and click **Upload**.

9. Wait for the upload to complete. You should see `customers_010626.csv` listed in the folder.

**Tags**

---

## Input 5

**Type:** File Upload

**Question:** Take a screenshot of the Azure Storage Browser showing `customers_010626.csv` inside the `raw/customers/` folder. Upload your screenshot here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- azure (tool)

---

## Input 6

**Type:** Text

### Instructions: Find Your Storage Access Key

To connect Databricks to your storage account, you need the Storage Account Access Key. Here is how to find it:

1. In your storage account, look at the **left-side menu**.

2. Scroll down to the **Security + networking** section.

3. Click **Access keys**.

4. You will see **key1** and **key2**. Click **Show** next to *key1*.

5. Copy the key value — you will paste it into your Databricks notebook in Scenario 2.

>[!WARNING]
>Never share this key publicly or commit it to GitHub. It gives full access to your storage account. Treat it like a password.

**Tags**

---

## Input 7

**Type:** Short Answer

**Question:** Where exactly in the Azure Portal did you find the storage access key? Describe the navigation path (for example: "Left menu → Security + networking → Access keys").

**Template:** null

**Tags**
- azure (tool)
- cloud-management (skill)

---

## Input 8

**Type:** File Upload

**Question:** Take a screenshot of the Access Keys page. Before uploading, blur or cover the actual key value — do not share your real key. We just want to confirm you found the right page.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- azure (tool)

---

## Input 9

**Type:** Choice

**Question:** Which protocol does Databricks use to read files from ADLS Gen2?

**Options:**
- wasbs:// — Windows Azure Storage Blob Secure
- abfss:// — Azure Blob File System Secure
- https:// — Standard web protocol
- hdfs:// — Hadoop Distributed File System

**Correct Options:**
- abfss:// — Azure Blob File System Secure

**Solution:**
abfss:// (Azure Blob File System Secure) is the ADLS Gen2 native protocol. The path format is: `abfss://CONTAINER@STORAGEACCOUNT.dfs.core.windows.net/FOLDER/`. Without Hierarchical Namespace enabled on the storage account, this protocol will not work.

**Tags**
- azure (tool)
- data-storage (skill)

---

## Input 10

**Type:** Short Answer

**Question:** Write the full `abfss://` path to your `raw/customers/` folder using your own storage account name.

The format is: `abfss://CONTAINER@STORAGEACCOUNT.dfs.core.windows.net/FOLDER/SUBFOLDER/`

Example: `abfss://amazon-data@globalmartvirincy.dfs.core.windows.net/raw/customers/`

**Template:** null

**Tags**
- azure (tool)
- data-storage (skill)

---

## Input 11

**Type:** Text

### Instructions: Connect Databricks to ADLS

1. Open your **Databricks workspace** and create a new notebook. Name it `Day1_HOL_PySpark_SparkSQL`.

2. Make sure your **cluster is running**. If it is not, click the cluster name at the top of the notebook and start it. Wait for the green dot before continuing.

3. In the first cell of your notebook, paste and run this setup code. Replace the two placeholder values with your own:

```python
# ─── ADLS Connection Setup ─────────────────────────────────────────────────
storage_account_name = "YOUR_STORAGE_ACCOUNT_NAME"   # ← your storage account name
container_name       = "amazon-data"
storage_account_key  = "YOUR_STORAGE_ACCOUNT_KEY"    # ← key1 from Azure Portal

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

5. If you see `Connection successful!` printed below the cell, you are ready for Scenario 2.

**Tags**

---

## Input 12

**Type:** File Upload

**Question:** Take a screenshot of your Databricks notebook showing the setup cell output with "Connection successful!" printed. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)

---

## Scenario 2 — Data Wrangling with PySpark & Spark SQL

**Overview:** With the customer data in ADLS and Databricks connected, you will explore the dataset, answer business questions using Spark SQL, apply PySpark transformations, and write cleaned data to a Bronze Delta table.

**Outcome:** A cleaned Bronze Delta table at `bronze/customers/` with trimmed strings and a new `LoyaltyTier` column.

> Continue working in the same notebook you created in Scenario 1. Add new cells below the setup cell for each question.

---

## Input 13

**Type:** Text

### Phase A — Understand the Data

In a new cell in your notebook, paste and run this code to load and explore the customer dataset:

```python
customers_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{raw_path}/customers_010626.csv")
)

print(f"Total rows: {customers_df.count()}")
customers_df.printSchema()
customers_df.show(5, truncate=False)
```

**Tags**

---

## Input 14

**Type:** Short Answer

**Question:** How many rows are in the dataset? List all 8 column names and their data types as detected by Spark (e.g. `CustomerID: StringType`).

**Template:** null

**Tags**
- data-understanding (skill)
- data-wrangling (skill)

---

## Input 15

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

## Input 16

**Type:** Text

### Phase B — Spark SQL

First, register the DataFrame as a temporary SQL view:

```python
customers_df.createOrReplaceTempView("customers")
print("Temp view 'customers' registered.")
```

Now answer the following business questions using Spark SQL (use `spark.sql("...")` or a `%sql` cell).

**Payment method distribution:**

```sql
SELECT PreferredPaymentMethodID,
       COUNT(*) AS customer_count
FROM customers
GROUP BY PreferredPaymentMethodID
ORDER BY customer_count DESC
```

**Tags**

---

## Input 17

**Type:** Short Answer

**Question:** Which payment method has the highest number of customers? How many customers prefer it? Paste your query output.

**Template:** null

**Tags**
- sql (tool)
- data-wrangling (skill)

---

## Input 18

**Type:** Code

**Question:** Write a Spark SQL query to find how many customers registered in each year. Sort results from most recent year to oldest. Hint: Use the `YEAR()` function on the `RegistrationDate` column.

**Language:** sql

**Snippet:**

**Tags**
- sql (tool)
- data-wrangling (skill)
- data-wrangling / group-by-aggregate (skill)

---

## Input 19

**Type:** Short Answer

**Question:** In which year did the most customers register? How many registered that year?

**Template:** null

**Tags**
- sql (tool)
- data-wrangling (skill)

---

## Input 20

**Type:** Code

**Question:** Write a Spark SQL query to count customers born between 1 January 1990 and 31 December 1999. Hint: Use `WHERE DateOfBirth BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'`.

**Language:** sql

**Snippet:**

**Tags**
- sql (tool)
- data-wrangling / filter (skill)
- data-wrangling / date-processing (skill)

---

## Input 21

**Type:** Choice

**Question:** Which Spark SQL function correctly extracts the year from a date column?

**Options:**
- DATE_YEAR(column)
- TO_YEAR(column)
- YEAR(column)
- EXTRACT_YEAR(column)

**Correct Options:**
- YEAR(column)

**Solution:**
YEAR() is a standard SQL function supported in both Spark SQL and most SQL databases. It takes a date or timestamp column and returns the integer year value. Example: YEAR(RegistrationDate) returns 2021 for a date of 2021-06-15.

**Tags**
- sql (tool)
- approach (skill)

---

## Input 22

**Type:** Text

### Phase C — PySpark Transformations

**Task 1 — Filter and Add Age Column:**

```python
from pyspark.sql.functions import col, year, floor, datediff, current_date, when, trim, length
from pyspark.sql.functions import min as spark_min, max as spark_max, avg

# Filter customers who registered 2020 or later
recent_customers = customers_df.filter(year(col("RegistrationDate")) >= 2020)
print(f"Customers registered 2020 or later: {recent_customers.count()}")

# Add age column
customers_with_age = customers_df.withColumn(
    "age",
    floor(datediff(current_date(), col("DateOfBirth")) / 365)
)
customers_with_age.agg(
    spark_min("age").alias("youngest"),
    spark_max("age").alias("oldest"),
    avg("age").alias("average_age")
).show()
```

**Tags**

---

## Input 23

**Type:** Short Answer

**Question:** How many customers registered in 2020 or later? What is the age of the youngest customer? The oldest?

**Template:** null

**Tags**
- data-wrangling (skill)
- data-wrangling / filter (skill)
- data-wrangling / date-processing (skill)

---

## Input 24

**Type:** Code

**Question:** Add a `LoyaltyTier` column to classify customers based on their registration date: registered before 2010 → "Gold", 2010–2019 → "Silver", 2020 or later → "Bronze". Use PySpark's `when / otherwise`. Then count customers in each tier using `groupBy`.

**Language:** python

**Snippet:**

**Tags**
- data-wrangling (skill)
- data-wrangling / dataframe-processing (skill)
- approach (skill)

---

## Input 25

**Type:** Text

### Phase C — Data Quality Fix

The dataset has a data quality issue: some `FirstName` values have trailing spaces (e.g. `"Ahana "` instead of `"Ahana"`). Identify and fix this:

```python
# Find rows with trailing/leading spaces in FirstName
dirty = customers_tiered.filter(
    length(col("FirstName")) != length(trim(col("FirstName")))
)
print(f"Rows with spaces in FirstName: {dirty.count()}")

# Fix: trim FirstName and Email
customers_clean = customers_tiered.withColumn(
    "FirstName", trim(col("FirstName"))
).withColumn(
    "Email", trim(col("Email"))
)
customers_clean.select("CustomerID", "FirstName", "Email").show(5, truncate=False)
```

**Tags**

---

## Input 26

**Type:** Short Answer

**Question:** How many rows had trailing or leading spaces in `FirstName`? Why is it important to fix this before writing data to the Silver layer?

**Template:** null

**Tags**
- data-quality (skill)
- data-wrangling (skill)

---

## Input 27

**Type:** Text

### Phase D — Write to Bronze

Write your cleaned DataFrame to the Bronze layer as a Delta table. Use `overwrite` mode so you can safely re-run this cell without creating duplicates:

```python
customers_clean.write \
    .format("delta") \
    .mode("overwrite") \
    .save(bronze_path)

print(f"Written to: {bronze_path}")

# Read back to verify
bronze_df = spark.read.format("delta").load(bronze_path)
print(f"Bronze row count: {bronze_df.count()}")
bronze_df.show(3, truncate=False)
```

**Tags**

---

## Input 28

**Type:** File Upload

**Question:** Take a screenshot of your Databricks notebook showing the Bronze table write output and the verified row count. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)
- data-storage (skill)

---

## Input 29

**Type:** Choice

**Question:** GlobalMart's data engineering team wants to add new customer records that arrive every day to the Bronze table, preserving all historical data. Which of the following commands should they use?

**Options:**
- df.write.mode("overwrite").format("delta").save(bronze_path)
- df.write.mode("append").format("delta").save(bronze_path)
- df.write.mode("replace").format("delta").save(bronze_path)
- df.write.mode("insert").format("delta").save(bronze_path)

**Correct Options:**
- df.write.mode("append").format("delta").save(bronze_path)

**Solution:**
`overwrite` deletes everything at the destination path and writes fresh data. `append` adds new rows on top of existing data without touching what is already there. Use `overwrite` for small reference tables that are fully refreshed. Use `append` for tables that grow over time, like new daily customer files.

**Tags**
- data-storage (skill)
- approach (skill)

---

## Input 30

**Type:** File Upload

**Question:** Upload your completed Databricks notebook (.ipynb file). Before uploading, replace your real storage account key with the placeholder `YOUR_STORAGE_ACCOUNT_KEY` in the setup cell.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, JUPYTER_NOTEBOOK

**Tags**
- databricks (tool)
