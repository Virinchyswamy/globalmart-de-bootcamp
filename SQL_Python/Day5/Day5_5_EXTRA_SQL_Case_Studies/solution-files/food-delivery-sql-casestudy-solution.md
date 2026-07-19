# Food Delivery SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> The Mumbai City Ops Lead wants a list of high-performing restaurant partners in the city — specifically those with a rating above 4.0. These restaurants will be featured in the **"Top Picks in Mumbai"** section on the app homepage this week.

**Your Task:**
Retrieve the name, cuisine, and rating of all restaurants in Mumbai with a rating above 4.0, sorted by rating from highest to lowest.

**Solution:**

```sql
SELECT name, cuisine, rating
FROM restaurants
WHERE city = 'Mumbai'
  AND rating > 4.0
ORDER BY rating DESC;
```

---

### Question 2 — Intermediate

> **Business Context:**
> The VP of Partnerships wants to know which cuisines are the real revenue drivers on the platform. She also wants to see average delivery time per cuisine — slow delivery on a popular cuisine is a red flag that needs to be addressed before the pitch. Only delivered orders should be counted.

**Your Task:**
For each cuisine, calculate the total revenue and average delivery time, considering only delivered orders.

**Solution:**

```sql
SELECT
    r.cuisine,
    SUM(oi.quantity * oi.price)          AS total_revenue,
    ROUND(AVG(o.delivery_time_mins), 2)  AS avg_delivery_time_mins
FROM orders o
JOIN restaurants r  ON o.restaurant_id = r.restaurant_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY r.cuisine;
```

---

### Question 3 — Intermediate

> **Business Context:**
> The Head of Customer Experience is building a **QuickBite Loyalist Program** for customers who have ordered from more than one unique restaurant. These are the platform's most exploratory users — they're engaged, they trust the platform, and they're worth rewarding. The team needs their details to craft a personalised offer.

**Your Task:**
Identify customers who have placed orders from more than one unique restaurant. Show their name, city, membership plan, and the number of unique restaurants they have ordered from.

**Solution:**

```sql
WITH explorer_customers AS (
    SELECT
        customer_id,
        COUNT(DISTINCT restaurant_id) AS unique_restaurants
    FROM orders
    GROUP BY customer_id
    HAVING COUNT(DISTINCT restaurant_id) > 1
)
SELECT
    c.full_name,
    c.city,
    c.membership,
    ec.unique_restaurants
FROM explorer_customers ec
JOIN customers c ON ec.customer_id = c.customer_id
ORDER BY ec.unique_restaurants DESC;
```

---

### Question 4 — Advanced

> **Business Context:**
> Each City Ops Lead is responsible for their city's restaurant revenue. Before the investor pitch, they want a **City Restaurant Leaderboard** — showing how each restaurant ranks within its city by revenue, and what share of the city's total platform revenue it accounts for. This will highlight which partners are carrying the city.

**Your Task:**
For each restaurant, show its name, city, total revenue, its rank within its city based on revenue (highest = Rank 1), and its revenue as a percentage of the city's total platform revenue, rounded to 2 decimal places. Order the result by city, then by rank.

**Solution:**

```sql
WITH restaurant_revenue AS (
    SELECT
        o.restaurant_id,
        SUM(oi.quantity * oi.price) AS total_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY o.restaurant_id
)
SELECT
    r.name,
    r.city,
    rr.total_revenue,
    RANK() OVER (PARTITION BY r.city ORDER BY rr.total_revenue DESC) AS city_rank,
    ROUND(
        rr.total_revenue * 100.0 / SUM(rr.total_revenue) OVER (PARTITION BY r.city),
        2
    ) AS pct_of_city_total
FROM restaurant_revenue rr
JOIN restaurants r ON rr.restaurant_id = r.restaurant_id
ORDER BY r.city, city_rank;
```
