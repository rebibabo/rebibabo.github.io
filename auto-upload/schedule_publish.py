"""
定时发布调度脚本
================
由 launchd / cron 在每天凌晨 00:00 触发，从 schedule_config.json 中
取出待发布文章，按 daily_limit 上限发布，完成后更新配置。

用法（手动测试）：
    python3 auto-upload/schedule_publish.py
"""

import json
import subprocess
import sys
import os
import threading
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "schedule_config.json")
PUBLISH_SCRIPT = os.path.join(SCRIPT_DIR, "publish_csdn.py")
LOG_FILE = os.path.join(SCRIPT_DIR, "schedule.log")


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    log("===== 定时发布开始 =====")

    # 读配置
    if not os.path.exists(CONFIG_FILE):
        log(f"❌ 配置文件不存在: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    daily_limit = config.get("daily_limit", 1)
    default_columns = config.get("default_columns", [])
    articles = config.get("articles", [])

    if not articles:
        log("📭 待发布列表为空，跳过")
        return

    log(f"📋 待发布 {len(articles)} 篇，今日上限 {daily_limit} 篇")

    published = 0
    remaining = []

    for article in articles:
        if published >= daily_limit:
            remaining.append(article)
            continue

        # 兼容两种格式：纯字符串路径，或 {"path": ..., "columns": [...], "tags": [...]}
        if isinstance(article, str):
            path, columns, tags = article, default_columns, []
        else:
            path = article["path"]
            columns = article.get("columns", default_columns)
            tags = article.get("tags", [])

        log(f"📝 发布 ({published + 1}/{daily_limit}): {path}")

        # 构建命令（-u 让子进程输出不缓冲，可实时透传）
        cmd = [sys.executable, "-u", PUBLISH_SCRIPT, path]
        if columns:
            cmd += ["-c", ",".join(columns)]
        cmd.extend(tags)

        blog_root = os.path.join(SCRIPT_DIR, "..")
        # 实时流式打印子进程输出（同时进日志），不再静默捕获
        proc = subprocess.Popen(cmd, cwd=blog_root, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        streamer = threading.Thread(
            target=lambda: [log(f"   │ {line.rstrip()}") for line in proc.stdout],
            daemon=True,
        )
        streamer.start()
        try:
            returncode = proc.wait(timeout=1800)
        except subprocess.TimeoutExpired:
            proc.kill()
            log(f"   ⏱️  发布超时（30分钟），保留在队列")
            remaining.append(article)
            continue
        streamer.join(timeout=5)

        if returncode == 0:
            published += 1
            log(f"   ✅ 发布成功")
        else:
            log(f"   ❌ 发布失败 (exit={returncode})")
            remaining.append(article)

    # 写回剩余
    config["articles"] = remaining
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    log(f"🎉 完成: 发布 {published} 篇，剩余 {len(remaining)} 篇")


if __name__ == "__main__":
    main()
