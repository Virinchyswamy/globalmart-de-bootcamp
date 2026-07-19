# Z-ORDER vs. Liquid Clustering on a Fact Table 
## Content Type
Scenario

## Overview
GlobalMart's real gold.fact_sales table gets refreshed incrementally every day, which means it slowly accumulates small files over time — exactly the condition that makes queries slow and that OPTIMIZE/ZORDER/Liquid Clustering exist to fix. In this hands-on, you will clone a fact-table-shaped dataset into your own fully isolated practice schema — never touching the real shared gbmart.gold tables again after the initial clone — deliberately fragment it, baseline three realistic business query shapes against it, apply OPTIMIZE with Z-ORDER, then build a second copy using Liquid Clustering, and empirically compare which technique actually holds up better once new data keeps landing on the table.

## Learning Objectives
- Build a fully isolated, shareable-nothing practice environment using SHALLOW CLONE, so every experiment is safe to run and re-run without affecting the shared gbmart catalog
- Deliberately reproduce the small-file fragmentation pattern a real incrementally-refreshed fact table develops over time
- Choose Z-ORDER columns from real query access patterns rather than guessing, and measure the before/after impact on file count and query time
- Build an equivalent Liquid Clustering table and compare its query performance against Z-ORDER on the same data
- Empirically measure which clustering technique re-clusters more cheaply after new data is appended — the real differentiator for a table that refreshes incrementally
- State a grounded, evidence-based recommendation for which technique fits an incrementally-refreshed fact table like fact_sales

## Prerequisites
- Performance in Modelling (Z-ORDER column selection from real query patterns)
-  first exposure to OPTIMIZE/ZORDER/Liquid Clustering mechanics on a generic practice table
- Read access to gbmart.gold.fact_sales, gbmart.gold.dim_product, gbmart.gold.dim_date, gbmart.gold.dim_address
- A Databricks workspace and catalog/schema you have CREATE/write permission on (never gbmart itself)

## Duration of Completion
60 minutes

## Level
Intermediate

## Industries
- e-commerce

## Tags
- data-engineering (skill)
- performance-tuning (skill)
- databricks (tool)

#### Overview
GlobalMart's real gold.fact_sales table gets refreshed incrementally every day, which means it slowly accumulates small files over time — exactly the condition that makes queries slow and that OPTIMIZE/ZORDER/Liquid Clustering exist to fix. In this hands-on, you will clone a fact-table-shaped dataset into your own fully isolated practice schema — never touching the real shared gbmart.gold tables again after the initial clone — deliberately fragment it, baseline three realistic business query shapes against it, apply OPTIMIZE with Z-ORDER, then build a second copy using Liquid Clustering, and empirically compare which technique actually holds up better once new data keeps landing on the table.

#### Level
intermediate

#### Industries
- e-commerce

#### Tags
- data-engineering (skill)
- performance-tuning (skill)
- databricks (tool)

#### Scenario Inputs
##### Input 1
**Type:** Text

>[!IMPORTANT]
>Everything from this point forward in this hands-on runs against your own practice schema — never against `gbmart` directly. Replace `YOUR_SCHEMA` below with a schema you actually own before running anything.

### Setup — Clone What You Need, Once

`SHALLOW CLONE` gives you an independent copy of a table's transaction history without physically copying the underlying data files — instant, and safe to `OPTIMIZE`/`ZORDER`/`CLUSTER BY` repeatedly without ever touching the source table those files still belong to.

```python
# ─── Personal practice schema — never write directly to shared gbmart tables ────
# HOW TO GET A SCHEMA NAME: use a catalog.PRACTICE_SCHEMA you already have CREATE permission on (ask your instructor if unsure), and pick something unique to you, e.g. catalog.PRACTICE_SCHEMA.
PRACTICE_SCHEMA = "catalog.PRACTICE_SCHEMA"   # ← replace with a schema you own
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {PRACTICE_SCHEMA}")

FACT_TABLE    = f"{PRACTICE_SCHEMA}.fact_sales_practice"
PRODUCT_TABLE = f"{PRACTICE_SCHEMA}.dim_product_practice"
DATE_TABLE    = f"{PRACTICE_SCHEMA}.dim_date_practice"
LIQUID_TABLE  = f"{PRACTICE_SCHEMA}.fact_sales_liquid_practice"

# SHALLOW CLONE: identical data to the real Gold tables right now, but a
# transaction history that's entirely yours — safe to rewrite repeatedly.
spark.sql(f"CREATE OR REPLACE TABLE {FACT_TABLE}    SHALLOW CLONE {catalog}.gold.fact_sales")
spark.sql(f"CREATE OR REPLACE TABLE {PRODUCT_TABLE} SHALLOW CLONE {catalog}.gold.dim_product")
spark.sql(f"CREATE OR REPLACE TABLE {DATE_TABLE}    SHALLOW CLONE {catalog}.gold.dim_date")

for t in [FACT_TABLE, PRODUCT_TABLE, DATE_TABLE]:
    print(f"{t}: {spark.table(t).count():,} rows")
```

