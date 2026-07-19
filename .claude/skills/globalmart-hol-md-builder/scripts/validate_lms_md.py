#!/usr/bin/env python3
"""
validate_lms_md.py -- structural check for one LMS-import hands-on .md before
you (or the skill) declares it done.

This exists because of two real, confirmed import failures on this project:
  1. "'name' is required" -- the YAML frontmatter was missing (or had an
     empty) `name` field.
  2. "Duplicate input number" -- `## Input N` numbering was reset back to 1
     at the start of a new Scenario instead of continuing to count up across
     the whole file (this is exactly what the visually-similar-but-wrong
     "reference_materials/reference_data_for_hands_on_docs/" export format does).

Both were fixed for real in this repo's history (commits `8094f64`,
`b60d56a`). This script mirrors both failure modes as named checks, plus two
more structural rules the proven-clean file
(Day1_5_HOL_PySpark_SparkSQL_ADLS.md) always satisfies: every **Type:** value
is one of the 5 known values (Text, Short Answer, Choice, Code, File Upload),
and Tags follow a question-gated rule -- an Input with a real learner-facing
question (Short Answer, Choice, Code, File Upload) must have a **Tags**
heading followed by at least one tag, while a pure-instructional Text Input
(no question at all) must have NO **Tags** heading at all -- not present,
not empty. Tags exist to classify what's being *assessed* -- a Text Input
assesses nothing, so a Tags heading on one is noise, not thoroughness.

This script deliberately does NOT check:
  - Whether Solution/Options/Snippet fields are present or well-formed --
    those vary legitimately by Type and are not known import-breakers.
  - Whether the content is pedagogically or technically correct -- that is
    what a human/agent read against references/architecture-facts.md and
    references/fact-sales-schema.md is for.
Keeping the check list to exactly the known failure modes avoids false
failures on files that are structurally fine but stylistically different.

Usage:
    python validate_lms_md.py path/to/hands_on.md

Exit code 0 = all 4 structural checks passed. Exit code 1 = at least one
failed (specific, line-referenced complaints are printed either way).

Dependencies: stdlib only. Deliberately does NOT use pyyaml -- this script
must work the same way in any environment this skill runs in, and a minimal
line-based frontmatter extractor is enough for the one field (`name`) that
has a known real failure mode behind it.
"""
import argparse
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

VALID_TYPES = {"Text", "Short Answer", "Choice", "Code", "File Upload"}

INPUT_HEADER_RE = re.compile(r"^(#{1,6})\s+Input\s+(\d+)\s*$")
SCENARIO_HEADER_RE = re.compile(r"^#{1,6}\s+Scenario\s+\d+\b")
TYPE_FIELD_RE = re.compile(r"^\*\*Type:\*\*\s*(.+?)\s*$")
TAGS_HEADER_RE = re.compile(r"^\*\*Tags\*\*\s*$")
NAME_FIELD_RE = re.compile(r"^name:\s*(.*\S)\s*$")


def extract_frontmatter(lines):
    """Return (frontmatter_lines, first_line_idx, last_line_idx) or
    (None, None, None) if the file doesn't open with a '---' frontmatter
    block. Only the FIRST '---' ... '---' pair is treated as frontmatter --
    a later standalone '---' (a horizontal rule, as seen right after the
    frontmatter in the proven example) is not re-parsed as a second block."""
    if not lines or lines[0].rstrip("\n") != "---":
        return None, None, None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\n") == "---":
            return lines[1:i], 0, i
    return None, None, None  # opened but never closed


def find_input_blocks(lines):
    """Return a list of dicts, one per '#{1,6} Input N' heading found, each
    with: number (int), level (int, count of '#'), line_no (1-based),
    block_start (0-based index of the heading line), block_end (0-based
    index, exclusive -- the next Input/Scenario heading or EOF)."""
    headers = []
    for idx, raw in enumerate(lines):
        line = raw.rstrip("\n")
        m = INPUT_HEADER_RE.match(line)
        if m:
            headers.append({
                "number": int(m.group(2)),
                "level": len(m.group(1)),
                "line_no": idx + 1,
                "block_start": idx,
            })
    # Compute block_end for each: next Input header OR Scenario header OR EOF.
    boundary_idxs = [h["block_start"] for h in headers]
    for i, h in enumerate(headers):
        end = len(lines)
        # Look for the next Input header (already known) ...
        if i + 1 < len(headers):
            end = headers[i + 1]["block_start"]
        # ... but a Scenario heading in between should end the block sooner.
        for j in range(h["block_start"] + 1, end):
            if SCENARIO_HEADER_RE.match(lines[j].rstrip("\n")):
                end = j
                break
        h["block_end"] = end
    return headers


