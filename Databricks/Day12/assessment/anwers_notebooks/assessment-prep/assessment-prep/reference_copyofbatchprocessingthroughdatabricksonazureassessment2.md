# Copy of Batch Processing through Databricks on Azure | Assessment - 2
## Content Type
Project

## Overview
<p style="text-align: center;">
<strong>Globalmart, an ecommerce startup, faces challenges with data inaccuracies, schema inconsistencies, and a lack of trust in data systems from stakeholders. What measures are necessary to address and resolve these issues?</strong>
</p>
<br>
<p style="text-align:justify;">
<strong>GlobalMart</strong> is a startup revolutionizing the shopping experience for its customers, both in the retail landscape and the online marketplace. As GlobalMart continues to expand, it is increasingly relying on data-driven decision making.
</p>
<p style="text-align: justify;">
For <strong>GlobalMart</strong> to be data-driven, the stakeholders needs to be provided with accurate and refreshed data. Unfortunately, this has become a great challenge and bottleneck. The journey that started as a way to enhance operational efficiency and decision-making is now leading lot of friction between stakeholders.
</p>

Globalmart is now faced with following challenges
<br>
- Data Silos and Absence of a Single Source of Truth
- Data Inconsistency and Quality Issues
- Lack of Access Control and Compliance Challenges
- Complex and Time-Consuming Data Transformation Processes
- Unclear Data Location and Origin Leading to Redundancy
<br>
<p style="text-align:justify;">
These issues led to lack of trust in data systems rendering them useless.
In this project you will be spending time to implement the following architecture that addresses all the problems that Globalmart is currently facing in their data systems
</p>

