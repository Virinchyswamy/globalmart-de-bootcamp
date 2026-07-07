---
name: globalmart-slide-deck-builder
description: >
  Builds one dark-themed, self-contained HTML slide deck (the .html file that
  accompanies an ILT or HOL .ipynb) for ONE GlobalMart Databricks bootcamp
  session, Chennai 2026 cohort, using the approved slide template
  (slide-cover/slide-section/slide-content/slide-demo, cards, highlight-box,
  pill, order-list, sql-table, syntax-highlighted code blocks) and real
  learner names from the Chennai 2026 roster as rotating worked-example
  protagonists. Use this whenever the user asks to build, generate, or
  present slides, a slide deck, an HTML explainer, or "the deck" for a
  GlobalMart Day N ILT or HOL -- including phrasings like "make the slides
  for Day 11's DLQ session", "build the HTML for the star schema hands-on",
  or "I need something to present before running the notebook". This skill
  always reads the matching .ipynb (and .md, if one exists) for the same
  session first and reflects their real content -- run
  globalmart-notebook-builder (and globalmart-hol-md-builder, for a HOL)
  first if those don't exist yet for this session.
---

# GlobalMart Slide Deck Builder

## Why this skill exists

Every ILT/HOL session in this course is presented from a slide deck before
the notebook is actually run — the deck sets up the "why" in plain language
before the room switches to real code. Every deck in this repo shares one
dark-theme visual system (the exemplar's CSS/JS), and every deck's *content*
must actually match the real notebook it introduces — a deck that shows a
nicer-sounding but wrong schema, or a phase the notebook doesn't have, misleads
the room before a single cell has run. This skill bundles the verified
component catalog and the real architecture facts so a new deck doesn't have
to re-derive either from memory, and it exists specifically so the deck's
claims stay grounded in a real, already-built notebook rather than in a
plausible-sounding guess.

## Workflow

### 1. Identify the target session and locate its siblings

Glob `C:\Yvirinchy\DE notebooks\Day{N}\Day{N}_*_{ILT|HOL}*_*.ipynb` for the
day/topic the user names. This is the ground truth this deck must reflect —
if it doesn't exist yet, **stop and tell the user to run
`globalmart-notebook-builder` first.** Never invent slide content that isn't
grounded in a real notebook; a deck built ahead of its notebook is exactly
the kind of drift this project's design is trying to avoid.

If the located session is a HOL, also Glob for a sibling
`Day{N}_*_HOL*_*.md` (the LMS hands-on file, built by
`globalmart-hol-md-builder`). It's optional — most built HOLs don't have one
yet — but when present, its `## Scenario N — Name` headers and `## Input N`
structure often make good section/agenda slide headers, since that's the
same structure the learner will be graded against. If it's missing, proceed
using the notebook alone and note the gap in your final report; don't block
on it and don't fabricate scenario content to fill the gap.

If the user names a topic instead of a day+type ("the DLQ one"), match it
against notebook titles/filenames you find via Glob rather than asking them
to look up the exact filename themselves.

### 2. Derive the output filename from the located `.ipynb` — don't recompute it

Take the located notebook's exact basename and swap `.ipynb` → `.html`
(e.g. `Day7_3_HOL2_Build_Gold_Layer_Fact_Sales.ipynb` →
`Day7_3_HOL2_Build_Gold_Layer_Fact_Sales.html`). **Do not independently
recompute `{order}`/`{type}`/`{x}` from the naming algorithm.**
`references/naming-convention.md` documents the full algorithm and several
real cases where it goes wrong if re-derived from scratch (a DEMO/REF file
inserted mid-day shifting later order numbers, a hands-on session split by
Lunch or spilling across a day boundary throwing off a naive count) —
`globalmart-notebook-builder` already resolved all of that correctly when it
named the sibling notebook. Recomputing independently risks a slide-deck
filename that silently disagrees with its own notebook's number, which
defeats the entire point of the naming convention (sibling files sorting
together in a folder listing). The notebook's real, already-decided filename
is always the more reliable source than re-deriving the number yourself.

### 3. Check for collisions before writing anything

Glob for the exact target `.html` path. If it already exists, **stop and show
what would change instead of silently overwriting it** — this is the same
Day 6 incident lesson every skill in this project carries: a background
process once silently overwrote correct content with stale content, and it
wasn't caught until someone noticed wrong facts in the output.

### 4. Read the notebook (and `.md`, if present) fully as ground truth

Read the whole notebook — not just the first few cells. You need: the title/
metadata, the stated Learning Objectives, the phase/step structure (this
usually maps directly to one `slide-content` slide per phase), any code
pattern worth showing on a `slide-demo` slide (not necessarily every cell —
pick the 1-3 that best show the session's core idea), and the Key Takeaways
(these usually become the closing recap slide). If a `.md` exists, read its
Scenario/Input structure too for section-header language.

Cross-check any schema claim you're about to put on a slide against
`references/architecture-facts.md` and `references/fact-sales-schema.md`
before it goes on the deck — **never let a slide state a fact the notebook
doesn't actually demonstrate.** If the notebook and a reference doc seem to
disagree, trust what the notebook actually does (it's the more specific,
more concretely-verified source for that one session) and flag the
discrepancy in your final report rather than silently picking one.

### 5. Pick a rotating learner protagonist

Run `scripts/read_learner_list.py --pick <day> <session_seed>` (e.g.
`--pick 7 HOL2_Build_Gold_Layer_Fact_Sales`, using the notebook's own
type+topic slug as the session seed so the same session always gets the same
name if this skill runs again). Use the returned name **lightly**, for any
slide with a worked-example analogy: a real name as a realistic protagonist
in a scenario ("Sneha needs to find last month's top-selling category before
the 9am standup") — never as the butt of a joke, a mistake, or any negative
framing. Humor lands on the concept or situation, never on the named learner.
This was explicitly confirmed with the user as house style, not a style
suggestion — see the "non-negotiable rule" at the top of
`references/slide-tone-and-components.md` for the full reasoning and the
"Rahul" precedent it's modeled on. Not every deck needs a named-learner
slide — use one only where a worked-example analogy actually helps, the same
way the exemplar uses "Rahul" on exactly one slide, not throughout.

### 6. Build the deck from the template — never rewrite the CSS/JS from memory

Start from `assets/slide_deck_template.html`. Its `<style>` and `<script>`
blocks are copied byte-for-byte from the approved exemplar
(`Day1_1_ILT1_GlobalMart_Problem_Statement.html`, itself a confirmed
byte-level match of the original studio deck) — copy this file in and fill
its `<!-- SLIDES GO HERE -->` placeholder with real `<div class="slide ...">`
blocks. Do not hand-write the CSS or navigation JS from memory; even a
close paraphrase risks a subtly broken selector or a counter that stops
working, and there's no reason to take that risk when the real, working
version is sitting right there in `assets/`.

Read `references/slide-tone-and-components.md` for the full component
catalog (slide types, grid layouts, card/highlight-box/pill/order-list/
sql-table, the `<pre>` span classes) with real excerpts for each, and for the
tone notes (plain analogies before jargon, one idea per slide, light emoji,
the "Instructor question:" callout pattern). Produce, in order:

1. A cover slide (`slide-cover`) — title, one-line subtitle, Day/session badge.
2. An agenda/section slide (`slide-section`) — 2-3 cards previewing today's
   content, mirroring the notebook's Learning Objectives.
3. One `slide-content` slide per notebook phase/concept — using `two-col`/
   `three-col`/`card`/`highlight-box`/`table.sql-table`/`order-list` as fits
   the content, plain-analogy language before jargon, one idea per slide.
4. A `slide-demo` slide for any live-code walkthrough worth showing — real
   code from the notebook (with real `<pre>` syntax-highlight spans), never
   invented code.
5. A closing recap/bridge-to-next slide (`slide-section`), typically a
   three-card "Recap / Up Next / Closing Check" pattern.

Match the observed rhythm: ILT decks run roughly 10-16 slides; HOL decks can
run longer (up to ~22) because they carry more `slide-demo` steps. Don't pad
or compress to hit a specific number — let the session's real content decide
the count.

Update the `<title>`, the nav `.logo` text, and the initial `id="counter"`
text (`1 / N`) to match this deck's real title and final slide count — the
counter's initial text is a static string in the HTML, not computed until
the first navigation click, so it must already be correct on first paint.

### 7. Write the file, then validate before declaring success

Write the `.html`, then run:
```
python scripts/validate_html_deck.py "Day{N}\Day{N}_{order}_{TYPE}{x}_Topic_Name.html"
```
Read its output. A tag-balance error, a missing/modified nav-or-JS snippet, a
slide-count/counter mismatch, or an external network reference outside a
`<pre>` block all mean the file is broken and needs fixing before anything
else. **Never report a deck as done without having run this and read the
output** — this is the same "re-open and check" discipline every skill in
this project follows, and skipping it is exactly how the Day 6 incident
happened.

### 8. Report back

Tell the user: the exact path written, the slide count, which learner name(s)
were used and on which slide(s), the validation result, and — this is the
part that lets the user actually spot-check fidelity — which specific real
notebook (and `.md`, if used) facts appear on which slides. Cite specifics
("Slide 6 shows the `Address_ID` one-to-many window-function pattern from
Step 4 of the notebook") rather than a generic "the deck covers the
notebook's content."

## The 7 guardrails

These apply to every deck this skill helps produce, no exceptions:

1. **Never silently overwrite.** Check for the target file first; if it
   exists, show what would change and stop.
2. **Never invent a fact.** If a schema/architecture detail isn't in
   `references/architecture-facts.md` or `references/fact-sales-schema.md`,
   or isn't actually demonstrated in the source notebook, ask rather than
   guessing something plausible-sounding.
3. **Never write or show code implying a real job/pipeline/cluster/warehouse
   trigger.** Any Jobs/Workflow config shown on a slide is an inspectable,
   clearly-commented-as-illustrative Python dict, never a real API call.
4. **Never embed a real credential** — even in an illustrative code-snippet
   slide. Always the same placeholder pattern the source notebook uses
   (`YOUR_CATALOG`/`YOUR_SCHEMA`-style) plus a comment on how to obtain the
   real value manually.
5. **Never claim to have live-checked sayli's workspace** (or the real
   `gbmart` workspace at all). This skill has no live Databricks access,
   period. Flag any such gap to the human instead of fabricating a check.
6. **Always validate after writing.** Run `scripts/validate_html_deck.py` and
   read its output every time before declaring success.
7. **Never let humor or an analogy target a named real learner negatively.**
   Rotate names via `scripts/read_learner_list.py` for realistic
   representation only — a real name is always a protagonist doing real work,
   never a punchline, never the one who got it wrong.

## Bundled references — when to read each

- `references/architecture-facts.md` — the real `gbmart` environment, the 2
  ingestion pathways / 7 Bronze tables, the "4 sources" trap, Bronze/Silver
  casing rule. Read for any pipeline-accurate session's deck.
- `references/fact-sales-schema.md` — both `fact_sales` framings and the
  decision rule between them, full real column list, the natural-key/
  degenerate-dimension gotchas. Read for any deck touching `fact_sales` or
  its dimensions.
- `references/safety-rules.md` — all 6 safety patterns, each with a real
  verbatim snippet. Read before putting any code sample on a `slide-demo`
  slide.
- `references/naming-convention.md` — the `{order}`/`{x}` algorithm plus
  worked real examples, and (at the bottom) exactly why this skill derives
  its filename from the sibling notebook instead of recomputing it. Read
  before finalizing any filename, especially if anything about the sibling
  notebook's own naming looks unusual.
- `references/slide-tone-and-components.md` — the full component catalog
  with real excerpts (slide types, grids, cards, highlight-box/pill/
  order-list/sql-table, `<pre>` span classes, nav/counter JS) plus the tone
  notes and the non-negotiable never-mock-a-named-learner rule. Read while
  drafting every deck.

## Bundled scripts

- `scripts/read_learner_list.py` — loads the Chennai 2026 roster and
  deterministically rotates a learner name per (day, session). Run with
  `--pick <day> <session_seed>` for one name, or `--self-test` to see the
  rotation across several sessions at once.
- `scripts/validate_html_deck.py` — structural validator (tag balance, nav/JS
  integrity, slide-count-vs-counter match, no external network refs outside
  `<pre>`). Run against every deck this skill writes before reporting success.

## Bundled assets

- `assets/slide_deck_template.html` — the verbatim CSS+JS starting point for
  every new deck, with a `<!-- SLIDES GO HERE -->` placeholder. Always copy
  this in; never reconstruct the styling from memory.
