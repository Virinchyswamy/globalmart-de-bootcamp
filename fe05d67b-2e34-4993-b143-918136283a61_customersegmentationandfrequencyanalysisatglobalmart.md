# Customer Segmentation and Frequency Analysis at GlobalMart
## Content Type
Scenario

## Overview
In this exercise, learners will perform customer segmentation and analyze purchase frequency to gain insights into customer behavior. By categorizing customers into **Potentials**, **Promoters**, and **Detractors**, learners will understand how customer engagement can be assessed and targeted for business strategies. Additionally, they will analyze the **order\_purchase\_frequency** to identify the most frequent buyers. This hands-on implementation will enhance learners' skills in customer data analysis, segmentation, and actionable insights for enhancing customer retention and engagement.

## Learning Objectives
- Develop skills to draw actionable insights from customer data to improve engagement and retention strategies.
- Understand how to calculate metrics like order_purchase_frequency and their business implications.
- Gain hands-on experience in creating and analyzing customer segmentation models.
- Learn how to categorize customers based on their purchase frequency and behavior.

## Prerequisites
- Experience in handling and analyzing customer data in tabular formats.
- Knowledge of how to calculate and interpret purchase frequency metrics.
- Familiarity with Python and Pandas for data manipulation.
- Basic understanding of customer segmentation techniques.

## Duration of Completion
90 minutes

## Level
Intermediate

## Industries
- e-commerce

## Tags
- approach (skill)
- data-understanding (skill)
- data-wrangling (skill)
- python (tool)

