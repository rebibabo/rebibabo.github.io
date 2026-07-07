"""
CSDN 自动发布文章脚本
=====================
用法：
    python3 auto-upload/publish_csdn.py <markdown文件路径> [标签1] [标签2] ...

示例：
    python3 auto-upload/publish_csdn.py source/_posts/xxx.md Java 高并发
"""

import re
import sys
import os
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright

# ============================================================
# 配置
# ============================================================
AUTH_FILE = os.path.join(os.path.dirname(__file__), "auth.json")
COLUMN_NAMES = ["Java高并发", "Java基础", "adss"]       # 专栏名列表，可多选
DEFAULT_TAGS = ["Java", "高并发"]   # 默认标签


# ============================================================
# Markdown 解析
# ============================================================
def parse_markdown(filepath: str) -> dict:
    """解析 hexo markdown，提取 title、正文、tags"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

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

    # 移除 hexo 特有标签
    body = re.sub(r'\{%\s*note[^%]*%\}|'r'\{%\s*endnote[^%]*%\}', '', body)
    body = re.sub(r'\{%[^%]*%\}', '', body)

    # 提取 tags
    raw_tags = front_matter.get("tags", "")
    tags = [t.strip().strip("'\"") for t in re.split(r'[,\n\[\]]+', raw_tags) if t.strip().strip("'\"")]

    return {"title": title, "body": body.strip(), "tags": tags}


# ============================================================
# 工具函数
# ============================================================
def safe_click(page, selector: str, timeout: int = 2000):
    """如果元素存在则点击，不存在则跳过"""
    try:
        el = page.locator(selector)
        el.wait_for(timeout=timeout)
        el.click()
        print(f"  ✅ 点击了: {selector}")
    except Exception:
        print(f"  ⏭️  未找到，跳过: {selector}")


# ============================================================
# 主流程
# ============================================================
def run(playwright: Playwright, title: str, body: str, tags: list[str]) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        storage_state=AUTH_FILE,
        viewport={"width": 1280, "height": 900},
        locale="zh-CN",
    )
    page = context.new_page()

    # ---- 第一步：打开 CSDN 后台，关闭广告 ----
    print("1. 打开 CSDN 创作后台...")
    page.goto("https://mp.csdn.net/")
    page.wait_for_timeout(2000)

    # 关闭广告弹窗（如果有的话）
    safe_click(page, ".close-btn")

    # ---- 第二步：点击「创作」→ 新标签页 ----
    print("2. 点击「创作」...")
    with page.expect_popup() as page1_info:
        page.get_by_role("link", name="创作").first.click()
    page1 = page1_info.value
    page1.wait_for_timeout(2000)

    # ---- 第三步：点击「使用 MD 编辑器」→ 再开一个标签页 ----
    print("3. 打开 MD 编辑器...")
    with page1.expect_popup() as page2_info:
        page1.get_by_role("button", name="使用 MD 编辑器").click()
    page2 = page2_info.value
    page2.wait_for_load_state("domcontentloaded")
    page2.wait_for_timeout(2000)

    # ---- 第四步：定位编辑器，清空模板内容，填入正文 ----
    print("4. 填入文章内容...")
    # 点一下编辑器区域获取焦点，然后全选清空
    page2.locator(".editor-pane, .CodeMirror, .markdown-editor, .editor").first.click()
    page2.wait_for_timeout(500)
    page2.keyboard.press("ControlOrMeta+a")
    page2.keyboard.press("Backspace")
    page2.wait_for_timeout(300)
    # 填入正文
    page2.keyboard.insert_text(body)
    print(f"  ✅ 已填入正文（{len(body)} 字）")

    # ---- 第五步：设置标题 ----
    print(f"5. 设置标题: {title}")
    # 点一下标题区域
    page2.locator("div").filter(has_text=re.compile(r"^【无标题】$")).click()
    page2.wait_for_timeout(300)
    page2.keyboard.press("ControlOrMeta+a")
    page2.keyboard.insert_text(title)
    page2.wait_for_timeout(300)

    # ---- 第六步：点击发布，弹出发布设置弹窗 ----
    print("6. 打开发布设置...")
    page2.get_by_role("button", name="发布文章").click()
    page2.wait_for_timeout(200)

    # ---- 第七步：打开专栏选择，选中目标专栏 ----
    print(f"7. 选择专栏: {COLUMN_NAMES}")
    # 先点开专栏选择面板
    try:
        page2.locator("#tagList .tag__btn-tag").wait_for(timeout=10_000)
        page2.locator("#tagList .tag__btn-tag").click()
        page2.wait_for_timeout(500)
        print("  ✅ 打开专栏选择面板")
    except Exception:
        print("  ⚠️  未找到专栏选择按钮，尝试直接选择...")

    # 遍历所有专栏，匹配配置中的专栏名
    columns = page2.locator(".spanIsAgree").all()
    column_texts = {col.text_content().strip(): col for col in columns}

    for name in COLUMN_NAMES:
        if name in column_texts:
            column_texts[name].click(timeout=600_000)
            print(f"  ✅ 已选择专栏: {name}")
            page2.wait_for_timeout(300)
        else:
            print(f"  ⚠️  未找到专栏「{name}」，跳过")

    page2.wait_for_timeout(500)

    # ---- 第八步：删除已有标签 ----
    print("8. 清理已有标签...")
    # 找到所有标签删除按钮
    delete_btns = page2.locator(".el-tag__close.el-icon-close")
    count = delete_btns.count()
    print(f"  当前有 {count} 个标签需要删除")
    for i in range(count):
        try:
            delete_btns.nth(0).click()  # 每次点第一个，因为删掉后索引会变
            page2.wait_for_timeout(300)
            print(f"  ✅ 删除第 {i + 1} 个标签")
        except Exception:
            break
    print("  ✅ 标签清理完成")

    # ---- 第九步：添加新标签 ----
    print(f"9. 添加标签: {tags}")
    # 点开添加标签面板
    page2.locator(".mark_selection .tag__btn-tag").click()
    page2.wait_for_timeout(500)

    for tag in tags:
        if not tag:
            continue
        try:
            tag_input = page2.locator('[placeholder*="搜索"], [placeholder*="标签"]').last
            tag_input.click()
            tag_input.fill(tag)
            page2.wait_for_timeout(300)
            tag_input.press("Enter")
            page2.wait_for_timeout(500)
            print(f"  ✅ 添加标签: {tag}")
        except Exception as e:
            print(f"  ⚠️  添加标签 {tag} 失败: {e}")

    # 关闭标签选择弹窗
    safe_click(page2, ".mark_selection_box_body .modal__close-button")

    # ---- 第十步：填摘要 ----
    print("10. 填写摘要...")
    summary = body[:200].replace("\n", " ").strip()
    try:
        summary_input = page2.locator(".desc-box textarea")
        summary_input.wait_for(timeout=600_000)  # 10 分钟超时
        summary_input.click()
        summary_input.fill(summary)
        print(f"  ✅ 已填入摘要")
    except Exception as e:
        print(f"  ⚠️  填写摘要失败: {e}")

    # ---- 第十一步：勾选文章备份 ----
    print("11. 勾选文章备份...")
    try:
        cb = page2.locator(".el-checkbox__inner")
        cb.wait_for(timeout=5000)
        is_checked = cb.evaluate("el => el.classList.contains('is-checked') || el.parentElement.classList.contains('is-checked')")
        if not is_checked:
            cb.click()
            print("  ✅ 已勾选文章备份")
        else:
            print("  ✅ 文章备份已勾选，跳过")
    except Exception as e:
        print(f"  ⚠️  文章备份复选框操作失败: {e}")

    # ---- 第十二步：最终发布（暂时禁用，测试用）----
    print("12. 🔒 跳过最终发布（测试模式）")
    # page2.get_by_label("Insert publishArticle").get_by_role("button", name="发布文章").click()
    # page2.wait_for_timeout(50000)
    page2.wait_for_timeout(600_000)  # 停 10 分钟让你手动检查

    print("\n🎉 发布流程完成！")
    context.close()
    browser.close()


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 auto-upload/publish_csdn.py <markdown文件路径> [标签1] [标签2] ...")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    article = parse_markdown(filepath)
    tags = sys.argv[2:] if len(sys.argv) > 2 else (article["tags"] or DEFAULT_TAGS)

    print(f"文章标题: {article['title']}")
    print(f"标签: {tags}\n")

    with sync_playwright() as playwright:
        run(playwright, article["title"], article["body"], tags)
