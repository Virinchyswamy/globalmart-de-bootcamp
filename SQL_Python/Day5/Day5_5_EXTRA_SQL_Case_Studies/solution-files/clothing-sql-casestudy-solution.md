# Clothing SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> The Merchandising team is curating the **Winter Sale** product lineup. As a starting point, they want to review all products priced above ₹1,500 — these are the premium items they plan to discount strategically to drive festive conversions.

**Your Task:**
Retrieve the name, category, and price of all products priced above ₹1,500, sorted by price from highest to lowest.

**Solution:**

```sql
SELECT name, category, price
FROM products
WHERE price > 1500
ORDER BY price DESC;
```

---

### Question 2 — Intermediate

> **Business Context:**
> The Finance Manager needs a **Category Revenue Report** for the festive season. However, she has explicitly asked to exclude returned orders from the numbers — only delivered orders should count toward revenue. This will give a clean picture of actual earnings per category.

**Your Task:**
For each product category, calculate the total revenue generated from delivered orders only. Use the revenue formula provided above.

**Solution:**

```sql
SELECT
    p.category,
    SUM(p.price * oi.quantity * (1 - oi.discount_pct / 100.0)) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
WHERE o.status = 'Delivered'
GROUP BY p.category;
```

---

### Question 3 — Intermediate

> **Business Context:**
> The CRM Lead is designing a **Repeat Buyer Reward Program**. Customers who have placed more than one order are considered high-intent buyers and will be the first to receive exclusive early access to the Winter Sale. The team needs a list of these customers to begin outreach.

**Your Task:**
Identify customers who have placed more than one order. For each such customer, show their name, city, membership tier, and the total number of orders they have placed.

**Solution:**

```sql
WITH repeat_buyers AS (
    SELECT
        customer_id,
        COUNT(order_id) AS total_orders
    FROM orders
    GROUP BY customer_id
    HAVING COUNT(order_id) > 1
)
SELECT
    c.full_name,
    c.city,
    c.membership_tier,
    rb.total_orders
FROM repeat_buyers rb
JOIN customers c ON rb.customer_id = c.customer_id
ORDER BY rb.total_orders DESC;
```

---

### Question 4 — Advanced

> **Business Context:**
> Each category head at StyleHub is accountable for their segment's performance. Going into the planning cycle, they want a **Product Leaderboard** for their category — showing how each product ranks by revenue within the category and what share of the category's total revenue it contributes. This will directly influence which products get more shelf space and marketing budget.

**Your Task:**
For each product, show its name, category, total revenue earned, its rank within its category based on revenue (highest = Rank 1), and its revenue as a percentage of the total revenue for that category, rounded to 2 decimal places. Order the result by category, then by rank.

**Solution:**

```sql
WITH product_revenue AS (
    SELECT
        p.product_id,
        p.name,
        p.category,
        SUM(p.price * oi.quantity * (1 - oi.discount_pct / 100.0)) AS total_revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.name, p.category
)
SELECT
    name,
    category,
    total_revenue,
    RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS category_rank,
    ROUND(
        total_revenue * 100.0 / SUM(total_revenue) OVER (PARTITION BY category),
        2
    ) AS pct_of_category_total
FROM product_revenue
ORDER BY category, category_rank;
```