![Image-image.png](https://cdn.enqurious.com/images/5db0d6ca-017d-4856-b361-05935d204ecd_image.webp)

## Learning Objectives
- Ingest and Process Data
- Implementing Medallion architecture
- Design and implement dimensional models for the Gold layer
- Efficiently loading only new or updated data to optimize ETL processes

## Prerequisites
- Understanding Medallion architecture
- Gain an understanding of how to manage incremental data loading.

## Duration of Completion
120 minutes

## Level
Intermediate

## Industries
- e-commerce

## Tags
- approach (skill)
- quality (skill)
- data-understanding (skill)
- data-storage (skill)
- data-quality (skill)
- data-wrangling (skill)
- batch-etl (skill)
- cloud-management (skill)
- distributed-processing (skill)
- databricks (tool)
- azure (tool)
- spark (tool)

## Scenarios
### Building ELT Layer
#### Overview
Building the bronze layer by loading data into the storage location, then ingesting it into the bronze layer for further processing.



#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- approach (skill)
- quality (skill)
- data-understanding (skill)
- data-storage (skill)
- data-quality (skill)
- data-wrangling (skill)
- batch-etl (skill)
- cloud-management (skill)
- distributed-processing (skill)
- databricks (tool)
- azure (tool)
- spark (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!NOTE] 
> Ensure that a Azure Data Lake Storage (ADLS) account is set up, data is stored in it, and the storage is mounted in Databricks.



**Tags**


##### Input 2
**Type:** Text

### Creation of Bronze Layer (Expected Duration:20 minutes)

####   
**Goal**

*   Considering the need to build an ELT pipeline you are requested to ingest data from source into the bronze layer

#### **Outcome:**

*   Data Ingested and available in Bronze Delta Lake

**Tags**


##### Input 3
**Type:** Code

**Question:** Write to code for the creation and data ingestion in the 'address' table in bronze layer.

**Language:** python

**Snippet:** 

**Tags**


##### Input 4
**Type:** Choice

**Question:** You are working on a Databricks project where you have a source delta table that stores raw addresses data and a sink table where you want to load this data. Your task is to load the data from the source delta table into the sink table in the most efficient way.

Given the scenario, can you use the COPY INTO command to load data from the source table into the sink table?

**Options:** 
- Yes

- No

**Correct Options:** 
- No

**Tags**
- data-storage / delta-lakehouse / copy-into (skill)

##### Input 5
**Type:** Choice

**Question:** You are part of a data engineering team working on a Databricks project for GlobalMart. The team is responsible for loading various data files into Delta tables for further processing and analysis. You are tasked with setting up the pipeline that ingests these files into the correct Delta tables using the COPY INTO command.

The team receives daily data files containing data from various sources. You need to load these files into a Delta tables.

Which of the following types of data sources can you use with the COPY INTO command to load the data into the respective delta table? (Select all that apply)

**Options:** 
- A Delta table storing raw Customers data.

- An Orders CSV file stored in a Azure Data Lake Storage (ADLS) container

- A Vendors Parquet file stored in an Amazon S3 bucket.

- A Products JSON file stored on the local file system of your Databricks cluster.

**Correct Options:** 
- An Orders CSV file stored in a Azure Data Lake Storage (ADLS) container

- A Vendors Parquet file stored in an Amazon S3 bucket.

- A Products JSON file stored on the local file system of your Databricks cluster.

**Tags**
- data-storage / delta-lakehouse / copy-into (skill)

##### Input 6
**Type:** Choice

**Question:** You have a folder in Azure Data Lake Storage (ADLS) which is mounted as /mnt/orders/2024/ that contains multiple CSV files. You want to load all CSV files from this folder into the orders delta table using the COPY INTO command.

Which of the following paths can you use in your COPY INTO command to achieve this? (Select all that apply)

**Options:** 
- /mnt/orders/2024/

- /mnt/orders/2024/*.csv

- /mnt/orders/2024/all_files.csv

- /mnt/orders/2024/2024_orders.csv

**Correct Options:** 
- /mnt/orders/2024/

- /mnt/orders/2024/*.csv

**Tags**
- data-storage / delta-lakehouse / copy-into (skill)

##### Input 7
**Type:** Text

You are using the following `COPY INTO` command to load data from storage into the `customers` table in the bronze layer:

    COPY INTO customers
    FROM '/path/to/files'
    FILEFORMAT = <format>
    FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true', 'mergeSchema' = 'true')
    COPY_OPTIONS ('mergeSchema' = 'true');

**Tags**


##### Input 8
**Type:** Choice

**Question:** Considering the use of inferSchema and mergeSchema options in the COPY INTO command, is it still necessary to define the customers table manually before running this command?

**Options:** 
- No, the table can be created automatically as the schema will be inferred and merged during the COPY INTO process.

- Yes, you must define the table manually because COPY INTO cannot create tables automatically, even with schema inference.

**Correct Options:** 
- Yes, you must define the table manually because COPY INTO cannot create tables automatically, even with schema inference.

**Tags**
- data-storage / delta-lakehouse / copy-into (skill)

##### Input 9
**Type:** Choice

**Question:** Due to an issue in the upstream pipeline, a duplicate file has been created and uploaded to Azure Data Lake Storage (ADLS). You are using the COPY INTO command to load files from ADLS into the bronze Delta Lake.

Considering the concept of idempotency, what will happen when the duplicate file is processed?

**Options:** 
- Yes, it will not load as COPY INTO is idempotent at the file level, ensuring the same file is not processed more than once.

- No, it will still load because COPY INTO does not support idempotency, resulting in duplicate records.

- Yes, it will load because only new or changed files are skipped, and this duplicate file is considered new.

- No, it will not load because COPY INTO enforces idempotency at the record level, preventing duplicate records from being added.

**Correct Options:** 
- Yes, it will not load as COPY INTO is idempotent at the file level, ensuring the same file is not processed more than once.

**Tags**
- data-storage / delta-lakehouse / copy-into (skill)

##### Input 10
**Type:** Text

Considering the special characters in header, would the data load into the bronze layer successfully when using the COPY INTO command in Databricks?

![](https://cdn.enqurious.com/images/419d2c4b-eeb1-4fd2-a5b7-fe1e987fab1c_image.webp)

**Tags**


##### Input 11
**Type:** Choice

**Question:** According to you, what would be the correct answer?

**Options:** 
- Yes, it will load successfully 

- No, the COPY INTO command will fail due to the special characters in the column name Cost (Rs).

**Correct Options:** 
- No, the COPY INTO command will fail due to the special characters in the column name Cost (Rs).

**Tags**
- data-storage / delta-lakehouse / copy-into (skill)
- data-wrangling / dataframe-processing (skill)

##### Input 12
**Type:** Choice

**Question:** You have a folder named orders containing three CSV files: orders1.csv, orders2.csv, and orders3.csv, each containing 100 records. These files need to be loaded into the Delta table orders_delta. You mistakenly ran the following commands twice:
<br>
COPY INTO orders_delta FROM '/mnt/orders/' FILEFORMAT = 'csv'
<br>
What will happen to the data in the Delta table orders_delta?

**Options:** 
- 300 records will be loaded only once, regardless of running the command twice.

- 300 new records will be appended each time the command is run, resulting in duplicates.

- 300 records will replace the existing records in the table each time the command is run.

**Correct Options:** 
- 300 records will be loaded only once, regardless of running the command twice.

**Tags**
- data-storage / delta-lakehouse / copy-into (skill)

##### Input 13
**Type:** File Upload

**Question:** Upload artifacts created a part of this activity

**Max No. of Files:** 3

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**


##### Input 14
**Type:** Text

### **Data Cleaning and Enrichment** (Expected Duration: 30 minutes)

### **Goal:**

*   Ingest data from the bronze layer.
*   Clean and address below data quality issues by enforcing business rules on specific columns in the Products and Payments datasets.
*   Track history and versions of cleaned data in the silver layer to ensure that any changes made to the data can be rolled back if necessary.
*   Ensure that your data pipeline is adaptable to evolving schemas by incorporating schema changes from the bronze layer.

###   
Outcome:

*   Data ingested and stored in the silver layer.
*   Business rules enforced on key columns like Actual\_Price to ensure data quality.
*   Silver Layer delta tables that support version control and schema evolution.

**Tags**


##### Input 15
**Type:** Code

**Question:** Write to code for the creation and data ingestion in the 'products' table in silver layer.

**Language:** python

**Snippet:** 

**Tags**


##### Input 16
**Type:** Text

GlobalMart has been reviewing the data quality of their product pricing and has identified that some of the prices coming from the source systems are invalid. As part of their new pricing policy, they want to ensure that the Actual\_Price of any product is not set below a certain threshold to maintain data consistency.

Business Rule:

*   The minimum allowed price for any product is 70.
*   If the Actual\_Price of any product is less than 70, it should be updated to 70.
*   If the Actual\_Price is already greater than or equal to 70, it should remain unchanged.

**Tags**


##### Input 17
**Type:** Code

**Question:** As a data engineer at GlobalMart, your job is to write the code that will validate and implement said Actual_Price business constraint on the product data.

**Language:** python

**Snippet:** 

**Tags**


##### Input 18
**Type:** Choice

**Question:** You have already created a Delta table called products to store information about GlobalMart’s product catalog. Now, you want to make changes to the schema definition to enforce a business rule which is:
* The column **Product_Rating** of the table should be between 0 and 5.
<br>
Which of the following options would best enforce this business rule in Products table? (Mark all that applies)

**Options:** 
- ALTER TABLE products
ADD CONSTRAINT Product_Rating 
CHECK (Product_Rating > 0 AND Product_Rating <= 5);

- ALTER TABLE products
ADD CHECK (Product_Rating >= 0 AND Product_Rating <= 5);

- ALTER TABLE products
ADD CONSTRAINT Product_Rating 
CHECK (Product_Rating BETWEEN 0 AND 5);

- ALTER TABLE products
ADD CONSTRAINT Product_Rating 
CHECK (Product_Rating >= 0 AND Product_Rating <= 5);

**Correct Options:** 
- ALTER TABLE products
ADD CONSTRAINT Product_Rating 
CHECK (Product_Rating BETWEEN 0 AND 5);

- ALTER TABLE products
ADD CONSTRAINT Product_Rating 
CHECK (Product_Rating >= 0 AND Product_Rating <= 5);

**Tags**
- databricks / delta-live-table / quality-constraints (tool)

##### Input 19
**Type:** Choice

**Question:** A user creates a global temporary view for the orders_df DataFrame. Afterward, she detaches the notebook. Later, when she reattaches the notebook for project-related work, what can be correctly stated about the global temporary view?

**Options:** 
- global temporary views are created in a database called temp database

- global temporary views can be still accessed even if the cluster is restarted

- global temporary views can be still accessed even if the notebook is detached and attached

- global temporary views can be accessed across many clusters

- global temporary views cannot be accessed once the notebook is detached and attached

**Correct Options:** 
- global temporary views can be still accessed even if the notebook is detached and attached

**Tags**
- data-wrangling / temporary-view (skill)

##### Input 20
**Type:** Choice

**Question:** You have been working with managed tables in your Delta Lake environment so far. Now, you need to switch to creating an external table where the data is stored in a specific location outside of the Delta Lake managed storage. This means the table data will reside outside the Delta Lake's default managed directory.

What steps would you follow to create an external table in Delta Lake?

**Options:** 
- CREATE EXTERNAL TABLE products_external
USING DELTA;

- CREATE TABLE products_external
USING DELTA
WITH EXTERNAL LOCATION '/mnt/delta/products';

- CREATE TABLE products_external
USING DELTA
LOCATION '/mnt/delta/products';

- CREATE TABLE products_external
WITH LOCATION '/mnt/delta/products';

**Correct Options:** 
- CREATE TABLE products_external
USING DELTA
LOCATION '/mnt/delta/products';

**Tags**
- data-storage / delta-lakehouse / external-table (skill)

##### Input 21
**Type:** File Upload

**Question:** Upload artifacts created a part of this activity

**Max No. of Files:** 3

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**


##### Input 22
**Type:** Choice

**Question:** You are designing the silver layer for a Delta Lake project in Databricks. You have two tables:

- silver.orders: Contains information about customer orders.
Columns: order_id, customer_id, order_date, order_amount
<br>
- silver.customers: Contains customer details.
Columns: customer_id, customer_name, customer_email
<br>
You want to  define customer_id as the primary key in silver.customers and as the foreign key insilver.orders to enforce relationships between the two tables. 

Which of the following statements about primary keys (PK) and foreign keys (FK) in Databricks are true? (Select all that apply)

**Options:** 
- Primary keys (PK) and foreign keys (FK) in Databricks are only used for reference purposes and are not enforced by the system.

- Defining primary and foreign keys in Databricks automatically ensures referential integrity between tables.

- You can use JOIN operations between orders_silver and customers_silver based on customer_id, even though foreign key constraints aren't enforced.

- Databricks will not prevent duplicate customer_id values in customers_silver even if you define it as a primary key.

- Primary and foreign keys in Databricks are enforced to prevent orphaned records (records in orders_silver without a matching customer_id in customers_silver).

**Correct Options:** 
- Primary keys (PK) and foreign keys (FK) in Databricks are only used for reference purposes and are not enforced by the system.

- You can use JOIN operations between orders_silver and customers_silver based on customer_id, even though foreign key constraints aren't enforced.

- Databricks will not prevent duplicate customer_id values in customers_silver even if you define it as a primary key.

**Tags**
- data-storage / delta-lakehouse / deltalake-constraints (skill)

##### Input 23
**Type:** Choice

**Question:** You are managing a Delta table silver.orders in Databricks, where you store order details. You want to enforce the following constraints:

- The order_id column should never be empty (i.e., it should have a NOT NULL constraint).
- The order_amount column should always be greater than zero (a CHECK constraint).
<br>
Which of the following statements about NOT NULL and CHECK constraints in Databricks are true? (Select all that apply)

**Options:** 
- The NOT NULL constraint ensures that no null values can be inserted into the order_id column.

- The CHECK constraint can be used to ensure that order_amount is always greater than zero.

- Databricks does not enforce NOT NULL and CHECK constraints; they must be handled manually.

- The CHECK constraint can be used to enforce complex business rules beyond simple value checks.

- The NOT NULL constraint is implemented by Databricks but CHECK constraint is for reference purpose only.

**Correct Options:** 
- The NOT NULL constraint ensures that no null values can be inserted into the order_id column.

- The CHECK constraint can be used to ensure that order_amount is always greater than zero.

- The CHECK constraint can be used to enforce complex business rules beyond simple value checks.

**Tags**
- data-storage / delta-lakehouse / deltalake-constraints (skill)

##### Input 24
**Type:** Text

### Dimensional Modelling: (Expected Duration: 20 minutes)

### **Goal**

*   With the clean data available, the next step is to design a dimensional model for the Gold layer to support analytical queries.
*   Ensure that the dimensional model is optimized for performance, allowing for efficient querying and reporting by downstream users.
*   Businesses looking into the analysis of the following facts for their shipping:
    *   **Shipping\_Duration**: Calculate the number of days between the OrderDate and ActualDeliveryDate.
    *   **On-time Delivery**: A boolean value indicating whether the delivery was on time.

### **Outcome**

*   Dimensional model implemented in the Gold layer, following a star schema design.
*   Fact and dimension tables created with appropriate granularity.

**Tags**


##### Input 25
**Type:** File Upload

**Question:** Upload the dimensional model

**Max No. of Files:** 2

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**


##### Input 26
**Type:** Text

Given the following list of attributes that your teammate has added to one of dimension tables:

**Order\_ID**

**Customer\_ID**

**Product\_Rating**

**Shipping\_Duration**

**City**

**Payment\_ID**

**SupplierName**

**On\_Time\_Delivery**

**Tags**


##### Input 27
**Type:** Choice

**Question:** According to you, which attribute CANNOT be a part of the dimension table?

**Options:** 
- Product_Rating

- SupplierName

- Shipping_Duration

- City

**Correct Options:** 
- Shipping_Duration

**Tags**
- data-understanding / dimensions (skill)

##### Input 28
**Type:** Choice

**Question:** True or False: Additive facts like Sales Amount or Quantity Sold can be summed across all dimensions, such as time, product, or region.

**Options:** 
- True

- False

**Correct Options:** 
- True

**Tags**
- data-understanding / dimensions (skill)

##### Input 29
**Type:** Choice

**Question:** Which of the following is a non-additive fact, meaning it cannot be summed across any dimension?

**Options:** 
- Sales Amount

- On-Time Delivery Rate

- Total Shipments

- Shipping Duration

**Correct Options:** 
- On-Time Delivery Rate

**Tags**
- data-understanding / dimensions (skill)

##### Input 30
**Type:** Text

### Building Gold Layer (Expected Duration: 20 minutes)  
 

### **Goal**

*   Implement the dimensional modelling 
*   Ensure your aggregated layer is optimal for concurrent queries from downstream teams.
    

### **Outcome**

*   Aggregated facts for downstream consumption as per dimensional model
    
*   Version control of all artifacts

**Tags**


##### Input 31
**Type:** Choice

**Question:** What is the total shipping duration for the Shipping Tier "SHP-004"?

**Options:** 
- 207691

- 2314

- 1463138

- 3045

**Correct Options:** 
- 2314

**Tags**
- data-wrangling / group-by-aggregate (skill)

##### Input 32
**Type:** Choice

**Question:** You are working with the Gold Layer in GlobalMart's data pipeline. You need to update the Shipping_Duration column for all records in the Gold Layer table, calculated as the number of days between OrderDate and ActualDeliveryDate. A new dataset containing updates and new records is available, and you need to merge it into the Gold Layer table.

Which of the following MERGE INTO operations correctly updates the Shipping_Duration column for existing records and inserts new records?

**Options:** 
- UPDATE SET *

- UPDATE SET target.Shipping_Duration = datediff(source.ActualDeliveryDate, source.OrderDate)

- INSERT SET *

- INSERT SET target.Shipping_Duration = datediff(source.ActualDeliveryDate, source.OrderDate)

**Correct Options:** 
- UPDATE SET target.Shipping_Duration = datediff(source.ActualDeliveryDate, source.OrderDate)

**Tags**
- data-storage / delta-lakehouse / merge-into (skill)

##### Input 33
**Type:** Choice

**Question:** During the process of loading the Products data into the dimension table, how many rows were inserted?

**Options:** 
- 0

- 443

- 442

- 450

**Correct Options:** 
- 442

**Tags**
- data-storage / delta-lakehouse / merge-into (skill)

##### Input 34
**Type:** Choice

**Question:** During the process of loading the Payments data into the dimension table, how many rows were updated?

**Options:** 
- 126036

- 0

- 20000

- 1200564

**Correct Options:** 
- 0

**Tags**
- data-storage / delta-lakehouse / merge-into (skill)

##### Input 35
**Type:** File Upload

**Question:** Upload artifacts created for this activity

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY

**Tags**


