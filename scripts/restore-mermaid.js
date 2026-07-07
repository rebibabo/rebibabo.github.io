#!/usr/bin/env node
/**
 * 从 .mmd 文件恢复源码到 markdown 中
 * 将 ![mermaid](...) 替换为 <pre>源码</pre> + ![](...)
 * 补全缺失的 PNG
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const POSTS_DIR = path.join(ROOT, 'source', '_posts', 'Java-advanced');
const IMAGES_DIR = path.join(ROOT, 'source', 'images', 'Java-advanced');

function findMdFiles(dir) {
  const files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isFile() && entry.name.endsWith('.md')) files.push(full);
  }
  return files.sort();
}

// 找到所有需要重新渲染的 PNG
const missingPNGs = [];
const mmdFiles = fs.readdirSync(IMAGES_DIR).filter(f => f.endsWith('.mmd'));
for (const mmd of mmdFiles) {
  const png = mmd.replace('.mmd', '.png');
  if (!fs.existsSync(path.join(IMAGES_DIR, png))) {
    missingPNGs.push(mmd);
  }
}

console.log(`缺失 ${missingPNGs.length} 个 PNG，开始补全...\n`);

// 补全渲染
for (const mmd of missingPNGs) {
  const mmdPath = path.join(IMAGES_DIR, mmd);
  const pngPath = mmdPath.replace('.mmd', '.png');
  try {
    execSync(`mmdc -i "${mmdPath}" -o "${pngPath}" -b transparent --scale 2`, {
      stdio: 'pipe', timeout: 60000
    });
    console.log(`  ✅ ${path.basename(pngPath)}`);
  } catch (e) {
    console.error(`  ❌ ${path.basename(pngPath)}: ${e.message}`);
  }
}

console.log(`\n补全完成，处理 markdown 文件...\n`);

// 处理 markdown 文件：替换 ![mermaid] 为 <pre>源码</pre> + ![]
const mdFiles = findMdFiles(POSTS_DIR);
let total = 0;

for (const mdFile of mdFiles) {
  let content = fs.readFileSync(mdFile, 'utf-8');
  let modified = false;

  // 匹配所有 ![mermaid](/images/.../IMG-xxx.png)
  const regex = /!\[mermaid\]\(\/images\/Java-advanced\/(IMG-[\d-]+\.png)\)/g;
  const matches = [...content.matchAll(regex)];

  // 从后往前替换
  for (let i = matches.length - 1; i >= 0; i--) {
    const m = matches[i];
    const basename = m[1].replace('.png', '');
    const mmdPath = path.join(IMAGES_DIR, `${basename}.mmd`);

    if (!fs.existsSync(mmdPath)) {
      console.warn(`   ⚠️  找不到源码: ${basename}.mmd`);
      continue;
    }

    const sourceCode = fs.readFileSync(mmdPath, 'utf-8').trim();
    const prefix = `<pre style="display:none">\n${sourceCode}\n</pre>\n`;
    const newRef = `![](/images/Java-advanced/${m[1]})`;

    content = content.slice(0, m.index) + prefix + newRef + content.slice(m.index + m[0].length);
    modified = true;
    total++;
  }

  if (modified) {
    fs.writeFileSync(mdFile, content, 'utf-8');
    console.log(`  ✅ ${path.basename(mdFile)} — ${matches.length} 个`);
  }
}

console.log(`\n✅ 完成: 补全 ${missingPNGs.length} 张 PNG, 修改 ${total} 处 markdown`);
