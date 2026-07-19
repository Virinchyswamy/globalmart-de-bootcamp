# GlobalMart Real Architecture — Ground Truth

This is the real, already-running Databricks environment every pipeline-accurate
notebook in this course points at. It is NOT a toy/simulated dataset built for
teaching — it's a real workspace with real (if training-scale) data, so every
table/column name a notebook uses must match what's actually there. If you
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
| Unity Catalog — Bronze/Silver | `harsh_kumar01_npmentorskool_onmicrosoft_com` (a personal catalog — real, confirmed in `Databricks/Day4/Day4_3_HOL1_Build_Bronze_Layer_Mounting.ipynb`, explicitly commented `# ← different catalog than gbmart`) |
| Unity Catalog — Gold | `gbmart` (real, confirmed in `Databricks/Day7/Day7_3_HOL2_Build_Gold_Layer_Fact_Sales.ipynb`) |
| External location | `gbmart-ext-loc` → `abfss://ecom-gbmart-data@ecomadlsdata.dfs.core.windows.net/raw-data` |
| Storage credential | `ecomprojectscredentials` (keyless, Unity Catalog managed — never a raw storage-account key in any notebook) |

**The Bronze/Silver-vs-Gold catalog split is deliberate, not a bug to unify.**
Don't "fix" it by normalizing to one catalog name if asked to touch this
content — it's a confirmed, intentional choice (see
`[[project_globalmart_bootcamp]]` memory for the incident history: this fact
flipped twice across this project before landing here).

**What learners see vs. what the real code shows — the placeholder
convention.** Every notebook genericizes catalog/storage names in *prose*
(`<your-catalog>`, `YOUR_STORAGE_ACCOUNT_NAME`, `YOUR_CONTAINER_NAME` — a
student's own values will differ). *Code cells* that show GlobalMart's own
real executed run keep the literal value (`gbmart`, or
`harsh_kumar01_npmentorskool_onmicrosoft_com`), each with an explicit
one-line callout naming it as the real run and noting the student's own
catalog will be named differently — see `Day7_3_HOL2_Build_Gold_Layer_Fact_Sales.ipynb`'s
own Note cell for the exact wording pattern to copy. Never invent a fake
placeholder-*looking* literal (no `<your-storage-account>`-style bracket
tokens in code, use a real Python variable assigned a real placeholder
string) and never leave a real storage-account key hardcoded — storage
auth is always Unity Catalog managed, never a raw account key, per Day 4's
mounting pattern.

## Exactly 2 ingestion pathways, 8 real Bronze tables — never 4, 6, or 7

This is the single fact most likely to drift wrong if you're generating from a
vague memory of "GlobalMart" rather than this doc, because it drifted wrong
*repeatedly* during this course's real build (early drafts said 4 sources;
later drafts said 6 or 7 Bronze tables, both missing `returns`). If you ever
see "4 sources" — or a Bronze table count other than 8 — asserted as
architectural fact anywhere, including in your own draft, stop and fix it.

1. **Postgres/Supabase CDC via Lakeflow Connect** — pipeline name
   `orders_data_ingestion_cdc`. Query/cursor-based on `updated_at`, NOT
   log-based WAL — this means it **does not capture hard deletes** (taught
   explicitly in Day 2 as a real limitation, not glossed over; this exact
   fact flipped to "log-based" and back to "cursor-based" once already during
   this project — cursor-based is the version grounded in a real screenshot/
   quiz from the actual pipeline config, in
   `reference_materials/hands_on_answer_keys_through_day9/`, not inference
   from a setup script). Feeds `bronze.orders` and `bronze.order_items`.
2. **ADLS Autoloader / mounting** — flat files landing under `raw-data/`,
   ingested via `cloudFiles` or a mount point. Feeds `bronze.customers`,
   `products`, `address`/`addresses`, `payments`, `payment_methods`,
   `returns` — **6 tables, not 4 or 5.** Confirmed directly against the real
   Day 4 Bronze-build notebooks (`Day4_3_HOL1_Build_Bronze_Layer_Mounting.ipynb`,
   `Day4_3_HOL1_Build_Bronze_Addresses.ipynb`,
   `Day4_3_HOL1_Build_Bronze_Layer_Remaining_Sources.ipynb`), and Day 1 ILT 1's
   own instructor note ("all 6 ADLS GlobalMart source tables").

That's **8 real Bronze tables total**: `orders`, `order_items` (CDC) +
`customers`, `products`, `address`, `payments`, `payment_methods`, `returns`
(Autoloader/mounting).

**Known, unresolved inconsistency — flag, don't silently "fix" elsewhere.**
As of 2026-07-19, `HOW_TO_USE_THIS_COURSE.html`, `00_Instructor_Guide_How_To_Use_This_Bootcamp.html`,
and `Databricks/Day4/Day4_1_ILT1_Ingestion_Patterns_Recap_All_4_Sources.ipynb`
still say "7 real Bronze tables" / list only 6 total (both missing
`payment_methods` and/or `returns` from the Autoloader list) — these have
NOT been corrected to 8 yet. If you're generating brand-new content, use 8
(the number confirmed against the real Day 4 build notebooks, which is the
most authoritative source available). If you're editing one of those three
already-inconsistent files specifically, flag the discrepancy to the human
rather than silently rewriting a number in a file outside this skill's
normal scope.

**Where "4 sources"/"4" legitimately appears and does NOT mean 4 systems:**
the real calendar itself uses "4" in a couple of session titles — e.g. Day 4's
"Recap: Ingestion Patterns Across All 4 Sources" and Day 4's Hands-on "Build
the Bronze Layer - all 4 sources", and Day 12's deferred hands-on title
"...Verify Lineage (4 Sources)". In every one of these, "4" means **4
Bronze-table-level ingestion tasks/checks**, or is a holdover from the
original spec's name — not 4 distinct source *systems*. If a calendar Module
title says "4" and you're not sure which "4" it means, it's the table-level
one; the source-system count is always 2. When you build a notebook whose
calendar title contains this "4", correct it explicitly and visibly in the
notebook text itself, the same way Day 3 ILT 1 and Day 4 ILT 1 do — don't just
silently avoid the word.

**Day 3's REST API + GraphDB/Cypher content is a deliberate side-exploration,
not a third pathway.** It's real, runnable content (useful patterns learners
will meet on other projects), but it lands in a `sandbox/` path and **never
touches the real `bronze` schema** (in either catalog). Never describe it as
feeding the real pipeline.

## Casing rule — Bronze vs. Silver

- **Bronze preserves the source's raw casing exactly.** PascalCase from CSV
  headers (e.g. `CustomerID`), and the CDC source's own casing for
  `orders`/`order_items` (e.g. `OrderID`, `CustomerID`, `updated_at`).
- **Silver renames everything to `snake_case`** (e.g. `customer_id`,
  `order_date`). This renaming **is Silver's job** — it never happens in
  Bronze, and Silver never leaves PascalCase behind. If you're writing a
  Bronze notebook and reach for `snake_case` column names, or a Silver
  notebook and see PascalCase survive untouched, something is wrong — flag
  it, don't quietly "fix" it by guessing which layer you're actually in.

## `fact_sales` and dimension schema

See `fact-sales-schema.md` for full detail — it's substantial enough to need
its own file, and it has two framings (simplified/story vs. real/technical)
that are NOT interchangeable.

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
having checked. Never write or imply that this skill re-verified anything
against a live workspace.

## Safety framing lives separately

Every notebook this skill helps build also needs to apply the safety rules in
`safety-rules.md` — practice-schema patterns, no live job/cluster triggers,
idempotent writes. Read that file too before drafting any write-heavy cell.
