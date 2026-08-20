---
name: Day 9 HOL 1 — Implement Watermark-Based Incremental Load (Control Table)
content_type: Scenario
overview: GlobalMart's real orders/order_items incremental load is already handled by a managed Lakeflow Connect pipeline, which tracks its own watermark internally — a black box you never see inside. This hands-on has you build that exact same cursor-based incremental loading idea by hand, against a small practice table you fully control, using your own control table to track a watermark value, an incremental read filtered against it, and a MERGE-based upsert into the target — so the mechanism stops being magic. You will prove it's genuinely incremental across multiple runs, then prove its real blind spot: it cannot detect a hard delete.
learning_objectives:
  - Build a control table that tracks a watermark value per source table
  - Implement an incremental read using a cursor-column filter against a stored watermark
  - Advance the watermark only after a successful downstream write, and explain why the order matters
  - Prove, with your own test data, that a new run loads only genuinely new or changed rows
  - Demonstrate that watermark-based incremental loading cannot detect hard deletes, and explain why
prerequisites:
  - Completed Day 9 ILT 2 — Watermark-Based Incremental Loading
  - A Databricks workspace with a schema you can create tables in
duration: 60 minutes
level: Intermediate
industries:
  - e-commerce
tags:
  - databricks (tool)
  - spark (tool)
  - sql (tool)
  - data-storage (skill)
---

---

## Scenario 1 — Simulate an Upstream Source With a Watermark Column

**Overview:** GlobalMart's real `orders`/`order_items` incremental load is already handled entirely by the Lakeflow-Connect-managed `orders_data_ingestion_cdc` pipeline (built Day 2) — a managed connector that tracks its own cursor internally, with nobody at GlobalMart hand-writing a control table for it. This lab has you build that same general-purpose technique by hand instead, against a small Delta table you fully control, standing in for "a Postgres table with an `updated_at` trigger." Building it yourself once is what makes the managed pipeline's behavior make sense, instead of feeling like magic — and it's exactly the pattern you'd reach for on any source that isn't sitting behind a managed CDC connector.

**Outcome:** A small Delta table, `practice_upstream_orders`, seeded with 5 starter rows all sharing the same `updated_at` — the "initial load" state, analogous to GlobalMart's real orders table before any incremental runs happened.

---

## Input 1

**Type:** Text

### Setup

>[!IMPORTANT]
>This lab uses a practice schema, not the shared `gbmart` catalog — replace `YOUR_SCHEMA` below with something unique to you. You are not touching any shared GlobalMart table in this lab. Everything you build here lives in your own `main.YOUR_SCHEMA` practice schema.

```python
# ─── Configuration — edit YOUR_SCHEMA before running anything else ────────────
YOUR_SCHEMA = "YOUR_SCHEMA"          # e.g. "virinchy_practice" — your own sandbox schema
CATALOG     = "main"                 # using main.YOUR_SCHEMA keeps this off the shared gbmart catalog entirely

SOURCE_TABLE  = f"{CATALOG}.{YOUR_SCHEMA}.practice_upstream_orders"
TARGET_TABLE  = f"{CATALOG}.{YOUR_SCHEMA}.practice_incremental_orders"
CONTROL_TABLE = f"{CATALOG}.{YOUR_SCHEMA}.practice_ingestion_control"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{YOUR_SCHEMA}")
```

---

## Input 2

**Type:** Text

### Seed the upstream source

```python
from pyspark.sql.functions import *

spark.sql(f"DROP TABLE IF EXISTS {SOURCE_TABLE}")

# 5 starter rows, all with the same updated_at — this is the "initial load" state.
initial_df = spark.createDataFrame(
    [(f"ORD-{i:03d}", 100.0 * i, "2026-06-01T09:00:00") for i in range(1, 6)],
    ["order_id", "amount", "updated_at"]
).withColumn("updated_at", to_timestamp("updated_at"))

initial_df.write.format("delta").mode("overwrite").saveAsTable(SOURCE_TABLE)
print(f"Seeded {SOURCE_TABLE} with 5 rows")
spark.table(SOURCE_TABLE).orderBy("order_id").show()
```

---

## Input 3

**Type:** Choice

**Question:** Why does this lab build a watermark loader by hand, when GlobalMart's real `orders`/`order_items` incremental load is already handled by a managed Lakeflow Connect pipeline?

