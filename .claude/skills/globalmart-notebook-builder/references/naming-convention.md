# File Naming Convention — Algorithm + Real Precedent

Source: `00_Instructor_Guide_How_To_Use_This_Bootcamp.html` Section 2 (slides
4-5) and `HOW_TO_USE_THIS_COURSE.html` Section 2 (slides 4-5), cross-checked
directly against the real Day1-Day12 folder contents and the calendar
workbook via `scripts/read_calendar.py`.

## The pattern

```
Day{N}/
  Day{N}_{order}_ILT{x}_Topic_Name.ipynb    # the notebook you run live
  Day{N}_{order}_ILT{x}_Topic_Name.html     # the slide-deck explainer (built by a sibling skill)
  Day{N}_{order}_HOL{x}_Topic_Name.ipynb    # hands-on lab (learners rebuild this themselves)
  Day{N}_{order}_HOL{x}_Topic_Name.html     # HOL instructions, same visual style
  Day{N}_{order}_HOL_Topic_Name.md          # only where an LMS-graded hands-on exists (built by a sibling skill)
  Day{N}_{order}_REF_Topic_Name.html/.ipynb # cert-prep content — OUT OF SCOPE for this skill
  Day{N}_{order}_DEMO_Topic_Name.ipynb/.html # instructor demo — OUT OF SCOPE for this skill
```

This skill builds `.ipynb` files for `ILT{x}` and `HOL{x}` sessions only.
DEMO and REF files exist in the real repo (see below) but this skill does not
build them — if a user asks for a DEMO or REF file, say so and ask how they
want to proceed rather than silently building an ILT/HOL in its place.

## `{order}` — the leading digit

1-based position of this file **among everything in the day's teaching
sequence**, added specifically so a plain alphabetical file-listing sorts in
teaching order (without it, `DEMO`/`HOL` sort before `ILT`, and `REF` sorts
after — scrambling the sequence a file browser shows).

