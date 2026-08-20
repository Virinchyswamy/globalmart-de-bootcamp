---
name: Day 12 HOL 2 — The Genie Problem Statement
content_type: Scenario
overview: GlobalMart's VP of Sales currently files a ticket every time she wants one number out of Gold, waits a day, and gets back a screenshot she can't drill into. This hands-on has you verify the real gbmart.gold objects a Genie Agent needs, build a real Genie Agent over them (entirely through the Databricks workspace UI, since that part can't be scripted), register 4 known-good sample questions, then deliberately push the Agent past its comfort zone with 5+ questions of your own designed to find where natural-language-to-SQL actually struggles.
learning_objectives:
  - Confirm the real Gold-layer objects a Genie Agent needs are present and queryable before building it
  - Build a real Genie Agent over gbmart.gold and register known-good sample questions against it
  - Deliberately push a working Genie Agent past its comfort zone with ambiguous, multi-view, governed, and out-of-scope questions
  - Recognize which parts of a Genie workflow are scriptable and which are UI/chat-only
prerequisites:
  - Completed Day 12 ILT 1 (Genie & Semantic Layer) and Day 12 HOL 1 (Unity Catalog Permissions)
  - A Databricks workspace with access to create a Genie Agent over gbmart.gold
duration: 90 minutes
level: Intermediate
industries:
  - e-commerce
tags:
  - databricks (tool)
  - sql (tool)
  - genie / semantic-layer (skill)
---

---

## Scenario 1 — Verify the Real Objects Genie Will Point At

**Overview:** A Genie Agent for GlobalMart's Gold layer needs to be scoped to 8 specific real objects: `gbmart.gold.fact_sales`, its 6 dimensions (`dim_customer`, `dim_product`, `dim_date`, `dim_address`, `dim_payment_method`, `dim_orders`), and its 2 certified views (`vw_monthly_category_sales`, `vw_regional_sales`) built back in Day 7 HOL 2. Before clicking through the UI to build the Agent, this scenario confirms all 8 actually exist and are queryable right now.

**Outcome:** Confirmed row counts for all 8 real `gbmart.gold` objects.

---

## Input 1

**Type:** Text

### Verify the 8 objects

```python
tables_to_check = [
    "fact_sales",
    "dim_customer", "dim_product", "dim_date",
    "dim_address", "dim_payment_method", "dim_orders",
    "vw_monthly_category_sales", "vw_regional_sales",
]

for obj in tables_to_check:
    df = spark.table(f"gbmart.gold.{obj}")
    print(f"{obj:<28} {df.count():>10,}")
```

If any object is missing or shows 0 rows, go back and re-run the relevant Day 7 HOL 2 (`fact_sales`, both views) or Day 6 HOL 1 (dimensions) cell before continuing.

---

## Input 2

**Type:** Short Answer

**Question:** List the row count printed for each of the 8 objects. Are all 8 present and queryable?

**Template:** null

**Tags**
- databricks (tool)

---

## Scenario 2 — Read the Real Genie Docs First

**Overview:** Day 12 ILT 1 taught the underlying concepts — what a Genie Agent is, what a semantic layer is — but not the current product surface, since Databricks' own docs move faster than any slide deck can keep up with (this course's own materials already had to be corrected once for exactly this reason: "Genie Space" became "Genie Agent"). Before touching the UI, read the two real, current Databricks Genie documentation pages.

**Outcome:** Answers to 4 real questions that can only be answered by actually reading the current documentation, not by recalling ILT 1's slides.

---

## Input 3

**Type:** Text

### Read these first

- `docs.databricks.com/aws/en/genie/` — the Genie overview, what the product actually covers today.
- `docs.databricks.com/aws/en/genie/set-up` — "Set up a Genie Agent," the real, current click-path and configuration reference. Phase 1 (Scenario 3) is built from this page.

---

## Input 4

**Type:** Short Answer

**Question:** The Genie overview page splits "Genie" into 3 distinct things, not 1. What are they, and which one is this entire hands-on session actually about?

**Template:** null

**Tags**
- genie / semantic-layer (skill)

---

## Input 5

**Type:** Short Answer