**Options:**
- Because Lakeflow Connect doesn't actually support incremental loading
- Because this is the general-purpose technique you'd reach for on any source that isn't sitting behind a managed CDC connector — a vendor API, an unwired internal system, a one-off migration — and building it once makes the managed version's behavior make sense instead of feeling like magic
- Because GlobalMart is planning to replace Lakeflow Connect with this exact hand-built loader
- Because control tables are required for all Delta tables

**Correct Options:**
- Because this is the general-purpose technique you'd reach for on any source that isn't sitting behind a managed CDC connector — a vendor API, an unwired internal system, a one-off migration — and building it once makes the managed version's behavior make sense instead of feeling like magic

**Solution:**
GlobalMart's real pipeline is a black box — Lakeflow Connect tracks its own cursor internally, and nobody hand-writes a control table for it. But the underlying technique is a real, widely-used industry pattern for any source that doesn't have a managed CDC connector available. Building it by hand once is like practicing long division: a calculator does it for you every day, but doing it manually once is what makes the calculator's answer make sense.

**Tags**
- approach (skill)

---

## Scenario 2 — Build the Control Table and Run the Initial Load

**Overview:** With `practice_upstream_orders` seeded (Scenario 1), the next piece is the control table itself — it holds exactly one row per source table, recording the highest `updated_at` value successfully loaded so far. Before any run has happened, that value is set to a very old timestamp (the epoch), meaning "everything is new." You will then run the core watermark-loading function for the first time, expecting all 5 starter rows to come through.

**Outcome:** A control table created and seeded at epoch, and a first run of `run_incremental_load()` that pulls all 5 starter rows into a new target table, since nothing has been loaded yet.

---

## Input 4

**Type:** Text

### Create and seed the control table

```python
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CONTROL_TABLE} (
        source_table          STRING,
        last_watermark_value  TIMESTAMP,
        last_run_at           TIMESTAMP
    ) USING DELTA
""")

existing = spark.sql(f"SELECT * FROM {CONTROL_TABLE} WHERE source_table = 'practice_upstream_orders'")
if existing.count() == 0:
    spark.sql(f"""
        INSERT INTO {CONTROL_TABLE}
        VALUES ('practice_upstream_orders', TIMESTAMP('1970-01-01 00:00:00'), NULL)
    """)
    print("Control row initialized at epoch — next read will pull everything.")
```

---

## Input 5

**Type:** Text

### The core watermark-loading pattern

```python
def run_incremental_load():
    """
    The core watermark pattern, in one function:
      1. Read the current watermark from the control table.
      2. Pull only source rows newer than that watermark.
      3. If there's anything to load, MERGE it into the target (upsert on order_id).
      4. Only on success, advance the watermark to the max updated_at just loaded.
    Steps 3 and 4 happen in that order deliberately — advancing the watermark
    before confirming the write would lose data on a failed run.
    """
    from delta.tables import DeltaTable

    last_watermark = spark.sql(
        f"SELECT last_watermark_value FROM {CONTROL_TABLE} WHERE source_table = 'practice_upstream_orders'"
    ).collect()[0]["last_watermark_value"]

    incremental_df = spark.table(SOURCE_TABLE).filter(col("updated_at") > lit(last_watermark))
    new_row_count = incremental_df.count()

    if new_row_count == 0:
        print("Nothing new — skipping write and watermark update.")
        return

    if not spark.catalog.tableExists(TARGET_TABLE):
        incremental_df.write.format("delta").mode("overwrite").saveAsTable(TARGET_TABLE)
    else:
        target = DeltaTable.forName(spark, TARGET_TABLE)
        (target.alias("tgt")
            .merge(incremental_df.alias("src"), "tgt.order_id = src.order_id")
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute())

    new_watermark = incremental_df.agg(spark_max("updated_at")).collect()[0][0]
    spark.sql(f"""
        UPDATE {CONTROL_TABLE}
        SET last_watermark_value = TIMESTAMP('{new_watermark}'), last_run_at = current_timestamp()
        WHERE source_table = 'practice_upstream_orders'
    """)
    print(f"Watermark advanced to: {new_watermark}")

# Run 1 — the initial load. Expect all 5 rows to come through (watermark started at epoch).
run_incremental_load()
```

---

## Input 6

**Type:** Choice

**Question:** Why does `run_incremental_load()` advance the watermark only *after* the write succeeds (Step 4), rather than updating it immediately after reading it in Step 1?

