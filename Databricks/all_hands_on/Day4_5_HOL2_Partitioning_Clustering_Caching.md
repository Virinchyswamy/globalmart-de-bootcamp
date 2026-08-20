---
name: Day 4 HOL 2 — Storage Formats, Partitioning & Performance Levers
content_type: Scenario
overview: This is a hands-on learning lab, not a quick exercise. Using a real 5,000,000-row (~976 MB) synthetic GlobalMart-shaped retail sales dataset, you will follow the pattern Concept → Code → Run → Observe → Why did this happen? → Production use case for every performance lever a Data Engineer actually reaches for — storage format choice, partitioning, file sizing, caching, clustering, and Delta's transaction-log features (UPDATE, DELETE, MERGE, schema evolution, time travel) — measuring real size and speed differences with your own hands instead of just reading about them. It closes with an unassisted final challenge where you apply everything yourself.
learning_objectives:
  - Explain why CSV requires an expensive two-pass read for schema inference, and why Parquet/Delta don't
  - Measure real size and speed differences between CSV, JSON, Parquet, and Delta on the same dataset
  - Partition a Delta table by Year/Month and prove partition pruning using .explain() and the Spark UI
  - Diagnose and fix the small-files problem using OPTIMIZE
  - Measure the real performance benefit of caching a reused DataFrame
  - Use ZORDER (or Liquid Clustering) to speed up filters on a high-cardinality column, and explain how it differs from partitioning
  - Use UPDATE, DELETE, MERGE, schema evolution, and time travel — the transaction-log features unique to Delta
  - Recognize that a single wall-clock timing comparison can be dominated by noise and doesn't always confirm the expected direction, even when the underlying mechanism (partition pruning, data skipping) is real and independently provable via .explain()/DESCRIBE HISTORY
  - Design and justify your own partitioning strategy for a new query pattern
prerequisites:
  - A Databricks workspace with a Unity Catalog Volume you can upload to
  - Completed Day 4 ILT 3 — Partitioning Strategy & Storage Formats & Performance Levers
  - retail_sales_dataset.csv (~976 MB, 5,000,000 rows) uploaded to your Volume
duration: 120 minutes
level: Intermediate
industries:
  - e-commerce
tags:
  - databricks (tool)
  - spark (tool)
  - data-storage (skill)
---

---

## Scenario 1 — Setup, and Why CSV Isn't a Storage Format

**Overview:** This hands-on lab uses a real 5,000,000-row (~976 MB) synthetic e-commerce sales dataset — large enough that file-size, partitioning, and caching effects are actually visible, which small sample CSVs can't show you. Before touching any performance lever, you will experience directly why CSV is a poor *storage* format even though it is a perfectly fine *exchange* format: when Spark reads a CSV with `inferSchema=true`, it has no type metadata to go on, so it scans the file once just to guess column types, then again to actually load the data.

**Outcome:** The dataset uploaded to a Unity Catalog Volume, and two DataFrames read from it — one with `inferSchema=true`, one with `inferSchema=false` — with your own measured timing showing the cost of the extra schema-inference pass.

---

## Input 1

**Type:** Text

### Setup

Upload `retail_sales_dataset.csv` to a Databricks Volume, then point your notebook at it:

```python
# ─── Setup: point at your Volume, and a scratch catalog/schema for this lab ────
# Replace these with your own catalog/schema/volume names.
CATALOG      = "YOUR_CATALOG"       # e.g. "gbmart"
LAB_SCHEMA   = "day4_lab"           # a scratch schema just for this lab — safe to drop entirely afterward
VOLUME_NAME  = "day4_lab"

volume_path = f"/Volumes/{CATALOG}/{LAB_SCHEMA}/{VOLUME_NAME}"
csv_path    = f"{volume_path}/retail_sales_dataset.csv"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{LAB_SCHEMA}")
```

---

## Input 2

**Type:** Text

### Read the same CSV two ways, and time both

```python
import time

# inferSchema=True triggers a two-pass read: one pass to guess types, one to load.
start = time.time()
sales_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(csv_path)
)
row_count = sales_df.count()   # forces the lazy read to actually execute
elapsed_infer = time.time() - start
print(f"Rows: {row_count:,}")
print(f"Time with inferSchema=true (two passes): {elapsed_infer:.2f}s")
```

```python
# ─── Compare: reading WITHOUT schema inference (single pass, everything as string) ──
start = time.time()
sales_df_nostring = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "false")   # every column lands as StringType
    .csv(csv_path)
)
row_count_2 = sales_df_nostring.count()
elapsed_nostring = time.time() - start
print(f"Time with inferSchema=false (one pass, all strings): {elapsed_nostring:.2f}s")
sales_df_nostring.printSchema()
```

>[!IMPORTANT]
>A real, full run of this lab on the actual 5,000,000-row dataset produced `inferSchema=true` in 38.51s and `inferSchema=false` in 6.50s. Your own numbers will vary with cluster size and warm-up state, but the two-pass cost should be clearly visible either way.

---

## Input 3

**Type:** Choice

**Question:** In a real, full run of this lab, reading the 5,000,000-row CSV with `inferSchema=true` took 38.51s, and the same file with `inferSchema=false` took 6.50s. Roughly what multiple slower was the `inferSchema=true` read?

**Options:**
- Roughly 2x slower
- Roughly 6x slower
- Roughly 12x slower
- Roughly 20x slower

**Correct Options:**
- Roughly 6x slower

**Solution:**
38.51 ÷ 6.50 ≈ 5.9x — close to 6x. That gap is the cost of the extra full pass over the file that `inferSchema=true` needs to guess every column's type, on top of the pass every read needs just to load the data. Your own exact numbers will depend on cluster size and warm-up state, but the same roughly 5-6x order of magnitude should hold, since the mechanism (one extra full file scan) doesn't change.

**Tags**
- data-understanding (skill)

---

## Input 4

**Type:** Choice

**Question:** Why does `inferSchema=true` require Spark to scan a CSV file twice instead of once?

**Options:**
- CSV files are always compressed, so Spark must decompress them twice
- CSV carries no type metadata, so Spark must scan once to guess each column's type before it can scan again to actually load the data
- Spark always reads every file format twice for safety
- inferSchema only affects how the data is displayed, not how it is read

**Correct Options:**
- CSV carries no type metadata, so Spark must scan once to guess each column's type before it can scan again to actually load the data

