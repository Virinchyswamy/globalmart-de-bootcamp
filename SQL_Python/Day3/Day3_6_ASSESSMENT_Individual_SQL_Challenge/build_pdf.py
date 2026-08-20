"""
build_pdf.py — generates the Day 3 individual, pen-and-paper SQL assessment.

Two outputs, run separately:
    python build_pdf.py --mode student   -> "Day3_Individual_SQL_Assessment - Student Booklet.pdf"
    python build_pdf.py --mode key       -> "Day3_Individual_SQL_Assessment - Instructor Answer Key.pdf"

Why this exists: the activity is closed-book / pen-and-paper (no laptop,
phone, or internet during the test), so every learner's section carries its
own full copy of the reference material — the real course ER diagram plus a
syntax cheat sheet, both on a single page, repeated immediately before each
learner's 3 questions — since nobody can look anything up mid-test. Learner
roster comes from the existing, already-solved deterministic roster loader
in the slide-deck-builder skill (reused, not reimplemented). Column casing
in every question/solution matches the real ER diagram image exactly
(lowercase snake_case, except the all-caps COGS), so what's printed is
internally consistent.

Rendering: HTML -> PDF via Playwright's bundled Chromium (already installed
in this environment; no new PDF library needed).
"""

import argparse
import base64
import re
import sys
from pathlib import Path

# Reuse the existing roster loader instead of re-implementing xlsx parsing.
_SKILL_SCRIPTS = Path(__file__).resolve().parents[3] / ".claude" / "skills" / "globalmart-slide-deck-builder" / "scripts"
sys.path.insert(0, str(_SKILL_SCRIPTS))
from read_learner_list import load_learners  # noqa: E402

HERE = Path(__file__).resolve().parent
ER_IMAGE_PATH = Path(r"C:\Yvirinchy\DE notebooks\datasets\Dataset for content\Er_diagram.png")


