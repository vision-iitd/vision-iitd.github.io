"""
Periodic (manual) updater: scrape Google Scholar for new conference/journal
entries and merge them into _data/publications.yml.

Run this locally whenever you want to check for new publications. It does
NOT touch the repo's git state — review the diff to _data/publications.yml
yourself and commit/push when you're happy with it.

Usage:
    python scripts/update_publications.py [--since-year 2024] [--dry-run]

Notes:
- Only entries from --since-year (default 2024) onward are considered, since
  everything before that is already migrated into publications.yml.
- Google Scholar profile listings give title + year cheaply. Venue/authors
  require an extra per-publication request, so those are only fetched for
  candidates that pass the year filter, to keep request volume low.
- Ambiguous entries (can't tell conference vs. journal vs. preprint/thesis)
  are written to _data/publications_review.yml for you to triage by hand,
  rather than being silently dropped or wrongly included.
- A small cache (_data/.scholar_seen.yml) remembers titles already triaged
  (added, excluded, or sent to review) so re-runs don't re-fetch and
  re-classify the same entries every time.
"""
import argparse
import re
import sys
import time
import unicodedata
from pathlib import Path

import yaml
from scholarly import scholarly

ROOT = Path(__file__).resolve().parent.parent
DATA_YAML = ROOT / "_data" / "publications.yml"
REVIEW_YAML = ROOT / "_data" / "publications_review.yml"
SEEN_YAML = ROOT / "_data" / ".scholar_seen.yml"

SCHOLAR_USER_ID = "Q8cTLNMAAAAJ"

CONFERENCE_KEYWORDS = [
    "conference", "workshop", "symposium", "proceedings", "congress",
    "meeting", "winter conference", "iccv", "cvpr", "eccv", "wacv",
    "miccai", "icip", "ijcai", "neurips", "icml", "iclr",
]
JOURNAL_KEYWORDS = [
    "journal", "transactions", "letters", "magazine", "reports",
    "pattern recognition", "image analysis", "radiology",
]
EXCLUDE_KEYWORDS = [
    "arxiv", "preprint", "thesis", "dissertation", "patent",
    "technical report", "biorxiv",
]


def normalize_title(title: str) -> str:
    title = unicodedata.normalize("NFKD", title)
    title = re.sub(r"[^a-z0-9 ]", "", title.lower())
    return re.sub(r"\s+", " ", title).strip()


def load_yaml(path: Path, default):
    if not path.exists():
        return default
    with path.open() as f:
        return yaml.safe_load(f) or default


def dump_yaml(path: Path, data):
    path.parent.mkdir(exist_ok=True)
    with path.open("w") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, width=1000)


def existing_titles(publications_data):
    titles = set()
    for group in publications_data:
        for entry in group.get("entries", []):
            titles.add(normalize_title(entry["title"]))
    return titles


def classify(venue: str, citation: str):
    text = f"{venue} {citation}".lower()
    if any(k in text for k in EXCLUDE_KEYWORDS):
        return "excluded"
    is_conf = any(k in text for k in CONFERENCE_KEYWORDS)
    is_journal = any(k in text for k in JOURNAL_KEYWORDS)
    if is_conf and not is_journal:
        return "conference"
    if is_journal and not is_conf:
        return "journal"
    return "review"


def format_authors(bib_author: str) -> str:
    # scholarly gives "A Agarwal and B Gupta and C Arora"
    parts = [p.strip() for p in bib_author.split(" and ") if p.strip()]
    if len(parts) <= 1:
        return bib_author
    return ", ".join(parts[:-1]) + ", and " + parts[-1]


def insert_into_year_group(publications_data, year: str, entry: dict):
    for group in publications_data:
        if str(group.get("year")) == year:
            group["entries"].insert(0, entry)
            return
    # New year group: insert at the top (years are listed newest-first).
    publications_data.insert(0, {"year": year, "entries": [entry]})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--since-year", type=int, default=2024)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--delay", type=float, default=2.0,
                         help="seconds to sleep between per-publication requests")
    args = parser.parse_args()

    publications_data = load_yaml(DATA_YAML, [])
    review_data = load_yaml(REVIEW_YAML, [])
    seen = load_yaml(SEEN_YAML, {})

    known_titles = existing_titles(publications_data)
    known_titles |= {normalize_title(e["title"]) for e in review_data}

    print(f"Fetching Scholar profile for user={SCHOLAR_USER_ID} ...")
    try:
        author = scholarly.search_author_id(SCHOLAR_USER_ID)
        author = scholarly.fill(author, sections=["publications"])
    except Exception as exc:
        print(f"ERROR: failed to fetch author profile: {exc}", file=sys.stderr)
        print("Google Scholar may be rate-limiting this IP. Try again later.",
              file=sys.stderr)
        sys.exit(1)

    candidates = []
    for pub in author.get("publications", []):
        bib = pub.get("bib", {})
        title = bib.get("title", "").strip()
        if not title:
            continue
        norm = normalize_title(title)
        if norm in known_titles:
            continue
        pub_year = bib.get("pub_year")
        try:
            year = int(pub_year)
        except (TypeError, ValueError):
            continue
        if year < args.since_year:
            continue
        if norm in seen:
            continue  # already triaged in a previous run
        candidates.append((pub, title, year, norm))

    print(f"{len(candidates)} new candidate(s) from {args.since_year} onward to triage.")

    added, excluded, sent_to_review = 0, 0, 0

    for pub, title, year, norm in candidates:
        try:
            filled = scholarly.fill(pub)
        except Exception as exc:
            print(f"  WARN: could not fetch details for '{title}': {exc}")
            continue
        time.sleep(args.delay)

        fbib = filled.get("bib", {})
        venue = fbib.get("venue", "") or ""
        citation = fbib.get("citation", "") or ""
        authors_raw = fbib.get("author", "")
        url = filled.get("pub_url") or fbib.get("url") or ""

        category = classify(venue, citation)
        venue_str = venue or citation or "Unknown venue"
        if year:
            venue_str = f"{venue_str}, {year}"

        entry = {
            "title": title,
            "authors": format_authors(authors_raw) if authors_raw else "",
            "venue": venue_str,
            "links": [{"label": "paper", "url": url}] if url else [],
        }

        seen[norm] = category

        if category == "excluded":
            print(f"  EXCLUDED ({venue_str}): {title}")
            excluded += 1
        elif category == "review":
            print(f"  REVIEW   ({venue_str}): {title}")
            review_data.append(entry)
            sent_to_review += 1
        else:
            print(f"  ADDED [{category}] ({venue_str}): {title}")
            insert_into_year_group(publications_data, str(year), entry)
            added += 1

    print(f"\nSummary: {added} added, {sent_to_review} sent to review, {excluded} excluded.")

    if args.dry_run:
        print("Dry run: no files written.")
        return

    if added:
        dump_yaml(DATA_YAML, publications_data)
    if sent_to_review:
        dump_yaml(REVIEW_YAML, review_data)
    if seen:
        dump_yaml(SEEN_YAML, seen)

    print("Done. Review the diff in _data/publications.yml" +
          (" and _data/publications_review.yml" if sent_to_review else "") +
          " before committing.")


if __name__ == "__main__":
    main()
