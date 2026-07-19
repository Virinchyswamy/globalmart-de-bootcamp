# Banking SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> The Relationship Manager is planning an exclusive **Wealth Club Invitation Drive** targeting high-value customers in Mumbai. She needs a list of all **Premium segment** customers from **Mumbai** to personally call them this week.

**Your Task:**
Retrieve the name and age of all Premium segment customers who are based in Mumbai.

**Solution:**

```sql
SELECT full_name, age
FROM customers
WHERE segment = 'Premium'
  AND city = 'Mumbai';
```

---

### Question 2 — Intermediate

> **Business Context:**
> The Finance team is preparing a **Cash Flow Report** for November 2024. They want to understand how much money came in (Credits) and went out (Debits) through each type of account. This will help them assess which account types are most active and where liquidity is concentrated.

**Your Task:**
For each account type, find out the total amount credited and the total amount debited.

**Solution:**

```sql
SELECT
    a.account_type,
    SUM(CASE WHEN t.txn_type = 'Credit' THEN t.amount ELSE 0 END) AS total_credited,
    SUM(CASE WHEN t.txn_type = 'Debit'  THEN t.amount ELSE 0 END) AS total_debited
FROM accounts a
JOIN transactions t ON a.account_id = t.account_id
GROUP BY a.account_type;
```

---

### Question 3 — Intermediate

> **Business Context:**
> The Loyalty Team is rolling out a **Multi-Account Reward Program**. Customers who hold **more than one account** are eligible for a special cashback bonus. The team needs a list of these customers along with their **total combined balance** across all accounts — sorted from highest to lowest balance so they can prioritize the outreach.

**Your Task:**
Identify customers who hold more than one account. For each such customer, show their name, how many accounts they hold, and their total balance across all accounts — sorted from highest to lowest balance.

**Solution:**

```sql
WITH multi_account AS (
    SELECT
        customer_id,
        COUNT(account_id)  AS number_of_accounts,
        SUM(balance)       AS total_balance
    FROM accounts
    GROUP BY customer_id
    HAVING COUNT(account_id) > 1
)
SELECT
    c.full_name,
    m.number_of_accounts,
    m.total_balance
FROM multi_account m
JOIN customers c ON m.customer_id = c.customer_id
ORDER BY m.total_balance DESC;
```

---

### Question 4 — Advanced

> **Business Context:**
> The three Regional Directors — one each for Mumbai, Delhi, and Bangalore — are meeting next Monday. Each director wants to know:
> 1. How their city's customers **rank** by total account balance (who's the wealthiest customer in their region?)
> 2. What **percentage** of the city's total deposits each customer represents (how dominant is one customer vs. others?)
>
> They need a single unified report covering all cities.

**Your Task:**
For each customer, show their name, city, and total balance across all their accounts. Within each city, rank customers by their total balance — the wealthiest customer gets Rank 1. Also calculate what percentage of their city's total deposits each customer holds, rounded to 2 decimal places. Order the result by city, then by rank.

**Solution:**

```sql
WITH customer_balance AS (
    SELECT
        c.customer_id,
        c.full_name,
        c.city,
        SUM(a.balance) AS total_balance
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    GROUP BY c.customer_id, c.full_name, c.city
)
SELECT
    full_name,
    city,
    total_balance,
    RANK() OVER (PARTITION BY city ORDER BY total_balance DESC) AS city_rank,
    ROUND(
        total_balance * 100.0 / SUM(total_balance) OVER (PARTITION BY city),
        2
    ) AS pct_of_city_total
FROM customer_balance
ORDER BY city, city_rank;
```
