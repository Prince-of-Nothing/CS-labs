#!/usr/bin/env python3
"""Refresh the generated status table inside README.md.

README.md is authored by hand and is never rewritten by this script: only
the block between the status markers is replaced, and it is built from
reportgen/status.json. To change a status, edit the flag in status.json
and re-run this script:

    python3 reportgen/build_readme.py

Because the table lives in one small JSON file, updating a single lab
never means re-authoring the README.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
STATUS = os.path.join(HERE, "status.json")
README = os.path.join(REPO, "README.md")

BEGIN = "<!-- status:begin -->"
END = "<!-- status:end -->"


def tick(flag: bool) -> str:
    return "\u2705" if flag else "\u2014"


def table(data: dict) -> str:
    rows = [
        "| Lab | Task | Language | Report | Verified | Presented |",
        "|:--|:--|:--|:--|:--:|:--:|",
    ]
    for lab in data["labs"]:
        rep = lab.get("report") or ""
        cell = f"[`{os.path.basename(rep)}`]({rep})" if rep else "\u2014"
        rows.append(
            f"| {lab['id']} | {lab['topic']} | {lab['language']} | {cell} "
            f"| {tick(lab['verified'])} | {tick(lab['presented'])} |")
    return "\n".join(rows)


def main() -> int:
    if not os.path.exists(README):
        print("README.md not found; create it with the status markers first "
              f"({BEGIN} ... {END})", file=sys.stderr)
        return 1
    with open(STATUS, encoding="utf-8") as fh:
        data = json.load(fh)
    with open(README, encoding="utf-8") as fh:
        text = fh.read()

    if BEGIN not in text or END not in text:
        print(f"status markers missing in README.md "
              f"(expected {BEGIN} ... {END})", file=sys.stderr)
        return 1

    block = f"{BEGIN}\n\n{table(data)}\n\n{END}"
    # Anchored to whole lines so prose that merely quotes the marker names
    # can never be mistaken for the block (or silently rewritten).
    pattern = re.compile(
        r"^" + re.escape(BEGIN) + r"[ \t]*$"
        r"\n.*?"
        r"^" + re.escape(END) + r"[ \t]*$",
        re.DOTALL | re.MULTILINE)
    updated, count = pattern.subn(lambda _m: block, text, count=1)
    if count != 1:
        print("status block could not be located unambiguously", file=sys.stderr)
        return 1
    if updated == text:
        print("README.md status table already up to date")
        return 0
    with open(README, "w", encoding="utf-8") as fh:
        fh.write(updated)
    print("README.md status table refreshed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
