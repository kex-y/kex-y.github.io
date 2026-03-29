#!/usr/bin/env python3
"""Generate index.html from individual .tex entry files."""

import re
from pathlib import Path

ENTRIES_DIR = Path(__file__).parent / "entries"

# Front matter matching the original exactly
FRONT_MATTER = """\
---
layout: default
title: Kexing Ying's website
author: <a href="mailto:kexing.ying@epfl.ch">kexing.ying@epfl.ch</a>
date: Last updated Mar. 2025
abstract: Welcome to the personal website of <a href="https://people.epfl.ch/kexing.ying/?lang=en">Kexing Ying</a> -
    a PhD student under the supervision of Prof. Xue-Mei Li within the chair of
    <a href="https://www.epfl.ch/labs/stoan/">Stochastic Analysis</a> at EPFL. I am also active in the
    formalisation of mathematics (mostly within probability theory) using the
    <a href="https://github.com/leanprover-community/mathlib"> Lean theorem prover</a>.

    I will post about maths and maybe some other stuff I find interesting.
---"""


def parse_entry(tex_path):
    """Parse a .tex file and return (id, title, date, body)."""
    text = tex_path.read_text()
    meta = {}
    lines = text.split("\n")
    body_start = 0
    for i, line in enumerate(lines):
        m = re.match(r"^%\s*(\w+):\s*(.+)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip()
        elif line.strip() == "":
            continue
        else:
            body_start = i
            break
    body = "\n".join(lines[body_start:])
    return meta["id"], meta["title"], meta["date"], body


def load_entries():
    """Load all entries from the entries directory, sorted newest first."""
    entries = []
    for date_dir in sorted(ENTRIES_DIR.iterdir(), reverse=True):
        if not date_dir.is_dir():
            continue
        for tex_file in date_dir.glob("*.tex"):
            entry_id, title, date, body = parse_entry(tex_file)
            entries.append({
                "id": entry_id,
                "title": title,
                "date": date,
                "dir_name": date_dir.name,
                "body": body,
            })
    return entries


def generate_toc_entry(entry, is_first=False, is_last=False):
    """Generate a single TOC entry."""
    eid, title, date = entry["id"], entry["title"], entry["date"]
    if is_first:
        return (
            f'<a href="#{eid}">\n'
            f'    <div class="Contents">\n'
            f'        {title}\n'
            f'    </div>\n'
            f'    <div class="ContentsRight">\n'
            f'        {date}\n'
            f'    </div>\n'
            f'</a>'
        )
    elif is_last:
        return (
            f'<p>\n'
            f'<a href="#{eid}" class="Subsection">\n'
            f'    <div>\n'
            f'        <div class="Contents">\n'
            f'            {title} \n'
            f'        </div>\n'
            f'        <div class="ContentsRight">\n'
            f'            {date}\n'
            f'        </div>\n'
            f'    </div>\n'
            f'</a>\n'
            f'</p>'
        )
    else:
        return (
            f'<p>\n'
            f'<a href="#{eid}">\n'
            f'    <div class="Contents">\n'
            f'        {title}\n'
            f'    </div>\n'
            f'    <div class="ContentsRight">\n'
            f'        {date}\n'
            f'    </div>\n'
            f'</a>\n'
            f'</p>'
        )


def generate_toc(entries):
    """Generate the table of contents HTML."""
    parts = ['<p class="Section">Contents</p>']
    for i, entry in enumerate(entries):
        parts.append("")
        parts.append(generate_toc_entry(
            entry,
            is_first=(i == 0),
            is_last=(i == len(entries) - 1),
        ))
    return "\n".join(parts)


def generate_entry_html(entry, index):
    """Generate the HTML for a single entry."""
    eid, title, date = entry["id"], entry["title"], entry["date"]
    # First two entries: trailing space after id, no &ensp;
    # Later entries: no trailing space, with &ensp;
    if index < 2:
        header = (
            f'<p class="Section" id="{eid}"> \n'
            f'    <i>{date}.</i> {title}</p>'
        )
    else:
        header = (
            f'<p class="Section" id="{eid}">\n'
            f'    <i>{date}.</i> &ensp; {title}</p>'
        )
    return header + "\n\n" + entry["body"]


def generate_entries(entries):
    """Generate all entry body HTML."""
    parts = []
    for i, entry in enumerate(entries):
        parts.append(generate_entry_html(entry, i))
    return "\n\n".join(parts)


def main():
    entries = load_entries()
    toc = generate_toc(entries)
    bodies = generate_entries(entries)

    html = FRONT_MATTER + "\n\n" + toc + "\n\n" + '<div class="spacer"></div>' + "\n\n" + bodies + "\n"

    output = Path(__file__).parent / "index.html"
    output.write_text(html)
    print(f"Generated {output} with {len(entries)} entries.")


if __name__ == "__main__":
    main()
