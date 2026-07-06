#!/usr/bin/env python3
"""Check all wikilinks in wiki/*.md files and report broken references."""

from __future__ import annotations

"""
Usage:
  python3 schema/check_links.py            # check all links
  python3 schema/check_links.py --empty    # also list empty files (Obsidian leftovers)
  python3 schema/check_links.py --fix      # delete empty auto-created placeholder files

Scans:
  - [[target]]              bare link
  - [[target|alias]]        aliased link
  - [[path/to/target]]      relative path
  - [[path/to/target|text]] path with alias

Resolves targets against source/ directory, handles .md extension inference.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

SOURCE_DIR = Path(__file__).resolve().parent.parent  # source/
WIKI_DIR = SOURCE_DIR / "wiki"


def find_all_md_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.md"))


def extract_wikilinks(content: str) -> list[tuple[str, str | None]]:
    """
    Extract all [[target|alias]] wikilinks.
    Handles escaped pipes (\\|) that appear in markdown tables.
    Returns list of (target, alias_or_None).
    """
    pattern = re.compile(r"\[\[([^\]]+?)\]\]")
    matches = []
    for m in pattern.finditer(content):
        inner = m.group(1)

        # Skip external URLs and anchor-only links
        if inner.startswith("http://") or inner.startswith("https://"):
            continue
        if inner.startswith("#"):
            continue

        # In markdown tables, | is escaped as \| to avoid being
        # treated as a cell separator. Unescape before parsing.
        # [[wiki/path\|display]] → target=wiki/path, alias=display
        inner_unescaped = inner.replace("\\|", "|")

        # Split on unescaped pipe: target|alias  or  just target
        parts = inner_unescaped.split("|", 1)
        target = parts[0].strip()

        # Skip raw post paths (these point to _posts/ which we don't check)
        if target.startswith("_posts/"):
            continue

        matches.append((target, m.group(0)))
    return matches


def resolve_target(target: str, source_file: Path) -> Path | None:
    """
    Resolve a wikilink target to an absolute file path.
    Tries multiple resolution strategies.
    """
    candidate = target
    rel_source = source_file.relative_to(SOURCE_DIR)

    # Strategy 1: absolute from source root (e.g. "wiki/concepts/concurrency/AQS")
    for ext in ("", ".md"):
        path = SOURCE_DIR / f"{candidate}{ext}"
        if path.exists():
            return path

    # Strategy 2: relative to source file's directory
    for ext in ("", ".md"):
        path = source_file.parent / f"{candidate}{ext}"
        if path.exists():
            return path

    # Strategy 3: relative to wiki/ root
    for ext in ("", ".md"):
        path = WIKI_DIR / f"{candidate}{ext}"
        if path.exists():
            return path

    # Strategy 4: short name — search wiki/ recursively
    # e.g. "DSP" → find wiki/glossary/programmatic-ads/DSP.md
    stem = candidate
    for ext in ("", ".md"):
        name = f"{stem}{ext}"
        found = list(WIKI_DIR.rglob(name))
        if found:
            return found[0]

    return None


def main():
    show_empty = "--empty" in sys.argv
    fix_empty = "--fix" in sys.argv

    all_files = find_all_md_files(WIKI_DIR)
    broken = defaultdict(list)  # target -> list of (source_file, line)
    empty_files = []

    for md_file in all_files:
        rel = str(md_file.relative_to(SOURCE_DIR))
        content = md_file.read_text(encoding="utf-8")

        # Check if this file is empty
        if len(content.strip()) == 0:
            empty_files.append(md_file)
            continue

        # Extract wikilinks with line numbers
        lines = content.split("\n")
        for lineno, line in enumerate(lines, 1):
            for target, full_match in extract_wikilinks(line):
                resolved = resolve_target(target, md_file)
                if resolved is None:
                    broken[target].append((rel, lineno, full_match))

    # Report empty files
    if empty_files:
        print("=" * 60)
        print(f" EMPTY FILES ({len(empty_files)})")
        print("  (Obsidian auto-created placeholders from dangling references)")
        print("=" * 60)
        for f in empty_files:
            rel = str(f.relative_to(SOURCE_DIR))
            print(f"  {rel}")
        print()

        if fix_empty:
            print("  Deleting empty files...")
            for f in empty_files:
                f.unlink()
                print(f"    removed: {f.relative_to(SOURCE_DIR)}")
            print(f"  Done. {len(empty_files)} file(s) deleted.")
            print()

    # Report broken links
    if broken:
        print("=" * 60)
        print(f" BROKEN LINKS ({len(broken)} unique missing targets)")
        print("  (wikilinks pointing to files that don't exist)")
        print("=" * 60)

        for target, refs in sorted(broken.items()):
            print(f"\n  [[{target}]]  ← referenced from:")
            for src_rel, lineno, match in refs:
                print(f"    {src_rel}:{lineno}  {match}")

        print()
        print(f"  Summary: {len(broken)} missing target(s) from {sum(len(r) for r in broken.values())} reference(s).")
    else:
        if not empty_files:
            print("All wikilinks OK — no broken references, no empty files.")

    # Exit code for CI/automation
    if broken or (empty_files and not fix_empty):
        sys.exit(1)


if __name__ == "__main__":
    main()
