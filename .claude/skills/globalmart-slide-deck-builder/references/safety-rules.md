# Safety Rules — Each With Real Precedent

These rules exist because this repo teaches real mechanics against a real,
shared Databricks workspace that other cohorts, the instructor, and a
colleague's (sayli's) own account all touch. A slide deck that's technically
correct but shows code that writes to the wrong place, triggers a real job, or
bakes in a credential is worse than useless — a learner could copy exactly
what's on the slide, mid-session, and break class for everyone else, or leak
something it shouldn't. Every rule below has a real, verbatim code snippet
already living in this repo's notebooks — if a `slide-demo` slide shows code,
copy the *pattern* shown here, not something invented fresh.

## 1. Practice schema / `SHALLOW CLONE` for anything write-heavy on a shared table

**Why:** if a MERGE/SCD/CDF/OPTIMIZE demo writes directly to a real shared
`gbmart.*` table, only the *first* person in the whole cohort to run it sees
real behavior — everyone after (including you, rehearsing before class) sees
"0 changed rows" and the exercise looks broken. `SHALLOW CLONE` gives an
independent transaction log over the same real data, so the exercise is
repeatable forever, for every student, every rehearsal. Any demo slide that
shows a MERGE/SCD/CDF/OPTIMIZE snippet should show this setup too (or at least
reference it), not just the interesting MERGE statement in isolation.

**Real precedent — Day 9 HOL 2** (`Day9_5_HOL2_Handling_Incremental_Data_Bronze_Silver.ipynb`):
```python
# ─── Personal practice schema — never write directly to shared gbmart tables ────
PRACTICE_SCHEMA = "main.YOUR_SCHEMA"   # ← replace with a schema you own
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {PRACTICE_SCHEMA}")

BRONZE_PRACTICE = f"{PRACTICE_SCHEMA}.bronze_payments_practice"
SILVER_PRACTICE = f"{PRACTICE_SCHEMA}.silver_payments_practice"

# SHALLOW CLONE: same real data as gbmart.bronze/silver.payments right now, but a
# transaction history that's entirely yours — safe to MERGE into repeatedly.
spark.sql(f"CREATE OR REPLACE TABLE {BRONZE_PRACTICE} SHALLOW CLONE harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.payments")
spark.sql(f"CREATE OR REPLACE TABLE {SILVER_PRACTICE} SHALLOW CLONE harsh_kumar01_npmentorskool_onmicrosoft_com.silver.payments")
spark.sql(f"ALTER TABLE {BRONZE_PRACTICE} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")
```

**Real precedent — Day 10 HOL 1** (`Day10_2_HOL1_SCD_Type2_Dim_Customer_MERGE.ipynb`),
same pattern for a dimension clone, with the markdown explaining *why*:
```
## Setup — Clone Your Own Copy
`SHALLOW CLONE` gives you an independent table (your own transaction log,
your own history) without copying the underlying data files — instant, and
safe to write to.
```
```python
SILVER_TABLE = f"{YOUR_SCHEMA}.silver_customers"
spark.sql(f"CREATE OR REPLACE TABLE {BRONZE_TABLE} SHALLOW CLONE harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.customers")
spark.sql(f"CREATE OR REPLACE TABLE {SILVER_TABLE} SHALLOW CLONE harsh_kumar01_npmentorskool_onmicrosoft_com.silver.customers")
```

Applies to: any HOL centered on MERGE/SCD/CDF/OPTIMIZE against a table other
cohorts also touch. First introduced Day 10, retrofitted into Day 9 HOL 2 and
Day 4 HOL 2, reused for Day 11's DLQ demo and Day 12's masking demo (as a
`main.YOUR_SCHEMA` practice table rather than a clone — see rule 5).

## 2. Never start, trigger, or schedule real job/pipeline/cluster/warehouse compute

**Why:** this repo is a teaching tool, not an operations console. Nothing in
it — including a slide's illustrative code sample — should look like it could
cost money or disrupt a real running system just by being copy-pasted and run
during a demo.

- Jobs/Workflow config shown on a slide is always an **inspectable, clearly-
  commented-as-illustrative Python dict**, constructed and printed — never
  submitted to a real Jobs API.
- Any streaming `.trigger(...)` shown either uses `availableNow=True`
  (terminates on its own) or explicitly calls `.stop()` before the cell
  finishes. A real gap of exactly this kind (a `.start()` with no matching
  `.stop()`) was found and fixed in Day 3's cert-prep notebook during a safety
  audit — that notebook is now the confirmed-fixed example, not a cautionary
  one.
- Day 9 HOL 2 Part 2 only **verifies** the real `orders_data_ingestion_cdc`
  pipeline picked up a change (real precedent below) — it never re-triggers
  it, and neither should any slide that walks through this.
- `VACUUM ... RETAIN 0 HOURS` never appears anywhere in this course (it
  permanently deletes file history) — any VACUUM shown on a slide is
  illustrative/commented-out only.

**Real precedent — Day 9 HOL 2 Part 2**, verification-only against a real
pipeline (`Day9_5_HOL2_...ipynb`):
```python
# Check 3 — Delta history. A new version here, timestamped around when the pipeline
# last ran, confirms the pipeline actually wrote something (vs. finding nothing new).
spark.sql("DESCRIBE HISTORY harsh_kumar01_npmentorskool_onmicrosoft_com.bronze.orders") \
    .select("version", "timestamp", "operation") \
    .orderBy("version", ascending=False) \
    .show(5, truncate=False)
```
No `pipelines.start_update()`, no `jobs.run_now()` anywhere near it — read-only
metadata and plain `SELECT`s only.