Run this once. From here on, every cell in this hands-on reads and writes only `FACT_TABLE`, `PRODUCT_TABLE`, `DATE_TABLE`, and `LIQUID_TABLE` — you will not see `gbmart.gold.*` referenced again anywhere below.

---

**Tags**


##### Input 2
**Type:** Choice

**Question:** Why does this hands-on use `SHALLOW CLONE` instead of a full `CREATE TABLE ... AS SELECT` copy of `fact_sales`?

**Options:** 
- `SHALLOW CLONE` is faster to type

- `SHALLOW CLONE` gives an independent transaction log without duplicating the underlying data files, so it's instant regardless of table size

- `SHALLOW CLONE` automatically applies Z-ORDER to the new table

- `SHALLOW CLONE` is required by Unity Catalog for any table with a surrogate key

**Correct Options:** 
- `SHALLOW CLONE` gives an independent transaction log without duplicating the underlying data files, so it's instant regardless of table size

**Solution:** 
A `CREATE TABLE ... AS SELECT` (a "deep" copy) physically rewrites every row into new Parquet files — for a table `fact_sales`'s size, that's real time and real storage cost every time you wanted a fresh practice copy. `SHALLOW CLONE` instead creates a new Delta table that points at the *same* underlying data files as the source, with its own brand-new, independent transaction log layered on top. The moment you run `OPTIMIZE`/`ZORDER`/`CLUSTER BY` or write new rows against the clone, only the clone's own log and any newly-written files change — the source table's files and history are completely untouched. That's what makes it safe to experiment on repeatedly without any risk to `gbmart.gold.fact_sales`.

**Tags**
- databricks (tool)
- data-storage (skill)

---

## Scenario 2 — Simulate Realistic File Fragmentation

**Tags**


##### Input 3
**Type:** Text

### Fragment the Practice Table

```python
# repartition(200) forces the write into 200 separate output files,
# simulating the small-file state an incrementally-refreshed fact_sales
# reaches after many small daily MERGE runs — without waiting months to
# actually get there.
(
    spark.table(FACT_TABLE)
    .repartition(200)
    .write.format("delta").mode("overwrite")
    .saveAsTable(FACT_TABLE)
)
print("Practice fact table rewritten across 200 files.")
```

---

**Tags**


##### Input 4
**Type:** Code

**Question:** Using PySpark, confirm the fragmentation actually worked by reporting the exact number of data files your practice fact table now has, and the average file size in megabytes across those files.

**Language:** python

**Snippet:** 

**Solution:** 
```python
detail = spark.sql(f"DESCRIBE DETAIL {FACT_TABLE}").collect()[0]
num_files = detail["numFiles"]
size_mb = detail["sizeInBytes"] / (1024 * 1024)
avg_file_mb = size_mb / num_files

print(f"Number of files : {num_files}")
print(f"Total size (MB) : {size_mb:.1f}")
print(f"Average file size (MB) : {avg_file_mb:.2f}")
```
`DESCRIBE DETAIL` reports the table's current file count and total size directly from Delta's transaction log, no need to list the underlying storage path by hand. The file count should read exactly **200** — one file per partition, since `repartition(200)` was used and `fact_sales` has enough rows that essentially none of the 200 partitions come out empty. The average file size depends on your real `fact_sales` row count, but on a table this shape it typically lands well under Delta's ~1 GB target file size — confirming these files are meaningfully smaller than they should be, exactly the "small file problem" `OPTIMIZE` exists to fix.

**Tags**
- databricks / databricks-architecture (tool)

##### Input 5
**Type:** Text

### Register the Three Query Shapes

