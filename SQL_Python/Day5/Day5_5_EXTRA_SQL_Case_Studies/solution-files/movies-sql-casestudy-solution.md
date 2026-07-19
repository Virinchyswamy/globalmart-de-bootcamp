# Movies SQL Case Study — Solutions

---

### Question 1 — Beginner

> **Business Context:**
> The Content team is launching a curated **"Best of English Cinema (Post-2020)"** collection for subscribers. They need a quick list of all eligible titles to start the selection process.

**Your Task:**
Retrieve the title and release year of all English language movies released after 2020, sorted by most recent first.

**Solution:**

```sql
SELECT title, release_year
FROM movies
WHERE language = 'English'
  AND release_year > 2020
ORDER BY release_year DESC;
```

---

### Question 2 — Intermediate

> **Business Context:**
> The Finance team is building a **Genre Performance Report** to decide where to increase licensing spend next year. They need to see how each genre is performing — both at the box office and in the eyes of the audience.

**Your Task:**
For each genre, find the total box office collection and the average user rating across all movies in that genre.

**Solution:**

```sql
SELECT
    m.genre,
    SUM(b.collection_cr)  AS total_collection_cr,
    ROUND(AVG(r.rating), 2) AS avg_rating
FROM movies m
JOIN box_office b ON m.movie_id = b.movie_id
JOIN reviews r    ON m.movie_id = r.movie_id
GROUP BY m.genre;
```

---

### Question 3 — Intermediate

> **Business Context:**
> CineStream is planning a **Director Spotlight Series** — an exclusive section that features directors with a strong catalog presence on the platform. Only directors with more than one movie on CineStream qualify for this feature. The partnerships team needs a list of eligible directors along with their catalog strength and combined box office pull.

**Your Task:**
Identify directors who have more than one movie in the catalog. For each such director, show their name, the number of movies they have directed, and the total box office collection across all their movies.

**Solution:**

```sql
WITH director_stats AS (
    SELECT
        m.director_id,
        COUNT(m.movie_id)    AS total_movies,
        SUM(b.collection_cr) AS total_collection_cr
    FROM movies m
    JOIN box_office b ON m.movie_id = b.movie_id
    GROUP BY m.director_id
    HAVING COUNT(m.movie_id) > 1
)
SELECT
    d.full_name,
    ds.total_movies,
    ds.total_collection_cr
FROM director_stats ds
JOIN directors d ON ds.director_id = d.director_id
ORDER BY ds.total_collection_cr DESC;
```

---

### Question 4 — Advanced

> **Business Context:**
> The Regional Marketing Managers each own a genre — Sci-Fi, Drama, and Thriller. They want a **Genre Leaderboard** to see how each movie in their genre ranks against the others by box office collection. They also want to know each movie's collection as a share of the genre's total — so they can pitch the strongest titles to advertisers.

**Your Task:**
For each movie, show its title, genre, box office collection, its rank within its genre based on collection (highest = Rank 1), and its collection as a percentage of the total collection for that genre, rounded to 2 decimal places. Order the result by genre, then by rank.

**Solution:**

```sql
WITH movie_collection AS (
    SELECT
        m.movie_id,
        m.title,
        m.genre,
        b.collection_cr
    FROM movies m
    JOIN box_office b ON m.movie_id = b.movie_id
)
SELECT
    title,
    genre,
    collection_cr,
    RANK() OVER (PARTITION BY genre ORDER BY collection_cr DESC) AS genre_rank,
    ROUND(
        collection_cr * 100.0 / SUM(collection_cr) OVER (PARTITION BY genre),
        2
    ) AS pct_of_genre_total
FROM movie_collection
ORDER BY genre, genre_rank;
```
