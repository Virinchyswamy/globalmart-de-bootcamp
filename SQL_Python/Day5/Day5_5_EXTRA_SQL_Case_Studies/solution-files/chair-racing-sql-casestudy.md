# Office Chair Racing SQL Case Study — SwivelSpeed League Analytics

---

## Problem Statement

**SwivelSpeed** began as a joke after hours: three departments, empty hallways, and office chairs with suspiciously good bearings. It is now an inter-department league with a real trophy, a real injury waiver, and — after Facilities found out — real lap-time tracking.

You've been pulled in as the Data Analyst. Your queries decide:
- Which department gets bragging rights (and the good parking spots)
- Who's fast enough to represent the company at the Inter-Office Championship
- Which racers keep showing up — worth watching, or worth worrying about
- Who's actually carrying their department versus coasting on one lucky lap

Anuj Khokhar, Head of Facilities, approved this "as a one-time thing" eleven weeks ago. A racer known only as Robert has crashed into the vending machine twice and is, somehow, still allowed to compete.

---

## Database Schema & Sample Data

### Table 1: `departments`

The three departments currently in a very unofficial rivalry.

| dept_id | dept_name   | floor_number | chair_budget |
|---------|-------------|--------------|---------------|
| 1       | Engineering | 3            | 50000         |
| 2       | Marketing   | 5            | 30000         |
| 3       | Finance     | 2            | 20000         |

---

### Table 2: `racers`

Competitors, by department and chair model.

| racer_id | full_name        | dept_id | chair_model     |
|----------|-------------------|---------|-------------------|
| 1        | Kabirkrishnan A   | 1       | TurboGlide 3000   |
| 2        | Raghul D          | 1       | TurboGlide 3000   |
| 3        | Swarna Choudhury  | 2       | ComfyZoom X       |
| 4        | Bhaskar Chauhan   | 3       | BudgetRoller      |
| 5        | Naman Prasad      | 2       | ComfyZoom X       |

---

### Table 3: `races`

Official tracks. All routes were "quality-checked" after hours.

| race_id | track_name       | race_date  | track_length_m |
|---------|------------------|------------|------------------|
| 1       | Hallway A Sprint | 2026-02-01 | 40               |
| 2       | Cafeteria Loop   | 2026-02-08 | 55               |
| 3       | Parking Lot GP   | 2026-02-15 | 80               |

---

### Table 4: `results`

Lap times, finishing position, and the occasional incident report.

| result_id | race_id | racer_id | lap_time_sec | position | incident               |
|-----------|---------|----------|---------------|----------|--------------------------|
| 1         | 1       | 1        | 12.5          | 1        | None                     |
| 2         | 1       | 2        | 14.0          | 2        | None                     |
| 3         | 2       | 1        | 18.3          | 1        | None                     |
| 4         | 2       | 3        | 19.5          | 2        | None                     |
| 5         | 3       | 2        | 25.0          | 1        | Minor spill collision    |
| 6         | 3       | 5        | 26.5          | 2        | None                     |
| 7         | 3       | 4        | 27.8          | 3        | None                     |

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> Anuj wants proof that Engineering's "TurboGlide 3000" chairs were worth the budget line item.

**Your Task:**
Show the racer's name and lap time for every result from an Engineering department racer with a lap time under 20 seconds, fastest first.

---

### Question 2 — Intermediate

> **Business Context:**
> Anuj needs a **Department Speed Report** for the next all-hands, mostly to justify why racing is "a team-building exercise."

**Your Task:**
For each department, show how many races were run by its racers and their average lap time, rounded to 2 decimals.

---

### Question 3 — Intermediate

> **Business Context:**
> The league wants to know who's a repeat racer — those are the ones worth insuring separately.

**Your Task:**
Show racers who have competed in more than one race — their name, race count, and total lap time across those races.

---

### Question 4 — Advanced

> **Business Context:**
> Anuj wants a **Speed Leaderboard** for the Inter-Office Championship team selection — fastest cumulative time per department wins the nomination.

**Your Task:**
For each racer, show their name, department, total lap time across all races, their rank within their department (lowest total time = Rank 1), and their share of the department's total lap time as a percentage rounded to 2 decimals.

---

*Somewhere, a chair wheel is squeaking ominously. Make the query count.*
