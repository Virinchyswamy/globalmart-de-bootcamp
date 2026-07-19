# Getting Started with ADLS & Databricks: From Ingestion to Insights
## Content Type
Project

## Overview
<p style="text-align:justify;">

GlobalMart, a retail e-commerce company, is struggling to make sense of data scattered across multiple source systems. In this project, you will take on the role of a Data Engineer and build the foundational layers of GlobalMart's data platform on Azure Databricks, from setting up cloud storage and landing raw data, to exploring and wrangling that data using PySpark and Spark SQL to answer real business questions.

## Learning Objectives
- Understand GlobalMart's business context and identify the data challenges that need to be solved
- Set up Azure Data Lake Storage Gen2 as the central storage layer and organise raw data using a structured folder hierarchy
- Apply core ADLS concepts, storage tiers, lifecycle management, versioning, and access control using RBAC and managed identities
- Upload data to Databricks Volumes and read it into Databricks for analysis
- Perform data exploration and wrangling using PySpark and Spark SQL to answer business queries

## Prerequisites
- Basic PySpark & Spark SQL
- Familiarity with Azure & Databricks Foundations

## Duration of Completion
110 minutes

## Level
Beginner

## Industries
- e-commerce

## Tags
- approach (skill)
- cloud-management (skill)
- azure (tool)
- databricks (tool)
- data-modelling (skill)
- data-wrangling (skill)
- data-quality (skill)
- spark (tool)

## Scenarios
### Working with Azure
#### Overview
Set up Azure Data Lake Storage Gen2 as the central storage layer for the GlobalMart data platform. Upload the source dataset, organise the folder structure, and explore core ADLS concepts around access, availability, and storage management.

#### Level
beginner

#### Industries
- e-commerce

#### Tags
- approach (skill)
- cloud-management (skill)
- azure (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!NOTE] 
> Use your Azure Lab for this activity.

You have been appointed as the **Data Engineer at GlobalMart**. The first step in building the data platform is setting up a reliable, well-organised cloud storage layer where all raw source data will land before any processing begins.

**You are required to:**

- Identify the most suitable **Azure storage service** for a data engineering workload that integrates with Databricks
- Create the storage resource in the **Azure Portal**
- Set up the following **folder structure** to organise GlobalMart's raw data by source table:

```
raw-data/
├── customers/
├── orders/
├── order_items/
├── products/
├── payments/
├── payment_methods/
├── address/
└── returns/
```

- Upload the **GlobalMart dataset** (downloaded from the Problem Statement activity) into the appropriate folders
- Ensure the storage is configured for **high availability** and is **accessible for integration** with Azure Databricks

**Expected Outcome:**

- A fully configured Azure storage resource with the GlobalMart dataset uploaded and organised by source table

**Tags**


##### Input 2
**Type:** File Upload

**Question:** Upload a snapshot of your Azure storage container that shows the folder structure and the uploaded dataset files.

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- azure / azure-data-lake / adls-hierarchical-namespace (tool)

##### Input 3
**Type:** Short Answer

**Question:** Which Azure storage service did you choose for GlobalMart's data platform, and why is it the most suitable option for a Databricks-based data engineering workload?

**Template:** null

**Tags**
- azure / azure-data-lake / adls-hierarchical-namespace (tool)

##### Input 4
**Type:** Choice

**Question:** Match the cloud platforms with their corresponding data lake storage services:

**Cloud Platforms:**

Amazon Web Services (AWS)
Microsoft Azure
Google Cloud Platform (GCP)

**Data Lakes:**
A. ADLS
B. S3
C. GCS

**Options:** 
- 1-B, 2-A, 3-C

- 1-A, 2-B, 3-C

- 1-C, 2-B, 3-A

- 1-A, 2-C, 3-B

**Correct Options:** 
- 1-B, 2-A, 3-C

**Solution:** 
Each major cloud provider has its own primary object / data lake storage service:
- **AWS** → **Amazon S3** (Simple Storage Service)
- **Microsoft Azure** → **ADLS Gen2** (Azure Data Lake Storage Gen2)
- **GCP** → **Google Cloud Storage (GCS)**

**Tags**