def er_image_data_uri() -> str:
    b64 = base64.b64encode(ER_IMAGE_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def display_name(username: str) -> str:
    """'harsh.kumar01' -> 'Harsh Kumar'; 'aditi' -> 'Aditi'."""
    parts = username.split(".")
    cleaned = []
    for p in parts:
        p = re.sub(r"\d+$", "", p)  # drop trailing digits, e.g. kumar01 -> kumar
        if p:
            cleaned.append(p.capitalize())
    return " ".join(cleaned) if cleaned else username


def first_name(display: str) -> str:
    return display.split(" ")[0]


# ---------------------------------------------------------------------------
# Shared CSS — print-friendly: light background, dark text, blue/teal accents
# only on headers/borders (a dark deck theme wastes ink on paper).
# ---------------------------------------------------------------------------
CSS = """
@page { size: A4; margin: 16mm 14mm; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Segoe UI', Arial, sans-serif;
  color: #1a2433;
  font-size: 12.5px;
  line-height: 1.55;
}
h1, h2, h3, h4 { font-family: 'Segoe UI', Arial, sans-serif; color: #0f2a4a; }
.page-break { page-break-before: always; }
.avoid-break { page-break-inside: avoid; }

/* --- Cover --- */
.cover { text-align: center; padding-top: 60mm; }
.cover .kicker { font-size: 12px; letter-spacing: 2px; text-transform: uppercase; color: #2563eb; font-weight: 700; margin-bottom: 10px; }
.cover h1 { font-size: 30px; font-weight: 800; margin-bottom: 14px; }
.cover .sub { font-size: 14px; color: #445067; max-width: 480px; margin: 0 auto 26px; line-height: 1.7; }
.rules-box { border: 2px solid #0f2a4a; border-radius: 10px; padding: 18px 24px; max-width: 420px; margin: 0 auto; text-align: left; background: #f4f7fb; }
.rules-box h4 { font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; color: #b91c1c; }
.rules-box li { margin-bottom: 6px; font-size: 12.5px; }
.joke { margin-top: 22px; font-size: 12px; color: #6b7385; font-style: italic; }

/* --- Section headers --- */
.section-tag { font-size: 10.5px; text-transform: uppercase; letter-spacing: 1.5px; color: #0891b2; font-weight: 700; margin-bottom: 3px; }
.section-title { font-size: 16px; font-weight: 800; margin-bottom: 8px; color: #0f2a4a; border-bottom: 2px solid #0f2a4a; padding-bottom: 5px; }

/* --- ER diagram (real course image, embedded) --- */
.er-img-wrap { margin: 8px 0 10px; text-align: center; }
.er-img-wrap img { width: 100%; max-width: 100%; height: auto; border: 1px solid #c7d0dd; border-radius: 6px; }
.er-caption { font-size: 9.5px; color: #6b7385; margin-top: 3px; }

/* --- Syntax cheat sheet --- */
.cheat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 6px; }
.cheat-card { border: 1px solid #c7d0dd; border-radius: 6px; padding: 6px 9px; background: #fbfcfe; }
.cheat-card h4 { font-size: 10.5px; color: #0f2a4a; margin-bottom: 3px; }
pre.code { background: #10182a; color: #e7edf7; border-radius: 5px; padding: 6px 8px; font-size: 9px; line-height: 1.42; overflow-x: auto; font-family: 'Consolas', monospace; white-space: pre-wrap; }
.cheat-card p { font-size: 9.5px; color: #445067; margin-top: 3px; }

/* --- Learner sections --- */
.name-banner { background: linear-gradient(90deg, #0f2a4a, #2563eb); color: #fff; border-radius: 10px; padding: 14px 20px; margin-bottom: 16px; }
.name-banner .label { font-size: 10.5px; text-transform: uppercase; letter-spacing: 1.5px; opacity: .85; }
.name-banner h2 { color: #fff; font-size: 22px; margin-top: 2px; }
.name-banner .meta { font-size: 11px; opacity: .85; margin-top: 4px; }

.q-block { border: 1px solid #c7d0dd; border-radius: 10px; padding: 14px 18px; margin-bottom: 16px; }
.q-head { display: flex; align-items: baseline; gap: 8px; margin-bottom: 6px; }
.q-num { background: #0f2a4a; color: #fff; font-weight: 800; font-size: 11px; border-radius: 999px; padding: 3px 10px; }
.q-title { font-size: 14px; font-weight: 800; color: #0f2a4a; }
.q-text { font-size: 12.5px; margin-bottom: 8px; }
.q-output { font-family: 'Consolas', monospace; font-size: 11px; background: #eef4fb; border: 1px dashed #2563eb; border-radius: 6px; padding: 6px 10px; margin-bottom: 8px; }
.hint { border-left: 3px solid #0891b2; background: #ecfeff; border-radius: 0 6px 6px 0; padding: 6px 10px; font-size: 11px; margin-bottom: 6px; }
.hint b { color: #0891b2; }
.write-space { border: 1px dashed #9aa5b8; border-radius: 8px; height: 34mm; margin-top: 8px; background:
  repeating-linear-gradient(#fff 0 8mm, #dfe4ec 8mm 8.2mm); }

/* --- Q4 bonus / creative block --- */
.q-block.fun { border-color: #d8b4fe; background: #faf5ff; }
.q-block.fun .q-num { background: #7c3aed; }
.q-block.fun .q-title { color: #6d28d9; }
.q-block.fun .not-graded { display: inline-block; font-size: 9.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; color: #7c3aed; background: #f3e8ff; border: 1px solid #d8b4fe; border-radius: 999px; padding: 2px 9px; margin-left: 6px; vertical-align: middle; }
.draw-space { border: 1.5px solid #c4b5fd; border-radius: 8px; height: 42mm; margin-top: 8px; background: #fff; }

/* --- Instructor key --- */
.sol h4 { font-size: 12px; color: #0f2a4a; margin: 8px 0 4px; }
.rubric li { font-size: 11.5px; margin-bottom: 4px; }
.badquery { border-left: 4px solid #b91c1c; }
.goodquery { border-left: 4px solid #16a34a; }
"""

SYNTAX_SHEET_HTML = """
<div class="cheat-grid">
  <div class="cheat-card">
    <h4>JOIN skeleton</h4>
    <pre class="code">SELECT ...
FROM table_a a
JOIN table_b b ON a.key = b.key
JOIN table_c c ON b.key2 = c.key2
WHERE ...
GROUP BY ...</pre>
  </div>
  <div class="cheat-card">
    <h4>WHERE operators</h4>
    <pre class="code">=  &lt;&gt;  &gt;  &lt;  &gt;=  &lt;=
BETWEEN a AND b
IN (a, b, c)
LIKE 'A%'
IS NULL / IS NOT NULL</pre>
  </div>
  <div class="cheat-card">
    <h4>Aggregates + GROUP BY</h4>
    <pre class="code">SUM(col)  COUNT(col)  AVG(col)
COUNT(DISTINCT col)
GROUP BY col1, col2</pre>
    <p>Every non-aggregated SELECT column must be in GROUP BY.</p>
  </div>
  <div class="cheat-card">
    <h4>Window function skeleton</h4>
    <pre class="code">RANK() OVER (
    PARTITION BY col
    ORDER BY other_col DESC
) AS rnk</pre>
    <p>Can't filter a window function in the same SELECT's WHERE — CTE it first, then filter.</p>
  </div>
  <div class="cheat-card">
    <h4>Date functions</h4>
    <pre class="code">YEAR(date_col)
MONTH(date_col)
DATENAME(month, date_col)  -- "January"
DATEDIFF(day, d1, d2)</pre>
  </div>
  <div class="cheat-card">
    <h4>CASE WHEN</h4>
    <pre class="code">CASE WHEN cond THEN 'A'
     WHEN cond2 THEN 'B'
     ELSE 'C' END</pre>
  </div>
  <div class="cheat-card">
    <h4>PIVOT skeleton</h4>
    <pre class="code">SELECT key_col, [2017], [2018]
FROM long_format_table
PIVOT(
    SUM(value_col)
    FOR [year_col] IN ([2017],[2018])
) AS pvt</pre>
    <p>Square brackets around pivoted values are mandatory.</p>
  </div>
  <div class="cheat-card">
    <h4>Optimization checklist (Day 3)</h4>
    <pre class="code">1. No SELECT *
2. Filter with WHERE, not HAVING
3. FROM the biggest table first,
   JOIN outward to smaller ones
4. GROUP BY beats DISTINCT</pre>
  </div>
</div>
"""


def reference_page_html(image_uri: str) -> str:
    return f"""
<div class="page-break">
  <div class="section-tag">Reference — Read Before Answering</div>
  <div class="section-title">Schema (ER Diagram) &amp; Syntax Cheat Sheet</div>
  <div class="er-img-wrap">
    <img src="{image_uri}" alt="GlobalMart ex_ tables ER diagram">
    <div class="er-caption">All column names below are written exactly as shown in this diagram — including COGS in capitals, everything else lowercase.</div>
  </div>
  {SYNTAX_SHEET_HTML}
</div>
"""


def question_block(qnum: int, title: str, text: str, output: str, hints: list[str]) -> str:
    hint_html = "".join(f'<div class="hint"><b>Hint {i+1}:</b> {h}</div>' for i, h in enumerate(hints))
    return f"""
<div class="q-block avoid-break">
  <div class="q-head"><span class="q-num">Q{qnum}</span><span class="q-title">{title}</span></div>
  <div class="q-text">{text}</div>
  <div class="q-output">Expected columns: {output}</div>
  {hint_html}
  <div class="write-space"></div>
</div>
"""


def fun_block(name: str) -> str:
    fn = first_name(name)
    return f"""
<div class="q-block fun avoid-break">
  <div class="q-head"><span class="q-num">Q4</span><span class="q-title">Draw It Out</span><span class="not-graded">Not graded — just for fun</span></div>
  <div class="q-text">{name}, put the pen down on SQL for a minute. Three cases cracked today: the Logistics
  Partner mystery, the Segment Profit mystery, and the Slow Query crime scene. In the box below, draw {fn} as
  the detective who solved all three — stick figures welcome, magnifying glass optional, artistic talent
  100% not required. This is the one question on the entire paper where "I have no idea" is a completely
  acceptable technical approach.</div>
  <div class="draw-space"></div>
</div>
"""


def learner_questions(name: str) -> str:
    fn = first_name(name)
    q1 = question_block(
        1, "The Logistics Partner Scorecard",
        f'{name}, Operations forwards a message from the VP: <em>"Before we renew any shipping partner '
        f'contracts next quarter, I want a real scorecard — not vibes. Who is actually fast, and who is '
        f'quietly costing us customers?"</em> Nobody on the team has ever actually pulled this number before, '
        f'which {fn} suspects is either a very good sign or a very bad one.<br><br>'
        f'<strong>Task:</strong> for each logistics partner, calculate how many delivered orders they have '
        f'handled and their average number of days from purchase to delivery. Rank the partners from fastest '
        f'average delivery time (rank 1) to slowest, so the VP knows exactly who to keep and who to have an '
        f'uncomfortable conversation with. Only count orders that actually reached the customer — an order '
        f'still "in transit" doesn\'t have a delivery time to average yet.',
        "partner_name | delivered_order_count | avg_delivery_days | speed_rank",
        [
            "Join ex_orders to ex_logistics_partners on partner_id. Filter to order_status = 'delivered' first "
            "— you can't average a delivery time that hasn't happened.",
            "avg_delivery_days = AVG(DATEDIFF(day, order_purchase_date, order_delivered_date)), grouped by "
            "partner. Rank with RANK() OVER (ORDER BY avg_delivery_days <b>ASC</b>) — ascending, because here "
            "lower is better, unlike most ranking examples you've seen so far.",
        ],
    )
    q2 = question_block(
        2, "Profit by Segment, Year over Year",
        f'{name}, Finance sends the request this time — not Robert, a nice change of pace. <em>"We want to '
        f'know if our Home Office customers are becoming more profitable, or if we\'re just moving more units '
        f'to them at thinner and thinner margins. Same question for Consumer and Corporate. Show me 2017 versus '
        f'2018, side by side, the way you laid out that order-count report earlier this week."</em><br><br>'
        f'<strong>Task:</strong> for each customer segment, calculate total profit (sales amount minus cost of '
        f'goods sold) for 2017 in one column and 2018 in another — the same pivoting technique from the PIVOT '
        f'session, just pointed at a completely different question this time.',
        "segment | [2017] | [2018]",
        [
            "Build the long version first: one row per segment per year with SUM(sales_amount - COGS) as "
            "profit — join ex_transactions &#8594; ex_orders &#8594; ex_customers, and use "
            "YEAR(order_purchase_date).",
            "Same PIVOT skeleton as the reference sheet, just pivoting a profit total by segment instead of an "
            "order count by month: <code>FOR order_year IN ([2017],[2018])</code>.",
        ],
    )
    q3 = question_block(
        3, "Spot the Slow Query",
        f'{name}\'s manager forwards a query with the subject line "this works fine, not sure why everyone\'s '
        f'complaining." It was written by a contractor who left the project three weeks ago — conveniently, '
        f'right before the optimization session {fn} sat through on Day 3. The query below does return the '
        f'correct numbers; Finance has been using its output all month without one complaint about accuracy. '
        f'The complaint is entirely about the 4 minutes and 40 seconds it takes to run, every single time '
        f'someone refreshes the dashboard.<br><br>'
        '<pre class="code">SELECT DISTINCT *\n'
        'FROM ex_customers c, ex_orders o, ex_transactions t\n'
        'WHERE c.customer_id = o.customer_id\n'
        '  AND o.order_id = t.order_id\n'
        'GROUP BY c.segment, o.order_status\n'
        "HAVING c.segment = 'Consumer' AND o.order_status = 'delivered'</pre>"
        f'<strong>Task:</strong> (a) list 3 specific things wrong with this query — "it\'s slow" doesn\'t count '
        f'as one of them — and (b) rewrite it so it does the same job properly.',
        "Written answer: 3 named issues + 1 rewritten query",
        [
            "Re-read Best Practices 1–3 from the optimization session: don't SELECT *, filter with WHERE not "
            "HAVING, and start FROM the table with the most rows instead of the smallest one.",
            "This query breaks more than one of those three at once — keep checking after you find the first "
            "issue.",
        ],
    )
    return q1 + fun_block(name) + q2 + q3


def build_student_html() -> str:
    learners = load_learners()
    names = sorted({display_name(u) for u, _ in learners})
    image_uri = er_image_data_uri()

    cover = f"""
<div class="cover">
  <div class="kicker">GlobalMart Data Engineering Bootcamp</div>
  <h1>Day 3 Individual SQL Assessment</h1>
  <p class="sub">Three SQL problems, your own logic, pen and paper only — plus one bonus round that has nothing to do with SQL at all.</p>
  <div class="rules-box">
    <h4>Before you start</h4>
    <ul>
      <li>No laptop, no phone, no internet. Just this booklet and a pen.</li>
      <li>Every learner's section opens with its own copy of the schema and syntax reference — flip back to it
      any time, you don't need to hold anything in memory.</li>
      <li>Write your SQL in the ruled space under each question.</li>
      <li>Hints are optional. Full marks either way.</li>
    </ul>
  </div>
  <p class="joke">If you get stuck, take a breath, re-read the hint, and remember: even Robert's "quick one"
  emails took three days to answer correctly.</p>
</div>
"""

    sections = []
    for name in names:
        banner = f"""
<div class="name-banner">
  <div class="label">Day 3 Individual Assessment</div>
  <h2>{name}</h2>
  <div class="meta">3 SQL problems + 1 for-fun bonus &middot; pen and paper &middot; hints available below each question</div>
</div>
"""
        sections.append(reference_page_html(image_uri))
        sections.append(f'<div class="page-break">{banner}{learner_questions(name)}</div>')

    return f"<html><head><style>{CSS}</style></head><body>{cover}{''.join(sections)}</body></html>"


def build_key_html() -> str:
    image_uri = er_image_data_uri()
    intro = f"""
<div class="section-tag">Instructor Only</div>
<div class="section-title">Day 3 Individual SQL Assessment — Answer Key</div>
<p>Same 3 problems as the student booklet (generic form below — students see their own name woven into the
problem text instead of "the learner"). Reference solution and a grading rubric follow each. Column casing
matches the real ER diagram exactly (lowercase, except COGS).</p>
<div class="er-img-wrap"><img src="{image_uri}" alt="GlobalMart ex_ tables ER diagram"></div>
"""

    q1 = """
<div class="q-block avoid-break">
  <div class="q-head"><span class="q-num">Q1</span><span class="q-title">The Logistics Partner Scorecard</span></div>
  <div class="q-text">For each logistics partner: delivered order count, average days purchase-to-delivery,
  ranked fastest to slowest. Output: partner_name | delivered_order_count | avg_delivery_days | speed_rank.</div>
  <div class="sol">
    <h4>Reference solution</h4>
    <pre class="code goodquery">WITH partner_perf AS (
    SELECT
        lp.partner_name,
        COUNT(o.order_id) AS delivered_order_count,
        AVG(DATEDIFF(day, o.order_purchase_date, o.order_delivered_date)) AS avg_delivery_days
    FROM ex_orders o
    JOIN ex_logistics_partners lp ON o.partner_id = lp.partner_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_date IS NOT NULL
    GROUP BY lp.partner_name
)
SELECT
    partner_name,
    delivered_order_count,
    avg_delivery_days,
    RANK() OVER (ORDER BY avg_delivery_days ASC) AS speed_rank
FROM partner_perf
ORDER BY speed_rank;</pre>
    <h4>Rubric</h4>
    <ul class="rubric">
      <li>Filters to order_status = 'delivered' (and/or delivered_date IS NOT NULL) BEFORE aggregating —
      otherwise the average is polluted by orders with no delivery date</li>
      <li>DATEDIFF(day, purchase, delivered) wrapped in AVG(), grouped by partner</li>
      <li>RANK() ordered ASCENDING on avg_delivery_days — flag this explicitly if a learner defaults to DESC out
      of habit from earlier ranking exercises</li>
      <li>Accept ROW_NUMBER() or DENSE_RANK() in place of RANK() — same intent</li>
    </ul>
  </div>
</div>
"""

    q2 = """
<div class="q-block avoid-break">
  <div class="q-head"><span class="q-num">Q2</span><span class="q-title">Profit by Segment, Year over Year</span></div>
  <div class="q-text">Total profit (sales_amount - COGS) per segment, 2017 vs 2018 side by side. Output:
  segment | [2017] | [2018].</div>
  <div class="sol">
    <h4>Reference solution</h4>
    <pre class="code goodquery">WITH segment_profit AS (
    SELECT
        c.segment,
        YEAR(o.order_purchase_date) AS order_year,
        SUM(t.sales_amount - t.COGS) AS profit
    FROM ex_transactions t
    JOIN ex_orders o ON t.order_id = o.order_id
    JOIN ex_customers c ON o.customer_id = c.customer_id
    WHERE YEAR(o.order_purchase_date) IN (2017, 2018)
    GROUP BY c.segment, YEAR(o.order_purchase_date)
)
SELECT segment, [2017], [2018]
FROM segment_profit
PIVOT(
    SUM(profit)
    FOR order_year IN ([2017],[2018])
) AS pvt
ORDER BY segment;</pre>
    <h4>Rubric</h4>
    <ul class="rubric">
      <li>Long-format aggregation built first: segment &times; year &times; profit</li>
      <li>Profit is computed as SUM(sales_amount - COGS), not SUM(sales_amount) - SUM(COGS) done separately then
      subtracted outside the aggregate — both are mathematically equivalent here, accept either</li>
      <li>PIVOT block structured correctly: aggregate / FOR order_year / IN ([2017],[2018])</li>
      <li>Accept an equivalent MAX(CASE WHEN order_year = 2017 THEN profit END) rewrite in place of PIVOT</li>
    </ul>
  </div>
</div>
"""

    q3 = """
<div class="q-block avoid-break">
  <div class="q-head"><span class="q-num">Q3</span><span class="q-title">Spot the Slow Query</span></div>
  <div class="q-text">Learner is given this query and asked to name 3 specific issues, then rewrite it.</div>
  <pre class="code badquery">SELECT DISTINCT *
FROM ex_customers c, ex_orders o, ex_transactions t
WHERE c.customer_id = o.customer_id
  AND o.order_id = t.order_id
GROUP BY c.segment, o.order_status
HAVING c.segment = 'Consumer' AND o.order_status = 'delivered'</pre>
  <div class="sol">
    <h4>The 3 required findings</h4>
    <ul class="rubric">
      <li><b>SELECT DISTINCT *</b> — fetches every column unnecessarily, and pairs DISTINCT with a GROUP BY that
      already dedupes; pick one, and neither should be a blanket *.</li>
      <li><b>Filtering in HAVING instead of WHERE</b> — <code>c.segment = 'Consumer'</code> and
      <code>o.order_status = 'delivered'</code> are row-level filters, not aggregate conditions. They belong in
      WHERE, before the GROUP BY, not after it.</li>
      <li><b>Wrong join order / old comma-join syntax</b> — starts FROM the smallest table (customers) and
      comma-joins outward instead of starting FROM the highest-granularity table (transactions) with explicit
      JOIN syntax.</li>
    </ul>
    <h4>Reference rewrite</h4>
    <pre class="code goodquery">SELECT
    c.segment,
    o.order_status,
    COUNT(DISTINCT o.order_id) AS order_count
FROM ex_transactions t
JOIN ex_orders o    ON t.order_id = o.order_id
JOIN ex_customers c ON o.customer_id = c.customer_id
WHERE c.segment = 'Consumer'
  AND o.order_status = 'delivered'
GROUP BY c.segment, o.order_status;</pre>
    <h4>Rubric</h4>
    <ul class="rubric">
      <li>Full marks requires naming all 3 issues above (in their own words is fine)</li>
      <li>Rewrite must use WHERE for the two filters, explicit JOIN syntax starting FROM ex_transactions, and
      select only needed columns</li>
      <li>COUNT(DISTINCT order_id) in the rewrite is correct and NOT the same mistake as SELECT DISTINCT * —
      don't penalize it</li>
    </ul>
  </div>
</div>
"""

    return f"<html><head><style>{CSS}</style></head><body>{intro}{q1}{q2}{q3}</body></html>"


def render_pdf(html: str, out_path: Path):
    from playwright.sync_api import sync_playwright

    tmp_html = HERE / "_tmp_render.html"
    tmp_html.write_text(html, encoding="utf-8")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(tmp_html.as_uri())
            page.pdf(path=str(out_path), format="A4", print_background=True,
                     margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"})
            browser.close()
    finally:
        tmp_html.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["student", "key"], required=True)
    args = parser.parse_args()

    if args.mode == "student":
        html = build_student_html()
        out = HERE / "Day3_Individual_SQL_Assessment - Student Booklet.pdf"
    else:
        html = build_key_html()
        out = HERE / "Day3_Individual_SQL_Assessment - Instructor Answer Key.pdf"

    render_pdf(html, out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
