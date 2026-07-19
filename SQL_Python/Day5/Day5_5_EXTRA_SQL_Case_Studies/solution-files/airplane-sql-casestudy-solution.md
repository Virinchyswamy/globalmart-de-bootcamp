# Airplane SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> The Marketing team is launching a **"Fly Punctual with SkyRoute"** campaign highlighting the airline's on-time performance. They want to feature real flights departing from Mumbai that operated without any delays or cancellations — these will be showcased in the campaign creatives.

**Your Task:**
Retrieve the flight number, destination, departure time, and arrival time of all flights departing from Mumbai that have a status of On-Time.

**Solution:**

```sql
SELECT flight_no, destination, departure_time, arrival_time
FROM flights
WHERE origin = 'Mumbai'
  AND status = 'On-Time';
```

---

### Question 2 — Intermediate

> **Business Context:**
> The Revenue Manager is preparing the **Seat Class Revenue Breakdown** for the quarterly review. She needs to know how many bookings were made in each seat class and how much total fare each class generated — this directly informs the pricing and upgrade strategy for Q4.

**Your Task:**
For each seat class, find the total number of bookings and the total fare collected.

**Solution:**

```sql
SELECT
    seat_class,
    COUNT(booking_id) AS total_bookings,
    SUM(fare)         AS total_fare
FROM bookings
GROUP BY seat_class;
```

---

### Question 3 — Intermediate

> **Business Context:**
> The Loyalty Program Director is reviewing eligibility for **SkyRoute Elite Status** — a special tier reserved for passengers who have booked more than one flight. These frequent travellers will receive priority boarding, complimentary upgrades, and dedicated support during the holiday rush.

**Your Task:**
Identify passengers who have made more than one booking. For each such passenger, show their name, nationality, frequent flyer tier, and total number of bookings.

**Solution:**

```sql
WITH frequent_flyers AS (
    SELECT
        passenger_id,
        COUNT(booking_id) AS total_bookings
    FROM bookings
    GROUP BY passenger_id
    HAVING COUNT(booking_id) > 1
)
SELECT
    p.full_name,
    p.nationality,
    p.frequent_flyer_tier,
    ff.total_bookings
FROM frequent_flyers ff
JOIN passengers p ON ff.passenger_id = p.passenger_id
ORDER BY ff.total_bookings DESC;
```

---

### Question 4 — Advanced

> **Business Context:**
> The Revenue team wants a **Route Revenue Leaderboard** to identify which specific flights on each route are pulling the most fare revenue. For any given origin-destination pair, they want to see how each flight ranks and what percentage of the route's total revenue it contributes — this drives decisions on flight frequency and pricing per route.

**Your Task:**
For each flight, show its flight number, origin, destination, total fare collected, its rank within its route (same origin and destination) based on total fare (highest = Rank 1), and its fare as a percentage of the route's total revenue, rounded to 2 decimal places. Order the result by route, then by rank.

**Solution:**

```sql
WITH flight_revenue AS (
    SELECT
        f.flight_id,
        f.flight_no,
        f.origin,
        f.destination,
        SUM(b.fare) AS total_fare
    FROM flights f
    JOIN bookings b ON f.flight_id = b.flight_id
    GROUP BY f.flight_id, f.flight_no, f.origin, f.destination
)
SELECT
    flight_no,
    origin,
    destination,
    total_fare,
    RANK() OVER (PARTITION BY origin, destination ORDER BY total_fare DESC) AS route_rank,
    ROUND(
        total_fare * 100.0 / SUM(total_fare) OVER (PARTITION BY origin, destination),
        2
    ) AS pct_of_route_total
FROM flight_revenue
ORDER BY origin, destination, route_rank;
```