**Solution:**
CSV is plain text with no schema information embedded in the file itself. Without `.schema(mySchema)` supplied explicitly, the only way Spark can know whether a column is an integer, a date, or a string is to scan the whole file once, then load it on a second pass with the types it inferred. Parquet and Delta store the schema as metadata inside the file, so neither format ever needs this extra pass.

**Tags**
- data-understanding (skill)
- approach (skill)

---

## Input 5

**Type:** Short Answer

**Question:** After loading `sales_df` with `inferSchema=true`, confirm the total row count and column count you see, and state whether the `Year`/`Month` breakdown you explored covers the full 2022–2026 range the dataset description mentions.

**Template:** null

**Tags**
- data-understanding (skill)

---

## Scenario 2 — Storage Format Comparison: CSV vs. JSON vs. Parquet vs. Delta

**Overview:** This hands-on lab uses the same real 5,000,000-row retail sales dataset from Scenario 1. Rather than just reading that Parquet and Delta are "better" than CSV, you will actually convert this same dataset into JSON, Parquet, and Delta, and measure the on-disk size and query speed differences yourself. Parquet stores data column-by-column instead of row-by-row, which means a query touching only a few columns can skip reading the rest entirely — Delta is Parquet plus a transaction log (`_delta_log/`) on top, which is what gives it ACID transactions, time travel, and reliable concurrent writes.

**Outcome:** The same dataset written as JSON, Parquet, and a managed Delta table, with your own measured comparison of on-disk size and read+aggregation speed across all four formats.

---

## Input 6

**Type:** Text

### Convert the same data into JSON, Parquet, and Delta

```python
json_path    = f"{volume_path}/formats/sales_json"
parquet_path = f"{volume_path}/formats/sales_parquet"

sales_df.write.mode("overwrite").json(json_path)
sales_df.write.mode("overwrite").parquet(parquet_path)
sales_df.write.mode("overwrite").saveAsTable(f"{CATALOG}.{LAB_SCHEMA}.sales_delta")
```

---

## Input 7

**Type:** Text

### Measure on-disk size for each format

```python
def folder_size_bytes(path):
    total = 0
    for f in dbutils.fs.ls(path):
        if f.isDir():
            total += folder_size_bytes(f.path)
        else:
            total += f.size
    return total

csv_size     = dbutils.fs.ls(csv_path)[0].size
json_size    = folder_size_bytes(json_path)
parquet_size = folder_size_bytes(parquet_path)

# Delta's size comes straight from its own metadata, not a manual folder traversal.
delta_detail = spark.sql(f"DESCRIBE DETAIL {CATALOG}.{LAB_SCHEMA}.sales_delta")
delta_size   = delta_detail.collect()[0]["sizeInBytes"]

for name, size in [("CSV", csv_size), ("JSON", json_size), ("Parquet", parquet_size), ("Delta", delta_size)]:
    ratio = csv_size / size if size else 0
    print(f"{name:<10} {size/1e6:>12.1f} MB   {ratio:>6.2f}x vs CSV")
```

>[!IMPORTANT]
>A real, full run of this lab produced: CSV 976.4 MB (1.00x), JSON 2530.9 MB (0.39x — larger than CSV), Parquet 166.0 MB (5.88x smaller), Delta 118.5 MB (8.24x smaller — the smallest of all four). Your own numbers will vary slightly, but this ranking (JSON largest, Delta smallest) should hold.

---

## Input 8

**Type:** Choice

**Question:** A real, full run of this lab measured CSV at 976.4 MB, JSON at 2530.9 MB, Parquet at 166.0 MB, and Delta at 118.5 MB. Which statement correctly describes this result?

**Options:**
- JSON was smaller than CSV because it compresses text more efficiently
- JSON was larger than CSV; Parquet and Delta were both smaller than CSV, with Delta the smallest of all four
- All three alternative formats (JSON, Parquet, Delta) were smaller than CSV
- Delta was the largest format because it stores a transaction log

**Correct Options:**
- JSON was larger than CSV; Parquet and Delta were both smaller than CSV, with Delta the smallest of all four

**Solution:**
JSON repeats every field name on every single record, adding real overhead with no compression to offset it — that's why it came out over 2.5x *larger* than the raw CSV, not smaller. Parquet's columnar, compressed layout got it down to about 1/6th the size of CSV, and Delta (Parquet plus a small transaction log) came out smallest of all at roughly 1/8th the size of CSV.

**Tags**
- data-storage (skill)

---

## Input 9

**Type:** Text

### Measure read + aggregation time for each format

Same query against each format — total `Sales` by `Category` — forces a full scan, so the timing reflects the storage format itself:

```python
def timed_aggregation(read_fn, label):
    start = time.time()
    df = read_fn()
    result = df.groupBy("Category").sum("Sales").collect()
    elapsed = time.time() - start
    print(f"{label:<10} {elapsed:>8.2f}s")
    return elapsed

csv_time     = timed_aggregation(lambda: spark.read.option("header","true").option("inferSchema","true").csv(csv_path), "CSV")
json_time    = timed_aggregation(lambda: spark.read.json(json_path), "JSON")
parquet_time = timed_aggregation(lambda: spark.read.parquet(parquet_path), "Parquet")
delta_time   = timed_aggregation(lambda: spark.table(f"{CATALOG}.{LAB_SCHEMA}.sales_delta"), "Delta")
```

>[!IMPORTANT]
>A real, full run of this lab produced: CSV 20.41s, JSON 31.17s, Parquet 2.04s, Delta 3.03s. Parquet was fastest, narrowly ahead of Delta; both were far ahead of CSV and JSON, with JSON the slowest of all four.

---

## Input 10

**Type:** Choice

**Question:** A real, full run of this lab measured CSV at 20.41s, JSON at 31.17s, Parquet at 2.04s, and Delta at 3.03s for the same `groupBy("Category").sum("Sales")` query. Which format was fastest, and which was slowest?

**Options:**
- CSV fastest, JSON slowest
- Parquet fastest, JSON slowest
- Delta fastest, CSV slowest
- JSON fastest, Parquet slowest

**Correct Options:**
- Parquet fastest, JSON slowest

**Solution:**
Parquet (2.04s) narrowly edged out Delta (3.03s) as fastest, while JSON (31.17s) was the slowest of all four — even slower than CSV (20.41s). This query only touches 2 of the dataset's 25 columns (`Category` and `Sales`), which is exactly what lets the columnar formats (Parquet, Delta) skip the other 23 columns entirely — CSV and JSON are row-based, so both have to read and parse every column of every row regardless of what the query actually needs.

