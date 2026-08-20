# Slide Component Catalog + Tone Notes

Source: verified directly against `Databricks\Day1\Day1_1_ILT1_GlobalMart_Problem_Statement.html`
(the approved slide-deck exemplar — a confirmed byte-level CSS/JS match of the
original `SQL_Python\Day1\Day1_1_ILT1_Basic_SQL_Revision\basic sql revison.html`
— this file moved here 2026-07-19 when the standalone `Chennai_batch` repo was
merged in as the `SQL_Python` track, still the same file, just a new path),
plus a skim of the original for tone, and a count of slides in
`Databricks\Day6\Day6_4_HOL1_Star_Schema_Design.html` (22 slides) and
`Databricks\Day9\Day9_1_ILT1_Need_For_Incremental_Loading.html` (14 slides) to
confirm the rhythm this project has settled into.

## The non-negotiable rule — read this one first

**Humor and analogy never target a named real learner negatively.** This
skill rotates real names from the current cohort's roster (Hyderabad 2026 by
default) into worked-example slides for realism — "Sneha needs to find last month's top-selling category"
reads better than "The user needs to find...". But the moment a joke, a
mistake, a "wrong answer," or any negative framing would land on that name,
stop and either remove the name (use "a learner" / "you") or reframe the
joke to land on the *concept* or *situation* instead. The exemplar's own
running example (`Rahul`, from the original `basic sql revison.html`) is
proof this works: he's used as a realistic protagonist doing real work
("These functions are the tools Rahul uses to clean it up before any
analysis") — never as someone who got something wrong. The user confirmed
this explicitly as house style; it is not a style suggestion, it's a hard
line for this skill.

## Slide types

Four `slide-*` classes, each combined with the base `.slide` class and shown
one at a time by the nav JS:

- **`slide-cover`** — the opening slide only. Dark gradient background
  (`linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)`), centered `<h1>`
  title, `.subtitle` paragraph, a `.badge` pill stating Day/Session/type, and
  optionally a small "what we'll cover today" teaser line. Real excerpt:
  ```html
  <div class="slide slide-cover active">
    <h1>GlobalMart Problem Statement</h1>
    <p class="subtitle">Who GlobalMart is, what their data problem is, and the 2-source Databricks architecture we'll build over 13 days</p>
    <div class="badge">Day 1 &nbsp;·&nbsp; ILT 1 &nbsp;·&nbsp; Trainer-Led Session</div>
  </div>
  ```
  `active` is only ever on the first slide in the markup (slide 1) — the JS
  manages which slide has it after that.

- **`slide-section`** — used for the agenda slide (always slide 2) and any
  section-divider/closing/bridge-to-next slide. Lighter background (`#1e293b`),
  a small uppercase `.section-tag` label above an `<h2>`. Real excerpt:
  ```html
  <div class="slide slide-section">
    <div class="section-tag">Overview</div>
    <h2>What We're Covering Today</h2>
  ```
  Closing/bridge section slides typically add
  `style="text-align:center; align-items:center;"` to center their content —
  the exemplar's "13-Day Journey" and "You're Ready for ILT 2" slides both do
  this.

- **`slide-content`** — the workhorse slide type for one idea per slide:
  objectives, concepts, comparisons, schema walkthroughs. Plain dark
  background (`#0f172a`), `<h3>` heading. Almost always contains a `.two-col`
  or `.three-col` grid, a `.card`, a `table.sql-table`, or an `.order-list`
  underneath — rarely just bare paragraphs.

- **`slide-demo`** — for any live-code walkthrough. Slightly different dark
  background (`#0c1a2e`) with a left accent border in amber
  (`border-left: 4px solid #f59e0b`), an amber `<h3>`, and a `.demo-label`
  caption line under it (e.g. "Live in the workspace" / "Watch, then try it
  yourself"). Always contains a `<pre>` code block. HOL decks lean much more
  heavily on this slide type than ILT decks — Day 6's HOL1 deck (22 slides)
  has 10 `slide-demo` slides; Day 9's ILT1 deck (14 slides) has 1.

## Grid layouts

- **`.two-col`** — `display:grid; grid-template-columns: 1fr 1fr;` — the most
  common layout on a `slide-content` slide: concept/explanation on one side,
  a card/table/diagram on the other.
- **`.three-col`** — three equal columns, used for the agenda slide and any
  "three things to compare/recap" slide (e.g. the closing "Recap / Up Next /
  Closing Check" triptych).

## `.card`

A bordered dark panel (`background:#1e293b; border:1px solid #334155;
border-radius:12px`) with an `<h4>` header in accent blue and body text in
`#cbd5e1`. The default container for a short list, a stat table, or a
"why this matters" note. Real excerpt:
```html
<div class="card">
  <h4>🏢 The Business</h4>
  <ul>
    <li>GlobalMart — a mid-sized e-commerce company</li>
    <li>~10,000+ customers, ~100,000+ products</li>
  </ul>
</div>
```

## `.highlight-box` (+ `warn` / `success` variants)

A callout box for the single most important sentence on a slide — an
"instructor question," a caution, or a payoff statement. Base variant uses a
blue border; `.warn` (amber border, dark amber background) flags a gotcha or
scope limitation; `.success` (green border, dark green background) marks a
positive outcome or recap point. Real excerpts:
```html
<div class="highlight-box warn">
  <p><strong style="color:#f59e0b;">Day 3 side-exploration only</strong> — REST API (exchange rates) + GraphDB (customer relationships) are useful patterns you'll see later, but they do <strong>not</strong> feed this pipeline.</p>
</div>
<div class="highlight-box success">
  <p><strong style="color:#22c55e;">What we're building instead:</strong> one combined, always-up-to-date "balance" — the <code>fact_sales</code> table...</p>
</div>
```
The "Instructor question:" pattern lives inside a plain `.highlight-box`:
```html
<div class="highlight-box">
  <p><strong style="color:#38bdf8;">Instructor question:</strong> "Have you ever seen Finance report one revenue number while Sales reports a different one?" That's Data Silos...</p>
</div>
```

## `.pill` (+ `pill-blue` / `pill-green` / `pill-amber` variants)

Small inline rounded-pill labels, used inside prose or lists to flag a
milestone (e.g. an assessment day). Real excerpt:
```html
<li>D7 Build Gold — dimensions, bridge table, fact_sales, Z-order · <span class="pill pill-blue">Assessment 1</span></li>
```

## `.order-list`

A numbered step list with a filled-circle counter badge before each item
(CSS `counter()`, not a literal `<ol>` number) — used for any "here's the
sequence" content: pipeline steps, today's schedule, pain points in order.
Real excerpt:
```html
<ol class="order-list">
  <li><strong>Data Silos</strong> — transaction data and reference files live in separate systems with no automatic connection</li>
  <li><strong>No Single Source of Truth</strong> — different teams pull numbers differently; reports don't match</li>
</ol>
```

## `table.sql-table`

A dark-themed data table — blue header row, alternating-row body. Used for
any tabular comparison or schema/metrics listing. Real excerpt:
```html
<table class="sql-table">
  <tr><th>Metric</th><th>Value</th></tr>
  <tr><td>Customers</td><td>~10,000+</td></tr>
</table>
```

## `<pre>` code blocks with syntax-highlight spans

Code samples use a `<pre>` block (not `<code>` alone) with hand-applied
`<span>` classes for coloring — this is manual syntax highlighting, not a
JS library, so every keyword/string/etc. needs its own span:
- `.kw` — keywords (`WHERE`, `SELECT`) — bold red-orange
- `.fn` — function names — purple
- `.str` — string literals/values — light blue
- `.cm` — comments — muted italic gray
- `.col` — column names — blue
- `.tbl` — table names — orange

Real excerpt:
```html
<pre><span class="cm">-- Query-based mode, in plain terms:</span>
Runs: <span class="kw">WHERE</span> updated_at &gt; last_run_time
INSERT <span class="cm">→ new row appears, gets picked up next run</span></pre>
```
Plain diagram/ASCII-art `<pre>` blocks (e.g. an architecture flow diagram)
skip the spans entirely and just use plain text — not every `<pre>` needs
syntax highlighting, only actual code/SQL samples.

## Navigation + counter (never modify the mechanism, only the counter text)

```html
<nav>
  <div class="logo">DAY 1 · ILT 1 — Problem Statement &amp; Architecture</div>
  <div class="controls">
    <button onclick="changeSlide(-1)">&#8592; Prev</button>
    <span class="slide-counter" id="counter">1 / 16</span>
    <button onclick="changeSlide(1)">Next &#8594;</button>
  </div>
</nav>
```
```javascript
let current = 0;
const slides = document.querySelectorAll('.slide');
const counter = document.getElementById('counter');

function showSlide(n) {
  slides[current].classList.remove('active');
  current = (n + slides.length) % slides.length;
  slides[current].classList.add('active');
  counter.textContent = (current + 1) + ' / ' + slides.length;
}

function changeSlide(dir) { showSlide(current + dir); }

document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') changeSlide(1);
  if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   changeSlide(-1);
});
```
The initial `id="counter"` text (`1 / 16` above) must state the *actual*
total slide count in the deck you write — the JS recalculates it correctly
after the first navigation, but the first paint before any click uses
whatever hardcoded text is in the HTML, so it must already be right.

## Tone notes

- **Plain-language analogy before technical content.** The exemplar never
  opens a concept with jargon — "Imagine you have money in two different
  banks, and neither bank can see the other's balance" comes before any
  mention of Postgres/ADLS on that slide.
- **One idea per slide.** Don't stack "the problem" and "the solution" on one
  slide — the exemplar spends a full slide each on the problem statement, the
  analogy, the business-question list, and the solution overview.
- **Light emoji/personality, not gimmicky.** Section-card headers use one
  emoji as a visual anchor (🏢 🔌 🎯 🔍 🔧 📚), never more than one per
  header, never inside body text.
- **✅ / ❌ annotations** appear in the original reference deck's recap/closing
  cards ("✅ Recap") to mark done/avoid items quickly — use sparingly, mainly
  on closing or comparison slides.
- **"Instructor question:" callout** — a real, recurring pattern for ending a
  content slide on a discussion prompt rather than just information. Use it
  on a `slide-content` slide where a pause-and-ask moment makes sense, not on
  every slide.
- **A running named-learner example, used lightly.** See the non-negotiable
  rule at the top of this file — this is where `scripts/read_learner_list.py`
  comes in for this skill's decks.
- **Observed slide-count rhythm.** ILT decks run roughly 10-16 slides
  (Day 1 ILT1: 16, Day 9 ILT1: 14). HOL decks can run longer because they
  carry more `slide-demo` steps (Day 6 HOL1: 22). Match the shape to the
  session's actual content — don't pad or compress to hit a number.
