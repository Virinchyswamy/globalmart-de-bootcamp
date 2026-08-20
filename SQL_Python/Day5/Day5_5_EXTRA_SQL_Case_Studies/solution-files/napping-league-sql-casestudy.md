# Competitive Napping SQL Case Study — SnoreZone League Analytics

---

## Problem Statement

**SnoreZone** is the official league for Competitive Professional Napping — a sport judged on nap duration, snore decibel level, and unmistakable, uninterrupted commitment to sleep. It sounds like a joke. It has three teams, sponsorship deals, and a very serious commissioner. It is not a joke.

You're the league's newly hired Data Analyst. Your queries will decide:
- Who gets called up for the National Napping Squad
- Which team gets the trophy — and the bigger sponsorship cheque
- Who's a repeat competitor worth building a rivalry storyline around
- How each napper stacks up against their own teammates

Aditi, the League Commissioner, needs this before the Sunday broadcast. One sponsor — who insists on being called only "a concerned stakeholder," suspiciously named Robert — has already asked if the judging can be "adjusted." It cannot. Ignore Robert.

---

## Database Schema & Sample Data

### Table 1: `teams`

The three franchises currently duking it out for the pillow.

| team_id | team_name       | home_city | coach            |
|---------|-----------------|-----------|-------------------|
| 1       | Pillow Panthers | Hyderabad | Naman Prasad      |
| 2       | Dream Weavers   | Chennai   | Kriti Tiwari      |
| 3       | Snoozing Suns   | Bengaluru | Bhaskar Chauhan   |

---

### Table 2: `nappers`

The athletes. Please do not wake them for questions.

| napper_id | full_name         | team_id | years_experience |
|-----------|-------------------|---------|--------------------|
| 1         | Prem Kushwah      | 1       | 5                  |
| 2         | Tanushi           | 1       | 3                  |
| 3         | Udhav Vinaik      | 2       | 7                  |
| 4         | Harsh Kumar       | 2       | 2                  |
| 5         | Agnik Chakraborty | 3       | 4                  |

---

### Table 3: `matches`

Fixtures. Kickoff is whenever everyone falls asleep.

| match_id | team1_id | team2_id | match_date | venue           |
|----------|----------|----------|------------|-----------------|
| 1        | 1        | 2        | 2026-01-10 | Hyderabad Dome  |
| 2        | 1        | 3        | 2026-01-17 | Hyderabad Dome  |
| 3        | 2        | 3        | 2026-01-24 | Chennai Arena   |

---

### Table 4: `performances`

The scoreboard that matters — duration, decibels, and the judges' verdict.

| perf_id | match_id | napper_id | nap_duration_min | snore_decibels | judge_score |
|---------|----------|-----------|--------------------|------------------|--------------|
| 1       | 1        | 1         | 45                 | 62               | 8.5          |
| 2       | 1        | 3         | 52                 | 58               | 9.0          |
| 3       | 2        | 2         | 38                 | 70               | 7.0          |
| 4       | 2        | 5         | 60                 | 55               | 9.5          |
| 5       | 3        | 4         | 41                 | 65               | 7.5          |
| 6       | 3        | 5         | 48                 | 60               | 8.0          |

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> Aditi wants a highlight reel of elite performances for the Sunday broadcast.

**Your Task:**
Show the napper's name and judge score for every performance that scored above 8, highest score first.

---

### Question 2 — Intermediate

> **Business Context:**
> Sponsorship money follows results. Aditi wants a **Team Form Report** before the sponsors' dinner.

**Your Task:**
For each team, show total nap duration (in minutes) across all performances and the average judge score, rounded to 2 decimals.

---

### Question 3 — Intermediate

> **Business Context:**
> The broadcast team wants storylines. A napper who shows up more than once is a rivalry waiting to happen.

**Your Task:**
Show nappers with more than one competitive performance — their name, performance count, and total nap duration.

---

### Question 4 — Advanced

> **Business Context:**
> Each coach wants to know who's carrying the team, so they know who to protect from Robert's "motivational" pep talks.

**Your Task:**
For each napper, show their name, team, total nap duration, their rank within their team by total duration (highest = Rank 1), and their share of the team's total duration as a percentage rounded to 2 decimals.

---

*Somewhere, a pillow is being fluffed for the trophy ceremony. Make the query count.*