**Tags**
- data-storage (skill)

---

## Input 11

**Type:** Choice

**Question:** What structural property of Parquet lets Spark skip reading 23 of this dataset's 25 columns when a query only needs `Category` and `Sales`?

**Options:**
- Parquet automatically deletes unused columns before saving
- Parquet stores data column-by-column, so a query can read only the columns it needs and skip the rest entirely
- Parquet compresses every column into a single value
- Parquet only allows queries on pre-selected columns

**Correct Options:**
- Parquet stores data column-by-column, so a query can read only the columns it needs and skip the rest entirely

**Solution:**
Row-based formats (CSV, JSON) store every column of every row together, so reading any column means reading all of them. Parquet's columnar layout stores all `Category` values together, all `Sales` values together, and so on — so a query referencing only those two columns can skip the other 23 entirely. This is called column pruning.

**Tags**
- data-storage (skill)
- data-wrangling / group-by-aggregate (skill)

---

## Input 12

**Type:** Choice

**Question:** Structurally, what is a Delta table relative to a Parquet folder?

**Options:**
- A completely different binary file format, unrelated to Parquet
- Parquet data files, plus a transaction log (`_delta_log/`) recording every write as a versioned commit
- A compressed version of CSV
- A row-based alternative to Parquet

**Correct Options:**
- Parquet data files, plus a transaction log (`_delta_log/`) recording every write as a versioned commit

**Solution:**
Delta gets its columnar storage benefits from Parquet — the data files underneath are Parquet. What Delta adds on top is the `_delta_log/` folder, which records every write as an atomic, versioned commit. That log is what gives Delta ACID transactions, reliable concurrent writes, and time travel — none of which plain Parquet has on its own.

**Tags**
- data-storage (skill)

---

## Scenario 3 — Partitioning Strategy & Partition Pruning

**Overview:** This hands-on lab continues using the same 5,000,000-row retail sales dataset. Partitioning means physically splitting a table's files into separate folders based on a column's value — for example, every row where `Year=2024` and `Month=6` lives in a folder literally named `Year=2024/Month=6/`. When a query filters on a partition column, Spark can skip entire folders by name alone, without ever opening the files inside them — this is called partition pruning, and it is a coarser, folder-level mechanism distinct from the column-level pruning you just measured in Scenario 2.

**Outcome:** A Delta table partitioned by `Year` and `Month`, with your own proof — via `.explain()` and real partition metadata — that partition pruning happens on a filtered query, plus an honest look at what wall-clock timing does and doesn't prove about it.

---

## Input 13

**Type:** Text

### Write partitioned by Year and Month, and inspect the real partition structure

```python
(sales_df.write
    .mode("overwrite")
    .partitionBy("Year", "Month")
    .saveAsTable(f"{CATALOG}.{LAB_SCHEMA}.sales_partitioned"))

print("Partition columns:")
spark.sql(f"DESCRIBE DETAIL {CATALOG}.{LAB_SCHEMA}.sales_partitioned").select("partitionColumns").show(truncate=False)

print("Sample partitions:")
spark.sql(f"SHOW PARTITIONS {CATALOG}.{LAB_SCHEMA}.sales_partitioned").show(50, truncate=False)
```

`DESCRIBE DETAIL`'s `partitionColumns` field and `SHOW PARTITIONS` both read partition metadata directly through Unity Catalog — no need to browse the raw storage path folder-by-folder to confirm `partitionBy("Year", "Month")` actually took effect.

---

## Input 14

**Type:** Text

### Query with a partition filter vs. without one, and prove pruning with .explain()

```python
partitioned_df = spark.table(f"{CATALOG}.{LAB_SCHEMA}.sales_partitioned")

start = time.time()
filtered_count = partitioned_df.filter("Year = 2024 AND Month = 6").count()
filtered_time = time.time() - start

start = time.time()
unfiltered_count = partitioned_df.count()
unfiltered_time = time.time() - start

print(f"WITH partition filter: {filtered_count:,} rows in {filtered_time:.2f}s")
print(f"WITHOUT filter (full table): {unfiltered_count:,} rows in {unfiltered_time:.2f}s")

partitioned_df.filter("Year = 2024 AND Month = 6").explain(True)
# Look for "PartitionFilters" in the physical plan — that line lists exactly
# which partition predicates Spark used to skip folders before reading anything.
```

>[!IMPORTANT]
>A real, full run of this lab produced a genuinely counter-intuitive result: the filtered query returned 82,151 rows in 0.49s, while the unfiltered full-table count returned 5,000,000 rows in 0.27s — the unfiltered count was actually *faster*, even though the real `.explain(True)` output confirmed `PartitionFilters` did skip folders for the filtered query. Input 16 asks you to reason through why. Your own run may show either direction — the point of this lab isn't "filtered is always faster," it's proving pruning happened via `.explain()`, independent of what the stopwatch shows.

---

## Input 15

**Type:** Short Answer

**Question:** In your `.explain(True)` output, what specific line in the physical plan confirms partition pruning happened for the filtered query, and what predicates does it list?

**Template:** null

**Tags**
- data-storage (skill)

---

## Input 16

**Type:** Choice

**Question:** A real, full run of this lab found the *unfiltered* full-table `count()` (5,000,000 rows, 0.27s) actually completed faster than the *filtered* `count()` (82,151 rows, 0.49s) — even though `.explain(True)` confirmed the filtered query's plan did contain `PartitionFilters` that skipped folders. What's the best explanation for this?

**Options:**
- Partition pruning didn't actually happen for the filtered query, despite what `.explain()` showed
- An unfiltered `COUNT` can sometimes be answered from Delta's stored file/row statistics without a real scan, while a filtered query still has to open and filter the matching files — so fewer rows read doesn't automatically mean faster wall-clock time
- The filtered query is always slower than a full count, in every case, regardless of partitioning
- `.explain(True)` results are unrelated to what actually executes

**Correct Options:**
- An unfiltered `COUNT` can sometimes be answered from Delta's stored file/row statistics without a real scan, while a filtered query still has to open and filter the matching files — so fewer rows read doesn't automatically mean faster wall-clock time

