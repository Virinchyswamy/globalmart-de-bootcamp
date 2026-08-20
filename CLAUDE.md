# GlobalMart Data Engineering Bootcamp — Repo Guide

This repo is the full teaching-material build for a Databricks Data
Engineering bootcamp ("GlobalMart" project), plus a parallel SQL & Python
track. It is not application code — every file here is either a lecture
deck, a hands-on notebook, a graded LMS assessment, or reference material
used to keep those three grounded in what the instructor actually built and
ran. Content was originally built for the Chennai 2026 cohort and is reused
as-is for the Hyderabad 2026 cohort (started 2026-08-12) — see `calendars/`
below for how the two cohorts' calendars map onto the same `Databricks/Day{N}`
folders.

## Directory map

| Path | What's there |
|---|---|
| `Databricks/Day1` – `Day12` | The Databricks track. One folder per teaching day, each file named `Day{N}_{order}_{TYPE}{x}_Topic.{ipynb,html}` (ILT = lecture-demo, HOL = hands-on lab, DEMO/REF = supplementary). Files also get a matching `.md` (LMS-import hands-on assessment) when the session has a graded lab. |
| `SQL_Python/Day1` – `Day8` | The SQL & Python track — merged in 2026-07-19 from a previously-separate repo (`Chennai_batch`). Same `DayN_M_TYPE_Title` naming convention, but its own independent Day 1–8 numbering — **do not renumber to align with `Databricks/`**. Per the master calendar the two tracks run sequentially (SQL/Python finishes before Databricks Day 1 starts), not interleaved by date. |
| `extras/` | Supplementary notebooks not tied to a specific calendar day (cert-prep, deep-dives). |
| `calendars/` | The master calendar spreadsheets, one pair (calendar + learner list) per cohort. `tred-alch-adv-dbx-chennai-2026-*` is the original cohort the `Databricks/`/`SQL_Python/` content was built against. `tred-alch-adv-dbx-hyderabad-2026-*` (added 2026-08-12) is the current batch reusing that same content — its calendar numbers the Databricks track **9–22** (continuous with its own SQL & Python Day 1–8), not 1–13 like Chennai's; see the mapping note in `globalmart-notebook-builder`'s `scripts/read_calendar.py`. Both skills' scripts default to the Hyderabad files and accept an override flag (`--calendar` / `--learner-list`) to read the Chennai ones instead. |
| `reference_materials/` | Ground-truth sources used to build/validate course content: real hands-on answer-key `.md` files (`hands_on_answer_keys_through_day9/`), the real executed Bronze/Silver/Gold pipeline notebooks (`working_notebooks_real_executed_pipeline/`), a colleague's read-only-exported account used as grounding (`sayli_account_export_grounding/`), Bronze/Silver build requirement docs, the architecture doc, and a `globalmart_v2_poc_scaffold/` (a separate CDC proof-of-concept, not course content). |
| `datasets/` | Standalone sample datasets (mostly duplicated inside `SQL_Python/_resources/` too — not yet deduplicated). |
| `marketing/` | LinkedIn post drafts. Unrelated to course structure. |
| `_archive/` | Stale backups (e.g. an old `Day3.zip` snapshot). Not current content. |
| `.claude/skills/` | Three skills that encode this project's real, hard-won conventions — see below. Use them instead of hand-writing new course content. |
| `00_Instructor_Guide_How_To_Use_This_Bootcamp.html`, `HOW_TO_USE_THIS_COURSE.html` | Top-level course entry points. Kept at repo root deliberately (not "extra" content). |

## The three skills — use these, don't hand-write course content

- **`globalmart-notebook-builder`** — builds one `.ipynb` (ILT or HOL) for a
  Databricks day. Reach for this before writing any GlobalMart-related
  PySpark/Spark SQL cell from scratch.
- **`globalmart-hol-md-builder`** — builds the LMS-import `.md` graded
  assessment for a HOL, in the one format confirmed to import cleanly (never
  the different, similar-looking export shape in
  `reference_materials/reference_data_for_hands_on_docs/`).
- **`globalmart-slide-deck-builder`** — builds the dark-themed HTML slide
  deck that accompanies an ILT/HOL notebook.

Each skill bundles its own `references/` (architecture facts, schema,
naming convention, safety rules, tone) — read those before generating
anything, don't rely on memory of "GlobalMart" facts, since several have
drifted wrong more than once during this project's real build (see below).

