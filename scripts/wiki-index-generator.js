/* global hexo */
'use strict';
const fs = require('fs');
const path = require('path');

hexo.extend.generator.register('wiki-index', function(locals) {
  const wikiDir = path.join(hexo.source_dir, 'wiki');
  const result = { maps: [], concepts: {}, glossary: {}, series: [] };

  // Parse front matter from a markdown file
  function readFM(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const m = content.match(/^---\n?([\s\S]*?)\n?---/);
      if (!m) return { title: path.basename(filePath, '.md') };
      const lines = m[1].split('\n');
      const fm = {};
      for (const line of lines) {
        const kv = line.match(/^(\w+):\s*(.*)/);
        if (kv) fm[kv[1]] = kv[2].replace(/^['"]|['"]$/g, '').trim();
      }
      return fm;
    } catch (e) {
      return { title: path.basename(filePath, '.md') };
    }
  }

  // Scan directories
  function scanDir(dirPath) {
    let items;
    try {
      items = fs.readdirSync(dirPath);
    } catch (e) {
      return;
    }
    items.forEach(item => {
      const full = path.join(dirPath, item);
      const stat = fs.statSync(full);
      if (item.startsWith('.') || item === 'index.md') return;

      if (stat.isDirectory()) {
        const subItems = fs.readdirSync(full).filter(f => f.endsWith('.md') && f !== 'index.md');
        const cat = item;
        if (!result.concepts[cat]) result.concepts[cat] = [];
        if (!result.glossary[cat]) result.glossary[cat] = [];

        subItems.forEach(f => {
          const fm = readFM(path.join(full, f));
          const entry = {
            name: f.replace(/\.md$/, ''),
            title: fm.title || f.replace(/\.md$/, ''),
            path: f.replace(/\.md$/, '')
          };
          if (full.includes('/concepts/')) result.concepts[cat].push(entry);
          else if (full.includes('/glossary/')) result.glossary[cat].push(entry);
        });
      }
    });
  }

  // Scan maps/
  const mapsDir = path.join(wikiDir, 'maps');
  try {
    const mapFiles = fs.readdirSync(mapsDir).filter(f => f.endsWith('.md'));
    mapFiles.forEach(f => {
      const fm = readFM(path.join(mapsDir, f));
      result.maps.push({
        name: f.replace(/\.md$/, ''),
        title: fm.title || f.replace(/\.md$/, ''),
        path: f.replace(/\.md$/, '')
      });
    });
  } catch (e) { /* maps dir missing */ }

  // Scan series/
  const seriesDir = path.join(wikiDir, 'series');
  try {
    const seriesFiles = fs.readdirSync(seriesDir).filter(f => f.endsWith('.md'));
    seriesFiles.forEach(f => {
      const fm = readFM(path.join(seriesDir, f));
      result.series.push({
        name: f.replace(/\.md$/, ''),
        title: fm.title || f.replace(/\.md$/, ''),
        path: f.replace(/\.md$/, '')
      });
    });
  } catch (e) { /* series dir missing */ }

  // Scan concepts/ and glossary/ subdirectories
  const conceptsDir = path.join(wikiDir, 'concepts');
  const glossaryDir = path.join(wikiDir, 'glossary');
  try { scanDir(conceptsDir); } catch (e) {}
  try { scanDir(glossaryDir); } catch (e) {}

  // Build category list (all unique categories from concepts and glossary)
  const allCats = new Set([
    ...Object.keys(result.concepts),
    ...Object.keys(result.glossary)
  ]);

  // Generate HTML for category tabs
  const catTabs = Array.from(allCats).sort().map(cat =>
    `<button class="wiki-cat-btn" data-cat="${cat}">${cat}</button>`
  ).join('\n');

  // Generate concept list
  function buildList(entries, prefix) {
    return entries.map(e =>
      `<li><a href="/wiki/${prefix}/${e.path}.html">${e.title}</a></li>`
    ).join('\n');
  }

  const conceptSections = Object.entries(result.concepts).sort().map(([cat, entries]) => {
    return `
    <div class="wiki-section" data-cat="${cat}">
      <h3>${cat}</h3>
      <ul class="wiki-link-list">
        ${buildList(entries.sort((a,b) => a.title.localeCompare(b.title)), 'concepts/' + cat)}
      </ul>
    </div>`;
  }).join('\n');

  const glossarySections = Object.entries(result.glossary).sort().map(([cat, entries]) => {
    return `
    <div class="wiki-section" data-cat="${cat}">
      <h3>${cat}</h3>
      <ul class="wiki-link-list">
        ${buildList(entries.sort((a,b) => a.title.localeCompare(b.title)), 'glossary/' + cat)}
      </ul>
    </div>`;
  }).join('\n');

  const mapsList = result.maps.sort((a,b) => a.title.localeCompare(b.title)).map(m =>
    `<li><a href="/wiki/maps/${m.path}.html">${m.title}</a></li>`
  ).join('\n');

  const seriesList = result.series.sort((a,b) => a.title.localeCompare(b.title)).map(s =>
    `<li><a href="/wiki/series/${s.path}.html">${s.title}</a></li>`
  ).join('\n');

  const pageContent = `
<div class="wiki-hero">
  <h1 class="wiki-title">
    <span class="typing-text">知识库</span>
    <span class="cursor">|</span>
  </h1>
  <p class="wiki-subtitle">概念 · 术语 · 学习路线 · 系列导航</p>
</div>

<div class="wiki-tabs">
  <button class="wiki-tab active" data-tab="maps">学习路线</button>
  <button class="wiki-tab" data-tab="concepts">概念</button>
  <button class="wiki-tab" data-tab="glossary">术语表</button>
  <button class="wiki-tab" data-tab="series">系列</button>
</div>

<div class="wiki-cat-filter" id="wiki-cat-filter">
  <button class="wiki-cat-btn active" data-cat="all">全部</button>
  ${catTabs}
</div>

<div class="wiki-content">
  <div class="wiki-tab-content active" id="tab-maps">
    <ul class="wiki-link-list">
      ${mapsList}
    </ul>
  </div>

  <div class="wiki-tab-content" id="tab-concepts">
    ${conceptSections}
  </div>

  <div class="wiki-tab-content" id="tab-glossary">
    ${glossarySections}
  </div>

  <div class="wiki-tab-content" id="tab-series">
    <ul class="wiki-link-list">
      ${seriesList}
    </ul>
  </div>
</div>

<style>
.wiki-hero { text-align:center; padding:40px 0 24px; }
.wiki-title { font-size:2.4rem; font-weight:700; margin:0 0 6px; background:linear-gradient(135deg,#667eea,#764ba2,#f093fb); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.wiki-subtitle { font-size:1rem; opacity:0.55; margin:0; }

.wiki-tabs { display:flex; justify-content:center; gap:4px; margin:24px 0 16px; flex-wrap:wrap; }
.wiki-tab { padding:8px 20px; border-radius:8px; border:1px solid rgba(128,128,128,0.15); background:transparent; cursor:pointer; font-size:0.92rem; color:var(--text-color); transition:all 0.2s; }
.wiki-tab:hover { background:rgba(102,126,234,0.08); border-color:rgba(102,126,234,0.25); }
.wiki-tab.active { background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; border-color:transparent; }

.wiki-cat-filter { display:flex; justify-content:center; gap:6px; margin-bottom:24px; flex-wrap:wrap; }
.wiki-cat-btn { padding:4px 14px; border-radius:20px; border:1px solid rgba(128,128,128,0.12); background:transparent; cursor:pointer; font-size:0.82rem; color:var(--text-color); transition:all 0.2s; }
.wiki-cat-btn:hover { background:rgba(102,126,234,0.06); border-color:rgba(102,126,234,0.2); }
.wiki-cat-btn.active { background:rgba(102,126,234,0.12); border-color:rgba(102,126,234,0.35); color:#667eea; }

.wiki-tab-content { display:none; }
.wiki-tab-content.active { display:block; }

.wiki-section { margin-bottom:20px; }
.wiki-section h3 { font-size:1rem; font-weight:600; margin:0 0 8px; padding-bottom:6px; border-bottom:1px solid rgba(128,128,128,0.1); color:var(--text-color); }
.wiki-link-list { list-style:none; padding:0; margin:0; columns:2; column-gap:32px; }
.wiki-link-list li { margin-bottom:6px; break-inside:avoid; }
.wiki-link-list a { font-size:0.9rem; color:var(--text-color); text-decoration:none; transition:color 0.2s; }
.wiki-link-list a:hover { color:#667eea; }

@media (max-width:768px) {
  .wiki-title { font-size:1.8rem; }
  .wiki-link-list { columns:1; }
  .wiki-tabs { gap:2px; }
  .wiki-tab { padding:6px 14px; font-size:0.85rem; }
}
</style>

<script>
(function(){
  var tabs = document.querySelectorAll('.wiki-tab');
  var contents = document.querySelectorAll('.wiki-tab-content');
  var catBtns = document.querySelectorAll('.wiki-cat-btn');
  var catFilter = document.getElementById('wiki-cat-filter');
  var sections = document.querySelectorAll('.wiki-section');

  // Tab switching
  tabs.forEach(function(tab) {
    tab.addEventListener('click', function() {
      var target = this.getAttribute('data-tab');
      tabs.forEach(function(t) { t.classList.remove('active'); });
      contents.forEach(function(c) { c.classList.remove('active'); });
      this.classList.add('active');
      var content = document.getElementById('tab-' + target);
      if (content) content.classList.add('active');

      // Show/hide category filter: only for concepts and glossary
      if (target === 'concepts' || target === 'glossary') {
        catFilter.style.display = 'flex';
        // Reset to "all"
        catBtns.forEach(function(b) { b.classList.remove('active'); });
        catBtns[0].classList.add('active');
        sections.forEach(function(s) { s.style.display = ''; });
      } else {
        catFilter.style.display = 'none';
      }
    });
  });

  // Category filtering
  catBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      var cat = this.getAttribute('data-cat');
      catBtns.forEach(function(b) { b.classList.remove('active'); });
      this.classList.add('active');

      sections.forEach(function(s) {
        if (cat === 'all' || s.getAttribute('data-cat') === cat) {
          s.style.display = '';
        } else {
          s.style.display = 'none';
        }
      });
    });
  });

  // Init: show category filter only if concepts tab is active
  var activeTab = document.querySelector('.wiki-tab.active');
  if (activeTab && activeTab.getAttribute('data-tab') !== 'concepts' && activeTab.getAttribute('data-tab') !== 'glossary') {
    catFilter.style.display = 'none';
  }
})();
</script>`;

  return {
    path: 'wiki/index.html',
    data: {
      title: '知识库',
      layout: 'page',
      content: pageContent
    },
    layout: 'page'
  };
});
