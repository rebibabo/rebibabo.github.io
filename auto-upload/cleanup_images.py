"""
清理未被引用的图片
===================
扫描所有 markdown 文件中的图片引用，找出 source/images/ 下没有任何文章引用的图片。

用法：
    python3 auto-upload/cleanup_images.py          # 干跑（只列出，不删除）
    python3 auto-upload/cleanup_images.py --delete # 实际删除
"""

import os
import re
import sys
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOG_ROOT = os.path.join(SCRIPT_DIR, "..")
POSTS_DIR = os.path.join(BLOG_ROOT, "source", "_posts")
IMAGES_DIR = os.path.join(BLOG_ROOT, "source", "images")


def collect_referenced_basenames() -> set[str]:
    """收集所有 markdown 文件中引用的图片 basename"""
    referenced = set()
    md_files = glob.glob(os.path.join(POSTS_DIR, "**", "*.md"), recursive=True)

    for md_path in md_files:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 匹配 ![alt](path) 和 <img src="path">
        paths = re.findall(r'!\[.*?\]\(([^)]+)\)', content)
        paths += re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        for p in paths:
            basename = os.path.basename(p)
            if basename:
                referenced.add(basename)

    return referenced


def collect_image_files() -> list[str]:
    """收集 source/images/ 下所有图片文件（绝对路径）"""
    extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".ico", ".tiff"}
    images = []
    for root, _dirs, files in os.walk(IMAGES_DIR):
        for f in files:
            if os.path.splitext(f)[1].lower() in extensions:
                images.append(os.path.join(root, f))
    return images


def main():
    dry_run = "--delete" not in sys.argv

    mode = "🔍 干跑模式（不删除）" if dry_run else "🗑️  删除模式"
    print(f"{mode}\n")

    print("1. 扫描 markdown 图片引用...")
    referenced = collect_referenced_basenames()
    print(f"   找到 {len(referenced)} 个引用 basename")

    print("2. 扫描 source/images/ 图片文件...")
    all_images = collect_image_files()
    print(f"   共 {len(all_images)} 个图片文件\n")

    orphaned = []
    kept = 0
    for img_path in all_images:
        basename = os.path.basename(img_path)
        if basename in referenced:
            kept += 1
        else:
            orphaned.append(img_path)

    print(f"已引用: {kept} 个")
    print(f"孤立:   {len(orphaned)} 个\n")

    if not orphaned:
        print("✅ 没有孤立图片")
        return

    total_size = 0
    for img_path in orphaned:
        size = os.path.getsize(img_path)
        total_size += size
        rel = os.path.relpath(img_path, BLOG_ROOT)
        print(f"  📄 {rel}  ({_format_size(size)})")

    print(f"\n总计: {len(orphaned)} 个文件, {_format_size(total_size)}")

    if dry_run:
        print(f"\n👉 加 --delete 参数确认删除")
    else:
        print(f"\n正在删除...")
        for img_path in orphaned:
            os.remove(img_path)
            rel = os.path.relpath(img_path, BLOG_ROOT)
            print(f"  ✅ 已删除: {rel}")
        print(f"\n✅ 清理完成")


def _format_size(size: int) -> str:
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


if __name__ == "__main__":
    main()
