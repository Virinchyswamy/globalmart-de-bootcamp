# Observed Notebook Structure — The Shape Every Real Notebook Follows

This isn't an arbitrary template — it's the shape that emerged, consistently,
across Day 1/7/9/12's real notebooks, because it solves real teaching
problems: a header that tells you what you need before you start, objectives
that set expectations, phased steps that build on each other with visible
checkpoints, and a closing that turns "I ran some cells" into "I can state
what I learned." Follow the shape; the specific headings can flex to fit the
session's content.

## 1. Header / metadata cell (first cell, markdown)

Always a title, a one-line course tag, then a small metadata table. The exact
columns vary by notebook but always answer "what came before this, what does
this depend on, how long will it take, what does it produce":

**Real excerpt — Day 7 HOL 2** (`Day7_3_HOL2_Build_Gold_Layer_Fact_Sales.ipynb`):
```markdown
# Day 7 | Hands-On 2: Build Gold Layer — `fact_sales`
### GlobalMart Data Engineering Bootcamp

| | |
|---|---|
| **Grain** | One row per order line item (`order_items`) |
| **Source** | `silver.order_items`, `silver.orders`, `silver.products`, `silver.payments`, `silver.address`, `gold.dim_date` |
| **Target** | `gbmart.gold.fact_sales` |
| **Duration** | ~2.5 hours (2 sessions) |
```

**Real excerpt — Day 11 ILT 4** uses a slightly different column set, oriented
around what's real vs. practice-only (`Day11_4_ILT4_Data_Governance_Unity_Catalog.ipynb`):
```markdown
| **Calendar slot** | Day 12 · 9:30 AM–10:30 AM · ILT |
| **Duration** | 60 minutes |
| **Builds on** | Day 6/7 (`gbmart.gold` dimensions + `fact_sales`), Day 9/10 (Delta version history via `DESCRIBE HISTORY`) |
| **Reads (real, read-only)** | Grants on the real `gbmart` catalog/schema/table, real version history of `gbmart.gold.dim_customer` |
| **Writes (practice only)** | One synthetic table + two functions in your own `main.YOUR_SCHEMA` — **never** `gbmart.*` |
```
Note the explicit **Reads (real)** vs. **Writes (practice only)** split — use
this shape whenever a notebook mixes real read-only access with practice-schema
writes, so a reader never has to guess which lines are "safe to run against
the real thing."

**Real excerpt — Day 9 HOL 2** uses **Follows** to anchor continuity
(`Day9_5_HOL2_Handling_Incremental_Data_Bronze_Silver.ipynb`):
```markdown
| **Follows** | ILT 3 — CDF-Based Incremental Loading |
| **Duration** | ~2 hours |
| **Output** | A real CDF-based Bronze→Silver incremental refresh for `payments`, plus a verified check of the watermark-based `orders`/`order_items` pipeline |
```

## 2. Learning Objectives (bullet list, right after the header)

3-6 bullets, each a concrete, checkable capability — not a vague topic label.
Compare a weak version ("Learn about incremental refresh") to the real one:

**Real excerpt — Day 7 HOL 2:**
```markdown
### Learning Objectives
- Build a real, multi-table Gold fact table step by step, verifying row counts after every join
- Handle the address one-to-many trap correctly (from ILT 1) inside a real build
- Make a fact-table cell safely re-runnable without restarting from scratch
- Serve the finished fact table through real, business-facing Gold views
```

## 3. Phased Step/Phase/Part structure (markdown + code cell pairs)

Every multi-step build breaks into named phases — `Step N`, `Phase X`, or
`Part N` depending on the session's shape — each with a markdown cell stating
the phase's goal *before* the code that does it. HOLs that are exercises
(rather than pure builds) use `Phase A/B/C...`; sequential pipeline builds use
`Step 1/2/3...`; multi-strategy labs use `Part 1/2...`.

**Real excerpt — Day 1 HOL** (`Day1_5_HOL_PySpark_SparkSQL_ADLS.ipynb`):
```markdown
---
## Phase A — Understand the Data
**Goal:** Read all three CSVs from the Volume and understand their structure.
```
followed later by Phase B (Spark SQL), Phase C (PySpark transformations),
Phase D (data quality check), Phase E (write to Bronze) — each phase is a
self-contained unit with its own goal statement, sub-steps (`A1`, `A2`, `B1`...),
and (for this HOL) an embedded **Q:** prompt with a blank `*Your answer:*`
line for learners to fill in, which is this course's lightweight in-notebook
comprehension check pattern for HOLs aimed at concept practice rather than a
pipeline build.

