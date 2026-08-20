# Pigeon Courier SQL Case Study — WingIt Express Delivery Analytics

---

## Problem Statement

**WingIt Express** is South Asia's fastest-growing pigeon courier startup — "Because drones need Wi-Fi, and our guys just need breadcrumbs." After a viral video of a pigeon named Turbo outrunning a delivery scooter, funding tripled overnight, and now the board wants numbers, not vibes.

You've been hired as the Data Analyst. Your queries decide:
- Which pigeons get promoted to the "Elite Wingspan" tier
- Which breed the marketing team should feature on the next billboard
- Which birds are quietly costing the company money in beak-related incidents
- How each pigeon stacks up against its own breed on distance flown

Pratyush Tiwari (your desk-mate and unofficial pigeon whisperer) has already named three of the birds after cricketers. Raghupatruni Thej, Head of Pigeon Operations, needs your first report before the 3pm "Feather Standup."

---

## Database Schema & Sample Data

### Table 1: `pigeons`

The active courier fleet. Yes, "fleet" is the correct term for a group of working pigeons here.

| pigeon_id | name    | breed         | base_city | top_speed_kmph |
|-----------|---------|---------------|-----------|-----------------|
| 1         | Turbo   | Homing Pigeon | Hyderabad | 92              |
| 2         | Waddles | Fantail       | Chennai   | 68              |
| 3         | Blaze   | Homing Pigeon | Bengaluru | 95              |
| 4         | Nibbles | Tumbler       | Hyderabad | 74              |
| 5         | Cyclone | Homing Pigeon | Mumbai    | 88              |

---

### Table 2: `clients`

Humans who trust birds with their parcels.

| client_id | full_name         | city      | membership_tier |
|-----------|-------------------|-----------|-------------------|
| 1         | Kriti Tiwari      | Hyderabad | Gold              |
| 2         | Naman Prasad      | Chennai   | Silver            |
| 3         | Swarna Choudhury  | Bengaluru | Gold              |
| 4         | Bhaskar Chauhan   | Hyderabad | Silver            |
| 5         | Agnik Chakraborty | Mumbai    | Gold              |

---

### Table 3: `deliveries`

Every completed (or Turbo-delayed) flight.

| delivery_id | pigeon_id | client_id | distance_km | delivery_status |
|-------------|-----------|-----------|--------------|-------------------|
| 101         | 1         | 1         | 45           | Delivered         |
| 102         | 2         | 2         | 12           | Delivered         |
| 103         | 3         | 3         | 60           | Delivered         |
| 104         | 1         | 4         | 30           | Delayed           |
| 105         | 5         | 5         | 25           | Delivered         |
| 106         | 4         | 1         | 8            | Delivered         |
| 107         | 3         | 2         | 15           | Delivered         |

---

### Table 4: `ratings`

Client feedback per flight. Yes, pigeons get star ratings now.

| rating_id | delivery_id | stars |
|-----------|-------------|-------|
| 1         | 101         | 5     |
| 2         | 102         | 4     |
| 3         | 103         | 5     |
| 4         | 104         | 2     |
| 5         | 105         | 5     |
| 6         | 106         | 4     |
| 7         | 107         | 5     |

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> Pratyush is drafting the "Homing Pigeons Do It Better" marketing deck and needs proof.

**Your Task:**
Show the pigeon name and distance for every delivery flown by a Homing Pigeon covering more than 20 km, longest distance first.

---

### Question 2 — Intermediate

> **Business Context:**
> Raghupatruni Thej wants a **Breed Performance Report** before deciding which breed gets the billboard.

**Your Task:**
For each breed, show total distance flown across all deliveries and the average client star rating, rounded to 2 decimals.

---

### Question 3 — Intermediate

> **Business Context:**
> WingIt is launching a **"Frequent Flyer" bonus** for pigeons who've earned their wings on more than one delivery.

**Your Task:**
Show pigeons with more than one delivery — their name, delivery count, and total distance flown.

---

### Question 4 — Advanced

> **Business Context:**
> The board wants a **Wingspan Leaderboard** — which pigeons are carrying their breed, and which are coasting on reputation.

**Your Task:**
For each pigeon, show name, breed, total distance flown, its rank within its breed by total distance (highest = Rank 1), and its share of the breed's total distance as a percentage rounded to 2 decimals.

---

*Turbo is watching. Make the query count.*