**Options:**
- It makes no difference — the order is arbitrary
- Advancing the watermark before confirming the write would permanently lose those rows if the write step failed partway through
- Step 1 cannot access the control table before Step 3 runs
- Databricks requires watermark updates to happen last for performance reasons

**Correct Options:**
- Advancing the watermark before confirming the write would permanently lose those rows if the write step failed partway through

**Solution:**
If the watermark were advanced right after being read, and the write in Step 3 then failed for any reason, the next run would start from the new (already-advanced) watermark — meaning the rows that failed to write would never be re-attempted and would be silently lost forever. Advancing the watermark only after a successful write guarantees a failed run can always be safely retried from where it actually left off.

**Tags**
- approach (skill)

---

## Input 7

**Type:** Code

**Question:** Separately from the full `run_incremental_load()` function, using PySpark, write a check that reads the current watermark from the control table for `practice_upstream_orders`, then reports how many rows in the source table are newer than that watermark — without writing anything to the target table.

**Language:** python

**Snippet:**
```python
# read the current watermark, then count source rows newer than it
```

**Solution:**
```python
last_watermark = spark.sql(
    f"SELECT last_watermark_value FROM {CONTROL_TABLE} WHERE source_table = 'practice_upstream_orders'"
).collect()[0]["last_watermark_value"]

new_row_count = spark.table(SOURCE_TABLE).filter(col("updated_at") > lit(last_watermark)).count()
print(f"Watermark: {last_watermark}, rows newer than watermark: {new_row_count}")
```
This isolates the "detect what's new" half of the pattern (Steps 1-2 of `run_incremental_load()`) from the "write and advance" half (Steps 3-4). Run immediately after Run 1 completes, this should report 0 rows newer than the watermark — the same result Scenario 3 confirms directly by re-running the full loader.

**Tags**
- spark (tool)
- data-wrangling / filter (skill)

---

## Scenario 3 — Prove Incremental Behavior: Run Again With No Changes

**Overview:** `practice_upstream_orders` and `practice_incremental_orders` both now hold the same 5 rows from Scenario 2's initial load, with the control table's watermark advanced to match. Running the exact same `run_incremental_load()` function again right now, with nothing changed upstream, is the real proof that this loader is genuinely incremental — not something that just happens to work correctly the first time.

**Outcome:** A second run that loads exactly 0 rows, confirming the loader only pulls rows that are actually new relative to the stored watermark.

---

## Input 8

**Type:** Text

### Run again with no upstream changes

```python
# Run 2 — nothing changed upstream. Expect "Rows newer than watermark: 0" and no write.
run_incremental_load()
```

---

## Input 9

**Type:** Choice

**Question:** Run 2 loads 0 rows even though `practice_upstream_orders` still physically contains 5 rows. What does that prove about this loader?

**Options:**
- That the source table was accidentally emptied
- That the loader is genuinely incremental — it filters by the stored watermark rather than re-reading and re-writing the entire source table every time
- That the control table is broken
- That Delta tables can only be read once

**Correct Options:**
- That the loader is genuinely incremental — it filters by the stored watermark rather than re-reading and re-writing the entire source table every time

**Solution:**
The source table is unchanged and still has all 5 rows — what's different is that the control table's watermark now equals the `updated_at` of every existing row, so the `updated_at > last_watermark` filter correctly finds nothing new. This is the actual proof of incremental behavior: a full reload would have re-processed all 5 rows again regardless of the watermark.

**Tags**
- approach (skill)

---

## Scenario 4 — Simulate an Upstream Change, Then Load Incrementally

**Overview:** With both runs so far behaving as expected (5 rows loaded, then 0 new), this scenario simulates a realistic upstream change: one existing row's `amount` changes (bumping its `updated_at`, exactly like GlobalMart's real `trg_orders_updated_at` trigger would), and one brand-new row arrives. Running the loader a third time should pick up only these 2 rows — not all 6.

**Outcome:** Exactly 2 rows (1 updated, 1 new) picked up by Run 3, upserted correctly into the target via `MERGE`.

---

## Input 10

**Type:** Text

### Simulate a change, then run the loader

```python
# Simulate: ORD-002's amount changes, and a brand-new ORD-006 arrives.
spark.sql(f"""
    UPDATE {SOURCE_TABLE}
    SET amount = 999.0, updated_at = TIMESTAMP('2026-06-02T10:00:00')
    WHERE order_id = 'ORD-002'
""")

spark.sql(f"""
    INSERT INTO {SOURCE_TABLE} VALUES ('ORD-006', 600.0, TIMESTAMP('2026-06-02T10:05:00'))
""")

# Run 3 — expect "Rows newer than watermark: 2", showing exactly ORD-002 and ORD-006.
run_incremental_load()
```

