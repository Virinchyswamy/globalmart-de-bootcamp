# Targeting Sub-Categories that Drive Revenue at GlobalMart
## Content Type
Scenario

## Overview
**What if you could tell a business exactly which products are worth doubling down on — and which ones are quietly dragging them down?**

In this hands-on scenario, you’ll act as the go-to data analyst at **GlobalMart**, a fast-growing ecommerce brand that’s preparing for next year’s big strategy. The leadership team senses that not all product lines are performing equally — but they don’t have the data to prove it. That’s where you come in.

Your job is to turn rows of raw data into a clear, ranked report that reveals what’s really driving revenue inside each category.

To get there, you’ll need to combine SQL skills like joins, aggregations, and window functions — but the real value is in how you’ll **connect the dots** and build a story the business can act on.

You won’t just learn _how_ to write SQL — you’ll learn how to _think_ like a data analyst who influences decisions.

Curious which sub-categories are secretly carrying the company?

Let’s just say — the data has answers. You just need to know where (and how) to look.


## Learning Objectives
- Implement SQL joins, filters, and aggregations to extract and summarize data 
- Apply window functions to rank data values and compute dynamic metrics
- Use Common Table Expressions (CTEs) to organize complex SQL queries into modular, readable components.
- Format and compute percentage-based insights using arithmetic operations and built-in SQL formatting functions.

## Prerequisites
- Ability to use SELECT, FROM, and WHERE to retrieve and filter data from tables
- Comfort with JOIN operations to combine data from multiple tables using common keys
- Understanding of GROUP BY and aggregation functions like SUM(), COUNT(), and AVG()
- Good understanding of Common Table Expressions (CTEs)  to structure multi-step queries
- Familiarity with window functions
- Ability to perform basic arithmetic operations and formatting within SQL queries

## Duration of Completion
90 minutes

## Level
Advanced

## Industries
- e-commerce

## Tags
- approach (skill)
- data-wrangling (skill)
- sql (tool)

#### Overview
**What if you could tell a business exactly which products are worth doubling down on — and which ones are quietly dragging them down?**

In this hands-on scenario, you’ll act as the go-to data analyst at **GlobalMart**, a fast-growing ecommerce brand that’s preparing for next year’s big strategy. The leadership team senses that not all product lines are performing equally — but they don’t have the data to prove it. That’s where you come in.

Your job is to turn rows of raw data into a clear, ranked report that reveals what’s really driving revenue inside each category.

To get there, you’ll need to combine SQL skills like joins, aggregations, and window functions — but the real value is in how you’ll **connect the dots** and build a story the business can act on.

You won’t just learn _how_ to write SQL — you’ll learn how to _think_ like a data analyst who influences decisions.

Curious which sub-categories are secretly carrying the company?

Let’s just say — the data has answers. You just need to know where (and how) to look.


#### Level
advanced

#### Industries
- e-commerce

