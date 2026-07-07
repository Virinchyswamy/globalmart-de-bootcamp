"""
validate_html_deck.py — structural validation for a GlobalMart slide-deck .html file.

Why this exists: this is the "re-open and check before declaring success" step
that every skill in this project follows (the Day 6 incident lesson) --
writing a file and never looking at it again is exactly how a broken or
stale deck slips through. This script uses only the Python standard library
(html.parser) -- no external dependencies -- so it can run anywhere this
skill runs.

Checks performed:
  1. Tag balance -- every opening tag has a matching close (void/self-closing
     HTML tags are allowed to have no explicit close).
  2. The nav block, id="counter", and the showSlide/changeSlide functions are
     present and match the exact approved template text -- the deck's
     keyboard/button navigation depends on this JS being unmodified.
  3. The number of `.slide` divs (class attribute containing the token
     "slide") matches the "N / Total" counter text baked into the initial
     HTML -- if these disagree, the deck will show the wrong total until the
     first click, and something was probably miscounted while drafting.
  4. No <script src=, <link href=, or http(s):// reference appears anywhere
     OUTSIDE of a <pre> code-sample block -- the deck must stay a single,
     offline-openable file with no external network dependency. (A URL shown
     *as example text inside a <pre> code sample* is fine -- e.g. an ADLS
     abfss:// path shown for teaching purposes -- so those are excluded.)

Usage:
    python validate_html_deck.py "Day7\\Day7_1_ILT1_Some_Topic.html"

Exit code 0 = all checks passed. Exit code 1 = at least one check failed.
"""

import re
import sys
from html.parser import HTMLParser

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

REQUIRED_JS_SNIPPETS = [
    "let current = 0;",
    "const slides = document.querySelectorAll('.slide');",
    "const counter = document.getElementById('counter');",
    "function showSlide(n) {",
    "function changeSlide(dir) { showSlide(current + dir); }",
    "document.addEventListener('keydown', e => {",
]

REQUIRED_NAV_SNIPPETS = [
    '<span class="slide-counter" id="counter">',
    'onclick="changeSlide(-1)"',
    'onclick="changeSlide(1)"',
]


class TagBalanceParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag in VOID_TAGS:
            return
        self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        # Explicitly self-closed (e.g. <br/>) -- fine regardless of VOID_TAGS.
        pass

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if not self.stack:
            self.errors.append(f"Unexpected closing </{tag}> at {self.getpos()} with no open tag.")
            return
        open_tag, pos = self.stack.pop()
        if open_tag != tag:
            self.errors.append(
                f"Mismatched tag: <{open_tag}> opened at {pos} but found </{tag}> at {self.getpos()}."
            )
            # Best-effort recovery: put it back if it doesn't match, so a single
            # typo doesn't cascade into hundreds of false positives.
            self.stack.append((open_tag, pos))


def check_tag_balance(html_text: str):
    parser = TagBalanceParser()
    parser.feed(html_text)
    errors = list(parser.errors)
    if parser.stack:
        for tag, pos in parser.stack:
            errors.append(f"Unclosed tag: <{tag}> opened at {pos} was never closed.")
    return errors


def check_nav_and_js(html_text: str):
    errors = []
    for snippet in REQUIRED_NAV_SNIPPETS:
        if snippet not in html_text:
            errors.append(f"Missing expected nav element: {snippet!r}")
    for snippet in REQUIRED_JS_SNIPPETS:
        if snippet not in html_text:
            errors.append(f"Missing or modified required JS snippet: {snippet!r}")
    if "<nav>" not in html_text:
        errors.append("Missing <nav> element entirely.")
    return errors


def check_slide_count_matches_counter(html_text: str):
    errors = []
    # Count slide divs: any element whose class attribute contains the
    # whitespace-delimited token "slide" (matches class="slide slide-cover
    # active", class="slide slide-content", etc.) but not other classes that
    # merely contain the substring "slide" (e.g. "slide-counter").
    slide_divs = re.findall(r'class="([^"]*)"', html_text)
    slide_count = 0
    for class_attr in slide_divs:
        tokens = class_attr.split()
        if "slide" in tokens:
            slide_count += 1

    counter_match = re.search(r'id="counter">\s*(\d+)\s*/\s*(\d+)\s*<', html_text)
    if not counter_match:
        errors.append("Could not find the initial 'N / Total' counter text next to id=\"counter\".")
        return errors, slide_count, None

    initial_n, initial_total = int(counter_match.group(1)), int(counter_match.group(2))
    if initial_n != 1:
        errors.append(f"Initial counter numerator should be 1 (first slide shown), found {initial_n}.")
    if initial_total != slide_count:
        errors.append(
            f"Counter text says {initial_total} total slides, but {slide_count} elements with "
            f"class token \"slide\" were found. These must match."
        )
    return errors, slide_count, initial_total


def check_no_external_refs(html_text: str):
    errors = []

    # Strip out <pre>...</pre> blocks before scanning for URLs / external refs --
    # a URL or path shown as illustrative code-sample TEXT inside a <pre> block
    # (e.g. an abfss:// path taught as a real value) is fine; the rule is about
    # the deck itself making a network request, not about what a code sample
    # displays as text.
    text_without_pre = re.sub(r"<pre\b.*?</pre>", "", html_text, flags=re.S | re.I)

    for match in re.finditer(r'<script\b[^>]*\bsrc\s*=', text_without_pre, re.I):
        errors.append(f"Found <script src=...> outside a <pre> block at offset {match.start()} -- "
                       f"decks must be a single offline-openable file with no external script.")
    for match in re.finditer(r'<link\b[^>]*\bhref\s*=', text_without_pre, re.I):
        errors.append(f"Found <link href=...> outside a <pre> block at offset {match.start()} -- "
                       f"decks must not reference external stylesheets.")
    for match in re.finditer(r'https?://', text_without_pre, re.I):
        errors.append(f"Found a bare http(s):// reference outside a <pre> block at offset "
                       f"{match.start()} -- move it inside a <pre> code sample if it's illustrative "
                       f"text, or remove it if it's a live external dependency.")
    return errors


def validate(path: str):
    with open(path, "r", encoding="utf-8") as f:
        html_text = f.read()

    all_errors = []
    all_errors += [f"[tag balance] {e}" for e in check_tag_balance(html_text)]
    all_errors += [f"[nav/js] {e}" for e in check_nav_and_js(html_text)]

    slide_errors, slide_count, initial_total = check_slide_count_matches_counter(html_text)
    all_errors += [f"[slide count] {e}" for e in slide_errors]

    all_errors += [f"[external refs] {e}" for e in check_no_external_refs(html_text)]

    print(f"Validating: {path}")
    print(f"  Slide divs found:        {slide_count}")
    print(f"  Counter text says total: {initial_total}")
    print()

    if all_errors:
        print(f"FAILED -- {len(all_errors)} issue(s) found:\n")
        for e in all_errors:
            print(f"  - {e}")
        return False
    else:
        print("PASSED -- tag balance OK, nav/JS intact, slide count matches counter, "
              "no external network references found outside <pre> blocks.")
        return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    ok = validate(sys.argv[1])
    sys.exit(0 if ok else 1)
