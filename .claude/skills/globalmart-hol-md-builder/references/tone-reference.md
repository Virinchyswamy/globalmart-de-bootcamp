# Tone Reference — STYLE ONLY, never structure

**Read this file for narrative voice and the shape of a good Code-type
Solution. Never copy this file's structural format into an actual `.md` you
write** — see `lms-format-spec.md` for the real, LMS-import-proven structure
(YAML frontmatter, `## Scenario N`, globally-numbered `## Input N`). The
files this tone was extracted from use a visually similar but structurally
different, incompatible export format (no frontmatter, `##### Input N`
headers that reset per scenario) from a different platform, and that
structure is exactly what caused this project's two real historical LMS
import failures ("Duplicate input number", "'name' is required" — see
`lms-format-spec.md` and the git commits `8094f64`/`b60d56a` that fixed
them). If you find yourself typing `#####` anywhere in a new hands-on `.md`,
stop — that is the wrong file's shape leaking in.

Source files (read for tone, in
`C:\Yvirinchy\tred-alch-adv-dbx\reference_materials\reference_data_for_hands_on_docs\`):
- `5425554a-...salescategoryanalysisreportofglobalmart.md`
- `539d04c1-...vendorperformanceanalysisandrankingframework.md`
- (others in the same folder follow the same two patterns below)

## Pattern 1 — Business-narrative scenario framing

The good, reusable idea in these files is opening a scenario by dropping the
learner into a concrete role at GlobalMart, with a specific business problem,
before any technical instruction appears. Real examples:

> "GlobalMart, an emerging E-Commerce player in North America and Europe,
> specializes in Technology, Office Supplies, and Furniture across 120
> markets. You recently joined GlobalMart as a Data Analyst. The upper
> management wants a detailed categorical analysis..."

> "GlobalMart is a fast-growing e-commerce company that sells products
> across three lines of business... The Vendor Operations team wants to
> track delivery health and identify vendors that frequently breach delivery
> expectations. Your task is to help the Data Intelligence team prepare
> vendor-level performance reports..."

Extract the pattern, not the exact wording: name a real GlobalMart team or
stakeholder (Vendor Operations, Data Intelligence, upper management,
marketing), state what they want to know or fix in plain business language,
and only then transition into the technical task. This is the same
instinct already used in `Day1_5_HOL_PySpark_SparkSQL_ADLS.md`'s Scenario
`**Overview:**` fields (e.g. "Before you can use data in Databricks, it
needs to live somewhere the cluster can read it...") — keep using it there,
inside the proven `**Overview:**` field, not as a structural addition.

## Pattern 2 — The phased shape of a Code-type `**Solution:**` field

The genuinely useful structural idea to reuse (inside the `**Solution:**`
field of a `Type: Code` Input — see `lms-format-spec.md` for that field's
exact place in the real format) is this fixed rhetorical shape, observed
consistently across both example files:

1. **Understanding the Problem** — restate what the business actually needs,
   in plain language, before any SQL/Python appears.
2. **Where is this data found?** — a short table naming the source
   table(s)/column(s) this solution reads from and why.
3. **Logic Before Building the Solution** — a numbered plan of the
   transformation steps, in prose, before any code.
4. **Phased build** — for a solution complex enough to need it, break the
   final query/script into labeled phases (`Phase 1 — ...`, `Phase 2 — ...`)
   each with its own small code fragment, building toward the final answer.
5. **Final Working Solution** — the complete, runnable code in one block.
6. **Common Mistakes & Point Deductions** — a short numbered list of the
   specific ways a learner's answer commonly goes wrong (wrong join,
   forgetting `PARTITION BY`, formatting before filtering, etc.) and why each
   one is wrong.

This shape works because it forces the solution to teach the *reasoning*,
not just present an answer — reuse it inside any Code-type Input's
`**Solution:**` field for a hands-on scenario complex enough to warrant it
(a simple one-line query solution doesn't need all six sections; use
judgment).

## The cautionary example — why credentials never appear in generated content

One of the source files in `reference_materials/reference_data_for_hands_on_docs/` contains a real,
plaintext database connection detail — a SQL Server hostname, a real
username, and a real plaintext password — pasted directly into an Input's
body text as a `>[!NOTE]` callout telling learners "here's the login to use."
That value is **not reproduced in this reference doc** (deliberately — citing
it here again would just create a second leak), but its existence is the
concrete, real reason `safety-rules.md` rule 6 is not hypothetical: a
generated hands-on `.md` must never embed a real credential of any kind, only
a placeholder plus a comment on how a learner obtains their own real value
(exactly like `Day1_5_HOL_PySpark_SparkSQL_ADLS.md`'s Volume-path pattern —
see `safety-rules.md` rule 6 for that pattern). If you ever see a real-looking
`Server name:` / `Username:` / `Password:` triplet while drafting from any
reference material, that is the shape to strip out, never to copy forward.
