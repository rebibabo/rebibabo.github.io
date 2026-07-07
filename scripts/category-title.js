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

// Intercept category page rendering to override title
hexo.extend.generator.register('category-page-override', function(locals) {
  const categories = locals.categories;
  if (!categories || !categories.length) return [];

  return categories.map(cat => {
    const slug = cat.name;
    const display = CATEGORY_MAP[slug];
    if (!display) return null;

    return {
      path: 'categories/' + slug + '/index.html',
      data: Object.assign({}, cat, {
        title: display,
        category: slug,
        layout: 'category'
      }),
      layout: 'category'
    };
  }).filter(Boolean);
});
