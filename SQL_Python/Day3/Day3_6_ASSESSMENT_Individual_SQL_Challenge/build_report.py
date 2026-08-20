"""
build_report.py — one-off activity execution report for the Day 3 Individual
SQL Assessment, for internal reporting after the activity was run.

Embeds the 3 photos from Captured_photos&videos/ (the video is referenced by
filename, not embedded — too large and not renderable in a static PDF).
Written as its own script, alongside build_pdf.py, so it's regenerable if the
photos are replaced/added to later.

Rendering: HTML -> PDF via Playwright's bundled Chromium (same approach as
build_pdf.py — no new tooling).
"""

import base64
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE_DIR = HERE / "Captured_photos&videos"


def img_data_uri(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    ext = path.suffix.lstrip(".").lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    return f"data:image/{mime};base64,{b64}"


CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Arial, sans-serif; color: #1a2433; font-size: 12.5px; line-height: 1.6; }
h1, h2, h3 { color: #0f2a4a; }
.page-break { page-break-before: always; }

.header { border-bottom: 3px solid #0f2a4a; padding-bottom: 14px; margin-bottom: 18px; }
.header .kicker { font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: #2563eb; font-weight: 700; margin-bottom: 6px; }
.header h1 { font-size: 24px; font-weight: 800; }
.header .sub { font-size: 13px; color: #445067; margin-top: 4px; }

.meta-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 16px 0; }
.meta-card { background: #f4f7fb; border: 1px solid #d7e0ee; border-radius: 8px; padding: 10px 12px; }
.meta-card .label { font-size: 9.5px; text-transform: uppercase; letter-spacing: .5px; color: #6b7385; font-weight: 700; }
.meta-card .value { font-size: 13px; font-weight: 700; color: #0f2a4a; margin-top: 3px; }

.section-title { font-size: 15px; font-weight: 800; color: #0f2a4a; margin: 20px 0 8px; padding-bottom: 4px; border-bottom: 1.5px solid #c7d0dd; }
p.body-text { margin-bottom: 8px; }
ul.list li { margin-bottom: 5px; margin-left: 16px; }

.status-pill { display: inline-block; background: #dcfce7; border: 1px solid #16a34a; color: #15803d; font-weight: 700; font-size: 11px; padding: 3px 12px; border-radius: 999px; }

table.fmt { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 11.5px; }
table.fmt th { background: #0f2a4a; color: #fff; text-align: left; padding: 6px 10px; }
table.fmt td { border: 1px solid #d7e0ee; padding: 6px 10px; }
table.fmt tr:nth-child(even) td { background: #f4f7fb; }

.gallery-item { margin-bottom: 20px; page-break-inside: avoid; }
.gallery-item img { width: 100%; border: 1px solid #c7d0dd; border-radius: 8px; }
.gallery-item .caption { font-size: 11px; color: #445067; margin-top: 5px; font-style: italic; }

.note-box { background: #fffbeb; border: 1px solid #f59e0b; border-radius: 8px; padding: 10px 14px; font-size: 11.5px; margin-top: 10px; }
.footer-note { margin-top: 24px; font-size: 10.5px; color: #8b98ab; border-top: 1px solid #d7e0ee; padding-top: 8px; }
"""


def build_html() -> str:
    group_uri = img_data_uri(EVIDENCE_DIR / "aLL_together.jpeg")
    solutions_uri = img_data_uri(EVIDENCE_DIR / "solution_files.jpeg")
    meme_uri = img_data_uri(EVIDENCE_DIR / "Meme_image.jpeg")
    video_size_mb = (EVIDENCE_DIR / "Vidoe.mp4").stat().st_size / (1024 * 1024)

    return f"""<html><head><style>{CSS}</style></head><body>

<div class="header">
  <div class="kicker">GlobalMart Data Engineering Bootcamp &middot; Hyderabad 2026</div>
  <h1>Activity Execution Report</h1>
  <div class="sub">Day 3 Individual SQL Assessment — pen-and-paper, closed-book</div>
</div>

<div class="meta-grid">
  <div class="meta-card"><div class="label">Date</div><div class="value">17 Aug 2026</div></div>
  <div class="meta-card"><div class="label">Cohort</div><div class="value">Hyderabad 2026 (20 learners)</div></div>
  <div class="meta-card"><div class="label">Format</div><div class="value">Individual, pen &amp; paper</div></div>
  <div class="meta-card"><div class="label">Status</div><div class="value"><span class="status-pill">Successfully Executed</span></div></div>
</div>

<div class="section-title">Objective</div>
<p class="body-text">End of Day 3 marks the close of the SQL &amp; Python track's most technically dense stretch —
joins, window functions, PIVOT/UNPIVOT, and query optimization. Rather than another group lab, this activity
was designed to check what each learner can do independently: no laptop, no internet, no teammate to lean on —
just their own understanding of the material, applied on paper.</p>

<div class="section-title">Activity Format</div>
<table class="fmt">
  <tr><th>Element</th><th>Details</th></tr>
  <tr><td>Delivery</td><td>Personalized booklet per learner — each learner's own name woven directly into every question, not just a header</td></tr>
  <tr><td>Reference material</td><td>Full ER diagram + syntax cheat sheet (JOIN, window functions, PIVOT, date functions, optimization checklist) printed immediately before each learner's questions — genuinely closed-book, nothing to look up</td></tr>
  <tr><td>Q1</td><td>The Logistics Partner Scorecard — joins + DATEDIFF/AVG + ascending RANK()</td></tr>
  <tr><td>Q2</td><td>Profit by Segment, Year over Year — PIVOT technique applied to a fresh business question</td></tr>
  <tr><td>Q3</td><td>Spot the Slow Query — identify and rewrite a deliberately inefficient query using Day 3's optimization best practices</td></tr>
  <tr><td>Q4 (bonus)</td><td>"Draw It Out" — an ungraded, non-technical creative prompt asking each learner to draw themselves as the detective who solved the day's 3 cases</td></tr>
</table>

<div class="section-title">Execution Summary</div>
<p class="body-text">The activity was run in person with the full cohort of 20 learners. All participants received
their personalized booklet and completed the assessment under pen-and-paper, no-device conditions. Photo
evidence (below) confirms full participation, engagement with the material well beyond a token attempt, and
a positive reception of the Q4 creative bonus round.</p>

<div class="note-box"><b>Note on scoring:</b> this report covers execution only. Grading against the instructor
answer key (SQL_Python/Day3/Day3_6_ASSESSMENT_Individual_SQL_Challenge/Day3_Individual_SQL_Assessment -
Instructor Answer Key.pdf) is a separate follow-up step — no score data is included here since grading
happens after collection.</p></div>

<div class="page-break">
<div class="section-title">Evidence</div>
<p class="body-text">Photos below; a supplementary video recap ({video_size_mb:.1f} MB, <code>Vidoe.mp4</code>)
is also available in the same evidence folder and is not embedded in this PDF.</p>

<div class="gallery-item">
  <img src="{group_uri}" alt="Full cohort holding up completed papers">
  <div class="caption">Full cohort (20/20) at completion — every learner holding up their finished booklet.</div>
</div>

<div class="gallery-item">
  <img src="{solutions_uri}" alt="Close-up of handwritten SQL solutions">
  <div class="caption">Close-up of submitted work: handwritten CTEs and a PIVOT block for Q2, a full rewrite
  attempt for Q3, and a hand-drawn sketch in the Q4 "Draw It Out" box — evidence the reference material was
  actually used, not just glanced at.</div>
</div>

<div class="gallery-item">
  <img src="{meme_uri}" alt="Learners working individually around the office">
  <div class="caption">Learners spread out across the office, each working independently in their own quiet
  corner — consistent with the closed-book, individual-effort intent of the activity.</div>
</div>

<div class="footer-note">Generated from SQL_Python/Day3/Day3_6_ASSESSMENT_Individual_SQL_Challenge/Captured_photos&amp;videos.
Source materials: Student Booklet.pdf and Instructor Answer Key.pdf in the parent folder.</div>
</div>

</body></html>"""


def main():
    from playwright.sync_api import sync_playwright

    html = build_html()
    tmp_html = HERE / "_tmp_report.html"
    tmp_html.write_text(html, encoding="utf-8")
    out = HERE / "Day3_Individual_Assessment - Activity Execution Report.pdf"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(tmp_html.as_uri())
            page.pdf(path=str(out), format="A4", print_background=True,
                     margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"})
            browser.close()
    finally:
        tmp_html.unlink(missing_ok=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
