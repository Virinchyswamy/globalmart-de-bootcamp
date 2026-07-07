# GlobalMart Real Architecture — Ground Truth

This is the real, already-running Databricks environment every pipeline-accurate
slide deck in this course must reflect accurately. It is NOT a toy/simulated dataset built for
teaching — it's a real workspace with real (if training-scale) data, so every
table/column name a slide states must match what's actually there. If you
need a fact that isn't here or in `fact-sales-schema.md`, say so and ask
instead of inventing a plausible-sounding name — a wrong table/column name is
worse than an honest "I don't know this one."

Source: `00_Instructor_Guide_How_To_Use_This_Bootcamp.html` (Sections 4, 5, 7)
and `HOW_TO_USE_THIS_COURSE.html` (Sections 3, 4, 5, 6, 8), cross-checked
directly against `Day7/Day7_3_HOL2_Build_Gold_Layer_Fact_Sales.ipynb` and the
Day 9/10/12 notebooks that write real code against this environment.

## The environment

| Thing | Real value |
|---|---|
| Databricks workspace | `adb-3530457219338656.16.azuredatabricks.net` |
| Unity Catalog | `gbmart` — schemas `bronze`, `silver`, `gold` |
| External location | `gbmart-ext-loc` → `abfss://ecom-gbmart-data@ecomadlsdata.dfs.core.windows.net/raw-data` |
| Storage credential | `ecomprojectscredentials` (keyless, Unity Catalog managed — never a raw storage-account key in any notebook) |

## Exactly 2 ingestion pathways, 7 real Bronze tables — never 4 sources

This is the single fact most likely to drift wrong if you're generating from a
vague memory of "GlobalMart" rather than this doc, because it drifted wrong
*twice already* during this course's real build (once in early drafts, once
again while extending Day 10-12). If you ever see "4 sources" asserted as
architectural fact — anywhere, including in your own draft slide — stop and fix it.

1. **Postgres/Supabase CDC via Lakeflow Connect** — pipeline name
   `orders_data_ingestion_cdc`. Query/cursor-based on `updated_at`, NOT
   log-based WAL — this means it **does not capture hard deletes** (taught
   explicitly in Day 2 as a real limitation, not glossed over). Feeds
   `gbmart.bronze.orders` and `gbmart.bronze.order_items` from source Postgres
   `globalmart.orders`/`order_items`.
2. **ADLS Autoloader** — flat files landing under `raw-data/`, ingested via
   `cloudFiles`. Feeds `gbmart.bronze.customers`, `products`, `address`,
   `payments`, `payment_methods`.

That's **7 real Bronze tables total**: `orders`, `order_items` (CDC) +
`customers`, `products`, `address`, `payments`, `payment_methods` (Autoloader).

**Where "4 sources"/"4" legitimately appears and does NOT mean 4 systems:**
the real calendar itself uses "4" in a couple of session titles — e.g. Day 4's
"Recap: Ingestion Patterns Across All 4 Sources" and Day 4's Hands-on "Build
the Bronze Layer - all 4 sources", and Day 12's deferred hands-on title
"...Verify Lineage (4 Sources)". In every one of these, "4" means **4
Bronze-table-level ingestion tasks/checks**, or is a holdover from the
original spec's name — not 4 distinct source *systems*. If a calendar Module
title says "4" and you're not sure which "4" it means, it's the table-level
one; the source-system count is always 2. When you build a slide deck for a
session whose calendar title contains this "4", correct it explicitly and
visibly on the slide itself, the same way Day 3 ILT 1 and Day 4 ILT 1 do in
their notebooks — don't just silently avoid the word.

**Day 3's REST API + GraphDB/Cypher content is a deliberate side-exploration,
not a third pathway.** It's real, runnable content (useful patterns learners
will meet on other projects), but it lands in a `sandbox/` path and **never
touches `gbmart.bronze`**. Never describe it on a slide as feeding the real
pipeline.

## Casing rule — Bronze vs. Silver

- **Bronze preserves the source's raw casing exactly.** PascalCase from CSV
  headers (e.g. `CustomerID`), and the CDC source's own casing for
  `orders`/`order_items` (e.g. `OrderID`, `CustomerID`, `updated_at`).
- **Silver renames everything to `snake_case`** (e.g. `customer_id`,
  `order_date`). This renaming **is Silver's job** — it never happens in
  Bronze, and Silver never leaves PascalCase behind. If a slide about a Bronze
  session shows `snake_case` column names, or a Silver-session slide shows
  PascalCase surviving untouched, something is wrong — flag it, don't quietly
  "fix" it by guessing which layer the session is actually about.

## `fact_sales` and dimension schema

See `fact-sales-schema.md` for full detail — it's substantial enough to need
its own file, and it has two framings (simplified/story vs. real/technical)
that are NOT interchangeable, and matter a lot for which vocabulary a slide
should use.

## Where the content came from (sayli grounding)

A colleague, sayli, already has a complete, real, working implementation of
much of this pipeline in the same shared workspace. Her code was read
**once, read-only** (`databricks workspace export-dir` and similar read-only
CLI calls) and used as the answer key for Bronze/Silver/Gold builds, the CDC
pipeline, and SCD/incremental merge logic — then rebuilt in this repo with
GlobalMart's naming, full comments, and a teaching narrative wrapped around
it. Kimball theory/grain/dimension-design content and the Day 10-12 standalone
modules (orchestration, DLQ, cost strategy, UC governance, Genie) were written
fresh — sayli's build doesn't cover those topics.

**This skill has no live access to sayli's workspace or to the real
`gbmart` workspace at all.** It cannot check either one. If a task requires
confirming something live (e.g. "did the CDC pipeline pick up a change
today?"), that is a gap to flag to the human, never something to fabricate
having checked. Never write or imply on a slide that this skill re-verified
anything against a live workspace.

## Safety framing lives separately

Any slide that shows illustrative code (a `slide-demo` walkthrough) also needs
to apply the safety rules in `safety-rules.md` — practice-schema patterns, no
live job/cluster triggers, idempotent writes. Read that file too before
drafting any code snippet for a slide.
