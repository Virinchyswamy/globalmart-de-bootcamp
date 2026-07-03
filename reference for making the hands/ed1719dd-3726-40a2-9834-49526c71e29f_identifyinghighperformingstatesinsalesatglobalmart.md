# Identifying High-Performing States in Sales at GlobalMart
## Content Type
Scenario

## Overview
In this scenario, you will step into the role of a Data Analyst at GlobalMart, a leading E-Commerce enterprise in North America and Europe. The company's Senior VP of Customer Relations is optimistic about the performance of sales across various states, but to validate this belief, a detailed data analysis is required. Your task will be to analyze the sales data and identify states that have exceeded the national average in terms of sales. This analysis will not only help in substantiating the perceived success but also in recognizing regions with exceptional sales performance.

## Learning Objectives
- Apply window functions to solve problems

## Prerequisites
- Basic understanding of SQL and database concepts.
- Familiarity with aggregate functions in SQL.

## Duration of Completion
30 minutes

## Level
Advanced

## Industries
- e-commerce

## Tags
- data-wrangling (skill)
- sql (tool)

#### Overview
In this scenario, you will step into the role of a Data Analyst at GlobalMart, a leading E-Commerce enterprise in North America and Europe. The company's Senior VP of Customer Relations is optimistic about the performance of sales across various states, but to validate this belief, a detailed data analysis is required. Your task will be to analyze the sales data and identify states that have exceeded the national average in terms of sales. This analysis will not only help in substantiating the perceived success but also in recognizing regions with exceptional sales performance.

#### Level
advanced

#### Industries
- e-commerce

#### Tags
- data-wrangling (skill)
- sql (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

**GlobalMart**, a burgeoning E-Commerce enterprise, dominates the markets in North America and Europe, catering to various products such as Technology, Office Supplies, and Furniture across 120 regions. 

The Senior VP of Customer Relations is optimistic about the company's performance, perceiving robust sales across all states. However, to substantiate this belief, there's a need to analyze data. 

As a newly appointed Data Analyst at GlobalMart, your task is to identify the states that have surpassed the national average in terms of sales. This analysis aims to validate the perceived success and pinpoint regions with outstanding sales performance.

Check the snapshot to understand the outcome format : 

![](https://cdn.enqurious.com/images/e3ac4286-6c61-4b95-90dd-195e97c37085_416cf34f-9ca6-42eb-8b6d-19bcc160795e_83d04ac6-cb74-4a96-a06a-e0d5442aa126_image.webp)

Use the connection details and tables mentioned [here](https://cdn.enqurious.com/documents/1a3a1540-9648-4f3a-a45c-4df6ee6b0c3b_database-credentials.txt) to work on this scenario.  
Download the data dictionary from [here](https://cdn.enqurious.com/others/b3e87239-a903-4106-87dd-d442c0459694_Data_dictionary_globalmart.xlsx).

**Tags**


##### Input 2
**Type:** Text

**GlobalMart**, a burgeoning E-Commerce enterprise, dominates the markets in North America and Europe, catering to various products such as Technology, Office Supplies, and Furniture across 120 regions. 

The Senior VP of Customer Relations is optimistic about the company's performance, perceiving robust sales across all states. However, to substantiate this belief, there's a need to analyze data. 

As a newly appointed Data Analyst at GlobalMart, your task is to identify the states that have surpassed the national average in terms of sales. This analysis aims to validate the perceived success and pinpoint regions with outstanding sales performance.

Check the snapshot to understand the outcome format : 
<figure class="image"><img src="https://cdn.enqurious.com/images/e3ac4286-6c61-4b95-90dd-195e97c37085_416cf34f-9ca6-42eb-8b6d-19bcc160795e_83d04ac6-cb74-4a96-a06a-e0d5442aa126_image.webp" width="1313" height="223"></figure>


>[!NOTE]
- Server name : mentorskool.database.windows.net
  Username : mskllearnlogin
  Password : !@#sw2aq1
- The data dictionary and the ER-diagram is shown below:

![Image-ER-diagram.png](https://cdn.enqurious.com/images/751b06c3-2660-442d-b3d8-5170bd949c92_ER-diagram.webp)




Use the **mskl-masterclass** database

[Here](https://cdn.enqurious.com/others/a9ff4875-993a-412c-bad8-fffaef0b4426_globalmart-dd.xlsx) is the data dictionary and ER diagram for the tables you'll be working with.


**Tags**


##### Input 3
**Type:** Code

**Question:** Write SQL query to fetch the outcome as shown in the table below:

| State          | Avg_Sales |
|----------------|----------:|
| Arizona        | 312.45 |
| Colorado       | 278.91 |
| Georgia        | 356.72 |
| Nevada         | 421.38 |
| Virginia       | 295.64 |

>[!IMPORTANT]
> These values are for representation purpose only and do not correspond to any actual dataset.

**Language:** sql

**Snippet:** 

**Solution:** 
```sql
/*-------------------------------------------------------------------------
CTE 1: TransactionData

Purpose:
Create a detailed transaction-level dataset by combining information from
multiple tables. This CTE enriches each transaction with:
- Order purchase date from the Orders table
- Customer state from the Locations table

Think of this as building a "master dataset" that contains all the
information needed for further analysis.
-------------------------------------------------------------------------*/
WITH TransactionData AS (
    SELECT
        t.*,
        o.order_purchase_date AS Order_Date,
        l.state
    FROM transactions t
    JOIN orders o
        ON t.Order_ID = o.order_id
    JOIN customers c
        ON o.Customer_ID = c.Customer_ID
    JOIN locations_01 l
        ON c.postal_code = l.postal_code
),

/*-------------------------------------------------------------------------
CTE 2: StateSummary

Purpose:
Aggregate transaction data at the state level.

For each state:
- Calculate the average sales value.
- Produce one row per state.

This helps us understand the sales performance of each state before
comparing it against the national average.
-------------------------------------------------------------------------*/
StateSummary AS (
    SELECT
        state,
        AVG(sales) AS sales
    FROM TransactionData
    GROUP BY state
),

/*-------------------------------------------------------------------------
CTE 3: AvgSales

Purpose:
Calculate the national average sales across all states.

The window function AVG() OVER() computes a single average value using
all rows from StateSummary and makes it available on every row.

This allows us to compare each state's average sales against the
overall national average.
-------------------------------------------------------------------------*/
AvgSales AS (
    SELECT
        *,
        AVG(sales) OVER() AS avg_national_sales
    FROM StateSummary
)

/*-------------------------------------------------------------------------
Final Query

Purpose:
Identify states whose average sales are greater than the national average.

Logic:
- Compare each state's average sales with avg_national_sales.
- Return only those states that outperform the national benchmark.
-------------------------------------------------------------------------*/
SELECT
    state,
    sales
FROM AvgSales
WHERE (
    CASE
        WHEN sales > avg_national_sales THEN 1
        ELSE 0
    END
) = 1;
```

**Tags**


##### Input 4
**Type:** Choice

**Question:** The count of states with a sales average surpassing the national average is _______

**Options:** 
- 12

- 11

- 13

- None of the above

- 10

**Correct Options:** 
- 13

**Tags**
- data-wrangling / sub-query (skill)

##### Input 5
**Type:** Choice

**Question:** The following state(s) have sales average surpassing the national average - 

**Options:** 
- Texas

- Washington

- Indiana

- California

**Correct Options:** 
- Texas

- Indiana

- California

**Tags**
- sql (tool)