**Real excerpt — Day 7 HOL 2** uses `Step N` for a strictly sequential build:
```markdown
---
## Step 5 — Look Up `Address_ID` (the One-to-Many Trap from ILT 1)
`silver.address` links to `Customer_ID`, not to a specific order — a customer
can have more than one address...
```

## 4. Row-count verification print after every join

This is the single most consistent code pattern across every multi-join build
in this course, and it exists because silent fan-outs from a bad join are
much cheaper to catch mid-build than after the table is "done":

**Real excerpt — Day 7 HOL 2, repeated after every join (Steps 2-6):**
```python
enriched_df = enriched_df.join(address_primary, "Customer_ID", "left")
print(f"Rows after address join: {enriched_df.count():,}")
print(f"Rows with no matching Address_ID: {enriched_df.filter(col('Address_ID').isNull()).count():,}")
print("Compare this row count to Step 4's -- it must be UNCHANGED. If it grew, the address")
print("ranking above isn't collapsing multi-address customers down to one row each -- go back and check it.")
```
Note the pattern: print the new count, print a null-check for the join key
just resolved, and print a plain-language statement of what the count
*should* do (stay the same / shouldn't drop) so a learner can self-diagnose
without needing to already know the answer.

## 5. Key Takeaways (markdown, near the end)

3-5 numbered points that state the *lesson*, not a recap of steps already
taken. Compare:

**Real excerpt — Day 7 HOL 2:**
```markdown
## Key Takeaways
1. **Verify the row count after every single join** — a fact-table build with 6+ joins is exactly where silent fan-outs hide, and they're much cheaper to catch mid-build than after the table is already "done."
2. **`is_current = true` filters are not optional** wherever you join to an SCD2 dimension from a fact table.
3. **Natural-key joins were a deliberate choice, not a shortcut** — you now know exactly what it costs (no point-in-time accuracy) and why it was still the right call for this program.
```

## 6. Submission Checklist (HOLs only)

A literal checkbox list of concrete, verifiable deliverables — screenshots,
specific counts, specific tables/views created. This is what a learner submits
against, so every line must be something they can point to and say "done."

**Real excerpt — Day 7 HOL 2:**
```markdown
### Submission Checklist
- [ ] Every step's printed row count reviewed — no unexplained jumps
- [ ] `gbmart.gold.fact_sales` written successfully
- [ ] Both `vw_monthly_category_sales` and `vw_regional_sales` created and queried
- [ ] Screenshot of the Step 8 write confirmation + one view's output for submission
```

**Real excerpt — Day 1 HOL** uses a fenced-code-block checklist with
fill-in-the-blank answers instead of pure checkboxes — appropriate for a
comprehension-focused HOL rather than a pipeline-build HOL:
```
Submission Checklist
────────────────────────────────────────────────────────
✅ Volume created and three folders (customers/, orders/, products/) uploaded
── Total rows (customers / orders / products):     ______
```
Either shape is fine — pick checkboxes for "did you build these real
artifacts" HOLs, fill-in-the-blank for "did you understand these results" HOLs.

## 7. Self-Check (ILTs, optional variant of Submission Checklist)

**Real excerpt — Day 11 ILT 4:**
```markdown
## Self-Check
- [ ] I can name all 4 levels of the Unity Catalog hierarchy, in order.
- [ ] I can explain, out loud, why today's row-filter/mask demo ran on a practice table instead of a real Gold-layer table.
```
Use this instead of a Submission Checklist for concept-only ILTs that don't
produce a gradable artifact.

## 8. Reset / cleanup cell (optional, end of file)

Write-heavy HOLs that build real tables often end with a commented-out reset
block, so the notebook is safely re-runnable without manual cleanup:

**Real excerpt — Day 7 HOL 2:**
```python
# spark.sql("DROP VIEW IF EXISTS gbmart.gold.vw_monthly_category_sales")
# spark.sql("DROP VIEW IF EXISTS gbmart.gold.vw_regional_sales")
# spark.sql("DROP TABLE IF EXISTS gbmart.gold.fact_sales")
# print("Reset complete")
```

## Instructions cell convention

The header cell (or the cell right after it) always ends with a one-line
instruction on how to run the notebook, tuned to whether it's fill-in-the-blank
or run-as-is:
- HOL with blanks: *"Run each cell with Shift + Enter. Fill in any `# YOUR CODE HERE` blanks before running."*
- ILT/HOL with no blanks: *"Run each cell in order with Shift + Enter, or Run All. No blanks to fill in today — every cell runs as-is."*