**Question:** Find the exact sentence in the docs that states what a Genie Agent used to be called. Why does it matter that this course's own ILT 1 and this HOL both had to be corrected mid-course because of exactly this rename?

**Template:** null

**Tags**
- genie / semantic-layer (skill)

---

## Input 6

**Type:** Short Answer

**Question:** The setup page lists 4 things a data analyst configures on a Genie Agent — Unity Catalog scope is one. Name the other 3.

**Template:** null

**Tags**
- genie / semantic-layer (skill)

---

## Input 7

**Type:** Short Answer

**Question:** What does the documentation say happens if you don't provide enough of your own sample/common questions when setting up a Genie Agent? How should that finding change how much effort you put into Scenario 4?

**Template:** null

**Tags**
- genie / semantic-layer (skill)

---

## Scenario 3 — Build the Genie Agent

**Overview:** With the 8 real objects verified (Scenario 1) and the current docs read (Scenario 2), this scenario builds the actual Genie Agent — entirely by clicking through the Databricks workspace UI, since this is the one part of a Genie workflow that genuinely cannot be scripted in a notebook.

**Outcome:** A real Genie Agent, scoped to all 8 verified objects, with Instructions written in your own words describing what GlobalMart sells and pointing Genie at the two certified views for common questions.

---

## Input 8

**Type:** Text

### Build the Agent

1. Click **Genie Agents** in the left sidebar.
2. Click **New** in the upper-right corner.
3. Choose your data sources, all from `gbmart.gold`: `fact_sales`; the 6 dimension tables; and the 2 certified views (`vw_monthly_category_sales`, `vw_regional_sales`). Click **Create**.
4. In the Agent's own **Instructions** field, write a short brief for Genie: what GlobalMart sells, what grain `fact_sales` is at, and a pointer that the two certified views already answer the most common questions.

>[!IMPORTANT]
>The instructions you write here live on the Genie Agent itself — personal, and separate from the `ALTER TABLE ... COMMENT` statements ILT 1 had you practice on a throwaway copy. Nothing in this Agent setup writes to a real Gold table's metadata.

---

## Input 9

**Type:** File Upload

**Question:** Take a screenshot of your created Genie Agent showing all 8 data sources in its scope, and your own written Instructions text (not left blank). Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)

---

## Scenario 4 — Register the Known-Good Questions

**Overview:** With the Genie Agent built (Scenario 3), this scenario registers 4 question-and-SQL pairs — drafted back in Day 12 ILT 1 specifically for this step — each mapping to one of the two certified views built in Day 7 HOL 2 (`vw_monthly_category_sales`, `vw_regional_sales`). Registering them turns Genie's natural-language matching into pattern-matching against something already known-good, instead of reconstructing the join and aggregation logic from raw `fact_sales` every time.

**Outcome:** All 4 known-good sample questions registered on the Genie Agent and confirmed correct in the live chat.

---

## Input 10

**Type:** Text

### The 4 known-good questions

| Sample question | Maps to |
|---|---|
| "What was our revenue by category last month?" | `SELECT category, SUM(total_revenue) FROM vw_monthly_category_sales WHERE ... GROUP BY category` |
| "Which states generate the most revenue?" | `SELECT state, SUM(total_revenue) FROM vw_regional_sales GROUP BY state ORDER BY total_revenue DESC` |
| "What is our average discount by category?" | `SELECT category, AVG(avg_discount_given) FROM vw_monthly_category_sales GROUP BY category` |
| "How many orders came from each region?" | `SELECT state, city, total_orders FROM vw_regional_sales` |

Type each question into your Genie Agent's Sample Questions area alongside its SQL, then actually ask Genie each one in the chat and confirm the answer.

---

## Input 11

**Type:** Choice

**Question:** Why do all 4 of these sample questions map to a certified view (`vw_monthly_category_sales` or `vw_regional_sales`) instead of a fresh query against raw `fact_sales`?

**Options:**
- Because Genie cannot query `fact_sales` directly under any circumstances
- Because registering them against a certified, already-agreed-upon view turns Genie's guessing into pattern-matching against something known-good, instead of re-deriving the same join and aggregation logic live every time
- Because `fact_sales` does not contain the columns these questions need
- Because certified views run faster than any query against `fact_sales`

