/* global hexo */
'use strict';

const fs = require('fs');
const path = require('path');

// Build mapping: category slug → directory display name
const CATEGORY_MAP = {};

(function buildMap() {
  const postsDir = path.join(hexo.source_dir, '_posts');
  let dirs;
  try { dirs = fs.readdirSync(postsDir); } catch (e) { return; }

  dirs.forEach(dir => {
    const dirPath = path.join(postsDir, dir);
    let stat;
    try { stat = fs.statSync(dirPath); } catch (e) { return; }
    if (!stat.isDirectory() || dir === '.obsidian') return;

    const files = fs.readdirSync(dirPath).filter(f => f.endsWith('.md'));
    if (files.length === 0) return;

    const content = fs.readFileSync(path.join(dirPath, files[0]), 'utf8');
    const fmMatch = content.match(/^---\n?([\s\S]*?)\n?---/);
    if (!fmMatch) return;

    const lines = fmMatch[1].split('\n');
    let inCat = false;
    for (const line of lines) {
      if (/^categories:/.test(line)) { inCat = true; continue; }
      if (inCat) {
        const m = line.match(/^\s*-\s*(.+)/);
        if (m) { CATEGORY_MAP[m[1].trim()] = dir; break; }
        if (line.trim()) inCat = false;
      }
    }
  });
})();

// Override category page title in generated HTML
hexo.extend.filter.register('after_render:html', function(html, data) {
  // Only process category listing pages
  if (!data.path || !/^categories\/[^/]+\/index\.html$/.test(data.path)) return html;

  const slug = data.path.split('/')[1];
  const display = CATEGORY_MAP[slug];
  if (!display) return html;

  // Replace title: "分类 - slug - site" → "display - site"
  // Also fix og:title
  html = html.replace(/<title>[^<]*<\/title>/, function(match) {
    // Match "分类 - slug" or just "slug" followed by " - site"
    return match.replace(/分类 - [^-]+/, display);
  });
  html = html.replace(/<meta property="og:title" content="[^"]*">/, function(match) {
    return match.replace(/分类 - [^-]+/, display);
  });

  return html;
}, 10);
