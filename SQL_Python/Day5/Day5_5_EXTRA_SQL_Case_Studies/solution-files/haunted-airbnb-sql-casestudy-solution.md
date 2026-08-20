# Haunted Airbnb SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> Ananya is building the "Seriously Haunted" homepage carousel and needs the top spenders first.

**Your Task:**
Show the property name and total amount paid for every booking at a property with haunting_level 4 or higher, highest amount paid first.

**Solution:**

```sql
SELECT p.property_name, b.total_paid
FROM bookings b
JOIN properties p ON b.property_id = p.property_id
WHERE p.haunting_level >= 4
ORDER BY b.total_paid DESC;
```

---

### Question 2 — Intermediate

> **Business Context:**
> The board meeting needs a **Property Performance Report** — revenue and guest satisfaction, side by side.

**Your Task:**
For each property, show total revenue from bookings and the average review star rating, rounded to 2 decimals.

**Solution:**

```sql
SELECT
    p.property_name,
    SUM(b.total_paid)        AS total_revenue,
    ROUND(AVG(gr.stars), 2)  AS avg_stars
FROM bookings b
JOIN properties p     ON b.property_id = p.property_id
JOIN ghost_reviews gr ON gr.booking_id = b.booking_id
GROUP BY p.property_name;
```

---

### Question 3 — Intermediate

> **Business Context:**
> Marketing wants to know which guests are repeat visitors, for a "Frequent Fright" loyalty push.

**Your Task:**
Show guests who have booked more than once — their name, booking count, and total amount spent.

**Solution:**

```sql
SELECT
    g.full_name,
    COUNT(b.booking_id) AS booking_count,
    SUM(b.total_paid)   AS total_spent
FROM bookings b
JOIN guests g ON b.guest_id = g.guest_id
GROUP BY g.guest_id, g.full_name
HAVING COUNT(b.booking_id) > 1;
```

---

### Question 4 — Advanced

> **Business Context:**
> Ananya wants a **Haunting Leaderboard** — within each haunting_level bracket, which property is actually pulling in the revenue.

**Your Task:**
For each property, show its name, haunting_level, total revenue, its rank within its haunting_level bracket by revenue (highest = Rank 1), and its share of that bracket's total revenue as a percentage rounded to 2 decimals.

**Solution:**

```sql
WITH property_revenue AS (
    SELECT
        p.property_id,
        p.property_name,
        p.haunting_level,
        SUM(b.total_paid) AS total_revenue
    FROM bookings b
    JOIN properties p ON b.property_id = p.property_id
    GROUP BY p.property_id, p.property_name, p.haunting_level
)
SELECT
    property_name,
    haunting_level,
    total_revenue,
    RANK() OVER (PARTITION BY haunting_level ORDER BY total_revenue DESC) AS level_rank,
    ROUND(
        total_revenue * 100.0 / SUM(total_revenue) OVER (PARTITION BY haunting_level),
        2
    ) AS pct_of_level_total
FROM property_revenue
ORDER BY haunting_level DESC, level_rank;
```
