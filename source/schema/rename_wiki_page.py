#!/usr/bin/env python3
"""
Rename a wiki page file AND update all wikilinks referencing it across the wiki.

Usage:
  python3 schema/rename_wiki_page.py <old_name> <new_name> [--dry-run]

Examples:
  # glossary single rename
  python3 schema/rename_wiki_page.py \\
    wiki/glossary/concurrency/Deadlock.md \\
    wiki/glossary/concurrency/死锁.md

  # dry-run first to see what will change
  python3 schema/rename_wiki_page.py \\
    wiki/glossary/concurrency/Deadlock.md \\
    wiki/glossary/concurrency/死锁.md \\
    --dry-run

  # batch rename from a mapping file (one "old -> new" per line)
  python3 schema/rename_wiki_page.py --batch mapping.txt

Rules:
  - old_name and new_name are relative to source/
  - Updates [[wikilinks]] in ALL .md files under source/wiki/
  - Updates the file's own frontmatter title and # heading if they match
  - Does NOT touch files under source/_posts/ (raw posts)
  - Dry-run shows what would change without making changes
"""

import os
import re
import sys
import shutil
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent.parent  # source/
WIKI_DIR = SOURCE_DIR / "wiki"


def find_all_md_files(root: Path):
    """Recursively find all .md files under root."""
    return sorted(root.rglob("*.md"))


def read_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: Path, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def make_wikilink_patterns(old_stem: str, new_stem: str):
    """
    Build regex patterns for wikilinks referencing the old page.

    Wikilinks can be:
      [[old_stem]]              — bare link
      [[old_stem|display text]] — aliased link
      [[old_stem.md|display]]   — with .md extension

    We match them all and replace the target part, preserving display text.
    """
    # Escape for regex: e.g. "concurrency/Deadlock" → "concurrency\/Deadlock"
    old_escaped = re.escape(old_stem)

    # Pattern: matches [[...]] where the target is old_stem (with optional .md)
    # Group 1: the old target (old_stem or old_stem.md)
    # Group 2: optional |display text (or \| escaped pipe in markdown tables)
    pattern = re.compile(
        r"\[\["
        + old_escaped
        + r"(\.md)?"               # optional .md
        + r"(\\?\|[^\]]+)?"        # optional | or \| display text
        + r"\]\]"
    )
    return pattern


def update_wikilinks(content: str, old_stem: str, new_stem: str) -> tuple[str, int]:
    """Replace all wikilinks pointing to old_stem with new_stem. Returns (new_content, count)."""
    pattern = make_wikilink_patterns(old_stem, new_stem)
    count = len(pattern.findall(content))

    def replacer(m):
        # m.group(0) is the full match: [[old|display]]
        alias = m.group(2) or ""  # |display text, or empty
        return f"[[{new_stem}{alias}]]"

    return pattern.sub(replacer, content), count


def update_title_and_heading(content: str, old_name: str, new_name: str) -> tuple[str, int]:
    """
    Update the file's own frontmatter `title` field and first `# heading`
    if they match the old filename stem.
    """
    changes = 0
    old_title = Path(old_name).stem  # e.g. "Deadlock"
    new_title = Path(new_name).stem  # e.g. "死锁"

    # Update frontmatter title:  ^title: OldTitle$
    title_pattern = re.compile(r"^(title:\s*)" + re.escape(old_title) + r"(\s*)$", re.MULTILINE)
    if title_pattern.search(content):
        content = title_pattern.sub(r"\1" + new_title + r"\2", content)
        changes += 1

    # Update first # heading:  # OldTitle  or  # OldTitle（...）
    heading_pattern = re.compile(
        r"^(#\s+)" + re.escape(old_title) + r"(\s*(?:（[^）]*）)?.*)$", re.MULTILINE
    )
    if heading_pattern.search(content):
        content = heading_pattern.sub(r"\1" + new_title + r"\2", content)
        changes += 1

    return content, changes