def validate(path):
    errors = []

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except UnicodeDecodeError as e:
        errors.append(f"File is not valid UTF-8: {e}")
        return errors, {}
    except OSError as e:
        errors.append(f"Could not open file: {e}")
        return errors, {}

    lines = raw.splitlines(keepends=True)
    if not lines:
        errors.append("File is empty.")
        return errors, {}

    stats = {}

    # ---- Check 1: "'name' is required" (real historical failure) ----
    fm_lines, fm_start, fm_end = extract_frontmatter(lines)
    if fm_lines is None:
        errors.append(
            "'name' is required check FAILED: file does not open with a "
            "'---' ... '---' YAML frontmatter block at all -- there is no "
            "frontmatter to hold a 'name' field. (Mirrors the real historical "
            "\"'name' is required\" import failure.)"
        )
    else:
        name_value = None
        name_line_no = None
        for i, raw_line in enumerate(fm_lines):
            m = NAME_FIELD_RE.match(raw_line.rstrip("\n"))
            if m:
                name_value = m.group(1).strip()
                name_line_no = fm_start + 2 + i  # 1-based line number
                break
        if not name_value:
            errors.append(
                "'name' is required check FAILED: no non-empty 'name:' line "
                "found inside the frontmatter block "
                f"(lines {fm_start + 1}-{fm_end + 1}). (Mirrors the real "
                "historical \"'name' is required\" import failure.)"
            )
        else:
            stats["name"] = name_value

    # ---- Locate all Input headers (any heading level) ----
    input_headers = find_input_blocks(lines)
    stats["input_count"] = len(input_headers)
    stats["scenario_count"] = sum(
        1 for line in lines if SCENARIO_HEADER_RE.match(line.rstrip("\n"))
    )

    if not input_headers:
        errors.append(
            "No '## Input N' headings found at all -- this file has zero "
            "graded Inputs, which is never a valid hands-on .md."
        )
        return errors, stats

    # ---- Check 2: heading level must be H2, never H5 (reference-format tell) ----
    wrong_level = [h for h in input_headers if h["level"] != 2]
    if wrong_level:
        examples = ", ".join(
            f"line {h['line_no']} ('{'#' * h['level']} Input {h['number']}', H{h['level']})"
            for h in wrong_level[:5]
        )
        more = f" (+{len(wrong_level) - 5} more)" if len(wrong_level) > 5 else ""
        errors.append(
            "Input heading level check FAILED: found "
            f"{len(wrong_level)} Input heading(s) that are not H2 "
            f"('## Input N'): {examples}{more}. This is the shape used by "
            "the incompatible 'reference_materials/reference_data_for_hands_on_docs/' export "
            "format ('##### Input N', H5) -- never copy that structure into "
            "an LMS-import file."
        )

    # ---- Check 3: "Duplicate input number" (real historical failure) ----
    numbers_in_order = [h["number"] for h in input_headers]
    expected = list(range(1, len(numbers_in_order) + 1))
    if numbers_in_order != expected:
        first_break = next(
            (i for i, (got, want) in enumerate(zip(numbers_in_order, expected)) if got != want),
            None,
        )
        detail = ""
        if first_break is not None:
            bad_header = input_headers[first_break]
            detail = (
                f" First mismatch at line {bad_header['line_no']}: expected "
                f"Input {expected[first_break]} but found Input {bad_header['number']}."
            )
        errors.append(
            "Duplicate input number check FAILED: Input numbering is not "
            "one strictly-increasing sequence starting at 1 across the "
            f"whole file. Found order: {numbers_in_order}."
            f"{detail} (Mirrors the real historical \"Duplicate input "
            "number\" import failure -- numbering must never reset at a "
            "new Scenario.)"
        )

    # ---- Check 4: every **Type:** is one of the 5 known values ----
    for h in input_headers:
        block = lines[h["block_start"]:h["block_end"]]
        type_value = None
        type_line_no = None
        for i, raw_line in enumerate(block):
            m = TYPE_FIELD_RE.match(raw_line.rstrip("\n"))
            if m:
                type_value = m.group(1).strip()
                type_line_no = h["block_start"] + i + 1
                break
        if type_value is None:
            errors.append(
                f"Input {h['number']} (line {h['line_no']}) is missing a "
                "'**Type:**' field entirely."
            )
        elif type_value not in VALID_TYPES:
            errors.append(
                f"Input {h['number']} (line {type_line_no}) has an unknown "
                f"'**Type:** {type_value}' -- must be one of "
                f"{sorted(VALID_TYPES)}."
            )

    # ---- Check 5: Tags are question-gated ----
    # Question-bearing types (anything with a real **Question:** field) must
    # have a '**Tags**' heading followed by at least one tag. Text (pure
    # instructional, no question) should have NO '**Tags**' heading at all
    # -- not present, not empty -- since tags classify what's being assessed
    # and a Text Input assesses nothing.
    QUESTION_TYPES = {"Short Answer", "Choice", "Code", "File Upload"}
    for h in input_headers:
        block = lines[h["block_start"]:h["block_end"]]
        type_value = None
        for raw_line in block:
            m = TYPE_FIELD_RE.match(raw_line.rstrip("\n"))
            if m:
                type_value = m.group(1).strip()
                break

        tags_line_idx = None
        for i, raw_line in enumerate(block):
            if TAGS_HEADER_RE.match(raw_line.rstrip("\n")):
                tags_line_idx = i
                break

        if type_value == "Text":
            if tags_line_idx is not None:
                tags_line_no = h["block_start"] + tags_line_idx + 1
                errors.append(
                    f"Input {h['number']} (line {tags_line_no}) is Type "
                    "'Text' (pure instructional, no question) but has a "
                    "'**Tags**' heading at all -- Text Inputs should omit "
                    "the Tags heading entirely, since there's no question "
                    "here to classify."
                )
            continue

        # Every other type (Short Answer/Choice/Code/File Upload) must have
        # a Tags heading followed by at least one non-empty tag.
        if tags_line_idx is None:
            errors.append(
                f"Input {h['number']} (line {h['line_no']}) is Type "
                f"'{type_value}' (has a question) but has no '**Tags**' "
                "section at all -- every question-bearing Input must have "
                "one."
            )
            continue

        has_content = False
        for raw_line in block[tags_line_idx + 1:]:
            stripped = raw_line.strip()
            if stripped == "" or stripped == "---":
                continue
            has_content = True
            break

        if not has_content:
            tags_line_no = h["block_start"] + tags_line_idx + 1
            errors.append(
                f"Input {h['number']} (line {tags_line_no}) is Type "
                f"'{type_value}' (has a question) but its 'Tags' section is "
                "empty -- every question-bearing Input must have at least "
                "one non-empty tag."
            )

    return errors, stats


def main():
    ap = argparse.ArgumentParser(
        description="Validate an LMS-import hands-on .md before declaring it done."
    )
    ap.add_argument("path", help="Path to the .md file")
    args = ap.parse_args()

    errors, stats = validate(args.path)

    print(f"Validating: {args.path}")
    print("-" * 70)

    if "name" in stats:
        print(f"name: {stats['name']!r}")
    if "scenario_count" in stats:
        print(f"Scenario count: {stats['scenario_count']}")
    if "input_count" in stats:
        print(f"Input count: {stats['input_count']}")
    print()

    if errors:
        print(f"FAILED -- {len(errors)} issue(s):")
        for e in errors:
            print(f"  - {e}")
    else:
        print(
            "PASSED -- frontmatter has a non-empty 'name', all Input "
            "headings are H2 and strictly sequential from 1 with no "
            "resets/gaps, every Type is one of the 5 known values, every "
            "question-bearing Input (Short Answer/Choice/Code/File Upload) "
            "has a Tags heading with at least one tag, and every Text "
            "Input has no Tags heading at all."
        )

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
