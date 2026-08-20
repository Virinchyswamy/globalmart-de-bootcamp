# Competitive Cup Stacking SQL Case Study — StackAttack League Analytics

---

## Problem Statement

**StackAttack** is the national league for Competitive Sport Stacking — stacking and unstacking plastic cups into pyramids, against the clock, with the intensity most people reserve for actual sports. Sponsors are real. The rivalries are realer.

You've joined as the league's Data Analyst. Your queries decide:
- Which team takes the National Pyramid trophy
- Which stacker gets the sponsorship spotlight
- Who's a serial competitor worth building a highlight reel around
- Who's actually the fastest hands on their own team

Prem Kushwah, Federation President, wants this on his desk before the Nationals press conference. Raghul D has already texted the group chat: "just checked, I'm still faster than Kabirkrishnan, right?" Let the data answer that, not the group chat.

---

## Database Schema & Sample Data

### Table 1: `teams`

The three franchises stacking their way to glory.

| team_id | team_name       | home_city | coach            |
|---------|-----------------|-----------|-------------------|
| 1       | Cup Crushers    | Hyderabad | Bhaskar Chauhan   |
| 2       | Stack Ninjas    | Chennai   | Naman Prasad      |
| 3       | Speed Pyramids  | Bengaluru | Kriti Tiwari      |

---

### Table 2: `stackers`

The athletes and their years of experience stacking cups under pressure.

| stacker_id | full_name        | team_id | years_competing |
|------------|-------------------|---------|--------------------|
| 1          | Raghul D          | 1       | 6                  |
| 2          | Kabirkrishnan A   | 1       | 2                  |
| 3          | Udhav Vinaik      | 2       | 8                  |
| 4          | Harsh Kumar       | 2       | 3                  |
| 5          | Aditi             | 3       | 5                  |

---

### Table 3: `tournaments`

This season's official events.

| tournament_id | event_name              | city      | event_date |
|----------------|--------------------------|-----------|------------|
| 1              | Deccan Cup Open          | Hyderabad | 2026-03-01 |
| 2              | Southern Speed Stack     | Chennai   | 2026-03-08 |
| 3              | National Pyramid Finals  | Bengaluru | 2026-03-15 |

---

### Table 4: `results`

Stack times (seconds — lower is faster) and finishing placement.

| result_id | tournament_id | stacker_id | stack_time_sec | placement |
|-----------|----------------|------------|------------------|------------|
| 1         | 1              | 1          | 5.2              | 1          |
| 2         | 1              | 3          | 5.8              | 2          |
| 3         | 2              | 1          | 4.9              | 1          |
| 4         | 2              | 4          | 6.1              | 2          |
| 5         | 3              | 2          | 5.5              | 2          |
| 6         | 3              | 5          | 5.0              | 1          |

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> Prem wants the "Under 5.5 Seconds Club" list for the Nationals promo poster.

**Your Task:**
Show the stacker's name and stack time for every result under 5.5 seconds, fastest time first.

---

### Question 2 — Intermediate

> **Business Context:**
> Prem needs a **Team Form Report** ahead of Nationals sponsorship renewals.

**Your Task:**
For each team, show the number of events its stackers competed in and their average stack time, rounded to 2 decimals.

---

### Question 3 — Intermediate

> **Business Context:**
> The broadcast wants a "most consistent competitor" segment for the Nationals stream.

**Your Task:**
Show stackers who have competed in more than one tournament — their name, tournament count, and total stack time across those events.

---

### Question 4 — Advanced

> **Business Context:**
> Raghul's group-chat question deserves a real answer. Prem wants a **Speed Leaderboard** settled once and for all.

**Your Task:**
For each stacker, show their name, team, total stack time across all events, their rank within their team (lowest total time = Rank 1), and their share of the team's total stack time as a percentage rounded to 2 decimals.

---

*The cups are stacked. The pressure is on. Make the query count.*
