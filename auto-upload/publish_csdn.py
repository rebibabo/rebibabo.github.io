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
import json
import ssl
import urllib.request
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import Playwright, sync_playwright

# ============================================================
# 配置
# ============================================================
AUTH_FILE = os.path.join(os.path.dirname(__file__), "auth.json")
COLUMN_NAMES = ["Java高并发", "Java基础"]       # 专栏名列表，可多选
DEFAULT_TAGS = ["学习笔记"]   # 默认标签（AI 失败时的兜底）
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = "deepseek-chat"    # flash 模型

# GitHub 图片外链配置
# 图片外链：用 jsDelivr CDN 代理 GitHub raw（国内访问更稳定，CSDN 不会转存失败）
GITHUB_RAW_BASE = "https://cdn.jsdelivr.net/gh/rebibabo/rebibabo.github.io@source/source"
BLOG_SOURCE_DIR = os.path.join(os.path.dirname(__file__), "..", "source")  # source/images/...


# ============================================================
# 图片外链替换
# ============================================================
def resolve_images_in_body(body: str, md_filepath: str) -> str:
    """将 markdown 中的本地图片路径替换为 GitHub raw 外链"""
    image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    md_dir = os.path.dirname(md_filepath)

    def find_local_image(img_path: str) -> str | None:
        """多策略查找本地图片，返回相对于 BLOG_SOURCE_DIR 的路径"""
        # 策略1：绝对路径 /images/... → source/images/...
        if img_path.startswith("/"):
            candidate = os.path.join(BLOG_SOURCE_DIR, img_path.lstrip("/"))
            if os.path.exists(candidate):
                return img_path.lstrip("/")

        # 策略2：相对路径（相对于 markdown 文件所在目录）
        candidate = os.path.normpath(os.path.join(md_dir, img_path))
        if os.path.exists(candidate):
            # 转回相对于 source/ 的路径
            return os.path.relpath(candidate, BLOG_SOURCE_DIR)

        # 策略3：按文件名在 source/images/ 下全局搜索
        filename = os.path.basename(img_path)
        for root, _dirs, files in os.walk(os.path.join(BLOG_SOURCE_DIR, "images")):
            if filename in files:
                return os.path.relpath(os.path.join(root, filename), BLOG_SOURCE_DIR)

        return None

    def replace_image(match: re.Match) -> str:
        alt = match.group(1)
        img_path = match.group(2)

        # 已经是外链就跳过
        if img_path.startswith("http://") or img_path.startswith("https://"):
            return match.group(0)

        # 查找本地文件
        rel_path = find_local_image(img_path)
        if not rel_path:
            print(f"  ⚠️  未找到图片: {img_path}")
            return match.group(0)

        local_file = os.path.join(BLOG_SOURCE_DIR, rel_path)
        # markdown 中保留原始路径（中文不编码，避免 CSDN 处理异常）
        raw_url = f"{GITHUB_RAW_BASE}/{rel_path}"
        # 内部检查用编码后的 URL
        encoded_path = "/".join(quote(part, safe="") for part in rel_path.split("/"))
        check_url = f"{GITHUB_RAW_BASE}/{encoded_path}"

        # 先查外链
        if _check_url(check_url):
            print(f"  🔗 {rel_path}")
            return f"![{alt}]({raw_url})"

        # 外链不可用，本地有 → 提示手动 push
        print(f"  ⚠️  图片外链不可用: {rel_path}")
        print(f"     👉 请先手动 git push，然后再跑脚本")
        print(f"     🔗 将使用: {raw_url}")
        return f"![{alt}]({raw_url})"

    return image_pattern.sub(replace_image, body)


def _check_url(url: str) -> bool:
    """检查 URL 是否可访问（HEAD 优先，GET 兜底）"""
    ctx = ssl._create_unverified_context()
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method)
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                return resp.status == 200
        except Exception:
            continue
    return False


