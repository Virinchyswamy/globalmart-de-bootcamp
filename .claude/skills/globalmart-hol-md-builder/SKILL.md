---
name: globalmart-hol-md-builder
description: >
  Builds the LMS-import-ready .md hands-on assessment file for ONE GlobalMart
  Databricks bootcamp HOL (hands-on lab) session, matching the exact proven
  format (YAML frontmatter + globally-numbered "## Input N" headings that
  never reset across scenarios) that is confirmed to import cleanly into the
  LMS -- never the visually-similar "reference_materials/reference_data_for_hands_on_docs/" export
  format, which is a different platform's export shape and will fail import.
  Use this whenever the user asks to build, generate, write, or fix a
  hands-on .md, LMS import file, graded assessment, or scenario/input file
  for a GlobalMart Day N HOL -- including phrasings like "make the LMS file
  for Day 6's hands-on", "write the graded assessment for the star schema
  lab", "turn this HOL into the .md format", or "why did my hands-on fail to
  import ('Duplicate input number' / "'name' is required")". Always use
  this skill instead of hand-writing the .md, even for a small fix, since the
  frontmatter and numbering rules are strict and have caused real import
  failures before.
---

# GlobalMart HOL `.md` Builder

## Why this skill exists

The LMS's `.md` import format looks almost identical to a different
platform's export format that also lives in this repo
(`reference_materials/reference_data_for_hands_on_docs/`) — same rough idea (frontmatter-ish
metadata, Scenario/Input structure), but different heading levels and
different numbering rules. Confusing the two isn't hypothetical: this
project has two real, git-committed fixes for exactly this confusion
(commits `8094f64`, `b60d56a`), for the errors `"'name' is required"` and
`"Duplicate input number"`. This skill exists so nobody has to re-learn that
distinction under deadline pressure — it bundles the one proven-correct
shape and a validator that catches both failure modes by name before you
ever try to import anything.

## Workflow

### 1. Identify the target HOL session and locate its notebook

Glob `C:\Yvirinchy\DE notebooks\Databricks\Day{N}\Day{N}_*_HOL*_*.ipynb` for the day the
user names (or the topic they describe — match against the notebook's title
cell if they give a topic instead of a day number). If more than one HOL
exists that day, ask which one (or match by topic keyword the user gave)
rather than guessing.

**If the notebook doesn't exist yet, STOP.** Tell the user to run the
`globalmart-notebook-builder` skill first. Never invent a parallel hands-on
scenario that isn't grounded in a real notebook — the whole point of this
skill is that the `.md` reflects what the notebook actually does, not a
plausible-sounding guess at what a Day N HOL "should" contain.

### 2. Derive the output `.md` filename from the notebook's own basename

Take the sibling `.ipynb`'s exact basename and swap `.ipynb` → `.md`. For
example, `Day6_4_HOL1_Star_Schema_Design.ipynb` becomes
`Day6_4_HOL1_Star_Schema_Design.md`.

**Do not independently recompute `{order}`/`{x}`.** `references/
naming-convention.md` documents several real, confirmed edge cases where a
naive calendar-only computation of these numbers drifts from the real
on-disk filename — a DEMO/REF file inserted earlier in the day shifting
everything after it (Day 3), a Lunch-split or cross-day-spillover session
throwing off a session count (Day 6, Day 10). Reading the number directly off
the real sibling `.ipynb` sidesteps all of these at once, because whoever (or
whichever skill) built that notebook already resolved them. Recomputing
independently risks silently reintroducing the exact bug this shortcut
avoids.

### 3. Check for collisions before writing anything

Glob for the exact target `.md` path. If it already exists, **stop and show
what would change instead of silently overwriting it** — this is the Day 6
incident lesson (a background agent once silently overwrote correct content
with stale content, and it wasn't caught until someone noticed wrong facts in
the output). Never repeat that.

### 4. Read the sibling `.ipynb` (and `.html` if present) in full

