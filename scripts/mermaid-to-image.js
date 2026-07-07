#!/usr/bin/env node
/**
 * 将 markdown 中的 mermaid 代码块渲染为 PNG 图片
 * 图片按分类存入 source/images/<category>/
 * markdown 中的 ```mermaid 替换为 ![](/images/<category>/IMG-xxx.png)
 *
 * 用法:
 *   node scripts/mermaid-to-image.js                          # 全部转换
 *   node scripts/mermaid-to-image.js --dir Java-advanced       # 只转指定分类
 *   node scripts/mermaid-to-image.js --dry-run                 # 干跑，只列出不改
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const POSTS_DIR = path.join(ROOT, 'source', '_posts');
const IMAGES_DIR = path.join(ROOT, 'source', 'images');
const TMP_DIR = path.join(ROOT, '.mermaid-tmp');

const args = process.argv.slice(2);
const filterDir = args.includes('--dir') ? args[args.indexOf('--dir') + 1] : null;
const dryRun = args.includes('--dry-run');

// --- 工具函数 ---

function findMdFiles(dir) {
  const files = [];
  try {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        files.push(...findMdFiles(fullPath));
      } else if (entry.isFile() && entry.name.endsWith('.md')) {
        files.push(fullPath);
      }
    }
  } catch { /* skip if dir doesn't exist */ }
  return files;
}

function extractMermaidBlocks(content) {
  const blocks = [];
  const regex = /```mermaid\n([\s\S]*?)```/g;
  let match;
  while ((match = regex.exec(content)) !== null) {
    blocks.push({
      code: match[1].trim(),
      fullMatch: match[0],
      startIndex: match.index,
      endIndex: match.index + match[0].length,
    });
  }
  return blocks;
}

/** 从文件路径提取分类名: .../_posts/Java-advanced/xxx.md → Java-advanced */
function getCategory(filePath) {
  const relative = path.relative(POSTS_DIR, filePath);
  return relative.split(path.sep)[0];
}

/** 生成唯一文件名: IMG-20260707-000001.png */
function generateFilename(index) {
  const now = new Date();
  const date = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}`;
  return `IMG-${date}-${String(index).padStart(6, '0')}.png`;
}

// --- 主流程 ---

function main() {
  console.log(dryRun ? '🔍 DRY RUN — 只列出不修改\n' : '🔄 开始转换 Mermaid → PNG\n');

  if (!dryRun && !fs.existsSync(TMP_DIR)) {
    fs.mkdirSync(TMP_DIR, { recursive: true });
  }

  const mdFiles = findMdFiles(POSTS_DIR);
  let globalIndex = 0;
  let totalBlocks = 0;
  let totalFiles = 0;

  for (const mdFile of mdFiles) {
    const category = getCategory(mdFile);
    if (filterDir && category !== filterDir) continue;

    const content = fs.readFileSync(mdFile, 'utf-8');
    const blocks = extractMermaidBlocks(content);
    if (blocks.length === 0) continue;

    totalFiles++;
    totalBlocks += blocks.length;
    console.log(`\n📄 ${path.relative(POSTS_DIR, mdFile)} (${blocks.length} 图)`);

    if (dryRun) {
      blocks.forEach((b, i) => {
        const firstLine = b.code.split('\n')[0].slice(0, 60);
        console.log(`   [${i + 1}] ${firstLine}...`);
      });
      continue;
    }

    const catImagesDir = path.join(IMAGES_DIR, category);
    if (!fs.existsSync(catImagesDir)) {
      fs.mkdirSync(catImagesDir, { recursive: true });
    }

    // 从后往前替换，避免 index 偏移
    let modifiedContent = content;

    for (let i = blocks.length - 1; i >= 0; i--) {
      const block = blocks[i];
      const filename = generateFilename(globalIndex++);
      const outputPath = path.join(catImagesDir, filename);
      const mmdPath = path.join(TMP_DIR, `${category}-${globalIndex - 1}.mmd`);

      // 写临时 .mmd 文件
      fs.writeFileSync(mmdPath, block.code, 'utf-8');

      // 用 mmdc 渲染
      try {
        execSync(
          `mmdc -i "${mmdPath}" -o "${outputPath}" -b transparent --scale 2`,
          { stdio: 'pipe', timeout: 60000 }
        );
        const imgRef = `![mermaid](${path.posix.join('/images', category, filename)})`;
        modifiedContent =
          modifiedContent.slice(0, block.startIndex) +
          imgRef +
          modifiedContent.slice(block.endIndex);
        console.log(`   ✅ [${i + 1}] ${filename}`);
      } catch (err) {
        console.error(`   ❌ [${i + 1}] 渲染失败: ${err.message}`);
      }

      // 清理临时文件
      try { fs.unlinkSync(mmdPath); } catch {}
    }

    if (modifiedContent !== content) {
      fs.writeFileSync(mdFile, modifiedContent, 'utf-8');
    }
  }

  // 清理临时目录
  if (!dryRun) {
    try { fs.rmSync(TMP_DIR, { recursive: true, force: true }); } catch {}
  }

  console.log(`\n${dryRun ? '🔍 DRY RUN' : '✅ 完成'}: 扫描 ${totalFiles} 个文件, ${totalBlocks} 个 mermaid 块`);
}

main();
