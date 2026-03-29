#!/usr/bin/env python3
"""Generate index.html from individual .tex entry files."""

import re
from pathlib import Path

ENTRIES_DIR = Path(__file__).parent / "entries"

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


def find_matching_brace(text, start):
    """Find the index of the closing brace matching the opening brace at start."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1


def convert_latex_commands(text):
    """Convert LaTeX formatting commands to HTML."""
    result = text
    for cmd, tag in [("textbf", "b"), ("textit", "i"), ("emph", "i")]:
        while True:
            m = re.search(rf"\\{cmd}\{{", result)
            if not m:
                break
            brace_start = m.end() - 1
            brace_end = find_matching_brace(result, brace_start)
            if brace_end == -1:
                break
            inner = result[brace_start + 1:brace_end]
            result = result[:m.start()] + f"<{tag}>" + inner + f"</{tag}>" + result[brace_end + 1:]
    return result


def tex_to_html(tex_body):
    """Convert LaTeX body text to HTML paragraphs."""
    # Split into paragraphs on blank lines
    # But we need to be careful not to split inside math environments
    paragraphs = re.split(r"\n\s*\n", tex_body.strip())

    html_parts = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Handle \qed
        if para == r"\qed":
            html_parts.append('    <p class="BodyText" style="text-align: right">🎉</p>')
            continue

        # Convert LaTeX commands to HTML
        para = convert_latex_commands(para)

        # Indent content lines
        lines = para.split("\n")
        indented = "\n".join("        " + line.strip() for line in lines)

        html_parts.append(f'    <p class="BodyText">\n{indented}\n    </p>')

    return "\n\n" + "\n\n".join(html_parts) + "\n"


def parse_entry(tex_path):
    """Parse a .tex file and return (id, title, date, body_html)."""
    text = tex_path.read_text()

    # Extract metadata from comments
    meta = {}
    for m in re.finditer(r"^%\s*(\w+):\s*(.+)$", text, re.MULTILINE):
        meta[m.group(1)] = m.group(2).strip()

    # Extract body between \begin{document} and \end{document}
    doc_match = re.search(
        r"\\begin\{document\}(.*?)\\end\{document\}",
        text, re.DOTALL,
    )
    if doc_match:
        body = doc_match.group(1)
    else:
        # Fallback: use everything after metadata lines
        lines = text.split("\n")
        body_start = 0
        for i, line in enumerate(lines):
            if re.match(r"^%\s*\w+:", line) or line.strip() == "":
                continue
            else:
                body_start = i
                break
        body = "\n".join(lines[body_start:])

    body_html = tex_to_html(body)
    return meta["id"], meta["title"], meta["date"], body_html


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
    return header + "\n" + entry["body"]


def generate_entries(entries):
    """Generate all entry body HTML."""
    parts = []
    for i, entry in enumerate(entries):
        parts.append(generate_entry_html(entry, i))
    return "\n".join(parts)


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
