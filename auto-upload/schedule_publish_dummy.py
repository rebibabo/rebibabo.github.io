"""
合盖测试 — 逐篇假装发布，每篇 10s，全部发完
用来验证 caffeinate + 合盖后 Mac 是否继续跑
"""

import json
import os
import time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "schedule_config.json")


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def main():
    log("===== 合盖干跑测试 =====")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    articles = config.get("articles", [])
    total = len(articles)

    for i, article in enumerate(articles):
        path = article["path"]
        log(f"({i + 1}/{total}) 📝 {path}")

        for sec in range(10, 0, -1):
            print(f"\r  ⏳ {sec:2d}s", end="", flush=True)
            time.sleep(1)
        print("\r  ✅ 完成" + " " * 10)

    log(f"🎉 全部完成: {total} 篇")


if __name__ == "__main__":
    main()