```python
import time

def category_month_query(fact_table_name):
    """Shape 1: category/month revenue rollup — joins dim_product and dim_date."""
    return spark.sql(f"""
        SELECT p.category, d.month, SUM(f.Sales_amount) AS revenue
        FROM {fact_table_name} f
        JOIN {PRODUCT_TABLE} p ON f.Product_ID = p.product_id AND p.is_current = true
        JOIN {DATE_TABLE} d    ON f.Time_ID = d.date_key
        GROUP BY p.category, d.month
    """)

def regional_query(fact_table_name):
    """Shape 2: state/city regional rollup — joins dim_address (via a re-clone below)."""
    return spark.sql(f"""
        SELECT a.state, a.city, SUM(f.Sales_amount) AS revenue, COUNT(DISTINCT f.Order_ID) AS orders
        FROM {fact_table_name} f
        JOIN {PRACTICE_SCHEMA}.dim_address_practice a ON f.Address_ID = a.address_id
        GROUP BY a.state, a.city
    """)

def product_point_lookup(fact_table_name, sample_product_id, start_date_key, end_date_key):
    """Shape 3: narrow point lookup — one Product_ID, a date range on Time_ID."""
    return spark.sql(f"""
        SELECT f.Order_ID, f.Time_ID, f.Quantity_purchased, f.Sales_amount
        FROM {fact_table_name} f
        WHERE f.Product_ID = '{sample_product_id}'
          AND f.Time_ID BETWEEN {start_date_key} AND {end_date_key}
    """)

# dim_address_practice wasn't cloned in Scenario 1 -- Shape 2 needs it, so clone it now,
# still only ever from gbmart, still a one-time read-only operation.
spark.sql(f"CREATE OR REPLACE TABLE {PRACTICE_SCHEMA}.dim_address_practice SHALLOW CLONE {catalog}.gold.dim_address")

# Pick one real Product_ID and a real 30-day date_key range to use for Shape 3,
# so every learner's point lookup is grounded in data that actually exists.
sample_row = spark.table(FACT_TABLE).select("Product_ID", "Time_ID").limit(1).collect()[0]
SAMPLE_PRODUCT_ID = sample_row["Product_ID"]
SAMPLE_START_DATE_KEY = sample_row["Time_ID"]
SAMPLE_END_DATE_KEY = sample_row["Time_ID"] + 30

print(f"Using Product_ID={SAMPLE_PRODUCT_ID}, Time_ID range {SAMPLE_START_DATE_KEY}-{SAMPLE_END_DATE_KEY} for the point-lookup query.")
```

---

**Tags**


##### Input 6
**Type:** Short Answer

**Question:** Before running any query, predict which of the three query shapes (category/month rollup, regional rollup, product point lookup) you expect to benefit the most from Z-ORDERing on `Product_ID` and `Time_ID`, and which you expect to benefit the least. Explain your reasoning in one or two sentences per query.

**Template:** null

**Tags**


##### Input 7
**Type:** Code

**Question:** Using PySpark, time how long the category/month revenue rollup query takes to run against your fragmented practice fact table, and report the result along with the row count it returns.

**Language:** python

**Snippet:** 

**Solution:** 
```python
start = time.time()
result_count = category_month_query(FACT_TABLE).count()
baseline_category_seconds = time.time() - start

print(f"Result rows : {result_count}")
print(f"Baseline category/month query time : {baseline_category_seconds:.3f}s")
```
Wrapping the query in `time.time()` before and after a `.count()` action (which forces Spark to actually execute the query rather than just build a lazy plan) gives a real wall-clock measurement. The exact number of seconds depends on your cluster size and current `fact_sales` volume — what matters for the rest of this hands-on is the relative comparison against the same query re-run later in Scenarios 4 and 5, not this number in isolation.

**Tags**
- databricks / databricks-architecture (tool)

##### Input 8
**Type:** Code

**Question:** Using PySpark, time how long the regional revenue rollup query takes to run against your fragmented practice fact table, and report the result along with the row count it returns.

**Language:** python

**Snippet:** 

**Solution:** 
```python
start = time.time()
result_count = regional_query(FACT_TABLE).count()
baseline_regional_seconds = time.time() - start

print(f"Result rows : {result_count}")
print(f"Baseline regional query time : {baseline_regional_seconds:.3f}s")
```
Same measurement pattern as the category/month query — a `time.time()` wrapper around a `.count()` action. Keep this number (`baseline_regional_seconds`) around; Scenarios 4 and 5 re-run this exact same query shape against the Z-ordered and Liquid-clustered tables so you can compare directly.

