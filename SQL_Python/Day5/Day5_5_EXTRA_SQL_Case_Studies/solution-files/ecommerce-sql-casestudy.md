# Ecommerce SQL Case Study — CartX Analytics

---

## Problem Statement

**CartX** is a D2C ecommerce platform that saw a massive surge in orders during the Diwali sale. Now, with the **Year-End Mega Sale** just around the corner, the leadership team needs to study what went right, what went wrong, and where to focus energy next.

The decisions on the table:
- Which products are running dangerously low on stock and need restocking before the sale goes live
- Which payment methods are customers trusting the most, and how much revenue each is generating
- Which customers are loyal enough to get early access to the sale
- Which products are the true revenue champions within each category

You are CartX's **Ecommerce Data Analyst**. The Head of Inventory, the Payments Lead, the CRM Manager, and the Category Heads are all waiting on your queries before the sale goes live next week.

---

## Database Schema & Sample Data

### Table 1: `products`

CartX's active product catalog.

| product_id | name                    | category    | price | stock_quantity |
|------------|-------------------------|-------------|-------|----------------|
| 1          | Wireless Earbuds        | Electronics | 2499  | 45             |
| 2          | Yoga Mat                | Sports      | 899   | 8              |
| 3          | Stainless Steel Bottle  | Kitchen     | 599   | 0              |
| 4          | Gaming Mouse            | Electronics | 1799  | 23             |
| 5          | Running Shoes           | Sports      | 3299  | 5              |

---

### Table 2: `customers`

Registered CartX shoppers and their account type.

| customer_id | full_name      | city       | account_type |
|-------------|----------------|------------|--------------|
| 1           | Aman Verma     | Pune       | Prime        |
| 2           | Shreya Das     | Hyderabad  | Registered   |
| 3           | Kartik Nair    | Chennai    | Prime        |
| 4           | Pooja Mehta    | Delhi      | Guest        |
| 5           | Vikram Singh   | Kolkata    | Registered   |

---

### Table 3: `orders`

Every order placed on CartX along with its payment method and current status.

| order_id | customer_id | order_date | payment_method | status    |
|----------|-------------|------------|----------------|-----------|
| 2001     | 1           | 2024-11-01 | UPI            | Delivered |
| 2002     | 2           | 2024-11-05 | Credit Card    | Delivered |
| 2003     | 3           | 2024-11-08 | UPI            | Returned  |
| 2004     | 1           | 2024-11-15 | Net Banking    | Delivered |
| 2005     | 4           | 2024-11-20 | Credit Card    | Delivered |

---

### Table 4: `order_items`

Individual products within each order.

| item_id | order_id | product_id | quantity | discount_pct |
|---------|----------|------------|----------|--------------|
| 1       | 2001     | 1          | 1        | 10           |
| 2       | 2001     | 4          | 1        | 5            |
| 3       | 2002     | 5          | 1        | 0            |
| 4       | 2004     | 2          | 2        | 15           |
| 5       | 2005     | 3          | 1        | 0            |

> Revenue per line item = `price × quantity × (1 - discount_pct / 100)`

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> The Head of Inventory has issued an urgent alert — the Year-End Mega Sale starts in 7 days and several products are already out of stock or critically low. Any product with fewer than 10 units remaining needs to be flagged immediately for emergency restocking. Missing a sale due to stockouts is not an option.

**Your Task:**
Retrieve the name, category, price, and stock quantity of all products with fewer than 10 units in stock, sorted by stock quantity from lowest to highest.

---

### Question 2 — Intermediate

> **Business Context:**
> The Payments Lead is in discussions with UPI platforms and credit card networks for better transaction fee rates before the next sale. To negotiate from a position of strength, she needs to know exactly how much revenue each payment method has generated from successfully delivered orders.

**Your Task:**
For each payment method, calculate the total revenue generated from delivered orders only. Use the revenue formula provided above.

---

### Question 3 — Intermediate

> **Business Context:**
> The CRM Manager is setting up an **Early Access Program** for the Year-End Sale — shoppers who have placed more than one order on CartX will get a 24-hour head start before the sale opens to the public. The team needs a list of qualifying customers to send out personalised invitations.

**Your Task:**
Identify customers who have placed more than one order. For each such customer, show their name, city, account type, and total number of orders placed.

---

### Question 4 — Advanced

> **Business Context:**
> Each Category Head owns the performance of their segment — Electronics, Sports, and Kitchen. Before the Year-End Sale, they want a **Category Product Leaderboard** showing how each product ranks within its category by revenue, and how much of the category's total revenue it contributes. This shapes which products get homepage banners and which get deeper discounts to drive volume.

**Your Task:**
For each product, show its name, category, total revenue earned, its rank within its category based on revenue (highest = Rank 1), and its revenue as a percentage of the category's total revenue, rounded to 2 decimal places. Order the result by category, then by rank.

---

*The sale goes live in 7 days. Make sure the data is ready before the banners are.*
