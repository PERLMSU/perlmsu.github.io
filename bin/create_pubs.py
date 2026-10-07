#!/usr/bin/env python3
"""Generate content/pages/pubs.md from the group bibliography.

Formats content/assets/bib/group_publications.bib (written by
bin/dedupe_bib.py) in APA style with pandoc's citeproc, groups the references
by year (newest first), and overwrites pubs.md, including the year links at
the top. pandoc comes from the pypandoc-binary package, so no system install
is needed.

Usage:
  uv run python bin/create_pubs.py              # overwrite content/pages/pubs.md
  uv run python bin/create_pubs.py preview.md   # write somewhere else to check first

Adapted from the CERL site (msu-cerl.github.io).
"""

import re
import sys
from pathlib import Path

import pypandoc

REPO = Path(__file__).parent.parent
INFILE = REPO / "templates" / "pubs-template.md"
BIBFILE = REPO / "content" / "assets" / "bib" / "group_publications.bib"
CSLFILE = REPO / "templates" / "apa.csl"
OUTFILE = REPO / "content" / "pages" / "pubs.md"


def extract_year(paragraph: str) -> str:
    # APA puts the year in parentheses, sometimes with a date after it:
    # "(2020)", "(2020a)", "(2017, July)".
    m = re.search(r"\(([12][0-9]{3})[a-z]?(?:,[^)]*)?\)", paragraph) or re.search(
        r"\. ([12][0-9]{3})[a-z]?\.", paragraph
    )
    return m.group(1) if m else "Unknown"


def main() -> None:
    outfile = Path(sys.argv[1]) if len(sys.argv) > 1 else OUTFILE

    raw = pypandoc.convert_file(
        str(INFILE),
        "markdown_strict",
        extra_args=[
            "--citeproc",
            f"--bibliography={BIBFILE}",
            f"--csl={CSLFILE}",
        ],
    )

    paragraphs = [p.strip() for p in re.split(r"\n\n+", raw) if p.strip()]

    year_refs: dict[str, list[str]] = {}
    for para in paragraphs:
        year_refs.setdefault(extract_year(para), []).append(para)

    years = sorted((y for y in year_refs if y != "Unknown"), reverse=True)
    if "Unknown" in year_refs:
        years.append("Unknown")

    lines = ["Title: Publications", "Slug: pubs", ""]
    lines += [" · ".join(f"[{y}](#{y.lower()})" for y in years), ""]
    for year in years:
        lines += [f"## {year}", ""]
        for ref in year_refs[year]:
            lines += [ref, ""]

    outfile.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(paragraphs)} references to {outfile}")
    if "Unknown" in year_refs:
        print(f"{len(year_refs['Unknown'])} references have no year; they are under ## Unknown")


if __name__ == "__main__":
    main()
