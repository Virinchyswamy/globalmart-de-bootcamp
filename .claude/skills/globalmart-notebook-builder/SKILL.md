---
name: globalmart-notebook-builder
description: >
  Builds one Databricks .ipynb teaching notebook (an ILT lecture-demo or a HOL
  hands-on lab) for the GlobalMart Azure Databricks Data Engineering bootcamp
  (Chennai 2026 cohort), for exactly one calendar session at a time, saved into
  C:\Yvirinchy\tred-alch-adv-dbx\Databricks\Day{N}\. Use this whenever the user asks to build,
  write, draft, continue, or fix a Day N notebook, ILT, HOL, hands-on lab, or
  pipeline-accurate PySpark/Spark SQL session for this bootcamp -- including
  phrasings like "build Day 13's notebook", "write the ILT for DLQ replay",
  "make the star schema hands-on notebook", "do the next session on the
  calendar", or "pick up where Day 9 left off" -- even if the user never says
  "notebook" explicitly. Always reach for this skill before writing any
  gbmart/GlobalMart-related PySpark or Spark SQL cell from scratch, since it
  encodes the real gbmart schema, the safety rules every other notebook in
  this repo follows, and the exact file-naming convention.
---

# GlobalMart Notebook Builder

## Why this skill exists

Every notebook in this course teaches against one real, shared Databricks
environment (`gbmart`), follows one naming convention, and applies the same
handful of safety patterns so it's safe to rehearse and safe for every cohort
to run. Re-deriving those facts from scratch each time a new session gets
built is exactly how mistakes creep in — this skill bundles the verified
ground truth so you don't have to reconstruct it, and it exists specifically
because reconstructing it from memory has already gone wrong once on this
project (see guardrail 1 below).

## Workflow

### 1. Identify the target Day + session

Run `scripts/read_calendar.py --day N` (from this skill's `scripts/`
directory) to get that day's ILT/Hands-on rows with computed `{order}`,
`{type}`, and `{x}` naming fields. The script forward-fills the calendar's
Week/Day/Date columns and excludes Lunch/Assessment/Internal rows from the
count automatically. If the user names a topic instead of a row number
("build the DLQ replay one"), match against the Module text the script prints
rather than asking them to look it up themselves.

If the user gives you a day but no session, and that day has more than one
ILT/HOL row, ask which one (or offer to build all of them in sequence) rather
than guessing.

Some days have real complications the script surfaces but doesn't fully
resolve on its own — read its output, don't just trust the last line:
- **Merged rows:** a `[merged N rows]` note means the calendar had duplicate,
  split, or Lunch-separated rows for one real session (see Day 9's split
  hands-on, Day 3's malformed duplicate row, and Day 10's Lunch-split hands-on
  in `references/naming-convention.md`) — this is already handled, no action
  needed.
- **DEMO/REF-adjacent days:** the script's `{order}` is relative to calendar
  rows only. Real DEMO/REF files (out of scope for this skill to build, but
  real files that already exist on disk) consume order numbers the calendar
  never lists. Day 3 is the worked example of this going wrong if ignored.
- **Cross-day spillover the script cannot see:** if a day's first calendar
  row has Module text identical to the previous day's last row(s), that's
  likely a session that spilled over and was already counted in the previous
  day's folder (Day 5 → Day 6 is the confirmed real example) — the script has
  no way to detect this since it only looks at one Day Number at a time.
  Check the previous day's real folder before trusting a phantom session here.
- **The drop-`{x}`-when-only-one rule has a known exception:** Day 6's real
  `HOL1` file is numbered even though it's the only Hands-on that day. Don't
  assume the rule is followed with zero exceptions — check the real folder
  for precedent when a day looks like a single-session day.

All of the above is exactly why step 2 below is not optional.

### 2. Check for filename collisions and reconcile `{order}` — before writing anything

Glob `Databricks\Day{N}\Day{N}_*` to see what's actually in the folder. Two separate
things to check here, not one:

- **Does the target file already exist?** If so, **stop and show what would
  change instead of silently overwriting it.** This is a hard lesson from a
  real incident on this project: a background process once silently
  overwrote correct Day 6 content with stale content, and it wasn't caught
  until someone noticed wrong facts in the output. Never repeat that.
- **Does the real folder's numbering match the script's calendar-only
  count?** If a DEMO or REF file already occupies a lower `{order}` slot than
  your new session would naively get (Day 3), or a cross-day spillover
  inflated a previous day's count in a way that shifts what "next" means
  (Day 5→6), your new file's real `{order}`/`{x}` can be different from what
  the script printed. Reconcile by hand before naming the file — these are
  real, observed failure modes from this repo's own build history, not
  hypothetical ones. See `references/naming-convention.md`'s worked examples
  (Day 3, Day 6, Day 9, Day 10) before finalizing a name on any day that
  doesn't look perfectly clean.

### 3. Decide which `fact_sales`/schema framing applies

