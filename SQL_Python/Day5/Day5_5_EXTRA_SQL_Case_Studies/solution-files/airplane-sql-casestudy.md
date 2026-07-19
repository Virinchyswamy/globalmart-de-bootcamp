# Airplane SQL Case Study — SkyRoute Airlines Analytics

---

## Problem Statement

**SkyRoute Airlines** operates domestic flights across India's major cities and is gearing up for the **winter holiday travel rush** — the busiest and most profitable quarter of the year. Before ramping up operations, the leadership team needs a clear picture of how the airline performed last quarter: which routes were packed, which flights were letting passengers down, and who SkyRoute's most valuable frequent flyers are.

The findings will drive decisions on:
- Which on-time flights to promote as reliability benchmarks in their marketing campaign
- How revenue is distributed across seat classes
- Which passengers deserve priority perks in the **SkyRoute Rewards** loyalty program
- Which flight routes are generating the most revenue

You are SkyRoute's **Aviation Data Analyst**. The Head of Operations, the Revenue Manager, and the Loyalty Program Director are all waiting on your queries before the Q4 planning meeting.

---

## Database Schema & Sample Data

### Table 1: `flights`

All domestic flights operated by SkyRoute this quarter.

| flight_id | flight_no | origin    | destination | departure_time | arrival_time | status    |
|-----------|-----------|-----------|-------------|----------------|--------------|-----------|
| 1         | SK-101    | Mumbai    | Delhi       | 06:00          | 08:10        | On-Time   |
| 2         | SK-202    | Delhi     | Bangalore   | 10:30          | 13:00        | Delayed   |
| 3         | SK-303    | Mumbai    | Bangalore   | 14:00          | 16:15        | On-Time   |
| 4         | SK-404    | Bangalore | Chennai     | 08:45          | 09:50        | Cancelled |
| 5         | SK-505    | Mumbai    | Delhi       | 19:00          | 21:05        | On-Time   |

---

### Table 2: `aircraft`

Aircraft in SkyRoute's fleet.

| aircraft_id | model        | total_seats | airline       |
|-------------|--------------|-------------|---------------|
| 1           | Boeing 737   | 180         | SkyRoute      |
| 2           | Airbus A320  | 165         | SkyRoute      |
| 3           | Boeing 777   | 350         | SkyRoute      |
| 4           | ATR 72       | 70          | SkyRoute      |

---

### Table 3: `passengers`

Registered SkyRoute passengers and their frequent flyer tier.

| passenger_id | full_name      | nationality | frequent_flyer_tier |
|--------------|----------------|-------------|---------------------|
| 1            | Meera Joshi    | Indian      | Gold                |
| 2            | David Chen     | Chinese     | Silver              |
| 3            | Aisha Patel    | Indian      | Bronze              |
| 4            | Thomas Wright  | British     | Gold                |
| 5            | Neha Saxena    | Indian      | Silver              |

---

### Table 4: `bookings`

Ticket bookings made by passengers across flights.

| booking_id | passenger_id | flight_id | seat_class | fare  | booking_date |
|------------|--------------|-----------|------------|-------|--------------|
| 1          | 1            | 1         | Business   | 8500  | 2024-10-20   |
| 2          | 2            | 2         | Economy    | 3200  | 2024-10-21   |
| 3          | 3            | 1         | Economy    | 4100  | 2024-10-22   |
| 4          | 1            | 3         | First      | 15000 | 2024-10-23   |
| 5          | 4            | 5         | Business   | 7800  | 2024-10-24   |

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> The Marketing team is launching a **"Fly Punctual with SkyRoute"** campaign highlighting the airline's on-time performance. They want to feature real flights departing from Mumbai that operated without any delays or cancellations — these will be showcased in the campaign creatives.

**Your Task:**
Retrieve the flight number, destination, departure time, and arrival time of all flights departing from Mumbai that have a status of On-Time.

---

### Question 2 — Intermediate

> **Business Context:**
> The Revenue Manager is preparing the **Seat Class Revenue Breakdown** for the quarterly review. She needs to know how many bookings were made in each seat class and how much total fare each class generated — this directly informs the pricing and upgrade strategy for Q4.

**Your Task:**
For each seat class, find the total number of bookings and the total fare collected.

---

### Question 3 — Intermediate

> **Business Context:**
> The Loyalty Program Director is reviewing eligibility for **SkyRoute Elite Status** — a special tier reserved for passengers who have booked more than one flight. These frequent travellers will receive priority boarding, complimentary upgrades, and dedicated support during the holiday rush.

**Your Task:**
Identify passengers who have made more than one booking. For each such passenger, show their name, nationality, frequent flyer tier, and total number of bookings.

---

### Question 4 — Advanced

> **Business Context:**
> The Revenue team wants a **Route Revenue Leaderboard** to identify which specific flights on each route are pulling the most fare revenue. For any given origin-destination pair, they want to see how each flight ranks and what percentage of the route's total revenue it contributes — this drives decisions on flight frequency and pricing per route.

**Your Task:**
For each flight, show its flight number, origin, destination, total fare collected, its rank within its route (same origin and destination) based on total fare (highest = Rank 1), and its fare as a percentage of the route's total revenue, rounded to 2 decimal places. Order the result by route, then by rank.

---

*The holiday season waits for no one. Get the data right before the rush hits.*
