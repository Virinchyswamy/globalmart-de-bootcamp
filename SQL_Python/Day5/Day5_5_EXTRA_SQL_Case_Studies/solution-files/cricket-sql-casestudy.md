# Cricket SQL Case Study — StrikeZone Analytics

---

## Problem Statement

**StrikeZone Analytics** is the official data partner for the **Premier Cricket League (PCL)** — a franchise-based T20 tournament featuring the best players from around the world. With the next **Player Auction** just two weeks away, team owners and their coaching staff are scrambling for data-backed insights to make smart buys and plug gaps in their squads.

The decisions on the table:
- Which players from rival teams are the most dangerous with the bat
- Which teams have dominated the scoreboard so far this season
- Which players have proven themselves across multiple matches
- Who the standout run-scorers are within each team's batting lineup

You are StrikeZone's **Cricket Data Analyst**. Four franchise owners and their head coaches are waiting on your queries. Every run, every wicket, every number matters when crores are on the line at the auction table.

---

## Database Schema & Sample Data

### Table 1: `teams`

The four franchises competing in the PCL this season.

| team_id | team_name          | city      | coach         |
|---------|--------------------|-----------|---------------|
| 1       | Mumbai Mavericks   | Mumbai    | Sanjay Patel  |
| 2       | Delhi Dynamos      | Delhi     | Arun Kapoor   |
| 3       | Bangalore Blazers  | Bangalore | Vijay Nair    |
| 4       | Chennai Champions  | Chennai   | Ravi Kumar    |

---

### Table 2: `players`

Player profiles across all four franchises.

| player_id | full_name      | team_id | role        | nationality  |
|-----------|----------------|---------|-------------|--------------|
| 1         | Aryan Singh    | 1       | Batsman     | Indian       |
| 2         | Jake Miller    | 1       | All-rounder | Australian   |
| 3         | Pradeep Rao    | 2       | Bowler      | Indian       |
| 4         | Carlos Gomez   | 2       | Batsman     | West Indian  |
| 5         | Rahul Verma    | 3       | Batsman     | Indian       |

---

### Table 3: `matches`

Match fixtures played this season along with the result.

| match_id | team1_id | team2_id | match_date | venue     | winner_team_id |
|----------|----------|----------|------------|-----------|----------------|
| 1        | 1        | 2        | 2024-04-05 | Mumbai    | 1              |
| 2        | 3        | 4        | 2024-04-07 | Bangalore | 3              |
| 3        | 1        | 3        | 2024-04-10 | Delhi     | 1              |
| 4        | 2        | 4        | 2024-04-12 | Chennai   | 2              |
| 5        | 1        | 4        | 2024-04-15 | Mumbai    | 4              |

---

### Table 4: `innings`

Individual player performance in each match — both batting and bowling stats.

| innings_id | match_id | player_id | runs_scored | balls_faced | wickets_taken | overs_bowled |
|------------|----------|-----------|-------------|-------------|---------------|--------------|
| 1          | 1        | 1         | 72          | 48          | 0             | 0            |
| 2          | 1        | 2         | 45          | 32          | 1             | 2            |
| 3          | 2        | 5         | 88          | 54          | 0             | 0            |
| 4          | 3        | 1         | 91          | 62          | 0             | 0            |
| 5          | 3        | 3         | 0           | 0           | 3             | 4            |

> Strike Rate = `(runs_scored / balls_faced) × 100`

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> The Chennai Champions coaching staff is planning their auction strategy around strengthening their batting lineup with Indian talent. Before shortlisting names, they want a full list of Indian batsmen currently playing in the PCL across all teams — potential targets they might bid for.

**Your Task:**
Retrieve the full name, team, and role of all Indian players whose role is Batsman.

---

### Question 2 — Intermediate

> **Business Context:**
> The tournament broadcaster wants to publish a **Team Power Rankings** segment before the next match day. They need each team's total runs scored across all matches this season, along with their overall strike rate — a measure of how aggressively each team bats.

**Your Task:**
For each team, find the total runs scored by all their players combined and the overall team strike rate across all matches. Round the strike rate to 2 decimal places.

---

### Question 3 — Intermediate

> **Business Context:**
> The auction analysts at StrikeZone define a **proven player** as someone who has featured in more than two matches this season. These are battle-tested performers, not one-match wonders. Franchise owners want this list with each player's total runs to assess their consistency.

**Your Task:**
Identify players who have featured in more than 2 matches. For each such player, show their name, team, number of matches played, and total runs scored — sorted by total runs in descending order.

---

### Question 4 — Advanced

> **Business Context:**
> Each franchise owner wants a **Batting Leaderboard** for their own team — who is their top scorer, who is carrying the team's run-scoring, and how much of the team's total runs does each player account for. This shapes their retention decisions at the auction.

**Your Task:**
For each player, show their name, team, total runs scored, their rank within their team based on runs (highest = Rank 1), and their runs as a percentage of their team's total runs, rounded to 2 decimal places. Order the result by team name, then by rank.

---

*The auction gavel drops in two weeks. Back your picks with data.*
