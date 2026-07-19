# Ecommerce SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> The Head of Inventory has issued an urgent alert — the Year-End Mega Sale starts in 7 days and several products are already out of stock or critically low. Any product with fewer than 10 units remaining needs to be flagged immediately for emergency restocking. Missing a sale due to stockouts is not an option.

**Your Task:**
Retrieve the name, category, price, and stock quantity of all products with fewer than 10 units in stock, sorted by stock quantity from lowest to highest.

**Solution:**

```sql
SELECT name, category, price, stock_quantity
FROM products
WHERE stock_quantity < 10
ORDER BY stock_quantity ASC;
```

---

### Question 2 — Intermediate

> **Business Context:**
> The Payments Lead is in discussions with UPI platforms and credit card networks for better transaction fee rates before the next sale. To negotiate from a position of strength, she needs to know exactly how much revenue each payment method has generated from successfully delivered orders.

**Your Task:**
For each payment method, calculate the total revenue generated from delivered orders only. Use the revenue formula provided above.

**Solution:**

```sql
SELECT
    o.payment_method,
    SUM(p.price * oi.quantity * (1 - oi.discount_pct / 100.0)) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
WHERE o.status = 'Delivered'
GROUP BY o.payment_method;
```

---

### Question 3 — Intermediate

> **Business Context:**
> The CRM Manager is setting up an **Early Access Program** for the Year-End Sale — shoppers who have placed more than one order on CartX will get a 24-hour head start before the sale opens to the public. The team needs a list of qualifying customers to send out personalised invitations.

**Your Task:**
Identify customers who have placed more than one order. For each such customer, show their name, city, account type, and total number of orders placed.

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
    c.account_type,
    rb.total_orders
FROM repeat_buyers rb
JOIN customers c ON rb.customer_id = c.customer_id
ORDER BY rb.total_orders DESC;
```

---

### Question 4 — Advanced

> **Business Context:**
> Each Category Head owns the performance of their segment — Electronics, Sports, and Kitchen. Before the Year-End Sale, they want a **Category Product Leaderboard** showing how each product ranks within its category by revenue, and how much of the category's total revenue it contributes. This shapes which products get homepage banners and which get deeper discounts to drive volume.

**Your Task:**
For each product, show its name, category, total revenue earned, its rank within its category based on revenue (highest = Rank 1), and its revenue as a percentage of the category's total revenue, rounded to 2 decimal places. Order the result by category, then by rank.

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
    JOIN orders o       ON oi.order_id = o.order_id
    WHERE o.status = 'Delivered'
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
