"""
CSDN 自动发布文章脚本
=====================
使用已保存的 auth.json 跳过登录，打开 CSDN 写文章页面，
自动填入标题和内容并发布。

用法：
    python3 auto-upload/publish_csdn.py <markdown文件路径>

示例：
    python3 auto-upload/publish_csdn.py source/_posts/xxx.md
"""

import sys
import os
import re
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

AUTH_FILE = os.path.join(os.path.dirname(__file__), "auth.json")
CSDN_WRITE_URL = "https://mp.csdn.net/mp_blog/creation/editor"


def parse_markdown(filepath: str) -> dict:
    """解析 hexo markdown 文章的 front matter 和正文"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析 front matter
    front_matter = {}
    body = content
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if m:
        body = content[m.end():]
        for line in m.group(1).strip().split("\n"):
            line = line.strip()
            if ":" in line:
                key, _, val = line.partition(":")
                front_matter[key.strip()] = val.strip().strip('"').strip("'")

    title = front_matter.get("title", Path(filepath).stem)

    # 处理 hexo 特有标签转为纯 markdown（简单处理）
    # 移除 {% ... %} 标签块
    body = re.sub(r'\{%\s*note[^%]*%\}|'r'\{%\s*endnote[^%]*%\}', '', body)
    body = re.sub(r'\{%[^%]*%\}', '', body)

    return {"title": title, "body": body.strip(), "tags": front_matter.get("tags", "")}


def publish(title: str, body: str, tags: str = ""):
    """用 Playwright 自动发布 CSDN 文章"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            storage_state=AUTH_FILE,
            viewport={"width": 1280, "height": 900},
            locale="zh-CN",
        )
        page = context.new_page()

        print("打开 CSDN 写文章页面...")
        page.goto(CSDN_WRITE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # 填入标题
        print(f"填入标题: {title}")
        try:
            title_input = page.locator('input[placeholder*="标题"], .article-title-input input, #article-title')
            title_input.wait_for(timeout=10000)
            title_input.click()
            title_input.fill("")
            title_input.fill(title)
        except Exception as e:
            print(f"⚠️  填写标题失败: {e}")

        # 填入正文（CSDN 编辑器通常是 contenteditable / markdown 编辑器）
        print("填入正文...")
        try:
            # CSDN 编辑器通常是一个 contenteditable 区域或者 CodeMirror/Monaco 编辑器
            # 尝试几种常见选择器
            editor = page.locator(
                ".editor-content, .markdown-editor, #editor, .CodeMirror, "
                "textarea, [contenteditable='true'].editor"
            ).first
            editor.wait_for(timeout=10000)
            editor.click()
            # 如果是纯文本编辑器直接填
            if editor.evaluate("el => el.tagName") == "TEXTAREA":
                editor.fill(body)
            else:
                # contenteditable 类型用键盘输入
                editor.fill(body)
        except Exception as e:
            print(f"⚠️  自动填写正文失败: {e}")
            print("正文需要手动粘贴，脚本已阻塞，请手动操作后按 Enter...")
            input()

        # 等待一下，让你确认内容
        print("\n内容已填入，请在浏览器中检查。")
        print("确认无误后按 Enter 发布，或 Ctrl+C 取消...")
        input()

        # 点击发布按钮
        print("正在点击发布...")
        try:
            publish_btn = page.locator(
                'button:has-text("发布"), .publish-btn, #publish, '
                '[class*="publish"]:not([class*="publish"])'
            ).first
            publish_btn.wait_for(timeout=5000)
            publish_btn.click()
            page.wait_for_timeout(5000)
            print("✅ 发布完成！")
        except Exception as e:
            print(f"⚠️  自动点击发布失败: {e}")
            print("请手动点击发布按钮。")

        page.wait_for_timeout(3000)
        browser.close()


def main():
    if len(sys.argv) < 2:
        print("用法: python3 auto-upload/publish_csdn.py <markdown文件路径>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    article = parse_markdown(filepath)
    print(f"文章标题: {article['title']}")
    publish(article["title"], article["body"], article.get("tags", ""))


if __name__ == "__main__":
    main()
