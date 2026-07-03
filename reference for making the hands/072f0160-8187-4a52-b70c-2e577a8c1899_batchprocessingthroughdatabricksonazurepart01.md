# Batch Processing through Databricks on Azure - Part 01
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

![Image](https://cdn.enqurious.com/images/e128963d-23c1-4516-88f9-3c8a99c88410_AzureDatabricks.webp)

## Learning Objectives
- Learn Databricks Fundamentals
- Ingest and Process Data
- Understanding ADLS
- Data Wrangling using Pyspark & Spark SQL

## Prerequisites
- SQL Basics
- Python Basics
- Fundamentals of Pyspark and Distributing Computing

## Duration of Completion
270 minutes

## Level
N A

## Industries
- e-commerce

## Tags
- data-storage (skill)
- cloud-management (skill)
- approach (skill)
- azure (tool)
- data-understanding (skill)
- data-quality (skill)
- data-wrangling (skill)
- databricks (tool)
- spark (tool)
- sql (tool)

## Scenarios
### Working with Azure
#### Overview
Working with Azure

#### Level
beginner

#### Industries
- e-commerce

#### Tags
- data-storage (skill)
- cloud-management (skill)
- approach (skill)
- azure (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!IMPORTANT] 
>Ensure to download following artifacts before proceeding with the hands on

<p style="text-align: justify;">
<strong>Globalmart</strong> have shared a dump of data for you to start building the ETL layer:
<a href="https://cdn.enqurious.com/others/ed78c320-ed57-4bb8-be63-5bce34508836_Ecom Dataset.zip">Dataset</a>
</p>

<p style="text-align: justify;">
Globalmart has also provided you with a <a href="https://cdn.enqurious.com/images/1a334d64-5868-4765-9d0c-895536b0a811_Ecom er-diagram.webp">Data Model</a> and <a href="https://cdn.enqurious.com/others/a63582a2-eeac-4cda-a064-59057717919f_Ecom_data_dict.zip">Data Dictionary</a> of their OLTP system since this becomes an important part of the pipeline.
</p>

**Tags**


##### Input 2
**Type:** Text

### **Instructions:**

You have recently been appointed as a data engineer at Globalmart. You are required to do the following: 

*   Identify the storage system which you would like to use as the ideal storage solution for Globalmart.
    
*   Ensure you optimize the availability of data in data storage
    
*   Data stored should be accessible to integrate with different analytic tools
    
*   Download the sample dataset provided and shift that to the storage system.
    

#### **Outcome:**

*   identify and create the storage solution in Azure
    
*   data loaded in the storage solution

**Tags**


##### Input 3
**Type:** File Upload

**Question:** Upload a snapshot of your console after completing the task.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- azure / azure-data-lake (tool)

##### Input 4
**Type:** Short Answer

**Question:** Give the name of the storage solution in Azure cloud which is the best fit for the requirement above. Explain why did you choose the said solution.

**Template:** null

**Tags**
- azure / azure-data-lake (tool)

##### Input 5
**Type:** Short Answer

**Question:** How did you ensure the reliability of the identified storage solution?

**Template:** null

**Tags**
- cloud-management / resilience-and-availability (skill)

##### Input 6
**Type:** Choice

**Question:** Match the cloud platforms with their corresponding **data lakes**:
<br>
Cloud Platforms:
1. Amazon Web Services (AWS)
2. Microsoft Azure
3. Google Cloud Platform (GCP)

Data Lakes:
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

**Tags**
- azure / azure-data-lake (tool)
- azure / blob-storage (tool)

##### Input 7
**Type:** Choice

**Question:** Which of the following is NOT a storage tier option in Azure Blob Storage?

**Options:** 
- Warm Storage

- Archive Storage

- Cool Storage

- Hot Storage

**Correct Options:** 
- Warm Storage

**Tags**
- azure / azure-data-lake (tool)

##### Input 8
**Type:** Choice

**Question:** How can you automate the deletion or transition of blobs to different access tiers in Azure Blob Storage?

**Options:** 
- By setting Azure RBAC roles

- By configuring lifecycle management policies

- By using Azure SQL Database settings

- By configuring virtual machine network security groups (NSGs)

**Correct Options:** 
- By configuring lifecycle management policies

**Tags**
- data-storage / delta-lakehouse / optimize (skill)
- cloud-management / resilience-and-availability (skill)

##### Input 9
**Type:** Choice

**Question:** GlobalMart is concerned about accidental deletions of product data in their Azure Data Lake Storage. They want to retain the ability to restore deleted blobs. What feature should they enable to address this concern?

**Options:** 
- Blob versioning

- Archive Storage

- Azure RBAC roles

- Lifecycle management policies

**Correct Options:** 
- Blob versioning

**Tags**
- cloud-management / disaster-recovery (skill)

##### Input 10
**Type:** Choice

**Question:** GlobalMart has enabled versioning on their product data container in ADLS. During an update, a large number of blobs were mistakenly overwritten. What steps should the team take to restore the previous versions of these blobs?

**Options:** 
- Use the Azure Portal to manually restore each blob

- Write a script to list and promote the previous versions of the blobs to the current versions

- Use Azure RBAC roles to revert the changes

- Disable versioning and re-upload the blobs

**Correct Options:** 
- Write a script to list and promote the previous versions of the blobs to the current versions

**Tags**
- cloud-management / disaster-recovery (skill)

##### Input 11
**Type:** Choice

**Question:** GlobalMart's IT department is setting up a new application that needs to access blobs in an ADLS container without any human intervention. What is the recommended way to control access for this application?

**Options:** 
- By using individual user accounts with the required Azure RBAC roles

- By making the container public

- By using a managed identity with the required Azure RBAC roles

- By configuring container policies only

**Correct Options:** 
- By using a managed identity with the required Azure RBAC roles

**Tags**
- cloud-management / authentication (skill)
- cloud-management / authorization (skill)

##### Input 12
**Type:** Choice

**Question:** GlobalMart wants to allow a third-party vendor to upload files to a specific ADLS container but restrict them from reading or deleting any blobs. What steps should the IT department take? (Select all that apply)

**Options:** 
- Make the container public and use monitoring logs to track uploads

- Assign the Storage Blob Data Contributor role to the third-party vendor

- Assign the Storage Blob Data Owner role to the third-party vendor

- Configure a container policy to restrict delete permissions

- Use Azure RBAC roles to control the permissions

**Correct Options:** 
- Assign the Storage Blob Data Contributor role to the third-party vendor

- Use Azure RBAC roles to control the permissions

**Tags**
- cloud-management / authorization (skill)
- cloud-management / authentication (skill)

### Data Ingestion and Transformation in Databricks
#### Overview
Data Ingestion and Transformation in Databricks

#### Level
beginner

#### Industries
- e-commerce

#### Tags
- data-understanding (skill)
- data-storage (skill)
- data-quality (skill)
- data-wrangling (skill)
- approach (skill)
- databricks (tool)
- spark (tool)
- sql (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

### **Initial data exploration**

#### **Goals:**

*   Create dataframes by ingesting the data into Databricks
*   Gain a comprehensive understanding of the provided data.
*   Perform thorough exploration to uncover any issues or patterns.
*   Perform data wrangling to answer business queries.  
     

#### **Outcomes:**

*   Explore the data and share your insights
*   Answer the business problems asked below

**Tags**


##### Input 2
**Type:** Short Answer

**Question:** Share your insights drawn from the initial exploration of the data.

**Template:** null

**Tags**
- approach / concept-clarity (skill)
- approach / logic-building (skill)
- data-understanding / data-types (skill)

##### Input 3
**Type:** Text

>[!NOTE] 
> Perform the below data exploration using Spark SQL.

**Tags**


##### Input 4
**Type:** Code

**Question:** Write a query to identify top 10 customers by total spend.

**Language:** sql

**Snippet:** 

**Tags**
- sql (tool)
- data-wrangling / filter (skill)
- data-wrangling / sort (skill)
- data-wrangling / group-by-aggregate (skill)
- approach / logic-building (skill)

##### Input 5
**Type:** Code

**Question:** Write a query to determine the most popular shipping tier for orders.

**Language:** sql

**Snippet:** 

**Tags**
- sql (tool)
- data-wrangling / sort (skill)
- data-wrangling / group-by-aggregate (skill)
- approach / logic-building (skill)
- data-wrangling / filter (skill)

##### Input 6
**Type:** Code

**Question:** Calculate Running Total of Sales for Each Product.

**Language:** sql

**Snippet:** 

**Tags**
- data-wrangling / window (skill)
- sql (tool)

##### Input 7
**Type:** Choice

**Question:** A data engineer wants to create a relational object by pulling data from two tables. The relational object must be used by other data engineers in other sessions on the same cluster only. In order to save on storage costs, the date engineer wants to avoid copying and storing physical data.

Which of the following relational objects should the data engineer create?

**Options:** 
- Temporary view

- Managed table

- External table

- Global Temporary view

**Correct Options:** 
- Global Temporary view

**Solution:** 
Explanation:
The view type should be Global Temporary view that can be accessed in other sessions on the same cluster. Global Temporary views are tied to a cluster temporary database called global_temp.

**Tags**
- sql (tool)

##### Input 8
**Type:** Text

GlobalMart wishes to design a loyalty program for its customers. It wishes to identify 3 groups : Promoters, Potentials and Detractors based on some scoring mechanism to allocate scores to each customer based on several purchase traits shown.

  
You are required to create a summary table at a Customer level which looks like below :

![](https://cdn.enqurious.com/images/07a63724-a3f1-4155-938c-4132cd518f6a_pic1.webp)

  
Meaning of columns :

*   **customer\_name** : Name of the customer
*   **tot\_orders** : Number of orders placed
*   **tot\_returns** : Number of orders returned
*   **order\_value** : Value of orders placed (worth of orders in monetary sense)
*   **avg\_basket\_size** : Total units across all baskets / Total baskets (Read orders when you read basket). Output rounded off to lower integer

![](https://cdn.enqurious.com/images/e6153bcc-2e93-41cb-9413-5836316d927c_pic2.webp)

The total units of items = 5 + 10 + 7. Total orders = 3. So, Average basket size = 7.3 rounded off to 7. Even if the average comes out as 7.89, round it off to lower integer, i.e 7

*   **avg\_basket\_value** : (Total value of orders / Total orders placed)

![](https://cdn.enqurious.com/images/944fbecb-3694-4d91-be66-156d5a446b4a_pic3.webp)

Value of orders can be derived from Sales column in transactions table. Here, total value of orders placed by customer C1 is 5000 + 2000 + 16000. So, the average basket value will be 7666.66. Additional points if you can present the outcome as $7666.66

*   **length\_of\_stay\_days** : Total time for which the customer is active in the system (In integral days)
*   **order\_purchase\_frequency** : On an average, how many days taken to place a new order? (Rounded off to nearest integral day)

**Tags**


##### Input 9
**Type:** Code

**Question:** Write the query to write the above report.

**Language:** sql

**Snippet:** 

**Tags**
- sql (tool)
- data-wrangling / sub-query (skill)
- data-wrangling / group-by-aggregate (skill)
- data-wrangling / join (skill)

##### Input 10
**Type:** Code

**Question:** Create a view to find out the number of products provided by each supplier. Ensure that this view is not restricted and can be accessed by other notebooks within the same cluster.

**Language:** sql

**Snippet:** 

**Tags**
- sql (tool)

##### Input 11
**Type:** Text

>[!NOTE] 
> Load data into respective dataframes and use pyspark for the below data wrangling.

**Tags**


##### Input 12
**Type:** Short Answer

**Question:** Write code to identify products with an average rating of 4.5 or higher.

**Template:** null

**Tags**
- data-wrangling / filter (skill)
- data-wrangling / dataframe-processing (skill)
- data-wrangling / math-calculations (skill)

##### Input 13
**Type:** Short Answer

**Question:** Calculate the number of days between the order placement and shipping date for each order.

**Template:** null

**Tags**
- data-wrangling / dataframe-processing (skill)
- data-wrangling / date-processing (skill)

##### Input 14
**Type:** Text

The month-over-month (MoM) growth rate in sales measures the percentage change in sales from one month to the next.

Formula for MoM Growth Rate:

![](https://cdn.enqurious.com/images/771e06e1-fd00-403d-8a55-5dcf496c0c05_pic6.webp)

**Tags**


##### Input 15
**Type:** Short Answer

**Question:** Calculate the month-over-month growth rate in sales.

**Template:** null

**Tags**
- data-wrangling / dataframe-processing (skill)
- data-wrangling / date-processing (skill)

##### Input 16
**Type:** Choice

**Question:** GlobalMart's data engineering team is tasked with updating the sales transactions table with new data that arrives every hour. The new data should be added to the existing data in the table, preserving the historical transactions.

Which of the following commands should they use to achieve this?

**Options:** 
- df.write.mode("add").format("delta").saveAsTable("globalmart.sales_transactions")

- df.write.mode("insert").format("delta").saveAsTable("globalmart.sales_transactions")

- df.write.append().saveAsTable("globalmart.sales_transactions")

- df.write.mode("append").format("delta").saveAsTable("globalmart.sales_transactions")

**Correct Options:** 
- df.write.mode("append").format("delta").saveAsTable("globalmart.sales_transactions")

**Tags**


##### Input 17
**Type:** Choice

**Question:** GlobalMart's data team maintains a product inventory table that gets updated nightly with the latest inventory levels. Each update should replace the existing inventory data to reflect the current stock levels accurately.

Which of the following commands should they use to achieve this?

**Options:** 
- df.write.overwrite().format("delta").saveAsTable("globalmart.product_inventory")

- df.write.mode("overwrite").saveAsTable("globalmart.product_inventory")

- df.write.mode("replace").format("delta").saveAsTable("globalmart.product_inventory")

- df.write.mode("overwrite").format("delta").saveAsTable("globalmart.product_inventory")

**Correct Options:** 
- df.write.mode("overwrite").format("delta").saveAsTable("globalmart.product_inventory")

**Tags**


##### Input 18
**Type:** Text

Globalmart wants the following report to be created to analyze its product performance and gain insights:

![](https://cdn.enqurious.com/images/4f865957-e0ba-42b6-b1a8-dafca2f4753a_pic5.webp)

**Tags**


##### Input 19
**Type:** Short Answer

**Question:** Write the code for the product analysis report below:

**Template:** null

**Tags**
- data-wrangling / math-calculations (skill)
- data-wrangling / join (skill)
- data-wrangling / dataframe-processing (skill)
- data-wrangling / filter (skill)

##### Input 20
**Type:** Text

Based on the total spending, classify customers into different loyalty tiers (e.g., Silver, Gold, Platinum). The criteria can be as follows:

Type 

Total Spend

Platinum

More than 1000

Gold   

500-1000

Silver

Below 500

**Tags**


##### Input 21
**Type:** Short Answer

**Question:** Write a code to classify the customers.

Note: Use 'lit' operator to complete this task

**Template:** null

**Tags**
- approach / concept-clarity (skill)
- data-wrangling / dataframe-processing (skill)
- data-wrangling / filter (skill)

##### Input 22
**Type:** File Upload

**Question:** Upload all the artifacts created a part of this activity

**Max No. of Files:** 4

**Max File Size:** 10

**Allowed File Types:** ANY, PYTHON, DOCUMENT, JUPYTER_NOTEBOOK

**Tags**