##### Input 5
**Type:** Choice

**Question:** Which of the following is **NOT** a valid storage tier in Azure Blob Storage?

**Options:** 
- Hot Storage

- Cool Storage

- Warm Storage

- Archive Storage

**Correct Options:** 
- Warm Storage

**Solution:** 
Azure Blob Storage offers three access tiers:
- **Hot** — for data accessed frequently
- **Cool** — for data accessed infrequently (stored for at least 30 days)
- **Archive** — for data rarely accessed and stored for at least 180 days

**Warm Storage** does not exist as an Azure storage tier.

**Tags**
- azure / azure-data-lake / adls-vs-blob-storage (tool)

##### Input 6
**Type:** Choice

**Question:** GlobalMart stores raw ingestion files in the Hot tier. Files older than 90 days are rarely accessed and should automatically move to the Cool tier to reduce costs. What is the recommended way to automate this?

**Options:** 
- By setting Azure RBAC roles on the container

- By configuring lifecycle management policies

- By using Azure SQL Database retention settings

- By configuring virtual network security groups (NSGs)

**Correct Options:** 
- By configuring lifecycle management policies

**Solution:** 
**Lifecycle management policies** in Azure Blob Storage allow you to define rules that automatically transition blobs between storage tiers (Hot → Cool → Archive) or delete them after a defined period — without any manual intervention. RBAC, SQL Database settings, and NSGs are unrelated to storage tier transitions.

**Tags**
- cloud-management / resilience-and-availability (skill)

##### Input 7
**Type:** Choice

**Question:** GlobalMart is concerned about accidental deletion of raw source files in their ADLS container. They want the ability to restore any deleted file within 30 days. Which feature should they enable?

**Options:** 
- Blob versioning

- Archive Storage

- Azure RBAC roles

- Lifecycle management policies

**Correct Options:** 
- Blob versioning

**Solution:** 
**Blob versioning** automatically maintains previous versions of a blob whenever it is overwritten or deleted. This allows GlobalMart to restore any file to a prior state within the retention window. Archive Storage is a cost tier, RBAC controls access permissions, and lifecycle policies manage tier transitions — none of these restore deleted files.

**Tags**
- azure / blob-storage / blob-storage-account-setup (tool)

##### Input 8
**Type:** Choice

**Question:** GlobalMart enabled versioning on their ADLS container. During a bulk upload, a large number of files were accidentally overwritten with incorrect data. What is the correct approach to restore the previous versions?

**Options:** 
- Use the Azure Portal to manually restore each file one by one

- Write a script to list all previous blob versions and promote them to the current version

- Disable versioning and re-upload all the original files

- Use Azure RBAC roles to revert the changes

**Correct Options:** 
- Write a script to list all previous blob versions and promote them to the current version

**Solution:** 
When versioning is enabled, Azure retains all previous versions of each blob. The correct approach at scale is to **write a script** (e.g. using Azure SDK or Azure CLI) that lists all blobs with prior versions and **copies the previous version back as the current version**. Manually restoring each file through the portal is impractical at scale, and disabling versioning or using RBAC will not recover the original data.

**Tags**
- azure / blob-storage / blob-storage-tiers (tool)

##### Input 9
**Type:** Choice

**Question:** GlobalMart's Databricks pipeline needs to read from and write to their ADLS Gen2 container automatically — with no human login or credential entry at runtime. What is the recommended way to grant this access?

**Options:** 
- Use individual user accounts with the required Azure RBAC roles

- Make the container public so Databricks can access it freely

- Use a managed identity with the required Azure RBAC roles

- Configure container-level access policies only

**Correct Options:** 
- Use a managed identity with the required Azure RBAC roles

**Solution:** 
A **managed identity** is an Azure Active Directory identity automatically managed by Azure for a service (in this case, the Databricks workspace or cluster). Assigning the required **RBAC role** (e.g. Storage Blob Data Contributor) to that managed identity allows Databricks to access ADLS securely without storing credentials anywhere. Making the container public is a security risk, and individual user accounts are not suitable for automated pipelines.

**Tags**
- cloud-management / authentication (skill)
- cloud-management / authorization (skill)