**Solution:**
Partition pruning is real here — the `PartitionFilters` line in the physical plan is independent proof of it, and doesn't depend on which query finished faster. But "prunes more folders" and "finishes faster in wall-clock time" are not the same guarantee: a plain unfiltered `count()` can sometimes be satisfied from Delta's own row-count statistics in its transaction log, without truly scanning file contents, while a filtered query still has to open, filter, and count rows in the files it kept. This is exactly why this lab treats `.explain()`'s `PartitionFilters` line as the real proof of pruning, and timing as a secondary, noisier signal — a single wall-clock comparison can be dominated by factors like this, cluster warm-up state, or caching from a previous cell.

**Tags**
- data-storage (skill)
- approach (skill)

---

## Input 17

**Type:** Choice

**Question:** How does partition pruning (this scenario) differ from column pruning (Scenario 2)?

**Options:**
- They are the same mechanism with two different names
- Partition pruning skips whole folders based on filter values matching folder names; column pruning skips individual columns within a file
- Partition pruning only works on Parquet; column pruning only works on Delta
- Partition pruning happens at query time; column pruning happens at write time

**Correct Options:**
- Partition pruning skips whole folders based on filter values matching folder names; column pruning skips individual columns within a file

**Solution:**
Column pruning (Scenario 2) operates *within* a file — Parquet's columnar layout lets Spark read only the columns a query needs. Partition pruning operates *above* the files entirely, at the folder-listing stage — Spark looks at folder names like `Year=2024/Month=6/` and skips folders that can't match the filter, before ever opening a single file inside them.

**Tags**
- data-storage (skill)

---

## Input 18

**Type:** Choice

**Question:** Why is a high-cardinality column like `CustomerID` a poor choice for `partitionBy()`?

**Options:**
- High-cardinality columns can't be used in filters
- It would create one folder per distinct value — potentially thousands of tiny folders, recreating the small-files problem
- Partitioning only works on numeric columns
- It would make queries run faster with no downside

**Correct Options:**
- It would create one folder per distinct value — potentially thousands of tiny folders, recreating the small-files problem

**Solution:**
Partitioning should be reserved for columns with a small number of distinct values (dozens, not thousands) — `Year`/`Month` is the classic case. A high-cardinality column like `CustomerID` would create one folder per customer, which is exactly the many-tiny-files problem you'll create on purpose in Scenario 4. Clustering (Scenario 6) is the right tool for high-cardinality filter columns instead.

**Tags**
- data-storage (skill)

---

## Scenario 4 — File Sizing: The Small-Files Problem

**Overview:** This hands-on lab continues using the same 5,000,000-row retail sales dataset. Too many small files is one of the most common real-world Spark performance killers — every file Spark opens carries fixed overhead (listing it, opening it, scheduling a task for it), and when data is spread across thousands of tiny files instead of a sensible number of larger ones, that per-file overhead can dominate the actual work being done. Databricks generally recommends roughly 128MB–1GB per file. In this scenario you will deliberately create the small-files problem, measure its cost, then fix it with `OPTIMIZE`.

**Outcome:** A table first written as ~200 small files, then compacted into far fewer, appropriately-sized files, with your own before/after query timing.

---

## Input 19

**Type:** Text

### Create the small-files problem on purpose

```python
many_small_path = f"{CATALOG}.{LAB_SCHEMA}.sales_many_small_files"

# repartition(200) spreads the data across 200 in-memory partitions before
# writing, so Delta writes roughly one small file per partition.
sales_df.repartition(200).write.mode("overwrite").saveAsTable(many_small_path)

# File count comes straight from Delta's own table metadata.
file_count = spark.sql(f"DESCRIBE DETAIL {many_small_path}").collect()[0]["numFiles"]
print(f"Files written: {file_count}")
```

---

## Input 20

**Type:** Choice

**Question:** A real, full run of this lab wrote `sales_delta`'s data via `repartition(200)` and confirmed the resulting file count via `DESCRIBE DETAIL`'s `numFiles` field. Given the dataset is ~976 MB total, roughly how large would each of the 200 files be on average, and how does that compare to the 128MB–1GB per-file guideline mentioned in this lab?

**Options:**
- ~5 MB each — far below the recommended range
- ~128 MB each — right at the low end of the recommended range
- ~500 MB each — comfortably within the recommended range
- ~1 GB each — right at the high end of the recommended range

**Correct Options:**
- ~5 MB each — far below the recommended range

**Solution:**
976 MB ÷ 200 files ≈ 4.9 MB per file — dramatically below the 128MB–1GB sweet spot. That's the small-files problem made concrete: 200 tiny files means 200 separate rounds of per-file overhead (listing, opening, scheduling a task) for the same amount of data a handful of properly-sized files would hold.

**Tags**
- data-storage (skill)

---

## Input 21

**Type:** Text

### Measure a query against the many-small-files table, then compact it

```python
start = time.time()
spark.table(many_small_path).groupBy("Category").sum("Sales").collect()
many_small_time = time.time() - start
print(f"Query time against {file_count} small files: {many_small_time:.2f}s")
```

```python
# OPTIMIZE rewrites the table's small files into a smaller number of
# appropriately-sized ones. Fallback if OPTIMIZE isn't available on your
# workspace: sales_df.repartition(8).write.mode("overwrite").saveAsTable(...)
try:
    spark.sql(f"OPTIMIZE {many_small_path}")
except Exception as e:
    print(f"OPTIMIZE not available here ({e}); falling back to a manual repartition+rewrite.")
    sales_df.repartition(8).write.mode("overwrite").saveAsTable(many_small_path)

# File count after compaction, again from Delta's own metadata.
file_count_after = spark.sql(f"DESCRIBE DETAIL {many_small_path}").collect()[0]["numFiles"]

start = time.time()
spark.table(many_small_path).groupBy("Category").sum("Sales").collect()
compacted_time = time.time() - start
print(f"Files after compaction: {file_count_after}, query time: {compacted_time:.2f}s")
```

>[!IMPORTANT]
>A real, full run of this lab produced: 200 files / 6.43s before `OPTIMIZE`, and 3 files / 1.34s after — roughly a 4.8x speedup from compacting the same data into far fewer files.

---

## Input 22

**Type:** Choice

**Question:** A real, full run of this lab measured the same `groupBy("Category").sum("Sales")` query at 6.43s against 200 small files, and 1.34s against 3 files after `OPTIMIZE` — the exact same underlying rows either way. What does this comparison demonstrate?

