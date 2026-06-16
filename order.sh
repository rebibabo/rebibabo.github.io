#!/bin/bash                                                                                                                                                          [16:01:34]

START_DATE="2026-06-02"

for f in *.md; do
    num=$(echo "$f" | cut -d'-' -f1)
    num=$((10#$num))

    offset=$((num - 1))

    newdate=$(date -j -v+${offset}d -f "%Y-%m-%d" "$START_DATE" "+%Y-%m-%d")

    sed -i '' "s/^date: .*/date: $newdate/" "$f"

    echo "$f -> $newdate"
done