---

## Input 11

**Type:** Choice

**Question:** After Run 3, how many rows should `practice_incremental_orders` contain in total, and how does the `MERGE` handle `ORD-002` versus `ORD-006`?

**Options:**
- 6 rows total — `ORD-002` matches on `order_id` and is updated in place (`whenMatchedUpdateAll`), `ORD-006` has no match and is inserted (`whenNotMatchedInsertAll`)
- 7 rows total — both `ORD-002` and `ORD-006` are inserted as new rows
- 5 rows total — `ORD-006` is rejected because it wasn't present in the initial load
- 6 rows total, but both are counted as inserts since MERGE cannot update existing rows

**Correct Options:**
- 6 rows total — `ORD-002` matches on `order_id` and is updated in place (`whenMatchedUpdateAll`), `ORD-006` has no match and is inserted (`whenNotMatchedInsertAll`)

**Solution:**
The target already has 5 rows (`ORD-001` through `ORD-005`) from Run 1. `ORD-002` exists in both source and target with the same `order_id`, so the `MERGE`'s `ON tgt.order_id = src.order_id` condition matches it, triggering `whenMatchedUpdateAll` — its `amount` and `updated_at` are updated in place, no new row added. `ORD-006` has no matching row in the target, so `whenNotMatchedInsertAll` inserts it as a genuinely new row. Total: still 6 distinct `order_id`s.

**Tags**
- data-storage (skill)
- approach (skill)

---

## Scenario 5 — Prove the Blind Spot Yourself: Hard Deletes

**Overview:** With the loader proven to correctly pick up both updates and new rows (Scenario 4), this final scenario tests its actual limitation: deleting a row from the upstream source and running the loader again. If watermark-based loading truly can't see deletes, the deleted row should still sit in the target table, undeleted, forever, with no error telling you it's stale — the exact same blind spot GlobalMart's real `orders_data_ingestion_cdc` pipeline has, since cursor-based CDC only detects a row whose `updated_at` changed, and a `DELETE` produces no such row at all.

**Outcome:** Proof that after deleting `ORD-001` from the upstream source and re-running the loader, `ORD-001` remains present in the target table.

---

## Input 12

**Type:** Text

### Delete a row upstream, then run the loader again

```python
spark.sql(f"DELETE FROM {SOURCE_TABLE} WHERE order_id = 'ORD-001'")
print(f"Upstream row count now: {spark.table(SOURCE_TABLE).count()}  (expect 5)")

# Run 4 — expect "Rows newer than watermark: 0". The delete produced no row with a
# newer updated_at, so the loader has no idea anything happened.
run_incremental_load()

still_there = spark.table(TARGET_TABLE).filter("order_id = 'ORD-001'").count()
print(f"ORD-001 still present in {TARGET_TABLE}: {still_there == 1}")
```

---

## Input 13

**Type:** Short Answer

**Question:** After deleting `ORD-001` from the upstream source and running the loader again, does `ORD-001` still appear in `practice_incremental_orders`? Why does watermark-based incremental loading fail to catch this deletion?

**Template:** null

**Tags**
- data-storage (skill)

---

## Input 14

**Type:** Choice

**Question:** Which of the following would actually catch a hard delete that watermark-based incremental loading misses?

**Options:**
- Increasing how frequently the loader polls the source table
- Switching to log-based CDC (or Delta's Change Data Feed), or running a periodic full reconciliation between source and target
- Adding more columns to the control table
- Running the loader on a larger cluster

**Correct Options:**
- Switching to log-based CDC (or Delta's Change Data Feed), or running a periodic full reconciliation between source and target

**Solution:**
Watermark-based loading only ever sees rows whose cursor column changed — a `DELETE` doesn't produce a row with a newer `updated_at`, so no amount of polling frequency or compute helps. Catching deletes requires either a fundamentally different capture mechanism (log-based CDC, which sees the delete operation itself) or a separate, periodic full comparison between source and target to find rows that vanished.

**Tags**
- data-storage (skill)

---

## Input 15

**Type:** File Upload

**Question:** Take a screenshot of your notebook showing Run 4's output and the final confirmation that `ORD-001` is still present in the target table after being deleted upstream. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)
