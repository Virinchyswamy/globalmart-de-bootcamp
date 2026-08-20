# Competitive Napping SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> Aditi wants a highlight reel of elite performances for the Sunday broadcast.

**Your Task:**
Show the napper's name and judge score for every performance that scored above 8, highest score first.

**Solution:**

```sql
SELECT n.full_name, p.judge_score
FROM performances p
JOIN nappers n ON p.napper_id = n.napper_id
WHERE p.judge_score > 8
ORDER BY p.judge_score DESC;
```

---

### Question 2 — Intermediate

> **Business Context:**
> Sponsorship money follows results. Aditi wants a **Team Form Report** before the sponsors' dinner.

**Your Task:**
For each team, show total nap duration (in minutes) across all performances and the average judge score, rounded to 2 decimals.

**Solution:**

```sql
SELECT
    t.team_name,
    SUM(p.nap_duration_min)  AS total_duration,
    ROUND(AVG(p.judge_score), 2) AS avg_score
FROM performances p
JOIN nappers n ON p.napper_id = n.napper_id
JOIN teams t   ON n.team_id = t.team_id
GROUP BY t.team_name;
```

---

### Question 3 — Intermediate

> **Business Context:**
> The broadcast team wants storylines. A napper who shows up more than once is a rivalry waiting to happen.

**Your Task:**
Show nappers with more than one competitive performance — their name, performance count, and total nap duration.

**Solution:**

```sql
SELECT
    n.full_name,
    COUNT(p.perf_id)          AS performance_count,
    SUM(p.nap_duration_min)   AS total_duration
FROM performances p
JOIN nappers n ON p.napper_id = n.napper_id
GROUP BY n.napper_id, n.full_name
HAVING COUNT(p.perf_id) > 1;
```

---

### Question 4 — Advanced

> **Business Context:**
> Each coach wants to know who's carrying the team, so they know who to protect from Robert's "motivational" pep talks.

**Your Task:**
For each napper, show their name, team, total nap duration, their rank within their team by total duration (highest = Rank 1), and their share of the team's total duration as a percentage rounded to 2 decimals.

**Solution:**

```sql
WITH napper_totals AS (
    SELECT
        n.napper_id,
        n.full_name,
        t.team_name,
        SUM(p.nap_duration_min) AS total_duration
    FROM performances p
    JOIN nappers n ON p.napper_id = n.napper_id
    JOIN teams t   ON n.team_id = t.team_id
    GROUP BY n.napper_id, n.full_name, t.team_name
)
SELECT
    full_name,
    team_name,
    total_duration,
    RANK() OVER (PARTITION BY team_name ORDER BY total_duration DESC) AS team_rank,
    ROUND(
        total_duration * 100.0 / SUM(total_duration) OVER (PARTITION BY team_name),
        2
    ) AS pct_of_team_total
FROM napper_totals
ORDER BY team_name, team_rank;
```