**Options:**
- OPTIMIZE deleted some of the data, making the query artificially faster
- Per-file overhead (listing, opening, scheduling a task) was being paid 200 separate times before compaction, and only 3 times after — even though the actual data volume never changed
- The 200-file version was corrupted and had to be re-read
- Query speed is unrelated to file count in Delta tables

**Correct Options:**
- Per-file overhead (listing, opening, scheduling a task) was being paid 200 separate times before compaction, and only 3 times after — even though the actual data volume never changed

**Solution:**
Both runs process the same 5,000,000 rows. What changed is how many times Spark pays the fixed cost of listing, opening, and scheduling a task for a file — 200 times before `OPTIMIZE`, 3 times after. At roughly 5 MB per file (Input 20), that per-file overhead was a large fraction of the total time; compacting into 3 appropriately-sized files cut it down to almost nothing, producing the observed ~4.8x speedup.

**Tags**
- data-storage (skill)

---

## Input 23

**Type:** Choice

**Question:** Why does a query against 200 small files run slower than the identical query against a handful of appropriately-sized files, given that both contain the exact same rows?

**Options:**
- Small files always contain corrupted data
- Each file carries fixed per-file overhead (listing, opening, scheduling a task) — with 200 files, that overhead is paid 200 separate times instead of a handful
- Spark cannot read more than one file at a time
- Small files are always stored on slower disks

**Correct Options:**
- Each file carries fixed per-file overhead (listing, opening, scheduling a task) — with 200 files, that overhead is paid 200 separate times instead of a handful

**Solution:**
The actual data volume is identical either way — what changes is how many times Spark pays the fixed cost of listing, opening, and scheduling a task for a file. When that overhead is spread across 200 small files instead of a handful of properly-sized ones, it can dominate the total time spent, even though the real computation work is unchanged.

**Tags**
- data-storage (skill)

---

## Scenario 5 — Caching

**Overview:** This hands-on lab continues using the same 5,000,000-row retail sales dataset, now as the Delta table you wrote earlier. Spark is lazy — a DataFrame is just a plan until an action like `.count()` or `.collect()` forces it to run, and normally every action re-executes the plan from scratch, including re-reading the source data. `.cache()` tells Spark to keep the first computed result in memory so later actions against the same DataFrame reuse it instead of recomputing everything.

**Outcome:** Your own measured timing showing a second run of the same query against a cached DataFrame running faster than the first, cold run.

---

## Input 24

**Type:** Text

### Cache a DataFrame and time the first (cold) run

```python
delta_df = spark.table(f"{CATALOG}.{LAB_SCHEMA}.sales_delta")

# .cache() only marks the DataFrame for caching — nothing is materialized
# until the first action runs.
delta_df.cache()

start = time.time()
first_result = delta_df.groupBy("Category").sum("Sales").collect()
first_run_time = time.time() - start
print(f"First run (cold, populates cache): {first_run_time:.2f}s")
```

---

## Input 25

**Type:** Text

### Time the second (cached) run

```python
start = time.time()
second_result = delta_df.groupBy("Category").sum("Sales").collect()
second_run_time = time.time() - start
print(f"Second run (from cache): {second_run_time:.2f}s")

delta_df.unpersist()  # good hygiene — free the cached memory once you're done with it
```

>[!IMPORTANT]
>A real, full run of this lab produced a first (cold) run of 24.07s and a second (cached) run of 0.57s — a 42.0x speedup.

---

## Input 26

**Type:** Choice

**Question:** A real, full run of this lab measured the first (cold) run of `delta_df.groupBy("Category").sum("Sales").collect()` at 24.07s, and the second run (same DataFrame, same query) at 0.57s. What does that 42x speedup demonstrate?

**Options:**
- The second query used a different, smaller dataset
- The first run both computed the result and populated the in-memory cache; the second run reused that cached copy instead of re-reading from storage
- `.cache()` compresses the data, making every future query faster regardless of caching
- Delta tables are always faster on the second query, with or without `.cache()`

**Correct Options:**
- The first run both computed the result and populated the in-memory cache; the second run reused that cached copy instead of re-reading from storage

**Solution:**
`.cache()` alone doesn't materialize anything — the first action (`.collect()`) is what actually triggers the read from storage, and because `.cache()` was called beforehand, Spark also stores that result in cluster memory as a side effect. The second `.collect()` reuses the in-memory copy instead of touching storage again, which is why it finished roughly 42x faster in this real run.

**Tags**
- data-storage (skill)

---

## Input 27

**Type:** Choice

**Question:** When is caching a DataFrame actually worth doing?

**Options:**
- Always — cache every DataFrame you create, just in case
- Only when the same DataFrame will be reused (queried) multiple times in the same session or job
- Only for DataFrames smaller than 1MB
- Never, on a shared cluster

**Correct Options:**
- Only when the same DataFrame will be reused (queried) multiple times in the same session or job

**Solution:**
Caching is valuable specifically when the same DataFrame gets queried more than once — a shared dimension table joined against several fact tables, for example. Caching something you only touch once adds overhead for zero benefit, and on a memory-constrained cluster it can even evict something more useful that was already cached.

**Tags**
- data-storage (skill)
- approach (skill)

---

## Scenario 6 — Clustering with Z-ORDER

**Overview:** This hands-on lab continues using the same 5,000,000-row retail sales dataset. Partitioning (Scenario 3) physically splits data into folders and should only be used on low-cardinality columns. Clustering — via `ZORDER`, or Liquid Clustering on newer Databricks runtimes — doesn't create folders at all; it co-locates rows with similar values in the clustered column physically near each other *within* the existing files, so Delta's file-level statistics can skip whole files for a filter on that column, without exploding the folder count the way partitioning by a high-cardinality column would.

**Outcome:** Your own before/after timing for a `Category` filter, measured before and after running `ZORDER BY (Category)` on `sales_delta`, plus an honest read on what one timing comparison can and can't prove.

---

## Input 28

**Type:** Text

### Baseline: filter on Category before clustering

```python
start = time.time()
before_count = spark.table(f"{CATALOG}.{LAB_SCHEMA}.sales_delta").filter("Category = 'Electronics'").count()
before_time = time.time() - start
print(f"Before ZORDER — filter on Category: {before_count:,} rows in {before_time:.2f}s")
```

---

## Input 29

**Type:** Text

### Run ZORDER, then re-measure the same filter