# ============================================================
# Markdown 解析
# ============================================================
def parse_markdown(filepath: str) -> dict:
    """解析 hexo markdown，提取 title、正文、tags"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    front_matter = {}
    body = content
    m = re.match(r"^(---+\s*\n)?(.*?)\n---+\s*\n", content, re.DOTALL)
    if m:
        body = content[m.end():]
        for line in m.group(2).strip().split("\n"):
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
# DeepSeek API — 摘要 + 标签
# ============================================================
def extract_metadata_via_ai(body: str, title: str) -> dict | None:
    """调用 DeepSeek 提取摘要（≤150字）和标签（≤7个），摘要超过250字则重试最多3次"""
    if not DEEPSEEK_API_KEY:
        print("  ⚠️  DEEPSEEK_API_KEY 未设置，将使用默认摘要和标签")
        return None

    prompt = (
        "根据以下文章内容生成摘要和标签。\n"
        "要求：\n"
        "1. 摘要：200~250字，概括文章核心内容和关键结论，不要评价\n"
        "2. 标签：5~7个，用简短关键词描述文章主题\n"
        "严格只返回 JSON，不要包含其他文字：\n"
        '{"summary": "...", "tags": ["...", "..."]}\n\n'
        f"文章标题：{title}\n\n文章内容：\n{body[:5000]}"
    )

    for attempt in range(3):
        try:
            data = json.dumps({
                "model": DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.deepseek.com/chat/completions",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                },
            )

            ctx = ssl._create_unverified_context()
            with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            content = result["choices"][0]["message"]["content"]
            # 提取 JSON（兼容 markdown 代码块包裹）
            m = re.search(r"\{.*\}", content, re.DOTALL)
            if not m:
                raise ValueError(f"未找到 JSON: {content[:100]}")

            metadata = json.loads(m.group())
            summary = metadata.get("summary", "").strip()
            ai_tags = metadata.get("tags", [])

            if len(summary) > 250:
                orig_len = len(summary)
                summary = summary[:250].rstrip("，。；、！？,.;!?")
                print(f"  ⚠️  摘要过长（{orig_len} 字），已截断至 {len(summary)} 字")

            print(f"  ✅ AI 摘要: {len(summary)} 字")
            print(f"  ✅ AI 标签: {ai_tags}")
            return {"summary": summary, "tags": ai_tags[:7]}

        except Exception as e:
            print(f"  ⚠️  API 调用失败（尝试 {attempt + 1}/3）: {e}")

    print("  ⚠️  AI 提取失败（已重试3次），使用默认摘要和标签")
    return None


# ============================================================
# 主流程
# ============================================================
def run(playwright: Playwright, title: str, body: str, tags: list[str], summary: str = "") -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        storage_state=AUTH_FILE,
        viewport={"width": 1280, "height": 900},
        locale="zh-CN",
        permissions=["clipboard-read", "clipboard-write"],
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

    # ---- 第四步：剪贴板粘贴正文（保留 markdown 格式）----
    print("4. 填入文章内容...")
    page2.wait_for_timeout(1000)

    # 先尝试 CodeMirror API，没有就用剪贴板粘贴
    is_cm = page2.evaluate("() => { const cm = document.querySelector('.CodeMirror'); return !!(cm && cm.CodeMirror); }")
    if is_cm:
        page2.evaluate("(content) => { document.querySelector('.CodeMirror').CodeMirror.setValue(content); }", body)
        print("  ✅ 通过 CodeMirror API 填入")
    else:
        # 点编辑器获取焦点，全选，剪贴板粘贴
        page2.locator(".editor-pane, .CodeMirror, .markdown-editor, .editor, [contenteditable='true']").first.click()
        page2.wait_for_timeout(500)
        page2.keyboard.press("ControlOrMeta+a")
        page2.wait_for_timeout(200)
        page2.evaluate("(content) => navigator.clipboard.writeText(content)", body)
        page2.wait_for_timeout(500)
        page2.keyboard.press("ControlOrMeta+v")
        page2.wait_for_timeout(1000)
        print("  ✅ 通过剪贴板粘贴填入")

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
    try:
        summary_input = page2.locator(".desc-box textarea")
        summary_input.wait_for(timeout=600_000)  # 10 分钟超时
        summary_input.click()
        summary_input.fill(summary)
        print(f"  ✅ 已填入摘要（{len(summary)} 字）")
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

    # 替换本地图片为 GitHub raw 外链
    print("-1. 替换图片为外链...", flush=True)
    article["body"] = resolve_images_in_body(article["body"], filepath)

    cli_tags = sys.argv[2:] if len(sys.argv) > 2 else []

    # 先调 AI 提取摘要和标签
    print("0. 调用 DeepSeek 提取摘要和标签...", flush=True)
    ai_result = extract_metadata_via_ai(article["body"], article["title"])

    # 标签优先级：命令行 > AI > front matter > 默认
    if cli_tags:
        tags = cli_tags
        print(f"  📌 使用命令行标签: {tags}", flush=True)
    elif ai_result and ai_result.get("tags"):
        tags = ai_result["tags"]
        print(f"  📌 使用 AI 标签: {tags}", flush=True)
    else:
        tags = article["tags"] or DEFAULT_TAGS
        print(f"  📌 使用兜底标签: {tags}", flush=True)

    # 摘要优先级：AI > 正文截取
    if ai_result and ai_result.get("summary"):
        summary = ai_result["summary"]
        print(f"  📌 使用 AI 摘要: {summary[:50]}...", flush=True)
    else:
        summary = article["body"][:200].replace("\n", " ").strip()
        print(f"  📌 使用截取摘要（兜底）", flush=True)

    print(f"\n文章标题: {article['title']}")
    print(f"最终标签: {tags}")
    print()

    with sync_playwright() as playwright:
        run(playwright, article["title"], article["body"], tags, summary)
