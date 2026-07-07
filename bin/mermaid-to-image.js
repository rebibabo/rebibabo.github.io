#!/usr/bin/env node
/**
 * 将 markdown 中的 mermaid 代码块渲染为 PNG 片
 * 片按分类存入 source/images/<category>/
 * 源码以 .mmd 文件与 PNG 并列保存，方便后续修改
 * markdown 中的 ```mermaid 替换为 ![](/images/<category>/IMG-xxx.png)
 *
 * 用法:
 *   node scripts/mermaid-to-image.js                          # 全部转换
 *   node scripts/mermaid-to-image.js --dir Java-advanced      # 只转指定分类
 *   node scripts/mermaid-to-image.js --dry-run                # 干跑，只列出不改
 *   node scripts/mermaid-to-image.js --concurrency 17         # 并发数（默认 17）
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');

const execAsync = promisify(exec);

const ROOT = path.join(__dirname, '..');
const POSTS_DIR = path.join(ROOT, 'source', '_posts');
const IMAGES_DIR = path.join(ROOT, 'source', 'images');
const TMP_DIR = path.join(ROOT, '.mermaid-tmp');

const args = process.argv.slice(2);
const filterDir = args.includes('--dir') ? args[args.indexOf('--dir') + 1] : null;
const dryRun = args.includes('--dry-run');
const concurrency = parseInt(args[args.indexOf('--concurrency') + 1], 10) || 17;

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
  } catch { /* skip */ }
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

function getCategory(filePath) {
  const relative = path.relative(POSTS_DIR, filePath);
  return relative.split(path.sep)[0];
}