**Tags**
- databricks / databricks-architecture (tool)

##### Input 9
**Type:** Code

**Question:** Using PySpark, time how long the single-product point lookup query takes to run against your fragmented practice fact table, using the sample `Product_ID` and date range from Input 5, and report the result along with the row count it returns.

**Language:** python

**Snippet:** 

**Solution:** 
```python
start = time.time()
result_count = product_point_lookup(FACT_TABLE, SAMPLE_PRODUCT_ID, SAMPLE_START_DATE_KEY, SAMPLE_END_DATE_KEY).count()
baseline_point_seconds = time.time() - start

print(f"Result rows : {result_count}")
print(f"Baseline point-lookup query time : {baseline_point_seconds:.3f}s")
```
This query filters on exact equality for `Product_ID` and a narrow range on `Time_ID` — both are the columns this hands-on Z-ORDERs by in Scenario 4, which makes this the query shape most likely to show the clearest improvement from data skipping, since a highly selective filter benefits the most from Delta being able to skip whole files without reading them at all.

**Tags**


##### Input 10
**Type:** Code

**Question:** Using Spark SQL, compact your practice fact table and Z-ORDER it by the columns that match the query patterns you baselined in Scenario 3, then report the file count before and after, and the percentage reduction in file count.

**Language:** sql

**Snippet:** 

**Solution:** 
```python
files_before = spark.sql(f"DESCRIBE DETAIL {FACT_TABLE}").collect()[0]["numFiles"]

spark.sql(f"OPTIMIZE {FACT_TABLE} ZORDER BY (Product_ID, Time_ID)")

files_after = spark.sql(f"DESCRIBE DETAIL {FACT_TABLE}").collect()[0]["numFiles"]
pct_reduction = round(100 * (files_before - files_after) / files_before, 1)

print(f"Files before : {files_before}")
print(f"Files after  : {files_after}")
print(f"Reduction    : {pct_reduction}%")
```
`Product_ID` and `Time_ID` are the right choice here specifically because they're the columns Scenario 3's category/month query joins/groups on and the point-lookup query filters on directly — Z-ORDER only helps a query that actually filters or joins on the Z-ordered columns, so picking columns nobody queries on would compact the files (fixing the small-file problem) without improving any real query. `OPTIMIZE` rewrites the 200 fragmented files down toward Delta's default ~1 GB target file size, which on a table this size collapses to a small handful of files — expect a reduction well above 90%, though the exact post-optimize count depends on your real data volume.

**Tags**
- sql (tool)
- data-storage / z-order (skill)
- data-storage / file-compaction (skill)

---

**Tags**
- databricks / databricks-architecture (tool)

##### Input 11
**Type:** Code

**Question:** Using PySpark, re-run all three query shapes (category/month, regional, point lookup) against your now-Z-ordered practice fact table, and report each new timing alongside its Scenario 3 baseline and the percentage improvement.

**Language:** python

**Snippet:** 

**Solution:** 
```python
start = time.time(); category_month_query(FACT_TABLE).count(); zorder_category_seconds = time.time() - start
start = time.time(); regional_query(FACT_TABLE).count(); zorder_regional_seconds = time.time() - start
start = time.time(); product_point_lookup(FACT_TABLE, SAMPLE_PRODUCT_ID, SAMPLE_START_DATE_KEY, SAMPLE_END_DATE_KEY).count(); zorder_point_seconds = time.time() - start

def pct_improvement(before, after):
    return round(100 * (before - after) / before, 1) if before > 0 else 0.0

print(f"{'Query':<20} {'Baseline':>10} {'Z-ORDER':>10} {'Improvement':>12}")
print(f"{'Category/Month':<20} {baseline_category_seconds:>9.3f}s {zorder_category_seconds:>9.3f}s {pct_improvement(baseline_category_seconds, zorder_category_seconds):>11}%")
print(f"{'Regional':<20} {baseline_regional_seconds:>9.3f}s {zorder_regional_seconds:>9.3f}s {pct_improvement(baseline_regional_seconds, zorder_regional_seconds):>11}%")
print(f"{'Point Lookup':<20} {baseline_point_seconds:>9.3f}s {zorder_point_seconds:>9.3f}s {pct_improvement(baseline_point_seconds, zorder_point_seconds):>11}%")
```
The category/month and point-lookup queries should both show a real improvement, since both filter/join directly on the Z-ordered columns (`Product_ID`, `Time_ID`) and benefit from Delta's data skipping — the point lookup typically improves the most, since its highly selective `WHERE` clause lets Delta skip the largest share of files entirely. The regional query, which filters on `Address_ID` (a column that was never Z-ordered), should show little to no improvement — its rows are scattered across files the same way they were before, since Z-ORDER only physically co-locates rows by the columns you actually named.