## Facts that have drifted wrong before — check the skill references, not memory

These specific facts have each been stated incorrectly at some point in this
project's history and re-corrected. If you're about to state one of them
from general recollection rather than reading the current
`architecture-facts.md`, stop and read it first:

- **Bronze/Silver and Gold are two different Unity Catalogs, not one.**
  Bronze/Silver write to `harsh_kumar01_npmentorskool_onmicrosoft_com`; Gold
  reads/writes `gbmart`. This is deliberate, not a bug to unify.
- **8 real Bronze tables, not 6 or 7.** 2 via Postgres/Lakeflow Connect CDC
  (`orders`, `order_items`) + 6 via ADLS Autoloader/mounting (`customers`,
  `products`, `address`, `payments`, `payment_methods`, `returns`). The root
  guide docs and `Databricks/Day4/Day4_1_ILT1...ipynb` still say 6 or 7 as of
  2026-07-19 — known, unresolved, flagged rather than silently fixed outside
  the scope of whatever task you're doing.
- **Lakeflow Connect CDC is cursor-based (query polling on `updated_at`),
  not log-based/WAL.** It cannot capture hard deletes. This fact has flipped
  twice in this project's history — trust the real hands-on answer-key file
  in `reference_materials/hands_on_answer_keys_through_day9/`, which shows an
  actual screenshot of "History tracking: Off (SCD Type 1)", over any
  inference from a setup script's `REPLICA IDENTITY FULL`/`PUBLICATION`
  calls (those exist but aren't what the real configured pipeline uses).
- **Bronze/Silver/Gold are Unity Catalog schemas, never ADLS folders.** ADLS
  only ever holds `raw-data/<table>/` (source files). If you see
  `bronze/`, `silver/`, `gold/` treated as ADLS subfolders anywhere, that's
  the old, corrected-in-2026-07 architectural error resurfacing.

## The placeholder convention (student-facing prose vs. real executed code)

Teaching prose (explanations, setup instructions, table descriptions) always
uses generic placeholders — `<your-catalog>`, `YOUR_STORAGE_ACCOUNT_NAME`,
`YOUR_CONTAINER_NAME` — since every student's own values differ. Code cells
that show GlobalMart's own real executed run may use the real literal
(`gbmart`, `harsh_kumar01_npmentorskool_onmicrosoft_com`) **with an explicit
one-line callout** naming it as the real run and noting the student's own
catalog will be named differently. Never show a raw storage-account key —
storage auth is always Unity Catalog managed (external location + storage
credential, or a mount point), never a hardcoded key in a notebook.

## Safety rules (apply to every notebook/scenario/slide touching real data)

- Practice-schema or `SHALLOW CLONE` only for any write-heavy demo — never
  write directly to shared `gbmart`/`harsh_kumar01...` tables (a shared-table
  demo is only repeatable once; it breaks for the next cohort or rehearsal).
- Never trigger a real job, pipeline, cluster, or SQL warehouse — Jobs/
  Workflow config in teaching content is always an inspectable, clearly-
  illustrative Python dict, never a real API call.
- Never embed a real credential — always a placeholder plus a comment on how
  to obtain the real value manually.
- A colleague's account (referenced in `reference_materials/sayli_account_export_grounding/`)
  was used **read-only, once**, as a grounding source. No skill or notebook
  in this repo has live access to it or to the real `gbmart` workspace —
  never claim to have live-checked either one.

## Naming convention

`Day{N}_{order}_{TYPE}{x}_Topic_Name.{ipynb,html,md}` — `{order}` is the
file's position in that day's real on-disk folder (not recomputed from the
calendar; DEMO/REF files and split/merged calendar sessions can shift it —
see `naming-convention.md` in the notebook-builder skill for the confirmed
edge cases). `{TYPE}` is `ILT`, `HOL`, `DEMO`, or `REF`; `{x}` is dropped
when only one session of that type exists that day.

## When editing existing content vs. adding new content

If you notice one of the "drifted wrong before" facts above stated
incorrectly in a file you weren't already asked to touch (e.g. the Bronze
table count in the root guide docs), **flag it, don't silently fix it as a
side effect** of an unrelated task — several of these facts have flipped
back and forth in this project's history specifically because a fix in one
place didn't get propagated everywhere, and a silent fix is harder to audit
than a flagged one.
