# Tag Vocabulary — Approved Sub-Tags for `**Tags**` Sections

Every question-bearing Input (Short Answer, Choice, Code, File Upload — see
`lms-format-spec.md` for why Text Inputs get no tags at all) needs a
`**Tags**` section drawn from real, already-used tags — not invented ones.
This file is the list, grep-verified against every `.md` in this repo as of
the last update. Extend it only when a task genuinely isn't covered by
anything here, and keep any new tag in the same 2-level
`parent / child (skill)` (or `(tool)`) shape — never 3 levels deep.

## The two skill parents this project organizes around

`data-wrangling (skill)` and `data-quality (skill)` are the two umbrella
skill tags. Every specific task gets a `parent / child (skill)` sub-tag
under one or both of these, not just the bare parent — the bare parent alone
is too coarse to be useful once a file has more than a couple of Inputs.

### `data-wrangling` sub-tags (real, in use elsewhere in this project)

```
data-wrangling / aggregate (skill)
data-wrangling / conditional-logic (skill)
data-wrangling / dataframe-processing (skill)
data-wrangling / date-processing (skill)
data-wrangling / derived-column (skill)
data-wrangling / filter (skill)
data-wrangling / group (skill)
data-wrangling / group-by-aggregate (skill)
data-wrangling / join (skill)
data-wrangling / joins (skill)
data-wrangling / math-calculations (skill)
data-wrangling / regex (skill)
data-wrangling / sort (skill)
data-wrangling / sub-query (skill)
data-wrangling / text-processing (skill)
data-wrangling / window (skill)
```

Note `join` and `joins` both exist (singular vs. plural) — this is a real,
pre-existing inconsistency in the vocabulary, not something to silently
"fix" by picking one. When tagging a join-related Input, either is
acceptable; don't invent a third variant.

### `data-quality` sub-tags

```
data-quality / duplicates (skill)
data-quality / missing-values (skill)
```

This list is much shorter because `data-quality` is used far less often
across the project than `data-wrangling`. `missing-values` was added
during the Day 1 HOL fix (2026-07) for a manufacturer-completeness check —
follow that same pattern (a concrete, specific data-quality *symptom*, not a
vague word like "quality" or "issues") for any new one.

## Other tags this file uses that aren't under the two parents

These are real tags too, just not sub-tagged under `data-wrangling`/
`data-quality` — use them as-is where they fit:

```
databricks (tool)
spark (tool)
sql (tool)
data-storage (skill)
data-understanding (skill)
approach (skill)
```

`sql (tool)` / `spark (tool)` are used at the Input level even though the
top-of-file frontmatter's `tags:` list already declares `databricks (tool)`
and `spark (tool)` once — per-Input tool tags say *which* tool this specific
Input exercises (a SQL-language Code Input gets `sql (tool)`, a PySpark one
gets `spark (tool)`), which is more specific than the file-level list.

## How to decide which tags an Input gets

1. **Type: Text** → no tags at all (blank `**Tags**` section). See the rule
   in `lms-format-spec.md` and `SKILL.md` Step 6 — this is a hard rule, not a
   style preference.
2. **Type: Short Answer / Choice / Code / File Upload** → at least one tag,
   chosen by what the Input actually exercises:
   - A SQL Code question doing a `GROUP BY` + sort → `sql (tool)`,
     `data-wrangling / group-by-aggregate (skill)`, and
     `data-wrangling / sort (skill)` if sorting is a distinct, graded part
     of the ask.
   - A PySpark Code question adding a derived column via `when/otherwise` →
     `spark (tool)`, `data-wrangling / conditional-logic (skill)`,
     `data-wrangling / derived-column (skill)`.
   - A join-based question (SQL `LEFT JOIN` or PySpark `.join()`) →
     `data-wrangling / joins (skill)` (or `/ join`), plus
     `data-wrangling / filter (skill)` if there's also a `WHERE`/`.filter()`
     step doing real work (e.g. the `IS NULL` anti-join pattern).
   - A data-quality/completeness check → `data-quality / missing-values
     (skill)` (or `/ duplicates`) alongside whatever `data-wrangling` tag
     covers the mechanics (usually `group-by-aggregate` or
     `conditional-logic`).
   - A File Upload (screenshot/notebook submission) → usually just
     `databricks (tool)`, plus `data-storage (skill)` if the screenshot is
     specifically evidence of a write/storage step.
   - A conceptual Choice question (e.g. "what does `inferSchema` do") →
     `data-understanding (skill)` and/or `approach (skill)`, not a
     data-wrangling sub-tag, since no wrangling is actually being assessed.
3. **When in doubt, tag narrower, not broader.** A bare `data-wrangling
   (skill)` with no sub-tag tells a learner (or a reviewer) almost nothing
   about what the Input actually tests — always reach for the specific
   `parent / child` pair.
