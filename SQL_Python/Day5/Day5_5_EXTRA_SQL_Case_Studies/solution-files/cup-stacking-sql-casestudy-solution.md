# Competitive Cup Stacking SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> Prem wants the "Under 5.5 Seconds Club" list for the Nationals promo poster.

**Your Task:**
Show the stacker's name and stack time for every result under 5.5 seconds, fastest time first.

**Solution:**

```sql
SELECT s.full_name, r.stack_time_sec
FROM results r
JOIN stackers s ON r.stacker_id = s.stacker_id
WHERE r.stack_time_sec < 5.5
ORDER BY r.stack_time_sec ASC;
```

---

### Question 2 — Intermediate

> **Business Context:**
> Prem needs a **Team Form Report** ahead of Nationals sponsorship renewals.

**Your Task:**
For each team, show the number of events its stackers competed in and their average stack time, rounded to 2 decimals.

**Solution:**

```sql
SELECT
    t.team_name,
    COUNT(r.result_id)          AS events_competed,
    ROUND(AVG(r.stack_time_sec), 2) AS avg_stack_time
FROM results r
JOIN stackers s ON r.stacker_id = s.stacker_id
JOIN teams t     ON s.team_id = t.team_id
GROUP BY t.team_name;
```

---

### Question 3 — Intermediate

> **Business Context:**
> The broadcast wants a "most consistent competitor" segment for the Nationals stream.

**Your Task:**
Show stackers who have competed in more than one tournament — their name, tournament count, and total stack time across those events.

**Solution:**

```sql
SELECT
    s.full_name,
    COUNT(r.result_id)   AS tournaments_played,
    SUM(r.stack_time_sec) AS total_time
FROM results r
JOIN stackers s ON r.stacker_id = s.stacker_id
GROUP BY s.stacker_id, s.full_name
HAVING COUNT(r.result_id) > 1;
```

---

### Question 4 — Advanced

> **Business Context:**
> Raghul's group-chat question deserves a real answer. Prem wants a **Speed Leaderboard** settled once and for all.

**Your Task:**
For each stacker, show their name, team, total stack time across all events, their rank within their team (lowest total time = Rank 1), and their share of the team's total stack time as a percentage rounded to 2 decimals.

**Solution:**

```sql
WITH stacker_totals AS (
    SELECT
        s.stacker_id,
        s.full_name,
        t.team_name,
        SUM(r.stack_time_sec) AS total_time
    FROM results r
    JOIN stackers s ON r.stacker_id = s.stacker_id
    JOIN teams t     ON s.team_id = t.team_id
    GROUP BY s.stacker_id, s.full_name, t.team_name
)
SELECT
    full_name,
    team_name,
    total_time,
    RANK() OVER (PARTITION BY team_name ORDER BY total_time ASC) AS team_rank,
    ROUND(
        total_time * 100.0 / SUM(total_time) OVER (PARTITION BY team_name),
        2
    ) AS pct_of_team_total
FROM stacker_totals
ORDER BY team_name, team_rank;
```
