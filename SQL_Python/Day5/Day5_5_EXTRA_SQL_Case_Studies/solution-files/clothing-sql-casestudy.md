# Clothing SQL Case Study — StyleHub Retail Analytics

---

## Problem Statement

**StyleHub** is a fast-growing D2C fashion brand selling across its website and physical stores in major Indian cities. With the **festive season just wrapped up**, the leadership team wants to evaluate how the business actually performed — which products flew off the shelves, who their most loyal customers are, and which categories need more attention.

The findings will shape decisions on:
- Which products to push in the upcoming **Winter Sale campaign**
- Which customers to target for exclusive **loyalty offers**
- Which categories are actually driving revenue vs. just volume
- How individual products are performing within their own category

You are StyleHub's **Retail Data Analyst**. The Head of Merchandising, the CRM Lead, and the Finance Manager are all waiting on your queries before the strategy call tomorrow.

---

## Database Schema & Sample Data

### Table 1: `products`

The complete catalog of items StyleHub sells.

| product_id | name               | category  | brand     | price |
|------------|--------------------|-----------|-----------|-------|
| 1          | Classic White Tee  | Tops      | UrbanEdge | 799   |
| 2          | Slim Fit Chinos    | Bottoms   | UrbanEdge | 1999  |
| 3          | Floral Sundress    | Dresses   | BloomWear | 2499  |
| 4          | Leather Jacket     | Outerwear | RawHide   | 5999  |
| 5          | Cargo Shorts       | Bottoms   | UrbanEdge | 1299  |

---

### Table 2: `customers`

Registered StyleHub customers and their loyalty tier.

| customer_id | full_name       | city      | membership_tier |
|-------------|-----------------|-----------|-----------------|
| 1           | Neha Kapoor     | Mumbai    | Platinum        |
| 2           | Ravi Shankar    | Delhi     | Gold            |
| 3           | Ananya Singh    | Bangalore | Silver          |
| 4           | Kabir Malhotra  | Mumbai    | Gold            |
| 5           | Tanya Bose      | Kolkata   | Platinum        |

---

### Table 3: `orders`

Every order placed on the platform.

| order_id | customer_id | order_date | status    |
|----------|-------------|------------|-----------|
| 1001     | 1           | 2024-10-05 | Delivered |
| 1002     | 2           | 2024-10-12 | Delivered |
| 1003     | 3           | 2024-11-01 | Returned  |
| 1004     | 1           | 2024-11-15 | Delivered |
| 1005     | 4           | 2024-11-20 | Pending   |

---

### Table 4: `order_items`

Line items within each order, including quantity and any discount applied.

| item_id | order_id | product_id | quantity | discount_pct |
|---------|----------|------------|----------|--------------|
| 1       | 1001     | 3          | 2        | 10           |
| 2       | 1001     | 1          | 1        | 0            |
| 3       | 1002     | 4          | 1        | 5            |
| 4       | 1004     | 2          | 1        | 0            |
| 5       | 1005     | 5          | 3        | 15           |

> Revenue per line item = `price × quantity × (1 - discount_pct / 100)`

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> The Merchandising team is curating the **Winter Sale** product lineup. As a starting point, they want to review all products priced above ₹1,500 — these are the premium items they plan to discount strategically to drive festive conversions.

**Your Task:**
Retrieve the name, category, and price of all products priced above ₹1,500, sorted by price from highest to lowest.

---

### Question 2 — Intermediate

> **Business Context:**
> The Finance Manager needs a **Category Revenue Report** for the festive season. However, she has explicitly asked to exclude returned orders from the numbers — only delivered orders should count toward revenue. This will give a clean picture of actual earnings per category.

**Your Task:**
For each product category, calculate the total revenue generated from delivered orders only. Use the revenue formula provided above.

---

### Question 3 — Intermediate

> **Business Context:**
> The CRM Lead is designing a **Repeat Buyer Reward Program**. Customers who have placed more than one order are considered high-intent buyers and will be the first to receive exclusive early access to the Winter Sale. The team needs a list of these customers to begin outreach.

**Your Task:**
Identify customers who have placed more than one order. For each such customer, show their name, city, membership tier, and the total number of orders they have placed.

---

### Question 4 — Advanced

> **Business Context:**
> Each category head at StyleHub is accountable for their segment's performance. Going into the planning cycle, they want a **Product Leaderboard** for their category — showing how each product ranks by revenue within the category and what share of the category's total revenue it contributes. This will directly influence which products get more shelf space and marketing budget.

**Your Task:**
For each product, show its name, category, total revenue earned, its rank within its category based on revenue (highest = Rank 1), and its revenue as a percentage of the total revenue for that category, rounded to 2 decimal places. Order the result by category, then by rank.

---

*The strategy call is at 10 AM. Get the numbers right.*
