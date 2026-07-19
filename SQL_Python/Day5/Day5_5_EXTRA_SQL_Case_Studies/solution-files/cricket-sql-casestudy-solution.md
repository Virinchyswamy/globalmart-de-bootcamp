# Cricket SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> The Chennai Champions coaching staff is planning their auction strategy around strengthening their batting lineup with Indian talent. Before shortlisting names, they want a full list of Indian batsmen currently playing in the PCL across all teams — potential targets they might bid for.

**Your Task:**
Retrieve the full name, team, and role of all Indian players whose role is Batsman.

**Solution:**

```sql
SELECT p.full_name, t.team_name, p.role
FROM players p
JOIN teams t ON p.team_id = t.team_id
WHERE p.nationality = 'Indian'
  AND p.role = 'Batsman';
```

---

### Question 2 — Intermediate

> **Business Context:**
> The tournament broadcaster wants to publish a **Team Power Rankings** segment before the next match day. They need each team's total runs scored across all matches this season, along with their overall strike rate — a measure of how aggressively each team bats.

**Your Task:**
For each team, find the total runs scored by all their players combined and the overall team strike rate across all matches. Round the strike rate to 2 decimal places.

**Solution:**

```sql
SELECT
    t.team_name,
    SUM(i.runs_scored)                                                        AS total_runs,
    ROUND(SUM(i.runs_scored) * 100.0 / NULLIF(SUM(i.balls_faced), 0), 2)    AS team_strike_rate
FROM innings i
JOIN players p ON i.player_id = p.player_id
JOIN teams t   ON p.team_id = t.team_id
GROUP BY t.team_name;
```

---

### Question 3 — Intermediate

> **Business Context:**
> The auction analysts at StrikeZone define a **proven player** as someone who has featured in more than two matches this season. These are battle-tested performers, not one-match wonders. Franchise owners want this list with each player's total runs to assess their consistency.

**Your Task:**
Identify players who have featured in more than 2 matches. For each such player, show their name, team, number of matches played, and total runs scored — sorted by total runs in descending order.

**Solution:**

```sql
WITH proven_players AS (
    SELECT
        player_id,
        COUNT(DISTINCT match_id) AS matches_played,
        SUM(runs_scored)         AS total_runs
    FROM innings
    GROUP BY player_id
    HAVING COUNT(DISTINCT match_id) > 2
)
SELECT
    p.full_name,
    t.team_name,
    pp.matches_played,
    pp.total_runs
FROM proven_players pp
JOIN players p ON pp.player_id = p.player_id
JOIN teams t   ON p.team_id = t.team_id
ORDER BY pp.total_runs DESC;
```

---

### Question 4 — Advanced

> **Business Context:**
> Each franchise owner wants a **Batting Leaderboard** for their own team — who is their top scorer, who is carrying the team's run-scoring, and how much of the team's total runs does each player account for. This shapes their retention decisions at the auction.

**Your Task:**
For each player, show their name, team, total runs scored, their rank within their team based on runs (highest = Rank 1), and their runs as a percentage of their team's total runs, rounded to 2 decimal places. Order the result by team name, then by rank.

**Solution:**

```sql
WITH player_runs AS (
    SELECT
        p.player_id,
        p.full_name,
        p.team_id,
        SUM(i.runs_scored) AS total_runs
    FROM players p
    JOIN innings i ON p.player_id = i.player_id
    GROUP BY p.player_id, p.full_name, p.team_id
)
SELECT
    pr.full_name,
    t.team_name,
    pr.total_runs,
    RANK() OVER (PARTITION BY pr.team_id ORDER BY pr.total_runs DESC) AS team_rank,
    ROUND(
        pr.total_runs * 100.0 / SUM(pr.total_runs) OVER (PARTITION BY pr.team_id),
        2
    ) AS pct_of_team_runs
FROM player_runs pr
JOIN teams t ON pr.team_id = t.team_id
ORDER BY t.team_name, team_rank;
```
