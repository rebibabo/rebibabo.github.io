# Incremental Update Workflow

This file defines how to maintain the wiki incrementally without loading the whole repository into model context every time.

## Goal

Use local snapshots and local diffing to answer one question efficiently:

> Since the last processed baseline, which raw files changed, and what changed inside them?

The LLM should then read only the affected files and update only the relevant wiki pages.

## Why this exists

If the repository grows large, asking the LLM to rescan everything on every update wastes time and context.

A snapshot workflow keeps most of the work on disk:

- snapshot metadata is stored locally
- text blobs are stored locally
- diffs are computed locally
- only the concise change report needs to be read into context

## Tool

Use:

```bash
python3 schema/wiki_snapshot.py
```

## What the script stores

The script keeps its local state under:

- `.llm-wiki/state.json`
- `.llm-wiki/snapshots/*.json`
- `.llm-wiki/blobs/*.txt`

Important:

- snapshot files store metadata and hashes
- text blobs are deduplicated by hash
- the LLM does not need to load all blobs, only the diff output for changed files

## Default scope

By default the script snapshots:

- `_posts/`
- `images/`

This is intentional because those are the raw source areas.

It does not treat `wiki/` as the primary change source for ingestion decisions.

## Recommended workflow

### 1. Initialize a baseline

After a known-good wiki sync:

```bash
python3 schema/wiki_snapshot.py capture --set-baseline
```

This creates the first baseline snapshot.

### 2. When new notes are added or edited

Before updating the wiki:

```bash
python3 schema/wiki_snapshot.py delta
```

This does two things:

- creates a fresh snapshot
- compares it against the saved baseline

The output includes:

- added files
- deleted files
- modified files
- local text diffs for changed text files

### 3. LLM performs incremental wiki update

The LLM should use the delta output to decide:

- which raw files need to be read
- which series pages need updates
- which concept pages need edits
- whether a new concept page is justified

### 4. Promote the new snapshot after the update is accepted

Once the wiki update is complete:

```bash
python3 schema/wiki_snapshot.py promote-latest
```

This marks the newest snapshot as the next baseline.

## Commands

### Show current state

```bash
python3 schema/wiki_snapshot.py status
```

### Create a snapshot manually

```bash
python3 schema/wiki_snapshot.py capture
```

### Compare two explicit snapshots

```bash
python3 schema/wiki_snapshot.py diff --old .llm-wiki/snapshots/OLD.json --new .llm-wiki/snapshots/NEW.json
```

## LLM behavior expectations

When a user says "update wiki" or "sync latest changes", the LLM should:

1. run `delta`
2. inspect the changed raw files only
3. update the relevant wiki pages only
4. summarize what changed
5. when the update is accepted, run `promote-latest`

## Guardrails

- Do not treat every edited post as a reason to rebuild the full wiki.
- Do not create a new concept page for every minor wording change.
- Prefer updating existing series and concept pages first.
- Use the diff output to limit context, not to replace reading the affected raw file when semantic changes matter.
