#!/usr/bin/env python3
"""
validate_ipynb.py -- structural + safety-pattern check for one Databricks
.ipynb before you (or the skill) declares it done.

This exists because of a real incident on this project: a background process
once reported a file as "written" when it actually wasn't, or was stale --
and nobody caught it until a human read the content directly. This script is
the "re-open and check" half of that lesson: it can't tell you the content is
PEDAGOGICALLY correct (that still needs a human/agent read), but it CAN catch
"this isn't even valid JSON" or "this cell has no cell_type" before those
ship, and it CAN flag code patterns that would trigger real billable Databricks
compute if run -- so a reviewer knows exactly which lines to look at twice.

Two things this script deliberately does NOT do:
  - It does not hard-fail on every denylisted pattern. A `.start()` on a
    streaming query that is properly `.stop()`'d in the same or a later cell
    is normal, real, and appears in this course's own notebooks (see the
    Day 3 cert-prep notebook, which was audited and fixed to always pair
    start/stop). So denylist hits are reported as WARNINGS to review by eye,
    not automatic failures -- judgment on "is this paired" is left to whoever
    reads the report.
  - It does not evaluate whether the notebook's claims about gbmart's schema
    are correct. That's what references/architecture-facts.md and
    references/fact-sales-schema.md are for, read by a human/agent, not this
    script.

Usage:
    python validate_ipynb.py path/to/notebook.ipynb

Exit code 0 = structurally valid (billable-pattern warnings do not affect
exit code, since they need human judgment). Exit code 1 = structural failure.

Dependencies: stdlib only (json, re, sys, argparse).
"""
import argparse
import json
import re
import sys

# Reconfigure stdout to UTF-8 -- notebook source commonly contains em dashes,
# arrows, and box-drawing characters that a cp1252 Windows console can't print.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

REQUIRED_TOP_KEYS = ["cells", "nbformat"]

# Each pattern paired with a short reason, so the report explains WHY it's
# worth a second look rather than just dumping a regex match.
BILLABLE_TRIGGER_PATTERNS = [
    (r"\.start\s*\(", "starts a streaming query -- confirm it's paired with a .stop() (or availableNow=True) in this cell/notebook"),
    (r"WorkflowClient", "Databricks Workflows API client -- confirm this is inspected/printed only, never used to submit a real job"),
    (r"\bjobs\.create\s*\(", "would create a real Databricks Job if executed"),
    (r"\bjobs\.run_now\s*\(", "would trigger a real Databricks Job run if executed"),
    (r"pipelines\.start_update\s*\(", "would trigger a real Lakeflow/DLT pipeline update if executed"),
    (r"pipelines\.create\s*\(", "would create a real Lakeflow/DLT pipeline if executed"),
    (r"clusters\.create\s*\(", "would provision a real cluster (billable compute) if executed"),
    (r"clusters\.start\s*\(", "would start a real cluster (billable compute) if executed"),
    (r"warehouses\.create\s*\(", "would create a real SQL warehouse if executed"),
    (r"warehouses\.start\s*\(", "would start a real SQL warehouse (billable compute) if executed"),
    (r"\bcreate_endpoint\s*\(", "would create a real serving/warehouse endpoint if executed"),
]

VALID_CELL_TYPES = {"markdown", "code", "raw"}


def cell_source_text(cell):
    """nbformat allows `source` to be a single string OR a list of line
    strings -- normalize to one string before scanning either way."""
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return src or ""


def validate(path):
    errors = []
    warnings = []

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except UnicodeDecodeError as e:
        errors.append(f"File is not valid UTF-8: {e}")
        return errors, warnings
    except OSError as e:
        errors.append(f"Could not open file: {e}")
        return errors, warnings

    try:
        nb = json.loads(raw)
    except json.JSONDecodeError as e:
        errors.append(f"Not valid JSON: {e}")
        return errors, warnings

    if not isinstance(nb, dict):
        errors.append("Top-level JSON is not an object.")
        return errors, warnings

    for key in REQUIRED_TOP_KEYS:
        if key not in nb:
            errors.append(f"Missing required top-level key: '{key}'")

    cells = nb.get("cells")
    if cells is None:
        return errors, warnings  # already reported above
    if not isinstance(cells, list):
        errors.append("'cells' is not a list.")
        return errors, warnings
    if len(cells) == 0:
        errors.append("'cells' is empty -- a notebook with zero cells is never a valid deliverable.")

    billable_hits = []
    for i, cell in enumerate(cells):
        if not isinstance(cell, dict):
            errors.append(f"Cell {i} is not a JSON object.")
            continue
        ctype = cell.get("cell_type")
        if ctype is None:
            errors.append(f"Cell {i} has no 'cell_type'.")
        elif ctype not in VALID_CELL_TYPES:
            errors.append(f"Cell {i} has unrecognized cell_type '{ctype}' (expected one of {sorted(VALID_CELL_TYPES)}).")

        if ctype == "code":
            src = cell_source_text(cell)
            for pattern, reason in BILLABLE_TRIGGER_PATTERNS:
                for m in re.finditer(pattern, src):
                    line_no = src.count("\n", 0, m.start()) + 1
                    billable_hits.append((i, line_no, m.group(0), reason))

    if billable_hits:
        warnings.append(f"Found {len(billable_hits)} potential billable-trigger pattern(s) -- review each by eye:")
        for cell_idx, line_no, match_text, reason in billable_hits:
            warnings.append(f"  - cell {cell_idx}, line {line_no}: '{match_text}' -- {reason}")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description="Validate a Databricks .ipynb before declaring it done.")
    ap.add_argument("path", help="Path to the .ipynb file")
    args = ap.parse_args()

    errors, warnings = validate(args.path)

    print(f"Validating: {args.path}")
    print("-" * 70)

    if errors:
        print(f"FAILED -- {len(errors)} structural error(s):")
        for e in errors:
            print(f"  - {e}")
    else:
        print("PASSED -- structurally valid notebook (parseable JSON, required keys present, every cell has a cell_type).")

    if warnings:
        print()
        for w in warnings:
            print(w)
    else:
        print("No billable-trigger patterns found.")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
