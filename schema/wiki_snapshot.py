#!/usr/bin/env python3
"""Snapshot and incremental diff helper for the local LLM wiki workflow."""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import json
from pathlib import Path
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
LLM_WIKI_DIR = ROOT / ".llm-wiki"
SNAPSHOT_DIR = LLM_WIKI_DIR / "snapshots"
BLOB_DIR = LLM_WIKI_DIR / "blobs"
STATE_PATH = LLM_WIKI_DIR / "state.json"

DEFAULT_INCLUDE = ["_posts", "images"]
IGNORE_PARTS = {".git", ".obsidian", ".llm-wiki", "node_modules", "public", ".deploy_git"}
TEXT_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".csv",
    ".tsv",
}


def ensure_dirs() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    BLOB_DIR.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")


def relative_posix(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_files(includes: list[str]) -> Iterable[Path]:
    seen: set[Path] = set()
    for include in includes:
        base = ROOT / include
        if not base.exists():
            continue
        if base.is_file():
            candidates = [base]
        else:
            candidates = sorted(p for p in base.rglob("*") if p.is_file())
        for path in candidates:
            if path in seen:
                continue
            if any(part in IGNORE_PARTS for part in path.parts):
                continue
            seen.add(path)
            yield path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def snapshot_file(path: Path) -> dict:
    stat = path.stat()
    rel = relative_posix(path)
    raw = path.read_bytes()
    entry = {
        "path": rel,
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }

    if is_text_file(path):
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", errors="replace")
        encoded = text.encode("utf-8")
        digest = sha256_bytes(encoded)
        blob_rel = f".llm-wiki/blobs/{digest}.txt"
        blob_path = ROOT / blob_rel
        if not blob_path.exists():
            blob_path.write_text(text, encoding="utf-8")
        entry.update(
            {
                "kind": "text",
                "sha256": digest,
                "blob": blob_rel,
                "line_count": text.count("\n") + (0 if not text else 1),
            }
        )
    else:
        digest = sha256_bytes(raw)
        entry.update(
            {
                "kind": "binary",
                "sha256": digest,
            }
        )

    return entry


def create_snapshot(includes: list[str]) -> Path:
    ensure_dirs()
    created_at = dt.datetime.now().astimezone().isoformat()
    files = [snapshot_file(path) for path in iter_files(includes)]
    payload = {
        "created_at": created_at,
        "root": str(ROOT),
        "includes": includes,
        "file_count": len(files),
        "files": files,
    }
    output = SNAPSHOT_DIR / f"{now_stamp()}.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return read_json(STATE_PATH)


def write_state(data: dict) -> None:
    ensure_dirs()
    STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def latest_snapshot() -> Path | None:
    ensure_dirs()
    files = list(SNAPSHOT_DIR.glob("*.json"))
    if not files:
        return None
    return max(files, key=lambda path: (path.stat().st_mtime_ns, path.name))


def file_map(snapshot: dict) -> dict[str, dict]:
    return {entry["path"]: entry for entry in snapshot["files"]}


def compare_snapshots(old_path: Path, new_path: Path) -> dict:
    old_snapshot = read_json(old_path)
    new_snapshot = read_json(new_path)
    old_files = file_map(old_snapshot)
    new_files = file_map(new_snapshot)

    old_paths = set(old_files)
    new_paths = set(new_files)

    added_paths = sorted(new_paths - old_paths)
    deleted_paths = sorted(old_paths - new_paths)
    common_paths = sorted(old_paths & new_paths)

    modified_paths = []
    unchanged_paths = []
    for rel in common_paths:
        old_entry = old_files[rel]
        new_entry = new_files[rel]
        if old_entry["sha256"] != new_entry["sha256"] or old_entry["size"] != new_entry["size"]:
            modified_paths.append(rel)
        else:
            unchanged_paths.append(rel)

    return {
        "old_snapshot": str(old_path.relative_to(ROOT)),
        "new_snapshot": str(new_path.relative_to(ROOT)),
        "added": [new_files[rel] for rel in added_paths],
        "deleted": [old_files[rel] for rel in deleted_paths],
        "modified": [{"old": old_files[rel], "new": new_files[rel]} for rel in modified_paths],
        "unchanged_count": len(unchanged_paths),
    }


def load_blob(rel_path: str) -> list[str]:
    blob_path = ROOT / rel_path
    if not blob_path.exists():
        return []
    return blob_path.read_text(encoding="utf-8").splitlines()


def diff_lines(old_entry: dict | None, new_entry: dict | None, context_lines: int) -> list[str]:
    old_lines = load_blob(old_entry["blob"]) if old_entry and old_entry.get("blob") else []
    new_lines = load_blob(new_entry["blob"]) if new_entry and new_entry.get("blob") else []
    from_label = old_entry["path"] if old_entry else "/dev/null"
    to_label = new_entry["path"] if new_entry else "/dev/null"
    return list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=from_label,
            tofile=to_label,
            n=context_lines,
            lineterm="",
        )
    )