This is the scenario's technical ground truth: real table/column names, the
exact phases/steps the notebook walks through, and whatever Submission
Checklist the notebook already ends with. The hands-on `.md` should feel like
a graded version of the same journey the notebook teaches — never a
differently-shaped pipeline invented from general GlobalMart knowledge. If
the notebook has a matching `.html` slide deck, skim it too for how the
session's own framing/narrative was pitched to learners; reuse that framing
rather than inventing a new one.

### 5. Load the reference docs you need

- `references/architecture-facts.md` and `references/fact-sales-schema.md` —
  for correctness of any schema claim the scenario makes (real Bronze/Silver/
  Gold table and column names, the two `fact_sales` framings and which one
  applies). Never state a table/column name that isn't grounded in these
  docs or in the sibling notebook itself.
- `references/adls-sample-data.md` — for real data-shape facts (row counts,
  columns, the `addresses`-folder-vs-`address`-table gotcha) if the scenario
  has the learner work directly with raw sample files rather than already-
  built `gbmart` tables.
- `references/tone-reference.md` — for narrative style only (business-
  framing sentences, the phased shape of a good Code Solution). Never copy
  this file's *structure* — see the warning at the top of that file.
- `references/naming-convention.md` — background on why Step 2 works the way
  it does; you generally won't need to re-read this once you've internalized
  Step 2, but it's there if a naming question comes up.
