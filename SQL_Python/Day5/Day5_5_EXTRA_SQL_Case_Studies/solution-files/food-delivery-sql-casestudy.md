# Food Delivery SQL Case Study — QuickBite Analytics

---

## Problem Statement

**QuickBite** is one of India's fastest-growing food delivery platforms, operating across 12 cities with over 8,000 restaurant partners. After a record-breaking Diwali season, the leadership team wants to dig into the numbers before their **Series B investor pitch**.

The investors are going to ask tough questions about:
- Which restaurant partners are actually performing vs. just taking up shelf space
- Which cuisines are driving the most revenue and delivering the fastest
- Who QuickBite's most loyal customers are
- Which restaurants dominate their city and by how much

You've been brought in as the **Growth Data Analyst**. The VP of Partnerships, the Head of Customer Experience, and the City Ops Leads are depending on your queries to walk into that pitch room with confidence.

---

## Database Schema & Sample Data

### Table 1: `restaurants`

Partner restaurants listed on the QuickBite platform.

| restaurant_id | name            | cuisine  | city      | rating |
|---------------|-----------------|----------|-----------|--------|
| 1             | Spice Garden    | Indian   | Mumbai    | 4.5    |
| 2             | Dragon Wok      | Chinese  | Delhi     | 4.2    |
| 3             | Pizza Palazzo   | Italian  | Mumbai    | 3.8    |
| 4             | Biryani Blues   | Indian   | Bangalore | 4.7    |
| 5             | Sushi Street    | Japanese | Delhi     | 4.1    |

---

### Table 2: `customers`

Registered QuickBite users and their membership plan.

| customer_id | full_name     | city      | membership |
|-------------|---------------|-----------|------------|
| 1           | Ankit Sharma  | Mumbai    | Prime      |
| 2           | Divya Nair    | Delhi     | Regular    |
| 3           | Rohan Mehta   | Mumbai    | Prime      |
| 4           | Preethi Rao   | Bangalore | Regular    |
| 5           | Sahil Gupta   | Delhi     | Prime      |

---

### Table 3: `orders`

Every order placed on the platform along with its delivery outcome.

| order_id | customer_id | restaurant_id | order_date | status    | delivery_time_mins |
|----------|-------------|---------------|------------|-----------|--------------------|
| 1001     | 1           | 1             | 2024-11-01 | Delivered | 32                 |
| 1002     | 2           | 2             | 2024-11-03 | Delivered | 45                 |
| 1003     | 3           | 3             | 2024-11-05 | Cancelled | NULL               |
| 1004     | 1           | 4             | 2024-11-10 | Delivered | 28                 |
| 1005     | 3           | 1             | 2024-11-12 | Delivered | 40                 |

---

### Table 4: `order_items`

Individual dishes within each order.

| item_id | order_id | dish_name       | quantity | price |
|---------|----------|-----------------|----------|-------|
| 1       | 1001     | Butter Chicken  | 2        | 320   |
| 2       | 1001     | Garlic Naan     | 3        | 60    |
| 3       | 1002     | Fried Rice      | 1        | 180   |
| 4       | 1004     | Chicken Biryani | 2        | 280   |
| 5       | 1005     | Paneer Tikka    | 1        | 250   |

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> The Mumbai City Ops Lead wants a list of high-performing restaurant partners in the city — specifically those with a rating above 4.0. These restaurants will be featured in the **"Top Picks in Mumbai"** section on the app homepage this week.

**Your Task:**
Retrieve the name, cuisine, and rating of all restaurants in Mumbai with a rating above 4.0, sorted by rating from highest to lowest.

---

### Question 2 — Intermediate

> **Business Context:**
> The VP of Partnerships wants to know which cuisines are the real revenue drivers on the platform. She also wants to see average delivery time per cuisine — slow delivery on a popular cuisine is a red flag that needs to be addressed before the pitch. Only delivered orders should be counted.

**Your Task:**
For each cuisine, calculate the total revenue and average delivery time, considering only delivered orders.

---

### Question 3 — Intermediate

> **Business Context:**
> The Head of Customer Experience is building a **QuickBite Loyalist Program** for customers who have ordered from more than one unique restaurant. These are the platform's most exploratory users — they're engaged, they trust the platform, and they're worth rewarding. The team needs their details to craft a personalised offer.

**Your Task:**
Identify customers who have placed orders from more than one unique restaurant. Show their name, city, membership plan, and the number of unique restaurants they have ordered from.

---

### Question 4 — Advanced

> **Business Context:**
> Each City Ops Lead is responsible for their city's restaurant revenue. Before the investor pitch, they want a **City Restaurant Leaderboard** — showing how each restaurant ranks within its city by revenue, and what share of the city's total platform revenue it accounts for. This will highlight which partners are carrying the city.

**Your Task:**
For each restaurant, show its name, city, total revenue, its rank within its city based on revenue (highest = Rank 1), and its revenue as a percentage of the city's total platform revenue, rounded to 2 decimal places. Order the result by city, then by rank.

---

*The pitch deck goes to the investors on Friday. The numbers start with you.*