```python
# ZORDER BY co-locates rows with similar Category values within files.
# If your workspace uses Liquid Clustering instead, the equivalent is:
#   ALTER TABLE ... CLUSTER BY (Category)
try:
    spark.sql(f"OPTIMIZE {CATALOG}.{LAB_SCHEMA}.sales_delta ZORDER BY (Category)")
except Exception as e:
    print(f"ZORDER not available here ({e}) — check whether Liquid Clustering is supported on your DBR/UC setup instead.")

start = time.time()
after_count = spark.table(f"{CATALOG}.{LAB_SCHEMA}.sales_delta").filter("Category = 'Electronics'").count()
after_time = time.time() - start
print(f"After ZORDER — filter on Category: {after_count:,} rows in {after_time:.2f}s")
```

>[!IMPORTANT]
>A real, full run of this lab produced another counter-intuitive result: before `ZORDER BY (Category)`, the filter returned 625,230 rows in 1.09s; after `ZORDER`, the same filter returned the same 625,230 rows in 1.15s — very slightly *slower*, not faster. `OPTIMIZE ... ZORDER BY` did complete successfully (confirmed in `DESCRIBE HISTORY`), so this isn't a sign clustering failed — it's a sign that one wall-clock comparison, on one run, can be dominated by noise (cluster/JVM warm-up state, prior caching, a single sample) even when the underlying file-skipping mechanism is real. Input 31 asks you to reason through this.

---

## Input 30

**Type:** Short Answer

**Question:** In your own words, what does "file-level data skipping" mean for `ZORDER BY (Category)`, and how is it different from the folder-level partition pruning you proved in Scenario 3? What would you check in `DESCRIBE HISTORY` or the Spark UI — rather than the stopwatch alone — to confirm `ZORDER` actually changed how files are laid out?

**Template:** null

**Tags**
- data-storage (skill)

---

## Input 31

**Type:** Choice

**Question:** A real, full run of this lab found the `Category = 'Electronics'` filter was *not* faster after `ZORDER BY (Category)` (1.15s after vs. 1.09s before), even though the `OPTIMIZE ... ZORDER BY` operation completed successfully. What is the most defensible conclusion?

**Options:**
- ZORDER doesn't actually work and shouldn't be used in production
- A single wall-clock timing comparison isn't sufficient proof either way — confirming ZORDER's effect requires checking DESCRIBE HISTORY (did the operation run?) and Spark UI file-skipping stats (were fewer files actually scanned?), not just one stopwatch reading
- The filter query must have had a bug, since ZORDER always makes filters faster
- ZORDER only works on partitioned tables, and this table wasn't partitioned by Category

**Correct Options:**
- A single wall-clock timing comparison isn't sufficient proof either way — confirming ZORDER's effect requires checking DESCRIBE HISTORY (did the operation run?) and Spark UI file-skipping stats (were fewer files actually scanned?), not just one stopwatch reading