- `references/tag-vocabulary.md` — the approved sub-tag list for every Input
  you tag (see Step 6's Tags rule above).

### 6. Draft the `.md` following `references/lms-format-spec.md` exactly

- YAML frontmatter with a non-empty `name` (the single field with a real,
  confirmed historical failure behind its absence), plus `content_type`,
  `overview`, `learning_objectives`, `prerequisites`, `duration`, `level`,
  `industries`, `tags` — all grounded in what the sibling notebook actually
  teaches.
- One or more `## Scenario N — Name` blocks, each with a business-narrative
  `**Overview:**` (style from `tone-reference.md`) and ideally an
  `**Outcome:**`.
  - **Scenario Block Structure Rule:** Insert a blank line before each
    `## Scenario N` heading (to clearly separate it from the previous
    Scenario's Solution blocks). The FIRST element after the heading must be
    a `**Overview:**` section that fully restates the business context — never
    assume the learner remembers the prior scenario. This prevents the
    scenario-switching narrative from bleeding into the previous Input's
    answer field.
- Globally-numbered `## Input N` headings — **track ONE running counter for
  the entire file, across every Scenario, and never reset it.** This is the
  single most important structural rule in this whole skill; get it wrong
  and the file will fail import the same way it has before.
- Every Input uses one of the 5 known `**Type:**` values (Text, Short Answer,
  Choice, Code, File Upload) with that type's correct required fields — see
  `lms-format-spec.md` for the exact field list per type.
- **Tags are question-gated, not universal — and a Text Input gets NO Tags
  heading at all, not an empty one.** A Text Input (pure instructional, no
  `**Question:**` field at all) omits the `**Tags**` heading entirely — it
  doesn't appear anywhere in that Input's block. Every other type (Short
  Answer, Choice, Code, File Upload) — anything that actually asks the
  learner something — gets a `**Tags**` heading followed by at least one
  tag, drawn from `references/tag-vocabulary.md`. Tags classify what's being
  *assessed*; a Text Input assesses nothing, so a Tags heading on one — even
  an empty one — is noise, not thoroughness. (This was tightened twice: first
  to "empty but present," then to "absent entirely," after direct user
  feedback that even an empty heading was still unwanted.)
- **Every Code and Choice Input ends with a complete `**Solution:**`,
  never blank.** A `**Snippet:**`/`**Solution:**` field left empty is not
  "the learner fills this in" — it's a defect. Write the real, correct code
  plus 1-3 sentences of explanation, grounded in the sibling notebook's
  actual behavior (see Step 4). Verify every number you state — segment
  counts, percentages, row counts — against what the source data or notebook
  actually produces; never estimate or round from memory.
- **Keep Solution code as simple and clear as possible — prefer building
  blocks already used earlier in the same file over a more compact but less
  obvious technique.** If a straightforward combination of `filter()`,
  `groupBy()`, and `join()` gets the same answer as a clever one-liner using
  a pattern not yet introduced (e.g. conditional aggregation with
  `count(when(...))`), write the straightforward version — even if it's a
  few more lines. A learner should be able to trace every Solution back to
  concepts the file already taught them, not be surprised by a new trick
  that happens to be shorter.
- **One Code Input per business question — never split "worked example that
  already solves it" from "now restate the answer."** A recurring defect in
  earlier drafts of these files: an instructional Text cell fully solves a
  business question via a given example, and a separate Short-Answer cell
  then asks the learner to just read off that same output. This teaches
  nothing (the code was never theirs to write) and wastes an Input. Instead:
  a short instructional Text cell should show only mechanical setup (e.g.
  registering temp views, deriving one intermediate column) or a trivial
  sanity-check unrelated to the real business questions — then every actual
  business question is its own single `Type: Code` Input, where the learner
  writes the query/code AND states the finding in one submission.
- **State the language, never the technique, in the question.** Every Code
  Input's prompt must explicitly say "Using Spark SQL, ..." or "Using
  PySpark, ..." at the start — matching its `**Language:**` field exactly —
  so the learner is never unsure which cell type to reach for. But the
  prompt must stay business-language only: never name a specific SQL clause,
  join type, function, or PySpark construct in the question itself (no
  "Hint: use a LEFT JOIN...", no "using YEAR(...)", no "using
  when/otherwise"). That technique explanation belongs only in the
  `**Solution:**`, after the fact — naming it in the question hands the
  learner the approach before they've had to find it themselves.

### 7. Scan the draft for anything credential-shaped before writing

Before saving, re-read your own draft looking for anything resembling a real
host/username/password/token/connection string. `tone-reference.md`
documents a real leaked credential found in one of the tone-reference source
files — that is not a hypothetical risk. If the source notebook has a
placeholder-style setup cell (it should, per `safety-rules.md` rule 6),
mirror that exact placeholder pattern (`YOUR_CATALOG`/`YOUR_SCHEMA` plus a
"how to obtain this yourself" comment) in the `.md` — never a literal value,
and never even a realistic-looking fake one that could be mistaken for live.

### 8. Write the file, then validate before declaring success

```
python scripts/validate_lms_md.py "Databricks\Day{N}\Day{N}_{order}_HOL{x}_Topic_Name.md"
```

Read its output. This script checks exactly the things known to have broken
a real import before: a missing/empty `name` in frontmatter, Input headings
that aren't H2 or aren't one strictly-increasing sequence from 1 (no resets,
no gaps), every Input having one of the 5 known Types, and the question-gated
Tags rule (a Tags heading with at least one tag on every Short
Answer/Choice/Code/File Upload Input, NO Tags heading at all on every Text
Input). **Never report the `.md` as done without having run this and read
the output** — this is the "re-open and check" half of the Day 6 lesson, and
skipping it is exactly how that incident happened.

### 9. Report back

Tell the user: the exact path written, the total Input count and Scenario
count (both printed by the validator), the validation pass/fail detail, and
any grounding gap you had to flag instead of guess (a fact not in the
sibling notebook or the bundled references, or something that would need a
live Databricks check this skill can't perform).

## The 9 universal guardrails

These apply to every hands-on `.md` this skill helps produce, no exceptions:

1. **Never silently overwrite.** Check for the target file first; if it
   exists, show what would change and stop.
2. **Never invent an architecture fact.** If a table/column name or schema
   detail isn't in the sibling notebook, `references/architecture-facts.md`,
   or `references/fact-sales-schema.md`, ask rather than guessing something
   plausible-sounding.
3. **Never write a Solution or Input that implies triggering a real job,
   pipeline, cluster, or SQL warehouse.** Jobs/Workflow config shown in a
   Solution is always an inspectable, clearly-commented-as-illustrative
   Python dict, never a real API call.
4. **Never embed a real credential.** Always a placeholder plus a comment
   explaining how to obtain the real value manually.
5. **Never claim to have live-checked sayli's Databricks workspace (or the
   real `gbmart` workspace at all).** This skill has no live Databricks
   access, period. Flag any such gap to the human instead of fabricating a
   check.
6. **After writing, re-open and validate before declaring success.** Run
   `scripts/validate_lms_md.py` and read its output every time.
7. **Never leave a Code or Choice Solution blank.** Every one gets real,
   verified code/reasoning — recompute the actual numbers from the source
   data if you have access to it, don't estimate.
8. **Never let a question's prompt reveal the technique its own Solution
   uses.** State the language (SQL vs. PySpark), never the clause/function/
   construct — see Step 6 above for the exact rule and examples.
9. **Never reach for a compact-but-unfamiliar technique in a Solution when a
   simpler one using already-taught building blocks gets the same answer.**
   A few extra lines of `filter`/`groupBy`/`join` a learner can trace beats
   one clever line they can't.
10. **Every `## Scenario N` block must start with clean context, never assume
    the learner remembers the previous scenario.** Insert a blank line before
    each `## Scenario N` heading (separation from the prior Solution block).
    The first content after `## Scenario N` must be a `**Overview:**` section
    that restates the business context in full — not a terse reference to the
    prior scenario. This prevents scenario-switching context from bleeding into
    the previous question's answer, and ensures each scenario is self-contained.

## Bundled references — when to read each

- `references/lms-format-spec.md` — the exact spec (frontmatter fields,
  Scenario/Input structure, the 5 Type values and their required fields, the
  question-gated Tags rule) plus the full `Day1_5_HOL_PySpark_SparkSQL_ADLS.md`
  embedded as a worked example. Read this every time you draft — it's the
  single source of truth for structure.
- `references/tag-vocabulary.md` — the exact list of `data-wrangling / ...`
  and `data-quality / ...` sub-tags already in use elsewhere in this project
  (plus the handful of other tool/skill tags this file uses). Draw every tag
  you assign from this list; only add a new sub-tag if the task genuinely
  isn't covered by anything here, and keep it in the same 2-level
  `parent / child (skill)` shape — never a 3-level tag.
- `references/architecture-facts.md` — the real `gbmart` environment, the 2
  ingestion pathways / 8 Bronze tables (incl. two catalogs), the "4 sources" trap, Bronze/Silver
  casing rule. Read for any scenario referencing the pipeline-accurate
  schema.
- `references/fact-sales-schema.md` — both `fact_sales` framings and the
  decision rule between them, full real column list, the natural-key/
  degenerate-dimension gotchas. Read for any scenario touching `fact_sales`
  or its dimensions.
- `references/adls-sample-data.md` — real folder/row/column facts for the
  raw sample data in `reference_materials/reference_data_for_hands_on_docs/adls_data_new/`,
  including the `addresses`-folder vs. `address`-table naming gotcha and the
  note that `returns` is supplementary, not one of the 7 official Bronze
  tables. Read when a scenario has the learner work with raw files directly.
- `references/tone-reference.md` — STYLE ONLY narrative/voice guidance
  (business-narrative scenario framing, the phased Code-Solution shape) and
  the credential-leak cautionary example. Never copy this file's structure.
- `references/naming-convention.md` — background on the `{order}`/`{x}`
  algorithm and its real edge cases, explaining why this skill derives its
  filename from the sibling notebook instead of recomputing (Step 2).
- `references/safety-rules.md` — all 6 safety patterns (practice schema,
  no live job triggers, sayli read-only, idempotent writes, no touching real
  governance, no real credentials), each with a real verbatim snippet. Read
  before drafting any Input whose Solution writes code.