##### Input 10
**Type:** Choice

**Question:** GlobalMart wants to allow a third-party logistics vendor to upload shipment status files to a specific ADLS folder, but must prevent them from reading or deleting any existing files. Which steps should the team take? (Select all that apply)

**Options:** 
- Make the container public and monitor uploads via logs

- Assign the Storage Blob Data Contributor role to the vendor

- Assign the Storage Blob Data Owner role to the vendor

- Configure a container-level policy to restrict delete permissions

- Use Azure RBAC roles to control permissions

**Correct Options:** 
- Assign the Storage Blob Data Contributor role to the vendor

- Use Azure RBAC roles to control permissions

**Solution:** 
- **Storage Blob Data Contributor** grants read, write, and delete access — but when combined with a scoped assignment (folder-level via SAS or a specific container), it allows uploads without broader access.
- **Azure RBAC** is the correct mechanism for controlling access to storage resources.
- **Storage Blob Data Owner** grants full control including ACL management — far more than needed.
- Making the container **public** removes all access control and is a security risk.

**Tags**
- cloud-management / authentication (skill)
- cloud-management / authorization (skill)

##### Input 11
**Type:** Choice

**Question:** GlobalMart chose Azure Data Lake Storage Gen2 over standard Azure Blob Storage for their data platform. What is the key capability that ADLS Gen2 adds over standard Blob Storage?

**Options:** 
- Support for larger file sizes

- A hierarchical namespace that enables true folder-level operations and fine-grained ACL permissions

- Built-in data transformation and cleansing

- Automatic integration with Power BI

**Correct Options:** 
- A hierarchical namespace that enables true folder-level operations and fine-grained ACL permissions

**Solution:** 
The defining feature of **ADLS Gen2** over standard Blob Storage is the **hierarchical namespace (HNS)**. HNS enables:
- True **directory and file semantics** (rename, move at folder level without copying data)
- **Fine-grained ACL permissions** at the folder and file level — not just at the container level
- Better **performance for analytics workloads** that traverse large directory trees

Standard Blob Storage treats everything as flat objects — there are no real folders, only path prefixes.

**Tags**
- azure / azure-data-lake / adls-hierarchical-namespace (tool)

##### Input 12
**Type:** Choice

**Question:** To allow Databricks to securely access GlobalMart's ADLS Gen2 container without hardcoding credentials in notebooks, which Unity Catalog objects must be configured?

**Options:** 
- A Delta Live Tables pipeline and a job cluster

- A storage credential and an external location

- A metastore and a SQL warehouse

- A cluster policy and an instance pool

**Correct Options:** 
- A storage credential and an external location

**Solution:** 
In **Unity Catalog**, secure access to external cloud storage (like ADLS Gen2) is configured using two objects:
- **Storage Credential** — stores the authentication method (e.g. a managed identity or service principal) that Databricks uses to authenticate with Azure
- **External Location** — maps a specific ADLS path to a name that notebooks and pipelines can reference, using the storage credential for authentication

This setup keeps credentials out of notebook code entirely and enforces access control at the Unity Catalog level.

**Tags**
- cloud-management / access-control (skill)

### GlobalMart: Problem Statement
#### Overview
Understand the GlobalMart business problem, the data landscape, the planned Medallion Architecture, and the dataset you will work with throughout this project.

#### Level
beginner

#### Industries
- e-commerce

