# /// script
# requires-python = ">=3.10"
# dependencies = ["anthropic"]
# ///
"""Merge the .bib files in content/assets/bib/ and flag duplicates.

Reads every *.bib in content/assets/bib/ except the two output files and writes:

  group_publications.bib  - entries known to be unique, plus the most complete
                            copy of each group Claude confirmed as duplicates
  possible_duplicates.bib - every entry in a group Claude was unsure about,
                            for review by hand

How it works:
  1. Each entry is kept as raw text, so the outputs preserve the original
     formatting. @comment, @string and @preamble blocks are skipped.
  2. Candidate pairs are found locally: same citation key, same DOI, or
     normalized titles at least TITLE_SIMILARITY alike.
  3. Pairs with the same DOI count as duplicates without asking. The rest go
     to Claude, PAIRS_PER_REQUEST at a time, and come back as "duplicate",
     "different" or "unsure". A batch with no usable answer is marked unsure.
  4. Entries linked by "duplicate" or "unsure" verdicts form groups. A group
     with any unsure link goes to possible_duplicates.bib in full; otherwise
     its entry with the most non-empty fields goes to group_publications.bib.

Both outputs are rewritten on every run, so resolve possible duplicates by
editing the input files (delete the weaker copy, or rename a clashing key)
and run again. The input files are never modified.

Usage (needs an Anthropic API key with credits, or a profile from
`ant auth login`):
  export ANTHROPIC_API_KEY=...
  uv run bin/dedupe_bib.py
"""

import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Literal

import anthropic
from pydantic import BaseModel

BIB_DIR = Path(__file__).resolve().parent.parent / "content" / "assets" / "bib"
UNIQUE_OUT = BIB_DIR / "group_publications.bib"
REVIEW_OUT = BIB_DIR / "possible_duplicates.bib"

MODEL = "claude-opus-5-5"
TITLE_SIMILARITY = 0.85  # threshold for sending a pair to Claude
PAIRS_PER_REQUEST = 20

SYSTEM_PROMPT = """\
You are deduplicating the publication list of a university physics education \
research group. The entries come from several BibTeX files exported from \
different sources (Google Scholar, Zotero, journal sites, ORCID), so the same \
paper often appears with different citation keys, abbreviations, capitalization, \
author-name formats, or missing fields.

For each numbered pair of BibTeX entries, decide whether they describe the same \
publication:

- "duplicate": the same work. Formatting differences, abbreviated journal names, \
missing DOIs or pages, and "First Last" vs "Last, F." author formats do not \
make two entries different.
- "different": distinct works. Watch for things that look alike but are not the \
same: a conference proceedings paper and a later journal article with a similar \
title, a preprint and a substantially different published version, a talk and \
a paper, parts I and II of a series, errata, different years of a recurring \
report, or the same title by different authors.
- "unsure": the evidence is genuinely ambiguous and a person should check.

Prefer "unsure" over guessing. Give a one-sentence reason for each verdict."""


class Verdict(BaseModel):
    pair: int
    verdict: Literal["duplicate", "different", "unsure"]
    reason: str


class Verdicts(BaseModel):
    verdicts: list[Verdict]


# ---------------------------------------------------------------------------
# Minimal BibTeX handling. Entries are kept as raw text so the output files
# preserve the original formatting.
# ---------------------------------------------------------------------------

class Entry:
    def __init__(self, raw: str, source: str):
        self.raw = raw.strip()
        self.source = source
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", self.raw)
        self.type = m.group(1).lower() if m else ""
        self.key = m.group(2) if m else ""
        self.fields = dict(
            (name.lower(), value)
            for name, value in iter_fields(self.raw[m.end():] if m else "")
        )

    @property
    def title(self) -> str:
        return re.sub(r"[^a-z0-9]", "", self.fields.get("title", "").lower())

    @property
    def doi(self) -> str:
        doi = self.fields.get("doi", "").lower().strip()
        return re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)

    def completeness(self) -> tuple[int, int]:
        return (sum(1 for v in self.fields.values() if v.strip()), len(self.raw))


def iter_fields(body: str):
    """Yield (name, value) pairs from the body of a BibTeX entry."""
    i = 0
    while True:
        m = re.compile(r"\s*,?\s*(\w[\w-]*)\s*=\s*").match(body, i)
        if not m:
            return
        name, i = m.group(1), m.end()
        if i >= len(body):
            return
        if body[i] == "{":
            depth, start = 0, i
            while i < len(body):
                if body[i] == "{":
                    depth += 1
                elif body[i] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            value, i = body[start + 1:i], i + 1
        elif body[i] == '"':
            end = body.find('"', i + 1)
            end = len(body) if end == -1 else end
            value, i = body[i + 1:end], end + 1
        else:
            m = re.compile(r"[^,}\s]+").match(body, i)
            if not m:
                return
            value, i = m.group(0), m.end()
        yield name, value