def rename_page(old_rel: str, new_rel: str, dry_run: bool = False):
    """
    Rename a wiki page and update all references.

    old_rel / new_rel are paths relative to SOURCE_DIR.
    """
    old_path = SOURCE_DIR / old_rel
    new_path = SOURCE_DIR / new_rel

    # Validate
    if not old_path.exists():
        print(f"ERROR: source file not found: {old_path}")
        return False

    if new_path.exists():
        new_size = new_path.stat().st_size
        if new_size > 0:
            print(f"ERROR: target file already exists with content: {new_path} ({new_size} bytes)")
            print(f"  Delete it first or choose a different name.")
            return False
        else:
            # empty file — likely an Obsidian auto-created placeholder, OK to overwrite
            print(f"  (target exists as empty file, will overwrite)")

    # Compute stems for wikilink matching.
    # e.g. wiki/glossary/concurrency/Deadlock.md → wiki/glossary/concurrency/Deadlock
    old_stem = old_rel.replace(".md", "")
    old_stem_no_ext = old_rel.replace(".md", "")
    new_stem = new_rel.replace(".md", "")

    # Also match the short form (just filename without path) for links within same directory
    old_short = Path(old_rel).stem
    new_short = Path(new_rel).stem

    print(f"Rename: {old_rel} → {new_rel}")
    if dry_run:
        print("  [DRY RUN — no changes will be made]")
    print()

    # 1. Scan all wiki files for references
    all_files = find_all_md_files(WIKI_DIR)
    updates = []

    for md_file in all_files:
        rel = str(md_file.relative_to(SOURCE_DIR))
        content = read_file(md_file)
        original = content

        # Update full-path wikilinks: wiki/glossary/concurrency/Deadlock
        content, count_full = update_wikilinks(content, old_stem_no_ext, new_stem)

        # If old and new are in same directory, also update short links just in case
        if Path(old_rel).parent == Path(new_rel).parent and old_short != new_short:
            short_old_stem = old_short
            short_new_stem = new_short
            content, count_short = update_wikilinks(content, short_old_stem, short_new_stem)
            total = count_full + count_short
        else:
            total = count_full

        # If this is the file being renamed, also update its title/heading
        if rel == old_rel:
            content, title_changes = update_title_and_heading(content, old_short, new_short)
            total += title_changes

        if content != original:
            updates.append((md_file, rel, total))

    if not updates:
        print("  No references found in wiki files.")
        if not dry_run and old_path != new_path:
            # Still do the rename even if no references
            print(f"  Renaming file only: {old_path} → {new_path}")
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_path), str(new_path))
        return True

    print(f"  Files to update: {len(updates)}")
    for md_file, rel, count in updates:
        print(f"    {rel}  ({count} reference{'s' if count > 1 else ''})")
    print()

    if dry_run:
        return True

    # 2. Apply changes: write updated content to all files
    for md_file, rel, count in updates:
        content = read_file(md_file)
        original = content

        content, _ = update_wikilinks(content, old_stem_no_ext, new_stem)

        if Path(old_rel).parent == Path(new_rel).parent and old_short != new_short:
            content, _ = update_wikilinks(content, old_short, new_short)

        if rel == old_rel:
            content, _ = update_title_and_heading(content, old_short, new_short)

        write_file(md_file, content)

    # 3. Rename the file itself
    if old_path != new_path:
        new_path.parent.mkdir(parents=True, exist_ok=True)
        # If new_path exists as empty, remove it first
        if new_path.exists() and new_path.stat().st_size == 0:
            new_path.unlink()
        shutil.move(str(old_path), str(new_path))
        print(f"  Moved: {old_rel} → {new_rel}")

    print(f"  Done. {len(updates)} file(s) updated.")
    return True


def batch_rename(mapping_file: str, dry_run: bool = False):
    """Read old→new mappings from a file and rename all."""
    with open(mapping_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    mappings = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Support "old -> new" or "old|new" or just "old new"
        parts = re.split(r"\s*->\s*|\s*\|\s*|\s{2,}", line)
        if len(parts) >= 2:
            mappings.append((parts[0].strip(), parts[1].strip()))

    if not mappings:
        print("No mappings found in file.")
        return

    print(f"Batch rename: {len(mappings)} entries")
    print()

    success = 0
    for old, new in mappings:
        if not rename_page(old, new, dry_run=dry_run):
            print(f"  FAILED: {old} → {new}")
        else:
            success += 1
        print()

    print(f"Complete: {success}/{len(mappings)} succeeded.")


def main():
    dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dry-run"]

    if not args:
        print(__doc__)
        print("\nERROR: missing arguments.")
        print("Usage: python3 schema/rename_wiki_page.py <old> <new> [--dry-run]")
        print("       python3 schema/rename_wiki_page.py --batch <mapping_file> [--dry-run]")
        sys.exit(1)

    if args[0] == "--batch":
        if len(args) < 2:
            print("ERROR: --batch requires a mapping file path")
            sys.exit(1)
        batch_rename(args[1], dry_run=dry_run)
    else:
        if len(args) < 2:
            print("ERROR: need both old and new paths")
            sys.exit(1)
        rename_page(args[0], args[1], dry_run=dry_run)


if __name__ == "__main__":
    main()