**Correct Options:**
- Because registering them against a certified, already-agreed-upon view turns Genie's guessing into pattern-matching against something known-good, instead of re-deriving the same join and aggregation logic live every time

**Solution:**
`vw_monthly_category_sales` and `vw_regional_sales` already encode the correct joins and aggregations that category managers and regional ops leads agreed on (Day 7 HOL 2). Pointing Genie's sample questions at these views means it can pattern-match a real user's question against a known-good example, rather than reconstructing the same multi-table join and `GROUP BY` from scratch every single time it's asked something similar.

**Tags**
- genie / semantic-layer (skill)

---

## Input 12

**Type:** Short Answer

**Question:** Confirm: did all 4 known-good questions return answers in the live Genie chat matching what the SQL above would actually return? Note anything unexpected.

**Template:** null

**Tags**
- genie / semantic-layer (skill)

---

## Scenario 5 — Now Go Break It

**Overview:** The 4 known-good questions from Scenario 4 prove Genie *can* work — they don't prove you understand it. This final scenario has you ask at least 5 questions nobody wrote SQL for ahead of time, deliberately probing where natural-language-to-SQL translation actually struggles: forcing a real join across both certified views, asking something deliberately ambiguous, touching a column governed/masked back in Day 12 HOL 1, and asking for something genuinely out of scope.

**Outcome:** At least 5 self-written questions asked and logged, with at least one genuine "Genie got this wrong, refused, or asked for clarification" moment.

---

## Input 13

**Type:** Text

### Question ideas to push past the known-good floor

- **Force a real join** — e.g. "which customers in the top-revenue state also got the biggest average discount?" — does Genie combine both views correctly, or guess a shortcut?
- **Be deliberately ambiguous** — e.g. "what's our biggest category?" (biggest by revenue? units? order count?) — does Genie ask you to clarify, or silently pick one and hope?
- **Touch a governed column** — `dim_customer` has real PII columns (`email`, `phone_number`) governed back in Day 12 HOL 1. Ask Genie for a customer's email directly and watch whether that governance applies automatically.
- **Ask something that doesn't exist** — e.g. "what's our profit margin by category?" if margin isn't a column anywhere in scope. Does Genie say so honestly, or invent something plausible-looking?

At least 5 questions total — pick from these or invent your own.

---

## Input 14

**Type:** Short Answer

**Question:** List your 5+ self-written questions, what Genie actually did for each, and your verdict for each (correct / wrong / honestly uncertain — e.g. it asked for clarification or said it didn't have the data).

**Template:** null

**Tags**
- genie / semantic-layer (skill)

---

## Input 15

**Type:** Choice

**Question:** If Genie is asked a deliberately ambiguous question like "what's our biggest category?" (biggest by revenue? by units? by order count?), what is the most trustworthy behavior for it to show?

**Options:**
- Silently pick one interpretation and answer as if there were no ambiguity
- Ask the user to clarify which interpretation they mean
- Refuse to answer the question at all
- Always default to whichever measure is listed first in the table

**Correct Options:**
- Ask the user to clarify which interpretation they mean

**Solution:**
An ambiguous question genuinely has more than one reasonable reading. Silently picking one (without saying so) risks giving a confidently wrong answer to a business user who has no way to know which interpretation was chosen. The trustworthy behavior is surfacing the ambiguity back to the user rather than resolving it invisibly.

**Tags**
- genie / semantic-layer (skill)

---

## Input 16

**Type:** Short Answer

**Question:** When you asked Genie to return a customer's email directly, what happened? Connect what you observed to what you set up in Day 12 HOL 1.

**Template:** null

**Tags**
- genie / semantic-layer (skill)

---

## Input 17

**Type:** File Upload

**Question:** Take a screenshot of your Genie chat showing at least one question where it got something wrong, refused, or asked for clarification. Upload it here.

**Max No. of Files:** 1

**Max File Size:** 10

**Allowed File Types:** ANY, IMAGE

**Tags**
- databricks (tool)
