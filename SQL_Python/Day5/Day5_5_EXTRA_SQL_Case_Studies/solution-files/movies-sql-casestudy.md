# Movies SQL Case Study — CineStream Content Analytics

---

## Problem Statement

**CineStream** is a fast-rising global OTT platform competing head-to-head with the biggest names in streaming. With thousands of titles and millions of subscribers, their data team is under pressure to deliver sharp insights ahead of the **Annual Content Strategy Meeting**.

The decisions made in that room will determine:
- Which movies get featured in curated collections next quarter
- Which genres are worth investing in based on financial and critical performance
- Which directors deserve a **Spotlight Series** deal
- How individual movies rank within their genre for future licensing decisions

You've been brought in as the **Content Data Analyst**. The Head of Content, the Finance Lead, and three Regional Marketing Managers are counting on your queries.

---

## Database Schema & Sample Data

### Table 1: `movies`

Contains the core catalog of movies available on the platform.

| movie_id | title             | genre    | release_year | language | director_id |
|----------|-------------------|----------|--------------|----------|-------------|
| 1        | The Last Horizon  | Sci-Fi   | 2021         | English  | 101         |
| 2        | Rang De Sapne     | Drama    | 2022         | Hindi    | 102         |
| 3        | Neon City         | Thriller | 2023         | English  | 103         |
| 4        | Andha Yug         | Drama    | 2021         | Telugu   | 102         |
| 5        | Starfall          | Sci-Fi   | 2020         | English  | 101         |

---

### Table 2: `directors`

Profiles of directors whose movies are in the CineStream catalog.

| director_id | full_name       | country | debut_year |
|-------------|-----------------|---------|------------|
| 101         | James Calloway  | USA     | 2015       |
| 102         | Arjun Reddy     | India   | 2018       |
| 103         | Sofia Mendes    | Brazil  | 2019       |
| 104         | Lena Fischer    | Germany | 2021       |

---

### Table 3: `box_office`

Tracks the budget and worldwide collection for each movie (figures in crores).

| bo_id | movie_id | budget_cr | collection_cr | release_country |
|-------|----------|-----------|---------------|-----------------|
| 1     | 1        | 120       | 310           | USA             |
| 2     | 2        | 45        | 98            | India           |
| 3     | 3        | 80        | 65            | Brazil          |
| 4     | 4        | 30        | 112           | India           |
| 5     | 5        | 95        | 220           | USA             |

---

### Table 4: `reviews`

User ratings and vote counts collected from streaming and review platforms.

| review_id | movie_id | platform       | rating | total_votes |
|-----------|----------|----------------|--------|-------------|
| 1         | 1        | IMDb           | 8.2    | 124000      |
| 2         | 2        | IMDb           | 7.5    | 43000       |
| 3         | 3        | IMDb           | 6.8    | 31000       |
| 4         | 4        | RottenTomatoes | 8.9    | 18000       |
| 5         | 5        | IMDb           | 7.1    | 89000       |

---

## Questions

---

### Question 1 — Beginner

> **Business Context:**
> The Content team is launching a curated **"Best of English Cinema (Post-2020)"** collection for subscribers. They need a quick list of all eligible titles to start the selection process.

**Your Task:**
Retrieve the title and release year of all English language movies released after 2020, sorted by most recent first.

---

### Question 2 — Intermediate

> **Business Context:**
> The Finance team is building a **Genre Performance Report** to decide where to increase licensing spend next year. They need to see how each genre is performing — both at the box office and in the eyes of the audience.

**Your Task:**
For each genre, find the total box office collection and the average user rating across all movies in that genre.

---

### Question 3 — Intermediate

> **Business Context:**
> CineStream is planning a **Director Spotlight Series** — an exclusive section that features directors with a strong catalog presence on the platform. Only directors with more than one movie on CineStream qualify for this feature. The partnerships team needs a list of eligible directors along with their catalog strength and combined box office pull.

**Your Task:**
Identify directors who have more than one movie in the catalog. For each such director, show their name, the number of movies they have directed, and the total box office collection across all their movies.

---

### Question 4 — Advanced

> **Business Context:**
> The Regional Marketing Managers each own a genre — Sci-Fi, Drama, and Thriller. They want a **Genre Leaderboard** to see how each movie in their genre ranks against the others by box office collection. They also want to know each movie's collection as a share of the genre's total — so they can pitch the strongest titles to advertisers.

**Your Task:**
For each movie, show its title, genre, box office collection, its rank within its genre based on collection (highest = Rank 1), and its collection as a percentage of the total collection for that genre, rounded to 2 decimal places. Order the result by genre, then by rank.

---

*The content strategy meeting is tomorrow. Make every query count.*