`scripts/read_calendar.py --day N` computes `{order}` for you, but only
relative to that day's **calendar-derived** ILT/Hands-on rows. Real DEMO/REF
files are never in the calendar at all, and they still consume order slots on
disk — see the Day 3 worked example below for exactly how this plays out.
**Always Glob the real `Day{N}\` folder and reconcile the script's number
against what's actually sitting there before finalizing a filename** —
treat the script's output as the right relative order among calendar-derived
sessions, not the final absolute number, whenever a DEMO or REF file might
already exist that day.

## `{x}` — the type-local sequence number

1-based position **within that type only** (`ILT1`, `ILT2`, ... / `HOL1`,
`HOL2`, ...) — always teach/run them in this order, since later ones often
depend on earlier ones (e.g. Day 7's `HOL2` fact-table build reads tables that
`HOL1`'s dimension build created).

**`{x}` is dropped entirely when the day has only one session of that type.**
Two different kinds of "only one" both apply this rule:

- Day 1 has exactly one Hands-on row all day → `Day1_5_HOL_PySpark_SparkSQL_ADLS`,
  not `Day1_5_HOL1_...`.
- Day 3 has exactly one `DEMO` and exactly one `REF` (types that only ever
  appear once per day in practice) → `Day3_4_DEMO_AutoLoader_v2` and
  `Day3_6_REF_Structured_Streaming_AutoLoader_CertPrep`, neither numbered.

Day 13 is a fresh instance of the first kind: its calendar has exactly one
ILT row ("Review & Doubt Discussion") and no Hands-on row at all, so that
file's real number is `Day13_?_ILT_Review_Doubt_Discussion...` — unnumbered,
`{order}` still to be determined (see caveat above; run
`scripts/read_calendar.py --day 13` first).

**This rule is not applied with zero exceptions across the repo** — Day 6's
real hands-on file is `Day6_4_HOL1_Star_Schema_Design`, numbered `HOL1` even
though it's the only Hands-on session in Day 6's real final folder (see the
Day 6 worked example below for why). When a day looks like a single-session
day, check the real folder for precedent rather than assuming the drop rule
applies unconditionally.

## Worked examples — real files, cross-checked against the calendar

### Day 1 — the clean case (no DEMO/REF collisions to worry about mid-sequence)

`read_calendar.py --day 1` output lines up with the real folder exactly:

| order | calendar row | real file |
|---|---|---|
| 1 | ILT "Databricks Problem Statement (GlobalMart)" | `Day1_1_ILT1_GlobalMart_Problem_Statement` |
| 2 | ILT "Azure Cloud, ADLS Gen2 & Lakehouse vs Warehouse vs Hybrid" | `Day1_2_ILT2_Azure_ADLS_Lakehouse_vs_Warehouse_vs_Hybrid` |
| 3 | ILT "Medallion Architecture & Delta Lake Fundamentals" | `Day1_3_ILT3_Medallion_Architecture_Delta_Lake` |
| 4 | ILT "Intro to Databricks for DE + PySpark & Spark SQL" | `Day1_4_ILT4_Intro_Databricks_PySpark_SparkSQL` |
| 5 | Hands-on "Data wrangling..." + "Work with ADLS" (one row) | `Day1_5_HOL_PySpark_SparkSQL_ADLS` (x dropped — only 1 HOL) |
| — | *(not in calendar — added beyond it)* | `Day1_6_REF_Ingestion_Lakeflow_Autoloader` (order continues past the calendar's last row) |

### Day 3 — the DEMO-insertion + duplicate-row case (read this one carefully)

The raw calendar has a genuinely messy row: "Connect to Public API + GraphDB..."
appears once tagged `Hands-on`, then again on the very next row tagged `ILT`
with the **identical Module text** — a real data-entry duplicate, not two
sessions. `read_calendar.py` merges these into one logical row (using the
first occurrence's type, `Hands-on`) and prints `[merged 2 rows]` when it does.

| order (script, calendar-only) | session | real file | real order (on disk) |
|---|---|---|---|
| 1 | ILT "API Ingestion Mechanics + GraphDB Basics" | `Day3_1_ILT1_API_Ingestion_GraphDB_Basics` | 1 |
| 2 | Hands-on "Connect to Public API + GraphDB" (merged) | `Day3_2_HOL1_Public_API_GraphDB` | 2 |
| 3 | ILT "Autoloder & Schema Evolution Concepts" | `Day3_3_ILT2_Schema_Evolution_Concepts` | 3 |
| — | *(not in calendar)* | `Day3_4_DEMO_AutoLoader_v2` | **4** |
| 4 | Hands-on "Autoloader - Ingestion from ADLS" | `Day3_5_HOL2_ADLS_AutoLoader_Bronze_Customers_Payments` | **5** (not 4!) |
| — | *(not in calendar)* | `Day3_6_REF_Structured_Streaming_AutoLoader_CertPrep` | 6 |

This is the concrete proof of the caveat above: the script correctly gets
`HOL2` as the 4th calendar-derived session, but its real order on disk is 5,
because `DEMO` (order 4) was inserted between `ILT2` and `HOL2` and isn't in
the calendar at all. If you were building a brand-new Day 3 file today without
checking the real folder first, you'd get this wrong.

### Day 9 — the split-session merge case

The calendar's last two rows both say "Handling incremental data - Bronze &
Silver" (one 3:30-4:30, one 4:30-5:30) — one hands-on session spanning two
grid time-blocks, not two sessions. `read_calendar.py` merges them
(`[merged 2 rows]`) into a single `HOL2`, matching the real single file
`Day9_5_HOL2_Handling_Incremental_Data_Bronze_Silver`. Real folder: `ILT1`,
`ILT2`, `HOL1`, `ILT3`, `HOL2` — 5 files, order 1-5, no DEMO/REF that day so
the script's numbers are also the final numbers here.

### Day 10 — the Lunch-split session case

Day 10's calendar has "Hands-on: Incremental Gold Refresh - MERGE-based fact
table updates" appearing once **before** Lunch (11:00 AM-1:00 PM) and again
**after** Lunch (2:00-3:00 PM) — one real session split by the Lunch row
sitting physically between its two halves, not two sessions. This only
merges correctly if you filter out Lunch/Assessment/Internal rows **first**,
then look for consecutive identical-text rows among what's left — filtering
after merging would miss it, since Lunch sits between the two real halves in
the raw sheet. `read_calendar.py` does the filter-then-merge in that order for
exactly this reason. Real folder, order 1-5, no DEMO/REF that day:

| order | session | real file |
|---|---|---|
| 1 | ILT "Implementing SCD Type 1 and Type 2 using MERGE..." | `Day10_1_ILT1_SCD_Type1_Type2_MERGE` |
| 2 | Hands-on "Implement SCD Type 2 for dim_customer using MERGE" | `Day10_2_HOL1_SCD_Type2_Dim_Customer_MERGE` |
| 3 | Hands-on "Incremental Gold Refresh..." (merged, split by Lunch) | `Day10_3_HOL2_Incremental_Gold_Refresh_Fact_MERGE` |
| 4 | ILT "Introduction to Orchestration..." | `Day10_4_ILT2_Orchestration_Need_DAG_Workflow_Design` |
| 5 | ILT "Databricks Workflows vs Airflow..." | `Day10_5_ILT3_Databricks_Workflows_vs_Airflow_Deep_Dive` |

### Day 6 — the cross-day spillover case (script gets this one wrong — read carefully)

Day 5's calendar ends with "Hands-on: Build Silver Layer - enrichment,
business rules, across all 4 sources" occupying its last **two** time-blocks
(2:00-3:30 PM and 3:30-5:30 PM), and Day 6's calendar then **starts** with
that exact same Module text again, as Day 6's first row (9:30-11:00 AM) —
three consecutive time-blocks of the same real session, spanning a day
boundary. The real build folded all three into Day 5's `HOL2`, and Day 6's
teaching content starts fresh with its own `ILT1`. Real Day 6 folder is
`ILT1, ILT2, ILT3, HOL1` (4 files) — no second HOL.

`scripts/read_calendar.py` **cannot detect this** — it only looks within one
Day Number at a time, by design (each Day{N} folder is built independently),
so it has no way to know Day 6's first row is a continuation of Day 5's
session rather than a new one. Running `--day 6` will show a phantom `HOL1`
(the spillover) followed by the real Star Schema Design hands-on mislabeled
`HOL2`. **If a day's first calendar row has identical Module text to the
previous day's last row(s), treat it as spillover already accounted for in
the previous day, not a new session for this day** — confirm by checking
whether the previous Day{N-1} folder's last HOL/ILT file already covers that
topic before trusting the script's count here.

**Bonus wrinkle:** Day 6's real hands-on file is `Day6_4_HOL1_Star_Schema_Design`
— numbered `HOL1` even though it's the *only* Hands-on session in Day 6's real
final folder. This is an inconsistency with the "drop `{x}` when only one of
a type" rule that Day 1's `HOL` and Day 3's `DEMO`/`REF` otherwise follow
consistently — worth knowing so you don't assume the drop-`{x}` rule is
applied with zero exceptions across the whole repo. When in doubt on a
single-session day, check whether that day already has a real precedent file
and match it; don't assume the rule is followed if you haven't checked.

### Day 13 — the no-Hands-on / unnumbered-ILT case

`read_calendar.py --day 13` returns exactly one row: `ILT` "Review & Doubt
Discussion", 2:00-4:00 PM. No Hands-on row exists in the calendar for Day 13
at all — confirmed directly, not assumed. Its real filename should be
`Day13_?_ILT_Review_Doubt_Discussion...` (drop `{x}` — only one ILT that day;
determine `{order}` by checking whether anything else already exists in
`Day13\`, which at the time this doc was written, does not).

## Standalone modules — a naming non-issue, but worth knowing

A handful of ILT/HOL sessions are deliberately **standalone modules**: real
Databricks/DE knowledge in GlobalMart flavor, but not wired into the
Bronze→Silver→Gold narrative and not required for later days to make sense
(Day 2 ILT/HOL 3 "Code Versioning Concepts" was the first; Day 10 ILT 2/3
orchestration, and the Day 11/Day 12 ILT sessions follow the same pattern).
These still get named with the exact same algorithm — standalone-ness affects
content and teaching order flexibility, not the naming convention.

## Day numbering has shifted from early drafts

Files were reorganized with `git mv` partway through this build to match the
real calendar. If you ever see a stray reference to an old day number in
conversation history or an old export, trust the **current folder location**,
not any memory of where something used to live.