#### Tags
- approach (skill)
- data-wrangling (skill)
- sql (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

As Q4 draws to a close, the leadership team at **GlobalMart** (a major e-commerce company operating across North America and Europe) is gathering to finalize next year’s inventory investments and marketing budgets.

During the annual strategic planning meeting, Rajiv, the Head of Merchandising, shares an interesting observation from the recent quarterly data:

> *"Last quarter, a 15% discount campaign on Office Supplies didn't quite deliver the returns we expected. On the flip side, the Furniture category actually outperformed our expectations, even without an extra marketing push."*

## The Business Question

This discrepancy has prompted a broader, company-wide question: **Are we investing in the right sub-categories within our main product lines?**

Currently, GlobalMart looks at performance at a high level across three major categories: Furniture, Office Supplies, and Technology. However, leadership suspects that uneven sales performance means a handful of specific sub-categories are driving the bulk of the revenue, while others might be underperforming.

To make the most of next year's budget, the team needs to move away from broad assumptions and look at the precise data.

As a Data Analyst at GlobalMart, you have been asked by the leadership team to build a **Sub-Category Sales Contribution Report**. This data-driven report will help stakeholders make informed, strategic decisions about where to focus marketing efforts and inventory planning for the upcoming year.

- Identify which sub-categories contribute the most within their respective product categories
- Understand which sub-categories drive the highest revenue at a company-wide level
- Make informed decisions about **where to focus marketing efforts and inventory planning**


As a Data Analyst at GlobalMart, you are required to create the following report : 
![Image-image.png](https://cdn.enqurious.com/images/5be16f9d-872c-42de-9be3-e09674dd662d_image.webp)
(***Note :*** The data shown in the above snapshot is for representational purposes only)


**<u>Description: </u>**

- **category :** The category of a product
- **sub_category :** The sub category of a product
- **sub_cat_sales :** The **total sales revenue** generated by a specific sub-category
- **sub_cat_rank :** The **ranking** of the sub-category **within its parent category**, based on total sales.
- **sales_contribution_to_category :** The **percentage of the category's total sales** that a particular sub-category contributes.
- **overall_sales_contribution :** The **percentage of total company sales** that the sub-category contributes.*

**Tags**


##### Input 2
**Type:** Text

>[!NOTE] 
> 
- Server name : mentorskool.database.windows.net
Username : mskllearnlogin
Password : !@#sw2aq1
- Use the **mskl-masterclass** database
- The data dictionary and the ER-diagram is shown below:
![Image-image.png](https://cdn.enqurious.com/images/581b5aa8-6549-4277-aaa7-3b26e2e6130d_image.webp)
- Download the data dictionary [here](https://cdn.enqurious.com/others/4082f65d-5ec3-4706-990c-e79692f41c26_globalmartdd.xlsx)

>[!IMPORTANT] 
> You should take only those orders into consideration that are not cancelled or unavailable. Check order_status from ex_orders to know about it. 

**Tags**


##### Input 3
**Type:** Choice

**Question:** The sales_contribution_to_category for **Appliances** is 

**Options:** 
- 14.69%

- 15.03%

- 39.89%

- 28.44%

**Correct Options:** 
- 14.69%

**Solution:** 
```sql
-- Explanation for CTE 1: base_data
-- -----------------------------------------------------
-- Objective: Prepare a foundational dataset that shows total sales for each sub-category.
-- 
-- Step-by-step reasoning:
-- 1. We start by joining three tables:
--    - `ex_products` gives us the `category` and `sub_category` for each product.
--    - `ex_transactions` provides transaction-level sales data linked via `product_id`.
--    - `ex_orders` is used to filter out orders that were either canceled or marked unavailable.
-- 2. We're only interested in valid, completed transactions — hence the filter on `order_status`.
-- 3. We group the data by both `category` and `sub_category` to calculate the total sales (`SUM`) for each unique combination.
-- 4. The result of this CTE is a simple but powerful table: one row per sub-category with its total sales.
--    This forms the base upon which all rankings and contribution metrics will be calculated.

with base_data as (
    SELECT
        p.category,
        p.sub_category,
        ROUND(SUM(t.Sales_Amount), 2) AS sub_cat_sales
    FROM ex_products p
    JOIN ex_transactions t
        ON t.product_id = p.product_id
    JOIN ex_orders o 
        ON o.order_id = t.order_ID AND o.order_status NOT IN  ('canceled','unavailable')
	GROUP BY p.category, p.sub_category
),

-- Explanation for CTE 2: aggregated_data
-- -----------------------------------------------------
-- Objective: Enrich the base data by adding rankings and total sales aggregations.
--
-- Step-by-step reasoning:
-- 1. For each row (i.e., each sub-category), we add a ranking (`sub_cat_rank`) that tells us how well it performed 
--    compared to other sub-categories within the same parent category. We use `DENSE_RANK()` for this so that if two sub-categories
--    have the same sales, they get the same rank without gaps in numbering.
-- 2. We then calculate `total_cat_sales` using a window function that sums up `sub_cat_sales` for each category.
--    This lets us later express each sub-category's performance as a percentage of its category.
-- 3. We also calculate `overall_sales` — the grand total of all sub-category sales — using a window function without any partitioning.
--    This is used to assess the sub-category’s contribution to the company's entire sales landscape.
-- 4. This CTE essentially prepares all the intermediate data we need for the final report — in a flat, reusable format.

aggregated_data AS (
    SELECT 
        * ,
        DENSE_RANK() OVER (PARTITION BY category ORDER BY sub_cat_sales DESC) AS sub_cat_rank,
        SUM(sub_cat_sales) OVER (PARTITION BY category) AS total_cat_sales,
		SUM(sub_cat_sales) OVER() AS overall_sales
    FROM base_data
)

-- Explanation for Final SELECT
-- -----------------------------------------------------
-- Objective: Generate a clean and insightful final report for business stakeholders.
--
-- Step-by-step reasoning:
-- 1. We select only the required columns to keep the output focused and readable.
--    - `category` and `sub_category` for context.
--    - `sub_cat_rank` to show relative performance within the category.
-- 2. We compute two contribution metrics:
--    - `sales_contribution_to_category`: How much does this sub-category contribute to its own category? (e.g., Chairs make up 40% of Furniture)
--    - `overall_sales_contribution`: How much does this sub-category contribute to total company sales?
-- 3. We use `FORMAT(..., 'P2')` to express both metrics as percentages with two decimal places — this makes them presentation-ready for dashboards or reports.
-- 4. The final result helps decision-makers answer: Which sub-categories are leading or lagging within their category and across the company?

SELECT category,
       sub_category,
       sub_cat_rank,
       FORMAT(sub_cat_sales / total_cat_sales, 'P2') AS sales_contribution_to_category,
       FORMAT(sub_cat_sales / overall_sales, 'P2') AS overall_sales_contribution
FROM aggregated_data
WHERE sub_category = 'Appliances'

```

**Tags**
- data-wrangling / derived-column (skill)
- data-wrangling / filter (skill)
- data-wrangling / window / sql-window-running-totals (skill)
- data-wrangling / text-processing (skill)
- data-wrangling / join (skill)
- data-wrangling / group (skill)

##### Input 4
**Type:** Choice

**Question:** Which of the following sub-categories contribute more than 7% to overall company sales?

**Options:** 
- Accessories

- Tables

- Storage

- Furnishings

**Correct Options:** 
- Accessories

- Tables

- Storage

**Solution:** 
```sql
-- Explanation for CTE 1: base_data
-- -----------------------------------------------------
-- Objective: Prepare a foundational dataset that shows total sales for each sub-category.
-- 
-- Step-by-step reasoning:
-- 1. We start by joining three tables:
--    - `ex_products` gives us the `category` and `sub_category` for each product.
--    - `ex_transactions` provides transaction-level sales data linked via `product_id`.
--    - `ex_orders` is used to filter out orders that were either canceled or marked unavailable.
-- 2. We're only interested in valid, completed transactions — hence the filter on `order_status`.
-- 3. We group the data by both `category` and `sub_category` to calculate the total sales (`SUM`) for each unique combination.
-- 4. The result of this CTE is a simple but powerful table: one row per sub-category with its total sales.
--    This forms the base upon which all rankings and contribution metrics will be calculated.

with base_data as (
    SELECT
        p.category,
        p.sub_category,
        ROUND(SUM(t.Sales_Amount), 2) AS sub_cat_sales
    FROM ex_products p
    JOIN ex_transactions t
        ON t.product_id = p.product_id
    JOIN ex_orders o 
        ON o.order_id = t.order_ID AND o.order_status NOT IN  ('canceled','unavailable')
	GROUP BY p.category, p.sub_category
),

-- Explanation for CTE 2: aggregated_data
-- -----------------------------------------------------
-- Objective: Enrich the base data by adding rankings and total sales aggregations.
--
-- Step-by-step reasoning:
-- 1. For each row (i.e., each sub-category), we add a ranking (`sub_cat_rank`) that tells us how well it performed 
--    compared to other sub-categories within the same parent category. We use `DENSE_RANK()` for this so that if two sub-categories
--    have the same sales, they get the same rank without gaps in numbering.
-- 2. We then calculate `total_cat_sales` using a window function that sums up `sub_cat_sales` for each category.
--    This lets us later express each sub-category's performance as a percentage of its category.
-- 3. We also calculate `overall_sales` — the grand total of all sub-category sales — using a window function without any partitioning.
--    This is used to assess the sub-category’s contribution to the company's entire sales landscape.
-- 4. This CTE essentially prepares all the intermediate data we need for the final report — in a flat, reusable format.

aggregated_data AS (
    SELECT 
        * ,
        DENSE_RANK() OVER (PARTITION BY category ORDER BY sub_cat_sales DESC) AS sub_cat_rank,
        SUM(sub_cat_sales) OVER (PARTITION BY category) AS total_cat_sales,
		SUM(sub_cat_sales) OVER() AS overall_sales
    FROM base_data
)

-- Explanation for Final SELECT
-- -----------------------------------------------------
-- Objective: Generate a clean and insightful final report for business stakeholders.
--
-- Step-by-step reasoning:
-- 1. We select only the required columns to keep the output focused and readable.
--    - `category` and `sub_category` for context.
--    - `sub_cat_rank` to show relative performance within the category.
-- 2. We compute two contribution metrics:
--    - `sales_contribution_to_category`: How much does this sub-category contribute to its own category? (e.g., Chairs make up 40% of Furniture)
--    - `overall_sales_contribution`: How much does this sub-category contribute to total company sales?
-- 3. We use `FORMAT(..., 'P2')` to express both metrics as percentages with two decimal places — this makes them presentation-ready for dashboards or reports.
-- 4. The final result helps decision-makers answer: Which sub-categories are leading or lagging within their category and across the company?

SELECT category,
       sub_category,
       sub_cat_rank,
       FORMAT(sub_cat_sales / total_cat_sales, 'P2') AS sales_contribution_to_category,
       FORMAT(sub_cat_sales / overall_sales, 'P2') AS overall_sales_contribution
FROM aggregated_data
WHERE sub_cat_sales * 1.0 / overall_sales > 0.07

```

**Tags**
- data-wrangling / filter (skill)
- data-wrangling / window / sql-window-running-totals (skill)
- data-wrangling / text-processing (skill)
- data-wrangling / join (skill)
- data-wrangling / sub-query (skill)

##### Input 5
**Type:** Choice

**Question:** What is the rank of the sub-category **Machines**?

**Options:** 
- 4

- 2

- 3

- 1

**Correct Options:** 
- 3

**Solution:** 
```sql
-- Explanation for CTE 1: base_data
-- -----------------------------------------------------
-- Objective: Prepare a foundational dataset that shows total sales for each sub-category.
-- 
-- Step-by-step reasoning:
-- 1. We start by joining three tables:
--    - `ex_products` gives us the `category` and `sub_category` for each product.
--    - `ex_transactions` provides transaction-level sales data linked via `product_id`.
--    - `ex_orders` is used to filter out orders that were either canceled or marked unavailable.
-- 2. We're only interested in valid, completed transactions — hence the filter on `order_status`.
-- 3. We group the data by both `category` and `sub_category` to calculate the total sales (`SUM`) for each unique combination.
-- 4. The result of this CTE is a simple but powerful table: one row per sub-category with its total sales.
--    This forms the base upon which all rankings and contribution metrics will be calculated.

with base_data as (
    SELECT
        p.category,
        p.sub_category,
        ROUND(SUM(t.Sales_Amount), 2) AS sub_cat_sales
    FROM ex_products p
    JOIN ex_transactions t
        ON t.product_id = p.product_id
    JOIN ex_orders o 
        ON o.order_id = t.order_ID AND o.order_status NOT IN  ('canceled','unavailable')
	GROUP BY p.category, p.sub_category
),

-- Explanation for CTE 2: aggregated_data
-- -----------------------------------------------------
-- Objective: Enrich the base data by adding rankings and total sales aggregations.
--
-- Step-by-step reasoning:
-- 1. For each row (i.e., each sub-category), we add a ranking (`sub_cat_rank`) that tells us how well it performed 
--    compared to other sub-categories within the same parent category. We use `DENSE_RANK()` for this so that if two sub-categories
--    have the same sales, they get the same rank without gaps in numbering.
-- 2. We then calculate `total_cat_sales` using a window function that sums up `sub_cat_sales` for each category.
--    This lets us later express each sub-category's performance as a percentage of its category.
-- 3. We also calculate `overall_sales` — the grand total of all sub-category sales — using a window function without any partitioning.
--    This is used to assess the sub-category’s contribution to the company's entire sales landscape.
-- 4. This CTE essentially prepares all the intermediate data we need for the final report — in a flat, reusable format.

aggregated_data AS (
    SELECT 
        * ,
        DENSE_RANK() OVER (PARTITION BY category ORDER BY sub_cat_sales DESC) AS sub_cat_rank,
        SUM(sub_cat_sales) OVER (PARTITION BY category) AS total_cat_sales,
		SUM(sub_cat_sales) OVER() AS overall_sales
    FROM base_data
)

-- Explanation for Final SELECT
-- -----------------------------------------------------
-- Objective: Generate a clean and insightful final report for business stakeholders.
--
-- Step-by-step reasoning:
-- 1. We select only the required columns to keep the output focused and readable.
--    - `category` and `sub_category` for context.
--    - `sub_cat_rank` to show relative performance within the category.
-- 2. We compute two contribution metrics:
--    - `sales_contribution_to_category`: How much does this sub-category contribute to its own category? (e.g., Chairs make up 40% of Furniture)
--    - `overall_sales_contribution`: How much does this sub-category contribute to total company sales?
-- 3. We use `FORMAT(..., 'P2')` to express both metrics as percentages with two decimal places — this makes them presentation-ready for dashboards or reports.
-- 4. The final result helps decision-makers answer: Which sub-categories are leading or lagging within their category and across the company?

SELECT sub_cat_rank
FROM (
    SELECT
        sub_category,
        DENSE_RANK() OVER (PARTITION BY category ORDER BY sub_cat_sales DESC) AS sub_cat_rank
    FROM base_data
) t
WHERE sub_category = 'Machines';

```

**Tags**
- data-wrangling / filter (skill)
- data-wrangling / sort (skill)
- data-wrangling / window / sql-window-running-totals (skill)
- data-wrangling / text-processing (skill)
- data-wrangling / join (skill)
- data-wrangling / group (skill)

