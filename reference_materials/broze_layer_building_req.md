# Data Ingestion and Building the Bronze Layer
## Content Type
Project

## Overview
<p style="text-align:justify;">
In this project, you will set up GlobalMart's data infrastructure and ingest raw data from two source systems into the Bronze layer on Databricks. Starting from the business problem, you will configure Azure Data Lake Storage and a Postgres database as data sources, then build ingestion pipelines, Autoloader for file-based data, and Lakeflow Connect for transactional CDC data, landing all source tables into the Bronze layer as Delta tables.



## Learning Objectives
- Understand the GlobalMart business problem and the two-source pipeline architecture
- Configure ADLS and Postgres as data sources ready for ingestion
- Ingest file-based data from ADLS into Delta tables using Autoloader with schema inference and evolution
- Build a Lakeflow Connect Ingestion Pipeline to ingest transactional data from Postgres using CDC

## Prerequisites
- Basic familiarity with SQL and PySpark
- Understanding of cloud storage concepts, containers, folders, and common file formats (CSV, JSON)
- Familiarity with the Databricks notebook interface

## Duration of Completion
100 minutes

## Level
Intermediate

## Industries
- retail-and-cpg
- e-commerce

## Tags
- data-understanding (skill)
- data-storage (skill)
- approach (skill)
- databricks (tool)
- spark (tool)
- azure (tool)
- batch-etl (skill)

## Scenarios
### Configuring Data Sources
#### Overview
Set up both data sources, Azure Data Lake Storage and the Postgres database, so they are accessible from Databricks before building the pipeline.

#### Level
intermediate

#### Industries
- retail-and-cpg

#### Tags
- data-understanding (skill)
- data-storage (skill)
- approach (skill)
- databricks (tool)
- spark (tool)
- azure (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!NOTE]
> Ensure you have downloaded all resources from the previous activity: Dataset, Data Model, and Data Dictionary before proceeding.