**Tags**
- databricks / databricks-architecture (tool)

##### Input 12
**Type:** Choice

**Question:** Of the three query shapes, which one shows the smallest improvement after Z-ORDERing by `Product_ID` and `Time_ID`, and why?

**Options:** 
- The category/month query, because joins are always slower than filters

- The point lookup, because it returns too few rows to measure accurately

- The regional query, because it filters on `Address_ID`, a column that was never included in the Z-ORDER

- All three queries improve by roughly the same amount, since `OPTIMIZE` compacts the whole table regardless of query shape

**Correct Options:** 
- The regional query, because it filters on `Address_ID`, a column that was never included in the Z-ORDER

**Solution:** 
`OPTIMIZE ... ZORDER BY (Product_ID, Time_ID)` physically co-locates rows that share similar `Product_ID`/`Time_ID` values into the same files, so any query filtering or joining on those two columns can skip files that don't match. The regional query filters on `Address_ID` instead — a column Z-ORDER never touched — so its matching rows are still scattered across files exactly as randomly as before. File compaction alone (fewer, bigger files) gives the regional query a small, indirect benefit from reduced file-open overhead, but nowhere near the direct data-skipping benefit the other two queries get from being Z-ordered on the columns they actually use.

**Tags**
- databricks / databricks-architecture (tool)

##### Input 13
**Type:** Text

### Build the Liquid Clustering Table

```python
spark.sql(f"DROP TABLE IF EXISTS {LIQUID_TABLE}")
spark.sql(f"""
    CREATE TABLE {LIQUID_TABLE}
    CLUSTER BY (Product_ID, Time_ID)
    AS SELECT * FROM {FACT_TABLE}
""")

# OPTIMIZE on a clustered table applies clustering incrementally -- no
# ZORDER BY clause needed; the table already knows its own cluster columns.
spark.sql(f"OPTIMIZE {LIQUID_TABLE}")
print(f"{LIQUID_TABLE} built and clustered on (Product_ID, Time_ID).")
```

---

**Tags**


##### Input 14
**Type:** Code

**Question:** Using PySpark, re-run all three query shapes against your Liquid-clustered practice table, and report each timing alongside the Z-ORDER timings from Scenario 4.

**Language:** python

**Snippet:** 

**Solution:** 
```python
start = time.time(); category_month_query(LIQUID_TABLE).count(); liquid_category_seconds = time.time() - start
start = time.time(); regional_query(LIQUID_TABLE).count(); liquid_regional_seconds = time.time() - start
start = time.time(); product_point_lookup(LIQUID_TABLE, SAMPLE_PRODUCT_ID, SAMPLE_START_DATE_KEY, SAMPLE_END_DATE_KEY).count(); liquid_point_seconds = time.time() - start

print(f"{'Query':<20} {'Z-ORDER':>10} {'Liquid':>10}")
print(f"{'Category/Month':<20} {zorder_category_seconds:>9.3f}s {liquid_category_seconds:>9.3f}s")
print(f"{'Regional':<20} {zorder_regional_seconds:>9.3f}s {liquid_regional_seconds:>9.3f}s")
print(f"{'Point Lookup':<20} {zorder_point_seconds:>9.3f}s {liquid_point_seconds:>9.3f}s")
```
On the *first* clustering pass, Liquid Clustering and Z-ORDER should produce roughly comparable query performance for the category/month and point-lookup queries — both are physically clustering the same two columns, just with a different underlying mechanism. The real difference between the two techniques isn't visible from a single snapshot like this one; it shows up in how cheaply each table re-clusters after new data arrives, which is exactly what the next two Inputs measure.

**Tags**
- databricks / databricks-architecture (tool)

