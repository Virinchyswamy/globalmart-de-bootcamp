# Office Chair Racing SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> Anuj wants proof that Engineering's "TurboGlide 3000" chairs were worth the budget line item.

**Your Task:**
Show the racer's name and lap time for every result from an Engineering department racer with a lap time under 20 seconds, fastest first.

**Solution:**

```sql
SELECT r.full_name, res.lap_time_sec
FROM results res
JOIN racers r      ON res.racer_id = r.racer_id
JOIN departments d ON r.dept_id = d.dept_id
WHERE d.dept_name = 'Engineering'
  AND res.lap_time_sec < 20
ORDER BY res.lap_time_sec ASC;
```

---

### Question 2 — Intermediate

> **Business Context:**
> Anuj needs a **Department Speed Report** for the next all-hands, mostly to justify why racing is "a team-building exercise."

**Your Task:**
For each department, show how many races were run by its racers and their average lap time, rounded to 2 decimals.

**Solution:**

```sql
SELECT
    d.dept_name,
    COUNT(res.result_id)        AS races_run,
    ROUND(AVG(res.lap_time_sec), 2) AS avg_lap_time
FROM results res
JOIN racers r      ON res.racer_id = r.racer_id
JOIN departments d ON r.dept_id = d.dept_id
GROUP BY d.dept_name;
```

---

### Question 3 — Intermediate

> **Business Context:**
> The league wants to know who's a repeat racer — those are the ones worth insuring separately.

**Your Task:**
Show racers who have competed in more than one race — their name, race count, and total lap time across those races.

**Solution:**

```sql
SELECT
    r.full_name,
    COUNT(res.result_id)   AS races_run,
    SUM(res.lap_time_sec)  AS total_lap_time
FROM results res
JOIN racers r ON res.racer_id = r.racer_id
GROUP BY r.racer_id, r.full_name
HAVING COUNT(res.result_id) > 1;
```

---

### Question 4 — Advanced

> **Business Context:**
> Anuj wants a **Speed Leaderboard** for the Inter-Office Championship team selection — fastest cumulative time per department wins the nomination.

**Your Task:**
For each racer, show their name, department, total lap time across all races, their rank within their department (lowest total time = Rank 1), and their share of the department's total lap time as a percentage rounded to 2 decimals.

**Solution:**

```sql
WITH racer_totals AS (
    SELECT
        r.racer_id,
        r.full_name,
        d.dept_name,
        SUM(res.lap_time_sec) AS total_lap_time
    FROM results res
    JOIN racers r      ON res.racer_id = r.racer_id
    JOIN departments d ON r.dept_id = d.dept_id
    GROUP BY r.racer_id, r.full_name, d.dept_name
)
SELECT
    full_name,
    dept_name,
    total_lap_time,
    RANK() OVER (PARTITION BY dept_name ORDER BY total_lap_time ASC) AS dept_rank,
    ROUND(
        total_lap_time * 100.0 / SUM(total_lap_time) OVER (PARTITION BY dept_name),
        2
    ) AS pct_of_dept_total
FROM racer_totals
ORDER BY dept_name, dept_rank;
```