def read_entries(path: Path) -> list[Entry]:
    text = path.read_text(encoding="utf-8")
    chunks = re.split(r"(?m)^(?=\s*@)", text)
    entries = []
    for chunk in chunks:
        if not chunk.strip().startswith("@"):
            continue
        entry = Entry(chunk, path.name)
        if entry.type in ("comment", "string", "preamble") or not entry.key:
            print(f"  skipping non-entry block in {path.name}: {chunk.strip()[:60]!r}")
            continue
        entries.append(entry)
    return entries


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def candidate_pairs(entries: list[Entry]) -> list[tuple[int, int]]:
    pairs = []
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            a, b = entries[i], entries[j]
            if a.key == b.key or (a.doi and a.doi == b.doi):
                pairs.append((i, j))
                continue
            if not a.title or not b.title:
                continue
            matcher = SequenceMatcher(None, a.title, b.title)
            if matcher.quick_ratio() >= TITLE_SIMILARITY and matcher.ratio() >= TITLE_SIMILARITY:
                pairs.append((i, j))
    return pairs


def judge_pairs(client: anthropic.Anthropic, entries: list[Entry],
                pairs: list[tuple[int, int]]) -> dict[tuple[int, int], str]:
    results = {}
    for start in range(0, len(pairs), PAIRS_PER_REQUEST):
        batch = pairs[start:start + PAIRS_PER_REQUEST]
        print(f"  asking Claude about pairs {start + 1}-{start + len(batch)} of {len(pairs)}")
        prompt = "\n\n".join(
            f"<pair number=\"{n}\">\n<entry_a>\n{entries[i].raw}\n</entry_a>\n"
            f"<entry_b>\n{entries[j].raw}\n</entry_b>\n</pair>"
            for n, (i, j) in enumerate(batch)
        )
        response = client.messages.parse(
            model=MODEL,
            max_tokens=16000,
            output_config={"effort": "medium"},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            output_format=Verdicts,
        )
        if response.stop_reason != "end_turn" or response.parsed_output is None:
            print(f"    no usable answer (stop_reason={response.stop_reason}); marking batch unsure")
            for pair in batch:
                results[pair] = "unsure"
            continue
        answered = {v.pair: v for v in response.parsed_output.verdicts}
        for n, pair in enumerate(batch):
            v = answered.get(n)
            results[pair] = v.verdict if v else "unsure"
            if v and v.verdict != "different":
                i, j = pair
                print(f"    {entries[i].key} / {entries[j].key}: {v.verdict} - {v.reason}")
    return results


def main() -> None:
    sources = sorted(p for p in BIB_DIR.glob("*.bib") if p not in (UNIQUE_OUT, REVIEW_OUT))
    if not sources:
        sys.exit(f"No input .bib files found in {BIB_DIR}")

    entries = []
    for path in sources:
        found = read_entries(path)
        print(f"{path.name}: {len(found)} entries")
        entries.extend(found)

    pairs = candidate_pairs(entries)
    print(f"{len(pairs)} candidate duplicate pairs")

    verdicts = {}
    if pairs:
        # Same DOI is treated as a certain duplicate without asking.
        to_ask = []
        for i, j in pairs:
            if entries[i].doi and entries[i].doi == entries[j].doi:
                verdicts[(i, j)] = "duplicate"
            else:
                to_ask.append((i, j))
        if to_ask:
            verdicts.update(judge_pairs(anthropic.Anthropic(), entries, to_ask))

    # Group entries linked by "duplicate" or "unsure" verdicts (union-find).
    parent = list(range(len(entries)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (i, j), verdict in verdicts.items():
        if verdict != "different":
            parent[find(i)] = find(j)

    unsure_roots = {find(i) for (i, _), v in verdicts.items() if v == "unsure"}
    groups: dict[int, list[int]] = {}
    for idx in range(len(entries)):
        groups.setdefault(find(idx), []).append(idx)

    unique, review = [], []
    for root, members in groups.items():
        if root in unsure_roots:
            review.append(members)
        else:
            unique.append(max((entries[m] for m in members), key=Entry.completeness))

    keys = [e.key for e in unique]
    for key in sorted({k for k in keys if keys.count(k) > 1}):
        print(f"warning: key {key!r} is used by different publications in {UNIQUE_OUT.name}")

    UNIQUE_OUT.write_text("\n\n".join(e.raw for e in unique) + "\n", encoding="utf-8")
    REVIEW_OUT.write_text(
        "\n\n".join(
            f"% ---- possible duplicate group {n} ----\n"
            + "\n\n".join(f"% from {entries[m].source}\n{entries[m].raw}" for m in members)
            for n, members in enumerate(review, 1)
        ) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(unique)} entries to {UNIQUE_OUT.name}")
    print(f"Wrote {sum(map(len, review))} entries in {len(review)} groups to {REVIEW_OUT.name}")


if __name__ == "__main__":
    main()