function generateFilename(index) {
  const now = new Date();
  const date = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}`;
  return `IMG-${date}-${String(index).padStart(6, '0')}`;
}

/** 并发执行器：同时最多跑 concurrency 个任务 */
async function runConcurrent(tasks, concurrency) {
  const results = new Array(tasks.length);
  const queue = [...tasks];
  let running = 0;
  let idx = 0;
  let done = 0;

  return new Promise((resolve) => {
    function next() {
      if (done === tasks.length) {
        resolve(results);
        return;
      }
      while (running < concurrency && queue.length > 0) {
        const task = queue.shift();
        const taskIdx = idx++;
        running++;
        task()
          .then((r) => { results[taskIdx] = r; })
          .catch((e) => { results[taskIdx] = { error: e }; })
          .finally(() => { running--; done++; next(); });
      }
    }
    next();
  });
}

const MERMAID_INIT = `%%{init: {"flowchart":{"nodeSpacing":14,"rankSpacing":26,"curve":"linear","diagramPadding":6},"themeVariables":{"fontSize":"13px"}}}%%`;

/** 渲染单个 mermaid 块，自动注入紧凑化配置 */
async function renderBlock(mmdContent, outputPath) {
  const mmdPath = outputPath.replace(/\.png$/, '.mmd');

  // 如果内容以 graph/flowchart 开头，注入 init 配置 + 替换 graph 为 flowchart
  let code = mmdContent.trim();
  if (/^(graph|flowchart)\s/.test(code)) {
    code = code.replace(/^(graph|flowchart)\s/, 'flowchart ');
    code = MERMAID_INIT + '\n' + code;
  }

  fs.writeFileSync(mmdPath, code, 'utf-8');

  const cmd = `mmdc -i "${mmdPath}" -o "${outputPath}" -b white --scale 2`;
  await execAsync(cmd, { timeout: 60000 });
  // .mmd 源码与 PNG 并列保存，方便后续修改
}

// --- 主流程 ---

async function main() {
  console.log(dryRun ? '🔍 DRY RUN\n' : `🔄 开始转换 (并发: ${concurrency})\n`);

  if (!dryRun && !fs.existsSync(TMP_DIR)) {
    fs.mkdirSync(TMP_DIR, { recursive: true });
  }

  const mdFiles = findMdFiles(POSTS_DIR);
  let globalIndex = 0;
  let totalBlocks = 0;
  let totalFiles = 0;

  // 第一阶段：干跑只统计，不处理
  if (dryRun) {
    for (const mdFile of mdFiles) {
      const category = getCategory(mdFile);
      if (filterDir && category !== filterDir) continue;
      const content = fs.readFileSync(mdFile, 'utf-8');
      const blocks = extractMermaidBlocks(content);
      if (blocks.length === 0) continue;
      totalFiles++;
      totalBlocks += blocks.length;
      console.log(`📄 ${path.relative(POSTS_DIR, mdFile)} (${blocks.length} )`);
      blocks.forEach((b, i) => {
        const firstLine = b.code.split('\n')[0].slice(0, 60);
        console.log(`   [${i + 1}] ${firstLine}...`);
      });
    }
    console.log(`\n📊 共 ${totalFiles} 个文件, ${totalBlocks} 个 mermaid 块`);
    return;
  }

  // 第二阶段：收集所有渲染任务
  const tasks = [];

  for (const mdFile of mdFiles) {
    const category = getCategory(mdFile);
    if (filterDir && category !== filterDir) continue;

    const content = fs.readFileSync(mdFile, 'utf-8');
    const blocks = extractMermaidBlocks(content);
    if (blocks.length === 0) continue;

    totalFiles++;
    totalBlocks += blocks.length;

    const catImagesDir = path.join(IMAGES_DIR, category);
    if (!fs.existsSync(catImagesDir)) {
      fs.mkdirSync(catImagesDir, { recursive: true });
    }

    // 对每个块创建渲染任务
    for (const block of blocks) {
      const basename = generateFilename(globalIndex++);
      const outputPath = path.join(catImagesDir, `${basename}.png`);
      const imgRef = `![](${path.posix.join('/images', category, `${basename}.png`)})`;

      tasks.push({
        category,
        basename,
        block,
        outputPath,
        imgRef,
        mdFile,
        contentRef: { current: content },
        sourceCode: block.code,
      });
    }
  }

  console.log(`📊 共 ${totalFiles} 个文件, ${totalBlocks} 个 mermaid 块，开始渲染...\n`);

  // 第三阶段：并发渲染
  let completed = 0;
  const renderTasks = tasks.map((t) => async () => {
    await renderBlock(t.sourceCode, t.outputPath);
    completed++;
    const pct = ((completed / tasks.length) * 100).toFixed(1);
    process.stdout.write(`\r  渲染进度: ${completed}/${tasks.length} (${pct}%) — ${path.basename(t.outputPath)}`);
    return t;
  });

  const renderedTasks = await runConcurrent(renderTasks, concurrency);
  process.stdout.write('\n\n');

  // 第四阶段：按文件分组替换
  const fileEdits = new Map();
  for (const t of renderedTasks) {
    if (t.error) {
      console.error(`   ❌ ${path.basename(t.outputPath)} 渲染失败: ${t.error.message}`);
      continue;
    }
    if (!fileEdits.has(t.mdFile)) {
      fileEdits.set(t.mdFile, []);
    }
    fileEdits.get(t.mdFile).push(t);
  }

  let modifiedCount = 0;
  for (const [mdFile, edits] of fileEdits) {
    // 从后往前排序
    edits.sort((a, b) => b.block.startIndex - a.block.startIndex);
    let content = fs.readFileSync(mdFile, 'utf-8');

    for (const edit of edits) {
      content =
        content.slice(0, edit.block.startIndex) +
        edit.imgRef +
        '\n' +
        content.slice(edit.block.endIndex);
    }

    fs.writeFileSync(mdFile, content, 'utf-8');
    modifiedCount++;
    const name = path.relative(POSTS_DIR, mdFile);
    console.log(`   ✅ ${name} — 替换 ${edits.length} 个`);
  }

  // 第五阶段：清理临时目录
  try { fs.rmSync(TMP_DIR, { recursive: true, force: true }); } catch {}

  console.log(`\n✅ 完成: ${modifiedCount} 个文件, ${totalBlocks} 张`);
  console.log(`   源码 .mmd 文件保存在 images 目录中，与 PNG 并列`);
}

main().catch(console.error);