def render_report(report: dict, context_lines: int, max_files: int, max_lines_per_file: int) -> str:
    lines: list[str] = []
    lines.append(f"baseline: {report['old_snapshot']}")
    lines.append(f"current:  {report['new_snapshot']}")
    lines.append("")
    lines.append(
        "changes: "
        f"{len(report['added'])} added, "
        f"{len(report['modified'])} modified, "
        f"{len(report['deleted'])} deleted, "
        f"{report['unchanged_count']} unchanged"
    )

    if report["added"]:
        lines.append("")
        lines.append("added files:")
        for entry in report["added"][:max_files]:
            lines.append(f"  + {entry['path']}")
        if len(report["added"]) > max_files:
            lines.append(f"  ... {len(report['added']) - max_files} more")

    if report["deleted"]:
        lines.append("")
        lines.append("deleted files:")
        for entry in report["deleted"][:max_files]:
            lines.append(f"  - {entry['path']}")
        if len(report["deleted"]) > max_files:
            lines.append(f"  ... {len(report['deleted']) - max_files} more")

    changed_text_entries: list[tuple[str, dict | None, dict | None]] = []
    for entry in report["added"]:
        if entry.get("kind") == "text":
            changed_text_entries.append(("added", None, entry))
    for pair in report["modified"]:
        if pair["new"].get("kind") == "text" and pair["old"].get("kind") == "text":
            changed_text_entries.append(("modified", pair["old"], pair["new"]))
    for entry in report["deleted"]:
        if entry.get("kind") == "text":
            changed_text_entries.append(("deleted", entry, None))

    if changed_text_entries:
        lines.append("")
        lines.append("text diffs:")
        shown = 0
        for change_type, old_entry, new_entry in changed_text_entries:
            if shown >= max_files:
                remaining = len(changed_text_entries) - shown
                lines.append(f"  ... {remaining} more changed text files")
                break
            ref = (new_entry or old_entry)["path"]
            lines.append("")
            lines.append(f"[{change_type}] {ref}")
            diff = diff_lines(old_entry, new_entry, context_lines)
            if not diff:
                lines.append("  (no textual diff available)")
            else:
                clipped = diff[:max_lines_per_file]
                lines.extend(clipped)
                if len(diff) > max_lines_per_file:
                    lines.append(f"... diff truncated, {len(diff) - max_lines_per_file} more lines")
            shown += 1

    return "\n".join(lines)


def cmd_capture(args: argparse.Namespace) -> int:
    snapshot_path = create_snapshot(args.include)
    if args.set_baseline:
        data = state()
        data["baseline_snapshot"] = str(snapshot_path.relative_to(ROOT))
        data["updated_at"] = dt.datetime.now().astimezone().isoformat()
        write_state(data)
    print(snapshot_path.relative_to(ROOT).as_posix())
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    data = state()
    latest = latest_snapshot()
    baseline = data.get("baseline_snapshot")
    print(f"root: {ROOT}")
    print(f"baseline: {baseline or '(not set)'}")
    print(f"latest: {latest.relative_to(ROOT).as_posix() if latest else '(none)'}")
    return 0


def cmd_delta(args: argparse.Namespace) -> int:
    data = state()
    baseline_rel = data.get("baseline_snapshot")
    snapshot_path = create_snapshot(args.include)
    print(f"new snapshot: {snapshot_path.relative_to(ROOT).as_posix()}")

    if not baseline_rel:
        print("baseline: (not set)")
        print("hint: run `python3 schema/wiki_snapshot.py capture --set-baseline` once after a known-good wiki sync.")
        return 0

    baseline_path = ROOT / baseline_rel
    if not baseline_path.exists():
        print(f"baseline missing: {baseline_rel}")
        return 1

    report = compare_snapshots(baseline_path, snapshot_path)
    print("")
    print(render_report(report, args.context_lines, args.max_files, args.max_lines_per_file))
    return 0


def cmd_promote_latest(_: argparse.Namespace) -> int:
    latest = latest_snapshot()
    if not latest:
        print("no snapshots available")
        return 1
    data = state()
    data["baseline_snapshot"] = str(latest.relative_to(ROOT))
    data["updated_at"] = dt.datetime.now().astimezone().isoformat()
    write_state(data)
    print(f"baseline -> {latest.relative_to(ROOT).as_posix()}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    old_path = ROOT / args.old
    new_path = ROOT / args.new
    if not old_path.exists():
        print(f"missing snapshot: {args.old}", file=sys.stderr)
        return 1
    if not new_path.exists():
        print(f"missing snapshot: {args.new}", file=sys.stderr)
        return 1
    report = compare_snapshots(old_path, new_path)
    print(render_report(report, args.context_lines, args.max_files, args.max_lines_per_file))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LLM wiki snapshot helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture = subparsers.add_parser("capture", help="create a snapshot")
    capture.add_argument("--include", action="append", default=list(DEFAULT_INCLUDE), help="relative path to include")
    capture.add_argument("--set-baseline", action="store_true", help="mark the new snapshot as the baseline")
    capture.set_defaults(func=cmd_capture)

    status = subparsers.add_parser("status", help="show current baseline and latest snapshot")
    status.set_defaults(func=cmd_status)

    delta = subparsers.add_parser("delta", help="capture a new snapshot and diff it against the baseline")
    delta.add_argument("--include", action="append", default=list(DEFAULT_INCLUDE), help="relative path to include")
    delta.add_argument("--context-lines", type=int, default=2, help="unified diff context lines")
    delta.add_argument("--max-files", type=int, default=20, help="maximum changed files to print")
    delta.add_argument("--max-lines-per-file", type=int, default=80, help="maximum diff lines per file")
    delta.set_defaults(func=cmd_delta)

    promote = subparsers.add_parser("promote-latest", help="mark the newest snapshot as the baseline")
    promote.set_defaults(func=cmd_promote_latest)

    diff = subparsers.add_parser("diff", help="diff two existing snapshots")
    diff.add_argument("--old", required=True, help="older snapshot path relative to repo root")
    diff.add_argument("--new", required=True, help="newer snapshot path relative to repo root")
    diff.add_argument("--context-lines", type=int, default=2, help="unified diff context lines")
    diff.add_argument("--max-files", type=int, default=20, help="maximum changed files to print")
    diff.add_argument("--max-lines-per-file", type=int, default=80, help="maximum diff lines per file")
    diff.set_defaults(func=cmd_diff)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
