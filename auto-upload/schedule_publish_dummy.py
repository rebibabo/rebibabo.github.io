"""
定时发布 — 干跑测试
每篇假装发布（sleep 10s），只输出文件名，不实际发到 CSDN。
"""

import json
import os
import time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "schedule_config.json")


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def main():
    log("===== 干跑测试开始 =====")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    daily_limit = config.get("daily_limit", 1)
    default_columns = config.get("default_columns", [])
    articles = config.get("articles", [])

    log(f"待发布 {len(articles)} 篇，上限 {daily_limit} 篇/天")
    log(f"默认专栏: {default_columns}")
    log("")

    for i, article in enumerate(articles):
        if i >= daily_limit:
            break

        path = article["path"]
        columns = article.get("columns", default_columns)
        tags = article.get("tags", [])

        log(f"({i + 1}/{daily_limit}) 📝 {path}")
        log(f"              专栏: {columns}")
        if tags:
            log(f"              标签: {tags}")

        for sec in range(10, 0, -1):
            print(f"\r  ⏳ 假装发布中... {sec:2d}s", end="", flush=True)
            time.sleep(1)
        print("\r  ✅ 假装发布完成" + " " * 20)

    log("")
    log(f"🎉 干跑完成: 模拟发布 {min(daily_limit, len(articles))} 篇")


if __name__ == "__main__":
    main()
