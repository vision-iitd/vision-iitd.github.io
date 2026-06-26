"""
One-time migration: parse the hardcoded entries in publications.html into
_data/publications.yml so the page can be re-templated to read from data.

Usage:
    python scripts/migrate_publications.py
"""
import re
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parent.parent
SRC_HTML = ROOT / "publications.html"
OUT_YAML = ROOT / "_data" / "publications.yml"


def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse_entry(li: Tag):
    p = li.find("p")
    if p is None:
        return None

    strong = p.find("strong")
    if strong is None:
        return None
    title = clean_text(strong.get_text())

    links = []
    for a in p.find_all("a"):
        href = (a.get("href") or "").strip()
        label = clean_text(a.get_text())
        if href:
            links.append({"label": label, "url": href})

    # Collect text lines between </strong> and the link list, split on <br>.
    lines = []
    current = []
    node = strong.next_sibling
    while node is not None:
        if isinstance(node, Tag) and node.name == "a":
            break
        if isinstance(node, Tag) and node.name == "br":
            text = clean_text("".join(current))
            if text:
                lines.append(text)
            current = []
        elif isinstance(node, NavigableString):
            current.append(str(node))
        elif isinstance(node, Tag):
            current.append(node.get_text())
        node = node.next_sibling
    text = clean_text("".join(current))
    if text and not text.startswith("["):
        lines.append(text)

    authors = lines[0] if len(lines) > 0 else ""
    venue = ", ".join(lines[1:]) if len(lines) > 1 else ""

    return {
        "title": title,
        "authors": authors,
        "venue": venue,
        "links": links,
    }


def main():
    soup = BeautifulSoup(SRC_HTML.read_text(), "html.parser")

    years = {}
    for h3 in soup.find_all("h3"):
        year_label = clean_text(h3.get_text())
        ul = h3.find_next_sibling("ul")
        if ul is None:
            continue
        # Use recursive=True: the source HTML has several unclosed/nested
        # <li> tags (e.g. in the "Before 2016" section), so entries can end
        # up nested inside a preceding <li> rather than as direct siblings.
        # Each <li>'s own first <p> child still belongs only to it, so this
        # does not cause duplicate parsing.
        entries = []
        for li in ul.find_all("li"):
            entry = parse_entry(li)
            if entry:
                entries.append(entry)
        if entries:
            years[year_label] = entries

    ordered = [{"year": year, "entries": entries} for year, entries in years.items()]

    OUT_YAML.parent.mkdir(exist_ok=True)
    with OUT_YAML.open("w") as f:
        yaml.dump(ordered, f, allow_unicode=True, sort_keys=False, width=1000)

    total = sum(len(y["entries"]) for y in ordered)
    print(f"Wrote {total} entries across {len(ordered)} year groups to {OUT_YAML}")


if __name__ == "__main__":
    main()