**Real precedent — Day 12 ILT 1**, `GRANT`/`REVOKE` shown as illustrative
syntax, never executed (`Day12_1_ILT1_Data_Governance_Unity_Catalog.ipynb`):
```
> The GRANT/REVOKE statements above are illustrative syntax only, shown
> against the practice schema naming pattern — nothing in this notebook
> actually executes a GRANT or REVOKE against anything. The only thing we
> execute against real grants is reading them, next.
```

## 3. Sayli's account — read-only, forever; this skill has no live access at all

**Why:** her workspace was a one-time, read-only export used as an accuracy
reference. Writing to or triggering anything there would be a real breach of
trust with a colleague whose real data this project depends on.

This skill (and every slide it produces) **has zero live access to
sayli's workspace or to the real `gbmart` workspace, period.** If a task
seems to require confirming something live — "did her pipeline change?",
"is this still accurate in her workspace today?" — that is a gap to flag to
the human, not something to fabricate having checked. Never write a slide
caption, comment, or claim implying a live check happened.

## 4. Idempotent by default outside clone-based demos

**Why:** rehearsing a "build" notebook more than once (which will happen —
instructors rehearse, cohorts repeat) should reproduce the same end state,
not duplicate rows or corrupt a shared table. A slide walking through this
build should show the real idempotent pattern, not a simplified `append` that
would misrepresent what the notebook actually does.

**Real precedent — Day 7 HOL 2**, the actual `fact_sales` build
(`Day7_3_HOL2_Build_Gold_Layer_Fact_Sales.ipynb`):
```python
# overwrite mode -- per ILT 1, this is the simple, always-correct strategy
# at GlobalMart's current volume. Incremental MERGE-based refresh replaces
# this in Day 9-10, once you've felt why a full rebuild gets wasteful.
fact_sales_df.write.format("delta").mode("overwrite").saveAsTable("gbmart.gold.fact_sales")
```
Builds that aren't clone-based (Day 4/5 Bronze/Silver builds, this Day 7 Gold
build) use `overwrite` or key-based `MERGE` — never a plain `append` into a
shared table.

## 5. Governance/masking demos never touch real `gbmart` security

**Why:** the instant a row filter or column mask is attached to a real shared
table, every other student's and the instructor's very next query is
filtered/masked too — mid-class, with no warning, and it doesn't expire on
its own (it needs an explicit `DROP` to undo).

**Real precedent — Day 12 ILT 1** (`Day12_1_ILT1_Data_Governance_Unity_Catalog.ipynb`):
```python
# --- Practice schema setup -- isolates this demo from the real gbmart catalog --
# Replace YOUR_SCHEMA with something unique to you if you run this again later
# (e.g. main.governance_lab) -- main.YOUR_SCHEMA as-is is fine for one live demo.
YOUR_SCHEMA = "main.YOUR_SCHEMA"
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {YOUR_SCHEMA}")

PRACTICE_TABLE  = f"{YOUR_SCHEMA}.practice_customers"
ROW_FILTER_FUNC = f"{YOUR_SCHEMA}.us_region_filter"
MASK_FUNC       = f"{YOUR_SCHEMA}.email_mask"
```
Every `ALTER TABLE ... SET ROW FILTER` / `... SET MASK` / `GRANT` / `REVOKE`
that actually *executes* in that notebook targets only this practice table —
the only things run against real `gbmart` are `SHOW GRANTS`, `DESCRIBE
HISTORY`, and plain `SELECT`s (all non-destructive, read-only). A slide
recreating this demo should show the same practice-table framing, not the
real catalog name in the executed statements.

## 6. Never embed a real credential — placeholder + "how to obtain" comment only

**Why:** a real leaked database credential was found in one file in
`reference_materials/reference_data_for_hands_on_docs/*.md` during this project — the cautionary
example that makes this rule concrete, not hypothetical. A slide is exactly
as public as a shared screen in a room full of learners; nothing shown on one
should ever be a real secret.

**Real precedent — Day 1 HOL** (`Day1_5_HOL_PySpark_SparkSQL_ADLS.ipynb`),
the pattern to copy for anything needing a per-learner value:
```python
# ─── Volume Setup ───────────────────────────────────────────────────────────
# HOW TO GET THIS VALUE: Catalog (left sidebar) → your catalog → your schema
# → raw_data volume → the path is shown at the top of the Volume browser.
volume_path = "/Volumes/YOUR_CATALOG/YOUR_SCHEMA/raw_data"   # ← replace with your path
```
Every credential-shaped value (storage keys, connection strings, tokens,
per-learner catalog/schema paths) shown on a slide follows this shape: an
obviously-fake placeholder (`YOUR_CATALOG`, `YOUR_SCHEMA`) plus a comment
telling the reader exactly where to go get their own real value — never a
real key, never even a real-looking fake one that could be mistaken for live.

## After writing: re-open and validate, every time

This is the Day 6 incident lesson (see `00_Instructor_Guide_How_To_Use_This_Bootcamp.html`
Section 7): a background agent once reported success while silently having
overwritten correct content with stale content, and it was only caught by a
direct read of the output — not by any failure signal. Never trust a "done"
report (including your own) without independently re-opening the file. For
this skill that means: run `scripts/validate_html_deck.py <path>` after
writing, and actually look at its output, before telling the user the deck is
ready.
