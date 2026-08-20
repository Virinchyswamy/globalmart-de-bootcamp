# Pigeon Courier SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> Pratyush is drafting the "Homing Pigeons Do It Better" marketing deck and needs proof.

**Your Task:**
Show the pigeon name and distance for every delivery flown by a Homing Pigeon covering more than 20 km, longest distance first.

**Solution:**

```sql
SELECT p.name, d.distance_km
FROM deliveries d
JOIN pigeons p ON d.pigeon_id = p.pigeon_id
WHERE p.breed = 'Homing Pigeon'
  AND d.distance_km > 20
ORDER BY d.distance_km DESC;
```

---

### Question 2 — Intermediate

> **Business Context:**
> Raghupatruni Thej wants a **Breed Performance Report** before deciding which breed gets the billboard.

**Your Task:**
For each breed, show total distance flown across all deliveries and the average client star rating, rounded to 2 decimals.

**Solution:**

```sql
SELECT
    p.breed,
    SUM(d.distance_km)      AS total_distance,
    ROUND(AVG(r.stars), 2)  AS avg_rating
FROM deliveries d
JOIN pigeons p ON d.pigeon_id = p.pigeon_id
JOIN ratings r ON r.delivery_id = d.delivery_id
GROUP BY p.breed;
```

---

### Question 3 — Intermediate

> **Business Context:**
> WingIt is launching a **"Frequent Flyer" bonus** for pigeons who've earned their wings on more than one delivery.

**Your Task:**
Show pigeons with more than one delivery — their name, delivery count, and total distance flown.

**Solution:**

```sql
SELECT
    p.name,
    COUNT(d.delivery_id) AS delivery_count,
    SUM(d.distance_km)   AS total_distance
FROM deliveries d
JOIN pigeons p ON d.pigeon_id = p.pigeon_id
GROUP BY p.pigeon_id, p.name
HAVING COUNT(d.delivery_id) > 1;
```

---

### Question 4 — Advanced

> **Business Context:**
> The board wants a **Wingspan Leaderboard** — which pigeons are carrying their breed, and which are coasting on reputation.

**Your Task:**
For each pigeon, show name, breed, total distance flown, its rank within its breed by total distance (highest = Rank 1), and its share of the breed's total distance as a percentage rounded to 2 decimals.

**Solution:**

```sql
WITH pigeon_totals AS (
    SELECT
        p.pigeon_id,
        p.name,
        p.breed,
        SUM(d.distance_km) AS total_distance
    FROM deliveries d
    JOIN pigeons p ON d.pigeon_id = p.pigeon_id
    GROUP BY p.pigeon_id, p.name, p.breed
)
SELECT
    name,
    breed,
    total_distance,
    RANK() OVER (PARTITION BY breed ORDER BY total_distance DESC) AS breed_rank,
    ROUND(
        total_distance * 100.0 / SUM(total_distance) OVER (PARTITION BY breed),
        2
    ) AS pct_of_breed_total
FROM pigeon_totals
ORDER BY breed, breed_rank;
```