**Solution:**
`ZORDER`'s benefit is real and well-documented, but a single before/after timing pair on one run is a noisy way to observe it — cluster warm-up state, prior caching, and normal timing variance can all mask or exaggerate the effect, especially when the "before" state already had a fast enough filter that there wasn't much headroom left to improve. The trustworthy way to confirm `ZORDER` did something is structural, not timing-based: `DESCRIBE HISTORY` showing the `OPTIMIZE ... ZORDER BY` operation actually ran, and the Spark UI showing fewer files scanned for the filter afterward (data skipping made visible as a metric, the same way Scenario 3 treated `.explain()`'s `PartitionFilters` as the real proof rather than the stopwatch).

**Tags**
- data-storage (skill)
- approach (skill)

---

## Input 32

**Type:** Choice

**Question:** A Gold fact table is frequently filtered by both a date range and a specific, high-cardinality `CustomerID`. What is the recommended combination of storage levers for this table?

**Options:**
- Partition by `CustomerID` only
- Partition by date (`Year`/`Month`) and Z-ORDER/cluster by `CustomerID`
- Z-ORDER by date and partition by `CustomerID`
- Use neither partitioning nor clustering, since caching alone is enough

**Correct Options:**
- Partition by date (`Year`/`Month`) and Z-ORDER/cluster by `CustomerID`

**Solution:**
Date columns are low-cardinality and always filtered — a natural partition column. `CustomerID` is high-cardinality, which would create a small-files problem if partitioned on directly, but Z-ORDER/clustering co-locates rows for the same customer within files without exploding the folder count. Real Gold tables commonly combine both: partition by date, cluster by a high-cardinality business key.

**Tags**
- data-storage (skill)

---

## Scenario 7 — Delta Lake Features: UPDATE, DELETE, MERGE, Schema Evolution, Time Travel

**Overview:** This hands-on lab continues using the `sales_delta` table built earlier from the same 5,000,000-row retail sales dataset. Everything so far has used the *storage* half of Delta — Parquet plus partitioning/clustering. This scenario covers the *transaction-log* half: `UPDATE`, `DELETE`, `MERGE` (upsert), schema evolution, and time travel — features that only exist because Delta records every change as a versioned, atomic commit in `_delta_log/`. None of these are possible on plain Parquet.

**Outcome:** Your `sales_delta` table updated in place, a `DELETE` run against it, one row upserted via `MERGE`, a new column added through schema evolution, and a time-travel query proving you can reconstruct the table exactly as it looked at version 0.

---

## Input 33

**Type:** Text

### UPDATE — change existing rows in place

```python
spark.sql(f"""
    UPDATE {CATALOG}.{LAB_SCHEMA}.sales_delta
    SET OrderPriority = 'Critical'
    WHERE OrderPriority = 'High' AND PaymentMethod = 'Cash on Delivery'
""")
```

### DELETE — remove rows

```python
before_delete = spark.table(f"{CATALOG}.{LAB_SCHEMA}.sales_delta").count()

spark.sql(f"""
    DELETE FROM {CATALOG}.{LAB_SCHEMA}.sales_delta
    WHERE Quantity <= 0
""")

after_delete = spark.table(f"{CATALOG}.{LAB_SCHEMA}.sales_delta").count()
print(f"Rows before: {before_delete:,}   Rows after: {after_delete:,}   Deleted: {before_delete - after_delete:,}")
```

>[!IMPORTANT]
>A real, full run of this lab showed 5,000,000 rows before and 5,000,000 rows after — 0 rows deleted. The synthetic generator for this dataset simply never produced a `Quantity <= 0` row.

---

## Input 34

**Type:** Choice

**Question:** A real, full run of this lab's `DELETE FROM sales_delta WHERE Quantity <= 0` removed 0 rows — the row count before and after was identical (5,000,000). Is that a sign the `DELETE` statement failed?

**Options:**
- Yes — a DELETE that removes 0 rows always indicates a bug in the WHERE clause
- No — it's an expected possible outcome if the source data genuinely has no rows matching the condition, which is plausible for a synthetic generator that never produced an invalid Quantity
- Yes — DELETE statements in Delta always remove at least one row if the table is not empty
- No — but only because DELETE silently ignores WHERE clauses on numeric columns

**Correct Options:**
- No — it's an expected possible outcome if the source data genuinely has no rows matching the condition, which is plausible for a synthetic generator that never produced an invalid Quantity

**Solution:**
A `DELETE` with a correct, well-formed `WHERE` clause that matches zero rows is not an error — it's Delta correctly reporting that no rows satisfied the condition. Real production Bronze/Silver data can absolutely contain 0 rows for a given data-quality check on a given day; this dataset's generator apparently never produced a `Quantity <= 0` row at all, so 0 deletions is the honest, correct result here.

**Tags**
- data-storage (skill)

---

## Input 35

**Type:** Text

### MERGE — upsert (insert new rows, update matching existing ones) atomically

```python
from pyspark.sql import Row

sample_existing_id = spark.table(f"{CATALOG}.{LAB_SCHEMA}.sales_delta").select("OrderID").first()["OrderID"]

incoming_batch = spark.createDataFrame([
    Row(OrderID="ORD-99999999", CustomerID="CUST-000001", Returned="No"),      # new row
    Row(OrderID=sample_existing_id, CustomerID="CUST-000001", Returned="Yes"), # updates an existing row
])

spark.sql(f"DROP TABLE IF EXISTS {CATALOG}.{LAB_SCHEMA}.incoming_batch")
incoming_batch.write.saveAsTable(f"{CATALOG}.{LAB_SCHEMA}.incoming_batch")

spark.sql(f"""
    MERGE INTO {CATALOG}.{LAB_SCHEMA}.sales_delta AS target
    USING {CATALOG}.{LAB_SCHEMA}.incoming_batch AS source
    ON target.OrderID = source.OrderID
    WHEN MATCHED THEN UPDATE SET target.Returned = source.Returned
    WHEN NOT MATCHED THEN INSERT (OrderID, CustomerID, Returned) VALUES (source.OrderID, source.CustomerID, source.Returned)
""")
```

---

## Input 36

**Type:** Choice

**Question:** In the `MERGE` statement above, what determines whether an incoming row triggers `WHEN MATCHED THEN UPDATE` versus `WHEN NOT MATCHED THEN INSERT`?

**Options:**
- The order the rows appear in the source DataFrame
- Whether `target.OrderID = source.OrderID` finds an existing match in the target table
- Whether the row has a `Returned` value
- MERGE always inserts every row regardless of matches

**Correct Options:**
- Whether `target.OrderID = source.OrderID` finds an existing match in the target table

**Solution:**
The `ON` clause is the matching condition. For each incoming row, Delta checks whether a row in the target table already has the same `OrderID`. If it does, `WHEN MATCHED` fires (an update); if not, `WHEN NOT MATCHED` fires (an insert). This is what makes `MERGE` a single atomic upsert instead of two separate operations.

**Tags**
- data-storage (skill)
- data-wrangling / joins (skill)

---

## Input 37

**Type:** Text

### Schema Evolution — add a new column without rewriting the whole table

```python
from pyspark.sql.functions import lit

enriched_df = sales_df.withColumn("LoyaltyTier", lit("Standard"))

enriched_df.write \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable(f"{CATALOG}.{LAB_SCHEMA}.sales_delta")

spark.table(f"{CATALOG}.{LAB_SCHEMA}.sales_delta").printSchema()
```

>[!IMPORTANT]
>This step appends the entire 5,000,000-row `sales_df` again — this time with the new `LoyaltyTier` column — on top of whatever was already in `sales_delta`. Keep that in mind for the row count you'll see in Input 39: this is an `append`, not an `overwrite`.

---

## Input 38

**Type:** Choice

**Question:** What does `.option("mergeSchema", "true")` do when appending a DataFrame with a new column to an existing Delta table?

**Options:**
- It deletes the old column that isn't in the new DataFrame
- It tells Delta this is an intentional schema change, so the new column is accepted instead of the write failing on a schema mismatch
- It merges the values of the new column into an existing column
- It has no effect unless the table is empty

**Correct Options:**
- It tells Delta this is an intentional schema change, so the new column is accepted instead of the write failing on a schema mismatch

**Solution:**
Without `mergeSchema`, Delta rejects a write whose columns don't match the existing table's schema, to protect against accidental structural drift. Setting `mergeSchema=true` explicitly tells Delta "yes, add this new column" — letting a source system add a field like `LoyaltyTier` without your pipeline breaking or needing a manual migration.

**Tags**
- data-storage (skill)

---

## Input 39

**Type:** Text

### Time Travel — query the table as it looked at a previous version

```python
display(spark.sql(f"DESCRIBE HISTORY {CATALOG}.{LAB_SCHEMA}.sales_delta"))
```

```python
original_version = spark.sql(f"SELECT COUNT(*) AS n FROM {CATALOG}.{LAB_SCHEMA}.sales_delta VERSION AS OF 0").collect()[0]["n"]
current_version   = spark.table(f"{CATALOG}.{LAB_SCHEMA}.sales_delta").count()

print(f"Version 0 (original write) row count : {original_version:,}")
print(f"Current version row count             : {current_version:,}")
```

>[!IMPORTANT]
>A real, full run of this lab produced `Version 0 (original write) row count: 5,000,000` and `Current version row count: 10,000,001`. Input 40 asks you to reason through why the current count is roughly double, not just a few rows higher.

---

## Input 40

**Type:** Choice

**Question:** A real, full run of this lab showed `VERSION AS OF 0` at 5,000,000 rows, and the current version at 10,000,001 rows — roughly *double*, not just a few rows more. Given this scenario's steps (`UPDATE`, `DELETE` with 0 rows removed, `MERGE` with 1 insert + 1 update, then schema evolution), what best explains that jump?

**Options:**
- `UPDATE` silently duplicated every row it touched
- The schema-evolution step appended the entire original 5,000,000-row dataset again (now with the new `LoyaltyTier` column) using `mode("append")`, and `MERGE` separately inserted 1 more row — together roughly doubling the table plus one
- `DESCRIBE HISTORY` counts every version separately and sums them
- `VERSION AS OF 0` is broken and doesn't reflect the real original row count

**Correct Options:**
- The schema-evolution step appended the entire original 5,000,000-row dataset again (now with the new `LoyaltyTier` column) using `mode("append")`, and `MERGE` separately inserted 1 more row — together roughly doubling the table plus one

**Solution:**
`UPDATE` and `DELETE` change or remove existing rows in place — they don't change the total row count on their own (and this run's `DELETE` removed 0 rows anyway). The real driver here is schema evolution's `enriched_df.write.mode("append")` — that appends the *entire* 5,000,000-row `sales_df` again, now carrying the new `LoyaltyTier` column, on top of whatever was already there. Combined with `MERGE`'s 1 newly inserted row (`ORD-99999999`), 5,000,000 (original) + 5,000,000 (appended) + 1 (merged insert) = 10,000,001 — exactly what this run measured.