Load `references/architecture-facts.md` and `references/fact-sales-schema.md`.
The decision rule is simple but easy to get backwards: **the moment a session
writes real code against real column names, use the real/technical schema —
always, regardless of day.** The simplified/story version (quantity/
unit_price/line_total, 5 dims) exists only for early motivational framing
before any real code appears. Never mix them within one notebook, and never
fall back to simplified language once real code has shown up, even in
surrounding markdown.

### 4. Read the immediately-preceding sibling notebook(s) for continuity

Read the notebook(s) that come right before this one in the same `Databricks\Day{N}\`
folder (by `{order}`), and the paired ILT if you're building a HOL. A learner
building today's session has whatever tables/columns/variable names those
earlier notebooks actually produced — not whatever a fresh derivation from the
architecture docs alone would produce. If today's session is a HOL that
continues a build (e.g. Day 7 HOL 2 depends on Day 6's dimension build), this
step is what keeps names consistent across the dependency chain.

### 5. Apply the relevant safety pattern

Load `references/safety-rules.md` and pick the pattern that fits the
session's content:
- Write-heavy demo against a table other cohorts also touch (MERGE/SCD/CDF/
  OPTIMIZE) → `SHALLOW CLONE` or a personal `main.YOUR_SCHEMA` practice table.
- Anything that could resemble triggering a real job/pipeline/cluster/
  warehouse → an inspectable, clearly-commented Python dict instead, never a
  real API call.
- Anything needing a credential-shaped value → a placeholder
  (`YOUR_CATALOG`/`YOUR_SCHEMA`-style) plus a comment on how to obtain the
  real value manually.

Each pattern in that file comes with a real verbatim snippet from this repo —
match the shape, not just the intent.

### 6. Draft cell-by-cell following the observed structure

Load `references/notebook-structure-patterns.md` and follow its shape: header/
metadata cell (with a table covering what this session builds on and
produces), a Learning Objectives list, phased Step/Phase/Part cells (markdown
goal statement, then code), row-count verification prints after every join,
Key Takeaways, and — for HOLs — a Submission Checklist (or Self-Check for
concept-only ILTs). The specific headings flex to the session's content; the
shape doesn't.

### 7. Write the file, then validate before reporting success

Write the `.ipynb`, then run:
```
python scripts/validate_ipynb.py "Databricks\Day{N}\Day{N}_{order}_{TYPE}{x}_Topic_Name.ipynb"
```
Read its output. A structural failure (bad JSON, missing `cell_type`) means
the file is broken and needs fixing before anything else. A billable-trigger
warning isn't automatically wrong (a `.start()` paired with a `.stop()` in the
same build is normal and appears in real notebooks in this course) — read
each flagged line and confirm it's paired correctly before moving on.
**Never report a notebook as done without having run this and read the
output** — this is the "re-open and check" half of the Day 6 lesson, and
skipping it is exactly how that incident happened.

### 8. Report back

Tell the user: the exact path written, the naming reasoning (so they can
sanity-check `{order}`/`{x}` themselves — especially on any day where you had
to reconcile against existing DEMO/REF files), the validation result, and any
grounding gap you had to flag instead of guess (a table/column name not in the
bundled references, a claim you couldn't verify because this skill has no
live Databricks access).

## The 6 universal guardrails

These apply to every notebook this skill helps produce, no exceptions:

1. **Never silently overwrite.** Check for the target file first; if it
   exists, show what would change and stop.
2. **Never invent an architecture fact.** If a table/column name or schema
   detail isn't in `references/architecture-facts.md` or
   `references/fact-sales-schema.md`, ask rather than guessing something
   plausible-sounding.
3. **Never write code that starts, triggers, or schedules a real job,
   pipeline, cluster, or SQL warehouse.** Jobs/Workflow config is always an
   inspectable, clearly-commented-as-illustrative Python dict, never a real
   API call.
4. **Never embed a real credential.** Always a placeholder plus a comment
   explaining how to obtain the real value manually.
5. **Never claim to have live-checked sayli's Databricks workspace (or the
   real `gbmart` workspace at all).** This skill has no live Databricks
   access, period. Flag any such gap to the human instead of fabricating a
   check.
6. **After writing, re-open and validate before declaring success.** Run
   `scripts/validate_ipynb.py` and read its output every time.

## Bundled references — when to read each

- `references/architecture-facts.md` — the real `gbmart` environment, the 2
  ingestion pathways / 8 Bronze tables (incl. two catalogs), the "4 sources" trap, Bronze/Silver
  casing rule. Read for any pipeline-accurate session.
- `references/fact-sales-schema.md` — both `fact_sales` framings and the
  decision rule between them, full real column list, the natural-key/
  degenerate-dimension gotchas. Read for any session touching `fact_sales` or
  its dimensions.
- `references/naming-convention.md` — the `{order}`/`{x}` algorithm plus
  worked real examples (including the Day 3 DEMO-insertion case and the Day 9
  merged-row case). Read before finalizing any filename.
- `references/safety-rules.md` — all 6 safety patterns, each with a real
  verbatim snippet. Read before drafting any write-heavy cell.
- `references/notebook-structure-patterns.md` — the observed cell-shape
  pattern with real excerpts. Read while drafting the notebook body.
