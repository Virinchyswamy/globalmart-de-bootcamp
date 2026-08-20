# Haunted Airbnb SQL Case Study — SpookyStay Booking Analytics

---

## Problem Statement

**SpookyStay** is the booking platform for guests who specifically want their vacation rental to be haunted — verified ghosts, rattling doors, the works. Business is, unfortunately for the ghosts, booming.

You're the new Data Analyst. Your queries decide:
- Which properties get promoted on the homepage this Halloween
- Which haunting level actually drives the most revenue
- Which guests keep coming back for more (unclear if for the ghosts or the amenities)
- Which property is really carrying its haunting-level bracket

Ananya Seth, Head of Guest Experience, needs this before the "Are We Legally a Hotel or a Paranormal Society" board meeting. One resident ghost, who signs his complaint emails only as "Robert (Attic, Unit 1)," insists his reviews are being "suppressed." They are not. He has a 2-star review and he earned it.

---

## Database Schema & Sample Data

### Table 1: `properties`

The listings. Haunting level is on a 1–5 scale, self-reported by the ghosts.

| property_id | property_name           | city    | haunting_level | nightly_rate |
|-------------|--------------------------|---------|------------------|---------------|
| 1           | The Weeping Willow Manor | Ooty    | 5                | 4500          |
| 2           | Crimson Attic B&B        | Shimla  | 3                | 2800          |
| 3           | Whispering Pines Cabin   | Manali  | 4                | 3200          |
| 4           | The Grinning Staircase   | Jaipur  | 2                | 2000          |
| 5           | Fogbound Lighthouse      | Goa     | 5                | 5000          |

---

### Table 2: `guests`

Brave (or curious) travelers.

| guest_id | full_name     | city      | loyalty_tier |
|----------|----------------|-----------|----------------|
| 1        | Aayush Sharma  | Hyderabad | Gold           |
| 2        | Ananya Seth    | Chennai   | Silver         |
| 3        | Anuj Khokhar   | Bengaluru | Gold           |
| 4        | Prem Kushwah   | Hyderabad | Silver         |
| 5        | Tanushi        | Mumbai    | Gold           |

---

### Table 3: `bookings`

Confirmed stays. All guests survived.

| booking_id | property_id | guest_id | nights_stayed | total_paid |
|------------|-------------|----------|-----------------|--------------|
| 101        | 1           | 1        | 3               | 13500        |
| 102        | 2           | 2        | 2               | 5600         |
| 103        | 3           | 3        | 4               | 12800        |
| 104        | 1           | 4        | 2               | 9000         |
| 105        | 5           | 5        | 1               | 5000         |
| 106        | 4           | 1        | 3               | 6000         |

---

### Table 4: `ghost_reviews`

Post-stay reviews. `mentions_ghost` tracks whether the review specifically brought up paranormal activity.

| review_id | booking_id | stars | mentions_ghost |
|-----------|------------|-------|------------------|
| 1         | 101        | 5     | Yes              |
| 2         | 102        | 4     | No               |
| 3         | 103        | 5     | Yes              |
| 4         | 104        | 2     | Yes              |
| 5         | 105        | 5     | Yes              |
| 6         | 106        | 4     | No               |

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> Ananya is building the "Seriously Haunted" homepage carousel and needs the top spenders first.

**Your Task:**
Show the property name and total amount paid for every booking at a property with haunting_level 4 or higher, highest amount paid first.

---

### Question 2 — Intermediate

> **Business Context:**
> The board meeting needs a **Property Performance Report** — revenue and guest satisfaction, side by side.

**Your Task:**
For each property, show total revenue from bookings and the average review star rating, rounded to 2 decimals.

---

### Question 3 — Intermediate

> **Business Context:**
> Marketing wants to know which guests are repeat visitors, for a "Frequent Fright" loyalty push.

**Your Task:**
Show guests who have booked more than once — their name, booking count, and total amount spent.

---

### Question 4 — Advanced

> **Business Context:**
> Ananya wants a **Haunting Leaderboard** — within each haunting_level bracket, which property is actually pulling in the revenue.

**Your Task:**
For each property, show its name, haunting_level, total revenue, its rank within its haunting_level bracket by revenue (highest = Rank 1), and its share of that bracket's total revenue as a percentage rounded to 2 decimals.

---

*Something just creaked upstairs. Probably the query planner. Make it count.*