**Tags**
- data-storage (skill)

---

## Input 41

**Type:** Choice

**Question:** Why is `VERSION AS OF <n>` possible on a Delta table but not on a plain folder of Parquet files?

**Options:**
- Parquet files are always deleted after being read once
- Delta's `_delta_log/` records every write as an immutable, numbered commit, so any earlier version can be reconstructed by replaying log entries up to that point
- VERSION AS OF actually works on plain Parquet too, just more slowly
- Delta stores a full duplicate copy of the table for every version

**Correct Options:**
- Delta's `_delta_log/` records every write as an immutable, numbered commit, so any earlier version can be reconstructed by replaying log entries up to that point

**Solution:**
Every Delta write — regardless of which statement caused it (a plain write, `UPDATE`, `DELETE`, `MERGE`, or a schema change) — is recorded as a new, immutable entry in `_delta_log/`. `VERSION AS OF` reconstructs the table exactly as it looked at a given log entry by replaying only the entries up to that point. Plain Parquet has no such log, so there is no earlier state to reconstruct.

**Tags**
- data-storage (skill)

---

## Scenario 8 — Final Challenge: Your Own Partitioning Strategy

**Overview:** This is the closing, unassisted challenge for this hands-on lab, using the same 5,000,000-row retail sales dataset you have worked with throughout. No code is given for this one. Having measured partitioning by `Year`/`Month` (Scenario 3) and caching (Scenario 5) with fully worked examples, you will now apply the same two patterns yourself, to a partitioning choice you pick.

**Outcome:** A new Delta table partitioned by a column combination you chose (other than `Year`/`Month`), your own filtered-vs-unfiltered timing comparison, your own caching before/after timing, and a written recommendation on whether you'd use this strategy for a real Gold table.

---

## Input 42

**Type:** Code

**Question:** Pick a partition column combination other than `Year`/`Month` (for example, `Country` alone, or `Country` and `Category` together). Using PySpark, write a new Delta table from `sales_df` partitioned by your chosen column(s), then measure and report the execution time of a realistic business query against it — once with a partition filter on your chosen column(s), and once without one.

**Language:** python

**Snippet:**
```python
# 1. Write sales_df partitioned by your chosen column(s)

# 2. Time a query WITH a filter on your partition column(s)

# 3. Time the same query WITHOUT the filter (full scan)
```

**Solution:**
```python
(sales_df.write
    .mode("overwrite")
    .partitionBy("Country")
    .saveAsTable(f"{CATALOG}.{LAB_SCHEMA}.sales_by_country"))

country_df = spark.table(f"{CATALOG}.{LAB_SCHEMA}.sales_by_country")

start = time.time()
filtered = country_df.filter("Country = 'India'").count()
filtered_time = time.time() - start

start = time.time()
unfiltered = country_df.count()
unfiltered_time = time.time() - start

print(f"WITH filter (Country=India): {filtered:,} rows in {filtered_time:.2f}s")
print(f"WITHOUT filter: {unfiltered:,} rows in {unfiltered_time:.2f}s")
```
`Country` is a reasonable partition choice here: the dataset spans only 6 countries (low cardinality, matching the "tens, not thousands" guideline from Scenario 3), and a per-country filter is a realistic query for a retail business (regional reporting). Your own timings will differ from Scenario 3's Year/Month numbers, and — as Scenario 3's real run showed — an unfiltered count isn't guaranteed to be slower than a filtered one on wall-clock time alone; the pattern that matters is `partitionBy()` plus comparing a filtered count against a full `count()`, the same as Scenario 3.

**Tags**
- data-storage (skill)

---

## Input 43

**Type:** Code

**Question:** Using PySpark, cache a DataFrame from this challenge that you query more than once, and measure the timing difference between the first (cold) run and the second (cached) run — the same pattern as Scenario 5.

**Language:** python

**Snippet:**
```python
# cache a DataFrame, time the first run, time the second run, then unpersist
```

**Solution:**
```python
country_df.cache()

start = time.time()
first = country_df.filter("Country = 'India'").count()
first_time = time.time() - start

start = time.time()
second = country_df.filter("Country = 'India'").count()
second_time = time.time() - start

print(f"First run (cold): {first_time:.2f}s")
print(f"Second run (cached): {second_time:.2f}s")

country_df.unpersist()
```
This is the identical `.cache()` → first-run → second-run → `.unpersist()` pattern from Scenario 5, applied to the partitioned DataFrame from Input 42 instead of `sales_delta` — caching benefits any DataFrame that gets queried more than once, not just the one specific table used earlier in the lab. Scenario 5's real run showed a 42x speedup from this exact pattern; your own should show a clear speedup too, even if the exact multiple differs.

**Tags**
- data-storage (skill)

---

## Input 44

**Type:** Short Answer

**Question:** Compare your results from this challenge (partition-filter timing, caching speedup) against this lab's Scenario 3 and Scenario 5 numbers. Were they better, worse, or about the same? Would you recommend your chosen partition column combination for a real Gold table querying this dataset — why or why not?

**Template:** null

**Tags**
- data-storage (skill)
- approach (skill)

---

## Input 45

**Type:** File Upload

**Question:** Upload your completed Databricks notebook (.ipynb), including your Final Challenge code and filled-in observations.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, JUPYTER_NOTEBOOK

**Tags**
- databricks (tool)