#### Tags
- approach (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

<p style="text-align: center;">
<strong>GlobalMart is sitting on a goldmine of data, but none of it is usable. Raw data is scattered across two different source systems, quality issues go undetected, and business teams cannot answer even the most basic questions. What will it take to build a reliable, analytics-ready data platform from scratch?</strong>
</p>

<br>

### About GlobalMart

**GlobalMart** is a fast-growing Indian retail e-commerce company serving customers across multiple states. They operate through two channels:

- **Online** — customers place orders via the web and mobile app
- **Retail PoS** — orders placed in-store at physical outlets

As GlobalMart scales, their data landscape has grown complex. Transactional data flows through a **Postgres database**, while customer profiles, product catalogues, payment records, and returns land as **raw files on cloud storage**, with no unified pipeline to bring it all together.

<br>

### The Problem

GlobalMart's data team is facing the following challenges:

- **No unified pipeline** — Order and order item data lives in Postgres and changes continuously, but there is no system to capture and propagate those changes into an analytics layer
- **Raw files with no validation** — Customer, product, payment, address, and returns data arrives as CSV and JSON files on Azure Data Lake Storage Gen2 with no schema enforcement or quality checks
- **Nested and complex structures** — The products dataset contains nested JSON (`specs`, `supplier_info` as structs and `tags` as an array) that cannot be queried directly without transformation
- **Silent data quality issues** — PinCode values lose their leading zeros during file parsing, some customer date-of-birth fields are invalid, and certain delivery dates appear before their corresponding shipping dates
- **Data silos** — There is no way to join orders with products, customers with their addresses, or payments with returns without significant manual effort
- **No analytics-ready layer** — Business teams cannot answer basic questions like *"Who are our top 10 customers by revenue?"* or *"Which product categories drive the most returns?"*

<br>

These issues have created a lack of trust in data across GlobalMart's teams, rendering existing reports unreliable and blocking data-driven decision making.

**Tags**


##### Input 2
**Type:** Text

### What You Will Build

To address GlobalMart's challenges, you will implement a **Medallion Architecture** on **Azure Databricks**, a layered approach that takes raw data from source systems and progressively refines it into analytics-ready tables.
<br>

#### The Three Layers

| Layer | Purpose | What happens here |
|---|---|---|
| **Bronze** | Raw ingestion | Data lands exactly as it comes from the source — no transformation. Audit columns (`_ingested_at`, `_source_file`) are added. |
| **Silver** | Clean & Conform | Data is cleaned, validated, renamed to a consistent format, and enriched with derived columns. Quality issues are flagged or quarantined. |
| **Gold** | Analytics-Ready | A Kimball star schema is built — dimension tables and a central fact table — optimised for business reporting and BI tools. |

<br>

GlobalMart's data originates from **two source systems** and spans **8 tables** covering orders, customers, products, payments, addresses, and returns. You will build a unified pipeline that brings all of it together into a single, trustworthy data platform.

**Tags**


##### Input 3
**Type:** Text

### Artifacts

Before you begin, download the following artifacts. You will refer to these throughout the project.

<br>

**Dataset**

> The GlobalMart dataset contains all 8 source tables in their raw format — CSV files, JSON files, and a Postgres database connection. You will use this data to build the pipeline end to end.

[Download GlobalMart Dataset](https://cdn.enqurious.com/others/b1771078-3263-4536-a88a-bf85952881ae_adlsdatanew.7z)

<br>

**Data Model**

> The entity-relationship diagram shows all 8 tables, their columns, primary keys, and the relationships between them. Refer to this when building your ingestion and transformation notebooks.

[View Data Model](https://cdn.enqurious.com/images/11b7f99e-9988-431a-8b34-4b56f3c76eb2_gbmart-data-model.webp)

<br>

**Data Dictionary**

> The data dictionary describes every column in every table — data type, nullability, business meaning, sample values, and known data quality patterns. This is your primary reference for the Silver layer transformations.

[Download Data Dictionary](https://cdn.enqurious.com/others/ca612aac-8626-486a-acfb-c44efa4120ec_globalmartdatadictionary.xlsx)

<br>

>[!IMPORTANT]
> Download all three artifacts before proceeding. The dataset must be uploaded to your ADLS Gen2 container before any ingestion notebooks can run.


**Tags**


###  PySpark & Spark SQL with Databricks Volumes
#### Overview
GlobalMart is a fast-growing e-commerce company that needs a reliable data platform to power its analytics. In this hands-on exercise, you will upload real GlobalMart customer, order, and product data into a Databricks Volume, read it into a notebook, and explore it using PySpark and Spark SQL. By the end, you will have cleaned Bronze Delta tables ready for further processing — and you will have done it without ever touching a storage account key.

#### Level
beginner

#### Industries
- e-commerce

#### Tags
- data-modelling (skill)
- data-wrangling (skill)
- data-quality (skill)
- databricks (tool)
- spark (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!IMPORTANT]
>Ensure you download all three datasets below before proceeding with the hands-on. Use your Databricks Lab for this activity.

>[!NOTE] 
> A cluster and a catalog with your login ID have already been created. You can use the existing cluster and catalog to interact with the data.

**Datasets:**
- `ex_customers.csv` — [Link](https://cdn.enqurious.com/documents/952b52f7-c480-4ada-a0a9-313679bf0486_excustomers.csv)
- `ex_orders.csv` — [Link](https://cdn.enqurious.com/documents/4b40a04c-65da-4936-9268-74ecb38364bd_exorders.csv)
- `ex_products.csv` — [Link](https://cdn.enqurious.com/documents/d5ac744f-01de-4b3d-b5c1-a0382ecba404_exproducts.csv) 

**Tags**


##### Input 2
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


##### Input 3
**Type:** Short Answer

**Question:** What is the full path to the Volume you created? (Format: `/Volumes/<catalog>/<schema>/<volume_name>/`)

**Template:** null

**Tags**


##### Input 4
**Type:** Text

### Instructions: Create Folders and Upload the Datasets

You are now inside your Volume. Create one folder per dataset and upload each file into its own folder.

1. Click **Create** → **Folder**, name it `customers`, click **Create**.
2. Click into the `customers` folder, click **Upload to this volume**, select `ex_customers.csv` from your computer, and upload it.
3. Go back to the Volume root. Repeat step 1 with the folder name `orders`, and upload `ex_orders.csv` into it.
4. Go back to the Volume root. Repeat step 1 with the folder name `products`, and upload `ex_products.csv` into it.
5. You should now see three folders inside your Volume, each containing exactly one CSV file.

**Tags**


##### Input 5
**Type:** File Upload

**Question:** Take a screenshot of the Volume browser showing all three folders (`customers`, `orders`, `products`), each containing its file. Upload your screenshot here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**


##### Input 6
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
- databricks / databricks-unity-catalog (tool)

##### Input 7
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


##### Input 8
**Type:** File Upload

**Question:** Take a screenshot of your Databricks notebook showing the `dbutils.fs.ls()` output with your three folders listed. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**


##### Input 9
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


##### Input 10
**Type:** Short Answer

**Question:** How many rows are in each of the three DataFrames? Name one column in `orders_df` that Spark inferred as a date/timestamp type, and one column it inferred as a string.

**Template:** null

**Tags**


##### Input 11
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
- databricks / databricks-unity-catalog (tool)

##### Input 12
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

**Tags**


##### Input 13
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
- data-wrangling / group-by-aggregate / sql-aggregate-filtering (skill)
- data-wrangling / grouping-sets (skill)

##### Input 14
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
- data-wrangling / group (skill)
- data-wrangling / group-by-aggregate / sql-aggregate-filtering (skill)

##### Input 15
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
- data-wrangling / join (skill)
- data-wrangling / group-by-aggregate / sql-aggregate-filtering (skill)

##### Input 16
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
- data-wrangling / group-by-aggregate / sql-aggregate-filtering (skill)
- data-wrangling / group (skill)

##### Input 17
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

**Tags**


##### Input 18
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
- data-wrangling / group-by-aggregate / sql-aggregate-filtering (skill)

##### Input 19
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
- data-wrangling / group-by-aggregate / sql-aggregate-filtering (skill)
- data-wrangling / group (skill)

##### Input 20
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

**Tags**


##### Input 21
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
- databricks / delta-live-table / quality-constraints (tool)
- data-wrangling / aggregate (skill)
- data-wrangling / conditional-logic (skill)

##### Input 22
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


##### Input 23
**Type:** File Upload

**Question:** Take a screenshot of your Databricks notebook showing the Bronze write output with all three row counts. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**


##### Input 24
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
- databricks / databricks-unity-catalog (tool)

##### Input 25
**Type:** File Upload

**Question:** Upload your completed Databricks notebook (.ipynb file). Your notebook never contained a storage account key, so there is nothing to redact before submitting.

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY, JUPYTER_NOTEBOOK

**Tags**
- data-wrangling / dataframe-processing (skill)

