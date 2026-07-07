#!/bin/bash
# ============================================================
# CSDN 定时发布 — caffeinate 包装
# 由 launchd 在 00:00 触发，caffeinate 防止执行中途合盖休眠
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$SCRIPT_DIR/schedule.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] caffeinate 启动" >> "$LOG"
exec caffeinate -i python3 "$SCRIPT_DIR/schedule_publish.py"