- [Dataset](https://cdn.enqurious.com/others/b62bca84-6a5b-47f2-bd78-54731e77ea8c_adlsdatanew.7z)

>[!IMPORTANT]
> Both data sources must be fully set up and verified before you begin building the Bronze Layer. Do not proceed to the next activity until all tasks in this activity are complete.

>[!IMPORTANT]
> For all file upload submissions throughout this project, ensure your account login ID is visible in the top-right corner of every screenshot. This applies to all activities and serves as verification that the work is completed in your own workspace.


**Tags**


##### Input 2
**Type:** Text

### Task 1: Source (ADLS) — Preparing Data Sources

**Goal:**

- Create the following folder structure inside the `raw-data` directory of your ADLS container:

```
<your-storage-account> (Storage Account)
└── <your-container> (Container)
    └── raw-data/
        ├── addresses/
        ├── customers/
        ├── payment_methods/
        ├── payments/
        ├── products/
        └── returns/
```

- Upload all files provided in the dataset into their respective folders as shown above.

**Outcome:**

- All dataset files are uploaded to the correct folder paths within the ADLS container.

**Things to Consider:**

- Verify each folder independently after uploading to confirm the correct files are in the correct location.

**Tags**


##### Input 3
**Type:** File Upload

**Question:** Upload the following screenshots as evidence that the ADLS source is ready:

1. Your ADLS container showing the `raw-data/` folder with all six source folders visible
2. At least two of those folders opened, showing the uploaded files inside

>[!NOTE]
> Ensure your login ID is visible in the top-right corner of each screenshot as proof that the work is being done in your own account.

**Max No. of Files:** 10

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- azure / azure-data-lake / adls-vs-blob-storage (tool)

##### Input 4
**Type:** Text

### Task 2: Source (Database) — Preparing Data Sources
<br/>

>[!NOTE]
> Download the Postgres setup script before starting this task.

>[!IMPORTANT]
> Run the script step by step — execute each step individually in the Supabase SQL Editor and verify the output before moving to the next. Do not select and run the entire script at once.

- [Postgres Setup Script](https://cdn.enqurious.com/others/816edfd8-c9e8-4f02-be3e-b0f56dca86d1_globalmartpostgressetup.sql)

> The script performs the following steps:
>
> - **Creates the `orders` table** — defines all source columns along with an `updated_at` column that tracks when each row was last modified
> - **Creates the `order_items` table** — defines line item columns with the same `updated_at` tracking column
> - **Sets up an `updated_at` trigger** — automatically updates the `updated_at` timestamp on both tables whenever a row is inserted or modified
> - **Enables `REPLICA IDENTITY FULL`** — required for CDC; ensures deleted and updated rows are fully captured in the Postgres transaction log
> - **Creates a publication** — exposes both tables to Lakeflow Connect so the Ingestion Pipeline can read changes from the WAL
> - **Runs a verification query** — confirms both tables are included in the publication before you proceed

**Tags**


##### Input 5
**Type:** Text

**Goal:**

- Run the provided Postgres setup script in your Supabase SQL Editor. The script creates the `orders` and `order_items` tables with the correct column structure and CDC configuration required by the Lakeflow Connect Ingestion Pipeline.
- Load data into both tables using Supabase's CSV import feature:
  - Go to **Table Editor** in Supabase
  - Select the table, click **Insert**, then select **Import data from CSV**
  - Upload `orders.csv` into the `orders` table and `order_items.csv` into the `order_items` table
 - [orders_data](https://cdn.enqurious.com/documents/c10b037f-ff12-4b28-9745-46659550fd3b_orders.csv)
 - [order_items_data](https://cdn.enqurious.com/documents/5467defe-4cf5-4175-9740-8d49b941c9e8_orderitems.csv)

![Image-image.png](https://cdn.enqurious.com/images/c46c45ad-4d93-4c79-97b4-eb05164eb2a0_image.webp)

**Outcome:**

- `orders` table contains approximately 126,000 rows
- `order_items` table contains approximately 377,000 rows
- Both tables are visible in the Lakeflow Connect catalog explorer from your Databricks workspace

**Things to Consider:**

- The dataset volume is too large for INSERT statements. Use Supabase's CSV import feature for both tables.
- The setup script configures CDC prerequisites required by the Ingestion Pipeline. Do not skip or modify any part of the script.
- Verify the row count in Supabase SQL Editor after each import before proceeding.

**Tags**


##### Input 6
**Type:** File Upload

**Question:** Upload the following screenshots as evidence that the database source is ready:
 - Supabase SQL Editor output showing `SELECT COUNT(*) FROM public.orders`
 - Supabase SQL Editor output showing `SELECT COUNT(*) FROM public.order_items`
 - Catalog Explorer view in Databricks showing both `orders` and `order_items` tables visible via the Lakeflow Connect connection

**Max No. of Files:** 5

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- approach / concept-clarity (skill)

##### Input 7
**Type:** Text

>[!CAUTION]
> Please ensure you complete all tasks in this activity and verify both sources before moving forward. You will not be able to return to this activity.

**Tags**


### Building Bronze Layer
#### Overview
Ingest all 8 GlobalMart source tables into the Bronze layer — 6 ADLS tables using Autoloader and 2 Postgres tables using the Lakeflow Connect Ingestion Pipeline.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- data-storage (skill)
- batch-etl (skill)
- approach (skill)
- databricks (tool)
- azure (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!IMPORTANT]
> All tables built in this activity must follow the three-level namespace:

- `<your-catalog>.bronze.<table_name>`

>[!NOTE]
> Keep your mount point name unique to avoid conflicts with other participants. 

- Use the format `<yourname>_gbmart_data` —for example, `/mnt/john_gbmart_data`.

**Tags**


##### Input 2
**Type:** Text

### Task 1: Data Ingestion from ADLS
<br/>

#### Goal:

- Create a logical path in Databricks that connects to your ADLS container and reflects the data from `raw-data/`. This mount point will serve as the base path for all Autoloader notebooks in this project.
- Ingest all 6 ADLS source tables into `<your-catalog>.bronze` using Autoloader:
  - `customers`, `addresses`, `payments`, `payment_methods`, `returns` — CSV format
  - `products` — JSON format
- Add the following audit columns to every ingested table:
  - `_source_file` — file path the row was loaded from
  - `_ingested_at` — timestamp at which the row was ingested
- Write each table to `<your-catalog>.bronze.<table_name>`.

**Outcome:**

- All 6 tables exist as Delta tables in `<your-catalog>.bronze`.
- Each table contains `_source_file` and `_ingested_at` audit columns.
- `_checkpoints/` and `_schemas/` subfolders are auto-created in ADLS after the pipeline runs.

**Things to Consider:**

- The configuration for ingesting JSON differs from CSV; think about what additional option `products` requires.
- Consider what `trigger(availableNow=True)` while writing data to the table does versus continuous streaming and why it suits a batch ingestion use case.
- Checkpoint and schema paths must point to their respective table subfolders, not the root `_checkpoints/` or `_schemas/` folder.
- Think about how the checkpoint and schema path variables you define in your notebook are what tell Autoloader where to create its state folders — these folders are generated programmatically on the first run and will appear in your ADLS container automatically. You do not need to create them in the Azure portal.

![Image-image.png](https://cdn.enqurious.com/images/212ab52f-3af1-4922-ac2c-adc5f1c4bd18_image.webp)

![Image-image.png](https://cdn.enqurious.com/images/86d4200d-8e90-4081-b76c-cfc6d4225d61_image.webp)

![Image-image.png](https://cdn.enqurious.com/images/7d94612f-70b7-4e4e-80d4-5abe790b425c_image.webp)

**Tags**


##### Input 3
**Type:** Choice

**Question:** GlobalMart's `customers` folder in ADLS grows by hundreds of new files every month. A colleague suggests using COPY INTO instead of Autoloader since both can load files from ADLS. What is the key reason Autoloader is more suitable here?

**Options:** 
- COPY INTO does not support CSV format — Autoloader is required for CSV file ingestion

- COPY INTO lists all files in the folder on every run — as the folder grows to thousands of files, this becomes a significant bottleneck. Autoloader uses file notification events and only processes files that have arrived since the last run, making it far more efficient at scale

- Autoloader automatically deduplicates rows on ingestion, while COPY INTO does not

- COPY INTO cannot write to Delta tables in Unity Catalog — only to external locations

**Correct Options:** 
- COPY INTO lists all files in the folder on every run — as the folder grows to thousands of files, this becomes a significant bottleneck. Autoloader uses file notification events and only processes files that have arrived since the last run, making it far more efficient at scale

**Solution:** 
COPY INTO maintains idempotency by tracking file names it has already loaded — but it achieves this by listing all files in the folder on every run and comparing them against its internal record. As a folder accumulates thousands of files over time, this directory listing becomes increasingly slow and resource-intensive. Autoloader solves this by subscribing to file notification events from cloud storage — it is notified when a new file arrives and processes only that file, without scanning the entire folder. This makes Autoloader the right choice for continuously growing, high-volume datasets like GlobalMart's source folders.

**Tags**
- data-storage / delta-lakehouse / copy-into (skill)

##### Input 4
**Type:** Short Answer

**Question:** Besides Autoloader, what are the other approaches available to connect Databricks with ADLS and ingest data from it? Briefly describe each approach and mention one scenario where it would be the right choice over Autoloader.

**Template:** null

**Tags**
- databricks / ingestion-and-parsing (tool)

##### Input 5
**Type:** Short Answer

**Question:** After running the Autoloader pipeline for `customers`, navigate to `_schemas/customers/_schemas/` in your ADLS container and open one of the files stored there.

![Image-image.png](https://cdn.enqurious.com/images/06d34566-d16e-498d-99d0-d134b090f45a_image.webp)

What does the file contain? In your own words, explain how Autoloader uses this information to handle schema evolution.

**Template:** null

**Tags**
- databricks / autoloaders (tool)

##### Input 6
**Type:** Choice

**Question:** After successfully running the Autoloader pipeline for customers, a teammate accidentally deletes the _checkpoints/customers/ folder from ADLS to "clean up storage." The pipeline is then re-run. What happens?

**Options:** 
- The pipeline fails immediately with a checkpoint not found error and does not ingest any data

- Autoloader detects the missing checkpoint, rebuilds it automatically from the schema folder, and resumes from where it left off

- Autoloader loses track of which files it already processed and reprocesses all files from the beginning, resulting in duplicate rows in <your-catalog>.bronze.customers

- Nothing changes, Autoloader reads directly from the source files and does not rely on the checkpoint folder for deduplication

**Correct Options:** 
- Autoloader loses track of which files it already processed and reprocesses all files from the beginning, resulting in duplicate rows in <your-catalog>.bronze.customers

**Tags**
- databricks / autoloaders (tool)

##### Input 7
**Type:** File Upload

**Question:** Upload all notebooks created for the ADLS ingestion as part of this task, along with a screenshot showing all 6 tables created in <your-catalog>.bronze.

**Max No. of Files:** 8

**Max File Size:** 100

**Allowed File Types:** ANY

**Tags**
- databricks / ingestion-and-parsing (tool)

##### Input 8
**Type:** Text

### Task 2: Data Ingestion from Postgres

**Goal:**

Your `orders` and `order_items` tables are now live in Postgres. Based on the GlobalMart architecture, these two transactional tables require CDC-based ingestion — any insert, update, or delete at the source must be reflected in the Bronze layer. To handle this, Lakeflow Connect with an Ingestion Pipeline is the approach.

- Create an Ingestion Pipeline in Databricks using the existing Lakeflow Connect connection to ingest `orders` and `order_items` from Postgres into `<your-catalog>.bronze`.
- Configure each table with the correct cursor column, primary key, and history tracking setting.
- Run the pipeline to perform the initial load of both tables.

**Outcome:**

- `orders` and `order_items` exist as Streaming Tables in `<your-catalog>.bronze`.
- Row counts match the source — approximately 126,000 rows for `orders` and 377,000 rows for `order_items`.
- The pipeline shows a successful run status with the correct upserted row count.

**Things to Consider:**

- Think about which column makes a reliable cursor and why — what property must a cursor column have to correctly detect new and updated rows?
- Consider what History tracking Off means for how updates are applied to the Delta table versus History tracking On.
- The Ingestion Pipeline creates Streaming Tables — think about how this differs from a regular Delta table and what it enables for future incremental loads.

**Tags**


##### Input 9
**Type:** File Upload

**Question:** Upload screenshots showing:

1. The completed Ingestion Pipeline with a successful run status and upserted row counts visible for both `orders` and `order_items,`, along with a screenshot showing all 2 tables created in <your-catalog>.bronze.
2. Query output from `SELECT COUNT(*) FROM <your-catalog>.bronze.orders` and `SELECT COUNT(*) FROM <your-catalog>.bronze.order_items`

**Max No. of Files:** 4

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks / ingestion-and-parsing (tool)

##### Input 10
**Type:** Choice

**Question:** You are setting up the Ingestion Pipeline for `orders`. A colleague suggests using `OrderDate` as the cursor column instead of `updated_at`. What is the problem with this approach?

**Options:** 
- `OrderDate` is not indexed in Postgres, which makes it slow to use as a cursor column

- `OrderDate` only captures when the order was placed. If a row is updated later, for example, the status changes from Shipped to Delivered, `OrderDate` does not change, and the pipeline will miss that update entirely

- `OrderDate` is a TIMESTAMPTZ type which is not supported as a cursor column in Lakeflow Connect

- Using `OrderDate` would cause duplicate rows because multiple orders can share the same date

**Correct Options:** 
- `OrderDate` only captures when the order was placed. If a row is updated later, for example, the status changes from Shipped to Delivered, `OrderDate` does not change, and the pipeline will miss that update entirely

**Solution:** 
A cursor column must increase monotonically on every change — both inserts and updates. `OrderDate` is set once when the order is created and never changes after that. Any subsequent updates to the row (status changes, delivery date updates) will not be reflected by a change in `OrderDate`, making it invisible to the pipeline. `updated_at`, on the other hand, is modified by the trigger function on every INSERT and UPDATE, ensuring the pipeline always picks up the latest state of every row that changed since the last run.

**Tags**
- approach / concept-clarity (skill)

##### Input 11
**Type:** Choice

**Question:** GlobalMart's business team raises a new requirement: "We want to track how our customers' addresses change over time; 

for example, if a customer moves from Mumbai to Bangalore, we need to retain both the old and the new address in our pipeline." Currently, whenever a customer updates their address, the old record is overwritten. Which SCD strategy should be applied to handle this requirement?

**Options:** 
- SCD Type 1 on `customers`, overwrite the old address with the new one but add a `last_updated` column to track when the change happened

- SCD Type 2 on `customers`, insert a new row for every address change, mark the old row as inactive, and set an `is_current` flag on the latest row so both historical and current records are preserved

- SCD Type 1 on `address`, retain only the current address since delivery systems only need the latest record

- SCD Type 2 on `payments` — payment records change frequently and need full history tracked

**Correct Options:** 
- SCD Type 2 on `customers`, insert a new row for every address change, mark the old row as inactive, and set an `is_current` flag on the latest row so both historical and current records are preserved

**Solution:** 
SCD Type 2 is the right strategy when the business needs to retain both the historical state and the current state of a record. For this requirement, every time a customer's address changes, the existing row is closed out (marked inactive with an `end_date` or `is_current = false`) and a new row is inserted representing the new address as the current version. This allows the team to query any point-in-time state — for example, "what address did this customer have during a specific order?" SCD Type 1 would simply overwrite the old address, making historical analysis impossible.

**Tags**
- approach / concept-clarity (skill)

##### Input 12
**Type:** Text

>[!CAUTION]
Please ensure you complete both tasks in this activity and verify all Bronze tables before proceeding. You will not be able to return to this activity.

>[!IMPORTANT]
> Enable Change Data Feed (CDF) on all Bronze tables before proceeding. CDF allows the Silver layer to track only the rows that changed since the last run — inserts, updates, and deletes — so that future incremental loads do not need to rescan the entire Bronze table.

```python
CATALOG = "<your-catalog>"
SCHEMA  = "bronze"

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


### Problem Statement & Project Setup
#### Overview
Introduction to the GlobalMart case study, project architecture, and all resources required to complete the pipeline build.

#### Level
beginner

#### Industries
- retail-and-cpg

#### Tags
- data-understanding (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

GlobalMart is a retail e-commerce company that processes transactions across online and in-store channels. Their operational data sits across two systems:

- **Postgres (Supabase):** Transactional records — orders and order line items
- **Azure Data Lake Storage Gen2:** Batch exports from upstream systems — customers, products, addresses, payments, payment methods, and returns

In this project, you will build an end-to-end data pipeline on Databricks that ingests raw data from both sources, cleans and enriches it, and delivers a reporting-ready Gold layer following the Medallion Architecture.


**Tags**


##### Input 2
**Type:** Text

>[!NOTE]
> Download the following resources before starting the project. These will be referenced across all activities.

- Ensure your ADLS storage account and container are set up with the following folder structure under `raw-data/` before proceeding to the next activity:

```
<your-storage-account> (Storage Account)
└── <your-container> (Container)
    └── raw-data/
        ├── addresses/
        ├── customers/
        ├── payment_methods/
        ├── payments/
        ├── products/
        └── returns/
```

- [Data Model](https://cdn.enqurious.com/images/d454da48-17dc-451e-b4ae-465353a66272_gbmart-data-model.webp)
- [Data Dictionary](https://cdn.enqurious.com/others/fa98985a-5e04-44b4-bfaf-37263a67516a_globalmartdatadictionary.xlsx)

**Tags**


##### Input 3
**Type:** Text

>[!IMPORTANT]
> Use an All-Purpose Cluster throughout this project for all notebook executions. Do not use Job Compute unless explicitly instructed.

>[!IMPORTANT]
> Your catalog has already been created in Unity Catalog. Create the following schemas within your catalog before starting:

- `bronze`
- `silver`
- `gold`

> All tables built across this project must follow the three-level namespace: `<your-catalog>.<schema>.<table>.`

**Tags**


