# Banking SQL Case Study — NeoBank Analytics Challenge

---

## Problem Statement

**NeoBank** is a fast-growing digital bank that recently crossed 1 million customers. The leadership team is preparing for a **Board Review Meeting** and needs quick insights from their transactional data. They've hired you as a **Data Analyst** to dig into their database and answer critical business questions.

Your findings will directly influence decisions on:
- Which customers get invited to the new **Wealth Club**
- Where the bank's money is actually moving
- Who qualifies for a **Loyalty Reward** for holding multiple accounts
- How each city's top customers compare against each other

The stakes are high. The CFO, the Head of Risk, and the Regional Directors are all waiting on your queries.

---

## Database Schema & Sample Data

### Table 1: `customers`

Stores the personal profile of every bank customer.

| customer_id | full_name     | city      | age | segment |
|-------------|---------------|-----------|-----|---------|
| 1           | Arjun Sharma  | Mumbai    | 34  | Premium |
| 2           | Priya Mehta   | Delhi     | 27  | Regular |
| 3           | Rohit Verma   | Mumbai    | 45  | Premium |
| 4           | Sneha Iyer    | Bangalore | 31  | Student |
| 5           | Aditya Nair   | Delhi     | 52  | Premium |

---

### Table 2: `accounts`

Each customer can hold one or more accounts of different types.

| account_id | customer_id | account_type  | balance      | opened_date |
|------------|-------------|---------------|--------------|-------------|
| 101        | 1           | Savings       | 85,000.00    | 2021-03-15  |
| 102        | 1           | Fixed Deposit | 2,00,000.00  | 2022-06-01  |
| 103        | 2           | Savings       | 12,500.00    | 2023-01-10  |
| 104        | 3           | Current       | 4,50,000.00  | 2020-08-20  |
| 105        | 4           | Savings       | 8,000.00     | 2024-02-28  |
| 106        | 5           | Fixed Deposit | 7,50,000.00  | 2019-11-05  |

---

### Table 3: `transactions`

Records every money movement (credit or debit) against an account.

| transaction_id | account_id | txn_type | amount       | txn_date   | description        |
|----------------|------------|----------|--------------|------------|--------------------|
| 1001           | 101        | Credit   | 25,000.00    | 2024-11-01 | Salary Credit      |
| 1002           | 101        | Debit    | 5,000.00     | 2024-11-05 | Grocery Store      |
| 1003           | 103        | Debit    | 2,000.00     | 2024-11-10 | Online Shopping    |
| 1004           | 104        | Credit   | 1,50,000.00  | 2024-11-12 | Business Income    |
| 1005           | 104        | Debit    | 30,000.00    | 2024-11-15 | Vendor Payment     |
| 1006           | 102        | Credit   | 10,000.00    | 2024-11-20 | FD Interest Payout |

---

### Table 4: `loan_applications`

Captures loan requests submitted by customers.

| loan_id | customer_id | loan_type | amount_requested | status   | applied_date |
|---------|-------------|-----------|------------------|----------|--------------|
| 201     | 2           | Personal  | 50,000.00        | Approved | 2024-10-01   |
| 202     | 3           | Home      | 50,00,000.00     | Approved | 2024-09-15   |
| 203     | 4           | Personal  | 30,000.00        | Rejected | 2024-11-01   |
| 204     | 5           | Home      | 80,00,000.00     | Pending  | 2024-10-20   |
| 205     | 1           | Auto      | 7,00,000.00      | Approved | 2024-08-10   |

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> The Relationship Manager is planning an exclusive **Wealth Club Invitation Drive** targeting high-value customers in Mumbai. She needs a list of all **Premium segment** customers from **Mumbai** to personally call them this week.

**Your Task:**
Retrieve the name and age of all Premium segment customers who are based in Mumbai.

---

### Question 2 — Intermediate

> **Business Context:**
> The Finance team is preparing a **Cash Flow Report** for November 2024. They want to understand how much money came in (Credits) and went out (Debits) through each type of account. This will help them assess which account types are most active and where liquidity is concentrated.

**Your Task:**
For each account type, find out the total amount credited and the total amount debited.

---

### Question 3 — Intermediate

> **Business Context:**
> The Loyalty Team is rolling out a **Multi-Account Reward Program**. Customers who hold **more than one account** are eligible for a special cashback bonus. The team needs a list of these customers along with their **total combined balance** across all accounts — sorted from highest to lowest balance so they can prioritize the outreach.

**Your Task:**
Identify customers who hold more than one account. For each such customer, show their name, how many accounts they hold, and their total balance across all accounts — sorted from highest to lowest balance.

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

---

## Evaluation Rubric

| Question | Level        | Max Marks | Key Focus                                          |
|----------|--------------|-----------|----------------------------------------------------|
| Q1       | Beginner     | 10        | Correct WHERE conditions, no unnecessary columns   |
| Q2       | Intermediate | 25        | Correct JOIN, accurate CASE-based aggregation      |
| Q3       | Intermediate | 25        | Well-structured CTE, correct HAVING filter         |
| Q4       | Advanced     | 40        | Correct window functions, accurate percentages     |

---

*Good luck! Remember — in the real world, your SQL query could directly impact a business decision. Write it like it matters.*