##### Input 15
**Type:** Text

### Simulate New Orders Landing

```python
# A small, realistic append -- roughly what one day of new orders might look
# like landing via Day 9-10's incremental MERGE, applied identically to both
# the Z-ordered table and the Liquid-clustered table so the comparison is fair.
new_rows_df = spark.table(FACT_TABLE).limit(500)

new_rows_df.write.format("delta").mode("append").saveAsTable(FACT_TABLE)
new_rows_df.write.format("delta").mode("append").saveAsTable(LIQUID_TABLE)

print(f"{FACT_TABLE}: {spark.table(FACT_TABLE).count():,} rows after append")
print(f"{LIQUID_TABLE}: {spark.table(LIQUID_TABLE).count():,} rows after append")
```

---

**Tags**


##### Input 16
**Type:** Code

**Question:** Using Spark SQL, run `OPTIMIZE` again on both your Z-ordered table and your Liquid-clustered table now that new rows have landed on each, and report how long each incremental `OPTIMIZE` took.

**Language:** sql

**Snippet:** 

**Solution:** 
```python
start = time.time()
spark.sql(f"OPTIMIZE {FACT_TABLE} ZORDER BY (Product_ID, Time_ID)")
zorder_reoptimize_seconds = time.time() - start

start = time.time()
spark.sql(f"OPTIMIZE {LIQUID_TABLE}")
liquid_reoptimize_seconds = time.time() - start

print(f"Z-ORDER re-OPTIMIZE time  : {zorder_reoptimize_seconds:.3f}s")
print(f"Liquid re-OPTIMIZE time   : {liquid_reoptimize_seconds:.3f}s")
```
This is the measurement that actually distinguishes the two techniques. Re-running `OPTIMIZE ... ZORDER BY` on the Z-ordered table re-evaluates clustering across the table again — at `fact_sales`'s real scale, that cost grows with total table size every single time it runs, no matter how small the new batch was. `OPTIMIZE` on the Liquid-clustered table, by contrast, is designed to cluster incrementally — it only needs to work on the files affected by the new 500-row append, not re-shuffle the whole table. On a practice-scale table the gap may look modest, but it is exactly this per-run cost, repeated every single day for years as Day 9–10's incremental refresh keeps landing new orders, that makes Liquid Clustering the more sustainable choice for a continuously-refreshed table like `fact_sales`.

**Tags**
- databricks / databricks-architecture (tool)

##### Input 17
**Type:** Code

**Question:** Using PySpark, build a single summary table showing, for each of the three query shapes, the baseline timing, the Z-ORDER timing, and the Liquid Clustering timing side by side.

**Language:** python

**Snippet:** 

**Solution:** 
```python
from pyspark.sql import Row

summary_rows = [
    Row(query="Category/Month", baseline=round(baseline_category_seconds, 3), zorder=round(zorder_category_seconds, 3), liquid=round(liquid_category_seconds, 3)),
    Row(query="Regional",       baseline=round(baseline_regional_seconds, 3), zorder=round(zorder_regional_seconds, 3), liquid=round(liquid_regional_seconds, 3)),
    Row(query="Point Lookup",   baseline=round(baseline_point_seconds, 3),    zorder=round(zorder_point_seconds, 3),    liquid=round(liquid_point_seconds, 3)),
]

summary_df = spark.createDataFrame(summary_rows)
summary_df.show(truncate=False)
```
Collecting every timing variable already captured earlier in this notebook into one `Row` per query, then building a small DataFrame from that list, is the same pattern used to compare grouped counts earlier in this course — no new technique, just organizing results that already exist so they're easy to read side by side and easy to include as evidence in the recommendation that follows.

**Tags**
- databricks / databricks-architecture (tool)

##### Input 18
**Type:** Short Answer

**Question:** Based on your Scenario 4-6 measurements — including the incremental re-OPTIMIZE timing, not just the query timings — which technique would you recommend GlobalMart use for the real fact_sales table, and why? Refer to your prediction from Input 6: was it right?

**Template:** null

**Tags**


##### Input 19
**Type:** File Upload

**Question:** Upload your completed Databricks notebook (.ipynb file) showing every measurement from Scenarios 1 through 6. Your notebook never contained a real credential — every table reference points at your own practice schema, so there is nothing to redact before submitting.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, JUPYTER_NOTEBOOK

**Tags**