#### Overview
In this exercise, learners will perform customer segmentation and analyze purchase frequency to gain insights into customer behavior. By categorizing customers into **Potentials**, **Promoters**, and **Detractors**, learners will understand how customer engagement can be assessed and targeted for business strategies. Additionally, they will analyze the **order\_purchase\_frequency** to identify the most frequent buyers. This hands-on implementation will enhance learners' skills in customer data analysis, segmentation, and actionable insights for enhancing customer retention and engagement.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- approach (skill)
- data-understanding (skill)
- data-wrangling (skill)
- python (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

**GlobalMart**, a rapidly expanding retail company, is planning to launch a customer loyalty program aimed at increasing customer engagement and rewarding long-term buyers. To ensure the success of this program, GlobalMart intends to classify its customers into three distinct categories: **Promoters**, **Potentials**, and **Detractors**.

Each customer will be assigned a score based on the **order_purchase_frequency** and **avg_basket_value**. As a **data analyst**, your role will be to analyze customer data and assign appropriate scores, enabling the company to effectively target each segment within the loyalty program.

>[!IMPORTANT] 

- Click [here](https://cdn.enqurious.com/others/920221bc-2abe-420f-a54c-8acf059361d6_GlobalMartERDiagram.xlsx) to download the data dictionary.

Copy the code below to load the DataFrames inside your Python Notebook.
```python
# Importing Libraries
import numpy as np
import pandas as pd

# Load the CSV files into DataFrames
customers_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/9eab6c04-532b-40d3-9d5e-2438ec366ee0_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20customers(1).csv")
orders_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/ae936127-9b09-4c93-912e-1d6a862b5f82_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20orders.csv")
transactions_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/dd2b3166-8bd1-4410-b2a2-a839345fb9e2_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20transactions.csv")
returns_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/78adf709-576b-4d70-9ce8-418aca84b0ef_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20returns.csv")
```

**Tags**


##### Input 2
**Type:** Text

**Task to perform** 
| customer\_name | tot\_orders | tot\_returns | total\_order\_value | avg\_basket\_size | avg\_basket\_value | length\_of\_stay\_days | order\_purchase\_frequency |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Customer A | 3 | 1 | 23000 | 7 | $7666.66 | 120 | 6 |

- **customer\_name**: The name of the customer.
- **tot\_orders**: The total number of orders placed by the customer.
- **tot\_returns**: The total number of orders returned by the customer.
- **total\_order\_value**: The total monetary value of all orders placed by the customer.
- **avg\_basket\_size**: The average number of units per order placed by the customer, rounded down to the nearest integer.

**Calculation**:
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mtext>avg_basket_size</mtext><mo>=</mo><mfrac><mtext>Total&nbsp;units&nbsp;across&nbsp;all&nbsp;baskets</mtext><mtext>Total&nbsp;number&nbsp;of&nbsp;orders&nbsp;(baskets)</mtext></mfrac></mrow><annotation encoding="application/x-tex">\text{avg\_basket\_size} = \frac{\text{Total units across all baskets}}{\text{Total number of orders (baskets)}}</annotation></semantics></math>avg\_basket\_size=Total number of orders (baskets)Total units across all baskets​
Round the result down to the nearest integer.

- Example:  
If the total units across all baskets are 5 + 10 + 7 (total = 22) and the total number of orders is 3, then the average basket size would be:
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mfrac><mn>22</mn><mn>3</mn></mfrac><mo>=</mo><mn>7.3</mn><mspace width="1em"></mspace><mtext>(rounded&nbsp;down&nbsp;to&nbsp;7)</mtext></mrow><annotation encoding="application/x-tex">\frac{22}{3} = 7.3 \quad \text{(rounded down to 7)}</annotation></semantics></math>322​=7.3(rounded down to 7)

- **avg\_basket\_value**: The average value of each order placed by the customer, formatted as currency.

**Calculation**:
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mtext>avg_basket_value</mtext><mo>=</mo><mfrac><mtext>Total&nbsp;value&nbsp;of&nbsp;orders</mtext><mtext>Total&nbsp;orders&nbsp;placed</mtext></mfrac></mrow><annotation encoding="application/x-tex">\text{avg\_basket\_value} = \frac{\text{Total value of orders}}{\text{Total orders placed}}</annotation></semantics>

- Example:  
If the total order values are 5000 + 2000 + 16000 (total = 23000), and the total orders placed are 3, the average basket value would be:
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mfrac><mn>23000</mn><mn>3</mn></mfrac><mo>=</mo><mn>7666.66</mn></mrow><annotation encoding="application/x-tex">\frac{23000}{3} = 7666.66</annotation></semantics></math>323000​=7666.66
    - The output should be formatted as **$7666.66**.

- **length\_of\_stay\_days**: The total number of days the customer has been active in the system, calculated from the first to the last purchase date.

**Calculation**:  
Subtract the **first purchase date** from the **last purchase date** to calculate the number of days the customer has been active.

- Example:  
If the first purchase was on **01-01-2023** and the last purchase was on **01-05-2023**, the length of stay would be:
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mtext>Length&nbsp;of&nbsp;stay</mtext><mo>=</mo><mn>120</mn><mspace width="1em"></mspace><mtext>days</mtext></mrow><annotation encoding="application/x-tex">\text{Length of stay} = 120 \quad \text{days}</annotation></semantics></math>Length of stay=120days

- **order\_purchase\_frequency**: The average number of days between each order placed by the customer, rounded to the nearest integer.

**Calculation**:
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mtext>order_purchase_frequency</mtext><mo>=</mo><mfrac><mtext>Length&nbsp;of&nbsp;stay</mtext><mtext>Number&nbsp;of&nbsp;orders&nbsp;placed</mtext></mfrac></mrow><annotation encoding="application/x-tex">\text{order\_purchase\_frequency} = \frac{\text{Length of stay}}{\text{Number of orders placed}}</annotation></semantics></math>order\_purchase\_frequency=Number of orders placedLength of stay​
Round the result to the nearest integer.

- Example:  
If the length of stay is 120 days and the customer has placed 20 orders, the frequency would be:
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mfrac><mn>120</mn><mn>20</mn></mfrac><mo>=</mo><mn>6</mn><mspace width="1em"></mspace><mtext>(rounded&nbsp;to&nbsp;6&nbsp;days&nbsp;per&nbsp;order)</mtext></mrow><annotation encoding="application/x-tex">\frac{120}{20} = 6 \quad \text{(rounded to 6 days per order)}</annotation></semantics></math>20120​=6(rounded to 6 days per order).


**avg_rank**: This column represents the ranking of customers based on average of **frequency_rank** and **avg_basket_value_rank**. Customers with lower frequency (more frequent orders) will have a higher rank, while those with higher frequency (less frequent orders) will have a lower rank. The **dense** ranking method is used to avoid gaps in ranking.

Similarly for Customer with **Higher Average Basket Value** will get top rank and **Lower Average Basket Value** Customer will get Lower rank.

**Customer\_Category**: Customers are categorized into three segments based on their **avg_rank**:

- **Detractors**: Customers with a rank of **300 or higher**.
- **Potentials**: Customers with a rank between **150 and 299**.
- **Promoters**: Customers with a rank **below 149**.

>[!IMPORTANT] 
> When pasting your work for each task, please include the entire working code. Ensure your code can run independently, incomplete or non-functional code will only receive partial score from the AI Evaluator.

**Tags**


##### Input 3
**Type:** Choice

**Question:** Based on the return reasons in the dataset, what is the most common reason customers return a product?

**Options:** 
- Not Satisfied

- Wrong Delivery

- Damaged

- Missing Parts

**Correct Options:** 
- Not Satisfied

**Solution:** 
```python
import pandas as pd

# Load the 'returns' dataset from the provided CSV URL into a DataFrame
# This dataset contains information about product returns including the reasons for the return
returns_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/78adf709-576b-4d70-9ce8-418aca84b0ef_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20returns.csv")

# Count the occurrences of each unique return reason in the 'return_reason' column
# The 'value_counts()' method returns a series with the count of each return reason
# 'reset_index()' is used to convert the result into a DataFrame with a new index
returns_df['return_reason'].value_counts().reset_index()
```

**Tags**
- approach / concept-clarity (skill)
- data-wrangling / dataframe-processing (skill)

##### Input 4
**Type:** Choice

**Question:** Who are the top 3 customers with the highest **avg_basket_value** (Top Spenders) based on the provided list?

**Options:** 
- Jason Klamczynski, Karen Bern, Susan MacKendrick

- Logan Haushalter, Keith Dawkins, Susan MacKendrick	

- Keith Dawkins, Susan MacKendrick, Mitch Gastineau	

- Keith Dawkins, Jocasta Rupert, Theresa Coyne	

**Correct Options:** 
- Jason Klamczynski, Karen Bern, Susan MacKendrick

**Solution:** 
```python
import pandas as pd
import numpy as np

# Load the CSV files into DataFrames
# These CSVs contain customer, order, transaction, and return data
customers_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/9eab6c04-532b-40d3-9d5e-2438ec366ee0_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20customers(1).csv")
orders_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/ae936127-9b09-4c93-912e-1d6a862b5f82_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20orders.csv")
transactions_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/dd2b3166-8bd1-4410-b2a2-a839345fb9e2_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20transactions.csv")
returns_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/78adf709-576b-4d70-9ce8-418aca84b0ef_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20returns.csv")

# Check for duplicate rows in each dataset (returns rows with duplicates)
# These lines check for duplicate entries within each dataset
customers_df[customers_df.duplicated()]
orders_df[orders_df.duplicated()]
transactions_df[transactions_df.duplicated()]
returns_df[returns_df.duplicated()]

# Remove duplicates from the orders dataset
# Drop duplicate rows from orders_df to avoid counting the same order multiple times
orders_df = orders_df.drop_duplicates()

# Convert the order_purchase_date column to datetime format for easier date comparison
# This step standardizes the date format and extracts only the date and time portion
orders_df['order_purchase_date'] = pd.to_datetime(orders_df['order_purchase_date'], format='%m/%d/%y %H:%M').dt.strftime('%Y-%m-%d %H:%M')

# Filter orders where the status is 'delivered'
# This step ensures that we only work with orders that were successfully delivered
orders = orders_df[orders_df['order_status'] == 'delivered']

# Handle missing customer_ids in the orders dataset (remove rows where customer_id is NaN)
# This ensures that all orders are linked to a valid customer
orders[orders['customer_id'].isna()]
orders = orders.dropna(subset=['customer_id'])

# Check for duplicate order IDs and drop them
# Ensure that each order is counted once by removing duplicates
orders[orders['order_id'].duplicated()]
orders = orders.drop_duplicates(subset=['order_id'])

# Calculate total orders per customer (group by customer_id and count order_id)
# This creates a summary of how many orders each customer has placed
final_orders = orders.groupby('customer_id').agg(total_orders=('order_id', 'count')).reset_index()

# Merge the returns dataset with the orders dataset to track returns against orders
# We join the two datasets on 'order_id' to associate each return with its corresponding order
returns = pd.merge(orders, returns_df, how='left', on='order_id')

# Calculate total returns per customer (group by customer_id and count return_reason)
# This aggregates the return data by customer to calculate how many returns each customer made
final_returns = returns.groupby('customer_id').agg(total_returns=('return_reason', 'count')).reset_index()

# Aggregate transactions data at the order level (sum of sales_amt and qty)
# Here, we calculate the total value of each order and the quantity of items ordered
transactions = transactions_df.groupby('order_id').agg(order_value=('sales_amt', 'sum'), total_qty=('qty', 'sum'))

# Merge the aggregated transactions with the orders dataset to link order details with transaction values
# This combines the order and transaction data, creating a single DataFrame with both order and financial information
df = pd.merge(orders, transactions, how='inner', on='order_id')

# Aggregating sales and quantity data at the customer level
# Summing the total order values and quantities for each customer
# Calculating the average basket size and value at the customer level
final_transactions = df.groupby('customer_id').agg(order_value=('order_value', 'sum'), sum_qty=('total_qty', 'sum'), total_orders=('order_id', 'count'))
final_transactions = df.groupby('customer_id').agg(order_value=('order_value', 'sum'), avg_basket_size=('total_qty', 'mean'), avg_basket_value=('order_value', 'mean')).reset_index()

# Round order_value and avg_basket_value to 2 decimal places, and floor avg_basket_size to the lower integer value
# This ensures consistency in the financial data and rounds basket sizes down to the nearest integer
final_transactions['order_value'] = final_transactions['order_value'].round(2)
final_transactions['avg_basket_size'] = np.floor(final_transactions['avg_basket_size'])
final_transactions['avg_basket_value'] = final_transactions['avg_basket_value'].round(2)

# Convert avg_basket_size to integer type for clarity in analysis
final_transactions['avg_basket_size'] = final_transactions['avg_basket_size'].astype(int)

# Calculate the first purchase date (joining date) for each customer
# This determines the date each customer made their first purchase
duration = orders.groupby('customer_id').agg(joining_date=('order_purchase_date', 'min'), last_purchase_date=('order_purchase_date', 'max')).reset_index()

# Extract the date part of the joining date (remove time from the date)
# This simplifies the date by focusing only on the date portion (removes time)
duration['joining_date'] = pd.to_datetime(duration['joining_date'], format='%Y-%m-%d %H:%M').dt.strftime('%Y-%m-%d')
duration['joining_date'] = pd.to_datetime(duration['joining_date'], format='%Y-%m-%d')

# Add last purchase date column (latest purchase date) and calculate the days spent in the system
# This calculates the total time (in days) that a customer has been active, from first to last purchase
duration['last_purchase_date'] = pd.to_datetime(duration['last_purchase_date'], format='%Y-%m-%d %H:%M')
duration['days_in_system'] = (duration['last_purchase_date'] - duration['joining_date']).dt.days

# Rename the column for clarity
# Rename the calculated column to make its meaning clearer
duration = duration.rename(columns={'days_in_system': 'length_of_stay_days'})

# Merge all the aggregated datasets (orders, returns, transactions, and duration) into one final dataset
# Combining all customer-level data into one DataFrame for easier analysis
result = final_orders.merge(final_returns, on='customer_id', how='inner')
result = result.merge(final_transactions, on='customer_id', how='inner')
result = result.merge(duration, on='customer_id', how='inner')

# Calculate the average order purchase frequency for each customer by dividing days in the system by total orders
# This gives us an idea of how frequently each customer makes a purchase
result['order_purchase_frequency'] = np.floor(result['length_of_stay_days'] / result['total_orders']).astype(int)

# Merge the customer details from the customers dataframe into the result dataset
# This step adds customer names and other details to the result dataset for a comprehensive output
result = result.merge(customers_df, on='customer_id', how='inner')

# Select only the required columns for the final output
# We are selecting specific columns for our final dataset output
reqd_columns = ['customer_name', 'total_orders', 'total_returns', 'order_value', 'avg_basket_size', 'avg_basket_value', 'length_of_stay_days', 'order_purchase_frequency']
result = result[reqd_columns]

# Rank the customers based on their order_purchase_frequency (higher frequency = higher rank)
# This ranks customers by how frequently they make purchases, using a dense ranking method
result['frequency_rank'] = result['order_purchase_frequency'].rank(method='dense').astype(int)

# Rank the customers based on their avg_basket_value (higher value = higher rank)
# This ranks customers by their average basket value in descending order (higher value = higher rank)
result['avg_basket_value_rank'] = result['avg_basket_value'].rank(method='dense', ascending=False).astype(int)

# Sort the result by order_purchase_frequency to view the most frequent buyers at the top
# Sorting ensures that we can easily view customers who make the most frequent purchases
result.head()

# Calculate the average rank by combining the frequency rank and the average basket value rank
# The average rank will give a balanced view of a customer's frequency and basket value performance
result['avg_rank'] = ((result['frequency_rank'] + result['avg_basket_value_rank']) / 2).astype(int)

# Display the Top 3 spenders from the list 
result[result['avg_basket_value_rank'].isin([1,2,3])]
```

**Tags**
- data-wrangling / filter (skill)
- data-wrangling / dataframe-processing (skill)
- data-wrangling / join (skill)
- data-wrangling / group (skill)
- data-wrangling / aggregate (skill)

##### Input 5
**Type:** Choice

**Question:** Which customer category has the highest number of customers?

**Options:** 
- Promoters

- Potentials

- Detractors

**Correct Options:** 
- Potentials

**Solution:** 
```python
import pandas as pd
import numpy as np

# Load the CSV files into DataFrames
# These CSVs contain customer, order, transaction, and return data
customers_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/9eab6c04-532b-40d3-9d5e-2438ec366ee0_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20customers(1).csv")
orders_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/ae936127-9b09-4c93-912e-1d6a862b5f82_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20orders.csv")
transactions_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/dd2b3166-8bd1-4410-b2a2-a839345fb9e2_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20transactions.csv")
returns_df = pd.read_csv("https://mentorskool-platform-uploads.s3.ap-south-1.amazonaws.com/documents/78adf709-576b-4d70-9ce8-418aca84b0ef_83d04ac6-cb74-4a96-a06a-e0d5442aa126_Dataset%20-%20Ecommerce.xlsx%20-%20returns.csv")

# Check for duplicate rows in each dataset (returns rows with duplicates)
# These lines check for duplicate entries within each dataset to ensure data quality
customers_df[customers_df.duplicated()]
orders_df[orders_df.duplicated()]
transactions_df[transactions_df.duplicated()]
returns_df[returns_df.duplicated()]

# Remove duplicates from the orders dataset to avoid counting the same order multiple times
orders_df = orders_df.drop_duplicates()

# Convert the 'order_purchase_date' column to datetime format for easier date comparisons
# This step standardizes the date format and extracts only the date and time portion
orders_df['order_purchase_date'] = pd.to_datetime(orders_df['order_purchase_date'], format='%m/%d/%y %H:%M').dt.strftime('%Y-%m-%d %H:%M')

# Filter orders where the status is 'delivered'
# This step ensures that we only work with orders that were successfully delivered
orders = orders_df[orders_df['order_status'] == 'delivered']

# Handle missing customer_ids in the orders dataset (remove rows where customer_id is NaN)
# This ensures that only valid customer data is included in the analysis
orders[orders['customer_id'].isna()]
orders = orders.dropna(subset=['customer_id'])

# Check for duplicate order IDs and drop them
# This ensures that each order is counted once by removing any duplicate order entries
orders[orders['order_id'].duplicated()]
orders = orders.drop_duplicates(subset=['order_id'])

# Calculate total orders per customer by grouping by 'customer_id' and counting the 'order_id'
# This creates a summary of how many orders each customer has placed
final_orders = orders.groupby('customer_id').agg(total_orders=('order_id', 'count')).reset_index()

# Merge the returns dataset with the orders dataset to track returns against orders
# We join the two datasets on 'order_id' to associate each return with its corresponding order
returns = pd.merge(orders, returns_df, how='left', on='order_id')

# Calculate total returns per customer by grouping by 'customer_id' and counting the 'return_reason'
# This aggregates the return data by customer to calculate how many returns each customer made
final_returns = returns.groupby('customer_id').agg(total_returns=('return_reason', 'count')).reset_index()

# Aggregate transaction data at the order level (sum of sales_amt and qty)
# Here, we calculate the total value of each order and the quantity of items ordered
transactions = transactions_df.groupby('order_id').agg(order_value=('sales_amt', 'sum'), total_qty=('qty', 'sum'))

# Merge the aggregated transactions data with the orders dataset to link order details with transaction values
df = pd.merge(orders, transactions, how='inner', on='order_id')

# Aggregating sales and quantity data at the customer level
# Summing the total order values and quantities for each customer
# Calculating the average basket size and value at the customer level
final_transactions = df.groupby('customer_id').agg(order_value=('order_value', 'sum'), sum_qty=('total_qty', 'sum'), total_orders=('order_id', 'count'))
final_transactions = df.groupby('customer_id').agg(order_value=('order_value', 'sum'), avg_basket_size=('total_qty', 'mean'), avg_basket_value=('order_value', 'mean')).reset_index()

# Round order_value and avg_basket_value to 2 decimal places, and floor avg_basket_size to the lower integer value
# This ensures consistency in the financial data and rounds basket sizes down to the nearest integer
final_transactions['order_value'] = final_transactions['order_value'].round(2)
final_transactions['avg_basket_size'] = np.floor(final_transactions['avg_basket_size'])
final_transactions['avg_basket_value'] = final_transactions['avg_basket_value'].round(2)

# Convert avg_basket_size to integer type for clarity in analysis
final_transactions['avg_basket_size'] = final_transactions['avg_basket_size'].astype(int)

# Calculate the first and last purchase date for each customer (joining date and last purchase date)
# This helps calculate the time span (i.e., how long each customer has been active)
duration = orders.groupby('customer_id').agg(joining_date=('order_purchase_date', 'min'), last_purchase_date=('order_purchase_date', 'max')).reset_index()

# Extract the date part of the joining date (removes time from the datetime)
# This step simplifies the date by focusing on the date portion only (removes time)
duration['joining_date'] = pd.to_datetime(duration['joining_date'], format='%Y-%m-%d %H:%M').dt.strftime('%Y-%m-%d')
duration['joining_date'] = pd.to_datetime(duration['joining_date'], format='%Y-%m-%d')

# Add last purchase date column and calculate the number of days the customer has been in the system
# This helps us determine how long each customer has been active, i.e., their length of stay
duration['last_purchase_date'] = pd.to_datetime(duration['last_purchase_date'], format='%Y-%m-%d %H:%M')
duration['days_in_system'] = (duration['last_purchase_date'] - duration['joining_date']).dt.days

# Rename the 'days_in_system' column to 'length_of_stay_days' for clarity
duration = duration.rename(columns={'days_in_system': 'length_of_stay_days'})

# Merge all the aggregated datasets (orders, returns, transactions, and duration) into one final dataset
# This combines all customer-level data into one DataFrame for easier analysis
result = final_orders.merge(final_returns, on='customer_id', how='inner')
result = result.merge(final_transactions, on='customer_id', how='inner')
result = result.merge(duration, on='customer_id', how='inner')

# Calculate the average order purchase frequency for each customer by dividing the total days in system by the total orders
# This gives us a sense of how often each customer makes purchases
result['order_purchase_frequency'] = np.floor(result['length_of_stay_days'] / result['total_orders']).astype(int)

# Merge the customer details from the customers dataframe into the result dataset
# This step adds customer names and other demographic information to the final dataset
result = result.merge(customers_df, on='customer_id', how='inner')

# Select only the required columns for the final output
# This step ensures that we have the necessary columns for further analysis or reporting
reqd_columns = ['customer_name', 'total_orders', 'total_returns', 'order_value', 'avg_basket_size', 'avg_basket_value', 'length_of_stay_days', 'order_purchase_frequency']
result = result[reqd_columns]

# Rank the customers based on their order_purchase_frequency (higher frequency = higher rank)
# We use a dense ranking method where customers with the same frequency get the same rank
result['frequency_rank'] = result['order_purchase_frequency'].rank(method='dense').astype(int)

# Rank the customers based on their avg_basket_value (higher value = higher rank)
# We rank customers by their average basket value in descending order
result['avg_basket_value_rank'] = result['avg_basket_value'].rank(method='dense', ascending=False).astype(int)

# Sort the result by order_purchase_frequency to view the most frequent buyers at the top
# Sorting ensures that we can easily view customers who make the most frequent purchases
result.head()

# Calculate the average rank by combining the frequency rank and the average basket value rank
# This step gives a balanced view of a customer's frequency and basket value performance
result['avg_rank'] = ((result['frequency_rank'] + result['avg_basket_value_rank']) / 2).astype(int)

# Define a function to segment customers based on their average rank
# Customers are categorized as 'Detractors', 'Potentials', or 'Promoters' based on their rank
def customer_segmentation(rank):
  if rank >= 300:
    return 'Detractors'
  elif rank >= 150:
    return 'Potentials'
  else:
    return 'Promoters'

# Apply the segmentation function to the 'avg_rank' column
result['Customer_Category'] = result['avg_rank'].apply(customer_segmentation)

# Get the count of customers in each category (Detractors, Potentials, Promoters)
# This shows how many customers fall into each category based on their performance
result['Customer_Category'].value_counts()

```

**Tags**
- approach / concept-clarity (skill)
- data-wrangling / join (skill)
- data-wrangling / group (skill)
- data-wrangling / aggregate (skill)
- data-wrangling / dataframe-processing (skill)

