/* global hexo */
'use strict';

const COLOR_CLASSES = ['card-concurrency', 'card-basic', 'card-advanced', 'card-llm', 'card-ads'];

const ICONS = [
  `<svg viewBox="0 0 48 48" fill="none"><rect x="4" y="4" width="17" height="17" rx="3" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.3)"/><rect x="27" y="4" width="17" height="17" rx="3" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.3)"/><rect x="14" y="27" width="17" height="17" rx="3" fill="rgba(255,255,255,0.25)" stroke="rgba(255,255,255,0.4)"/></svg>`,
  `<svg viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="18" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/><circle cx="24" cy="18" r="8" fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.3)"/><circle cx="24" cy="32" r="5" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.2)"/></svg>`,
  `<svg viewBox="0 0 48 48" fill="none"><rect x="8" y="8" width="14" height="32" rx="2" stroke="rgba(255,255,255,0.25)" stroke-width="1.5"/><rect x="26" y="8" width="14" height="32" rx="2" stroke="rgba(255,255,255,0.25)" stroke-width="1.5"/></svg>`,
  `<svg viewBox="0 0 48 48" fill="none"><path d="M16 36 L24 10 L32 36" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" fill="none"/><circle cx="16" cy="36" r="3" fill="rgba(255,255,255,0.2)"/><circle cx="32" cy="36" r="3" fill="rgba(255,255,255,0.2)"/><circle cx="24" cy="10" r="3" fill="rgba(255,255,255,0.3)"/></svg>`,
  `<svg viewBox="0 0 48 48" fill="none"><polygon points="24,4 44,16 40,34 24,44 8,34 4,16" stroke="rgba(255,255,255,0.2)" stroke-width="1.5" fill="none"/><circle cx="24" cy="22" r="6" fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.25)"/></svg>`
];

hexo.extend.generator.register('series-page', function(locals) {
  const posts = locals.posts.sort('source').toArray();
  const groups = new Map();

  posts.forEach(post => {
    const source = post.source; // "_posts/Java高并发底层原理/01-xxx.md"
    const parts = source.split('/');
    if (parts.length < 2) return;
    const dir = parts[1];

    if (!groups.has(dir)) {
      groups.set(dir, {
        posts: [],
        category: '',
      });
    }
    const g = groups.get(dir);
    g.posts.push(post);

    // Get category slug from first post's front matter
    if (!g.category && post.categories && post.categories.data && post.categories.data.length > 0) {
      g.category = post.categories.data[0].name;
    }
  });

  // Build cards, skip groups with no category slug
  const entries = Array.from(groups.entries())
    .filter(([, g]) => g.category)
    .sort((a, b) => a[0].localeCompare(b[0]));

  const cardsHtml = entries.map(([dir, g], i) => {
    const colorClass = COLOR_CLASSES[i % COLOR_CLASSES.length];
    const icon = ICONS[i % ICONS.length];
    return `
  <a href="/categories/${g.category}/" class="series-card ${colorClass}">
    <div class="card-glow"></div>
    <div class="card-icon">${icon}</div>
    <h2>${dir}</h2>
    <span class="card-count">${g.posts.length} 篇</span>
    <div class="card-arrow">→</div>
  </a>`;
  }).join('\n');

  return {
    path: 'series/index.html',
    data: {
      title: 'rebibabo的博客',
      layout: 'page',
      content: `
<div class="series-hero">
  <div class="series-particles" aria-hidden="true"></div>
  <div class="series-hero-content">
    <h1 class="series-title">
      <span class="typing-text">知识体系</span>
      <span class="cursor">|</span>
    </h1>
    <p class="series-subtitle">探索 Java 高并发 · 工程实践 · 技术思考</p>
    <div class="series-hero-line"></div>
  </div>
</div>

<div class="series-grid">
${cardsHtml}
</div>

<div class="series-footer">
  <p class="footer-quote">"计算机科学中没有什么问题是不能通过增加一个间接层解决的。"</p>
  <p class="footer-attribution">— David Wheeler</p>
</div>

<style>
.series-hero{position:relative;padding:48px 0 36px;text-align:center;overflow:hidden}
.series-hero-content{position:relative;z-index:2}
.series-title{font-size:2.8rem;font-weight:700;margin:0 0 8px;background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#f093fb 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:shimmer 3s ease-in-out infinite;background-size:200% 200%}
@keyframes shimmer{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.cursor{display:inline-block;-webkit-text-fill-color:#764ba2;animation:blink 1s step-end infinite;font-weight:300}
@keyframes blink{50%{opacity:0}}
.series-subtitle{font-size:1.1rem;opacity:0.65;margin:0;letter-spacing:0.05em}
.series-hero-line{width:60px;height:3px;margin:20px auto 0;background:linear-gradient(90deg,#667eea,#764ba2,#f093fb);border-radius:2px;animation:pulse-line 2s ease-in-out infinite}
@keyframes pulse-line{0%,100%{width:60px;opacity:0.6}50%{width:120px;opacity:1}}
.series-particles{position:absolute;inset:0;z-index:1;pointer-events:none}
.series-particles::before,.series-particles::after{content:'';position:absolute;border-radius:50%;opacity:0.12;animation:float 8s ease-in-out infinite}
.series-particles::before{width:120px;height:120px;background:radial-gradient(circle,#667eea,transparent 70%);top:10%;left:15%;animation-delay:0s}
.series-particles::after{width:100px;height:100px;background:radial-gradient(circle,#764ba2,transparent 70%);top:50%;right:10%;animation-delay:-4s}
@keyframes float{0%,100%{transform:translate(0,0) scale(1)}25%{transform:translate(30px,-20px) scale(1.2)}50%{transform:translate(-10px,15px) scale(0.9)}75%{transform:translate(-20px,-10px) scale(1.1)}}
.series-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:24px;padding:0 0 48px}
.series-card{position:relative;display:block;padding:32px 28px 24px;border-radius:16px;text-decoration:none!important;overflow:hidden;transition:transform 0.35s cubic-bezier(0.25,0.46,0.45,0.94),box-shadow 0.35s ease;backdrop-filter:blur(8px);background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06)}
.series-card:hover{transform:translateY(-6px);box-shadow:0 20px 50px rgba(0,0,0,0.2)}
.card-glow{position:absolute;top:-50%;left:-50%;width:200%;height:200%;opacity:0;transition:opacity 0.5s;pointer-events:none}
.card-concurrency .card-glow{background:radial-gradient(circle at 30% 20%,rgba(102,126,234,0.15),transparent 50%)}
.card-basic .card-glow{background:radial-gradient(circle at 70% 20%,rgba(118,75,162,0.12),transparent 50%)}
.card-advanced .card-glow{background:radial-gradient(circle at 50% 80%,rgba(240,147,251,0.12),transparent 50%)}
.card-llm .card-glow{background:radial-gradient(circle at 30% 80%,rgba(102,126,234,0.12),transparent 50%)}
.card-ads .card-glow{background:radial-gradient(circle at 70% 80%,rgba(118,75,162,0.12),transparent 50%)}
.series-card:hover .card-glow{opacity:1}
.card-icon{width:48px;height:48px;margin-bottom:18px;position:relative;z-index:1}
.card-icon svg{width:100%;height:100%}
.series-card h2{font-size:1.2rem;font-weight:650;margin:0 0 8px;position:relative;z-index:1}
.series-card p{font-size:0.9rem;opacity:0.55;margin:0 0 14px;line-height:1.5;position:relative;z-index:1}
.card-count{display:inline-block;padding:3px 12px;border-radius:999px;font-size:0.78rem;font-weight:500;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);position:relative;z-index:1}
.card-arrow{position:absolute;right:28px;bottom:28px;font-size:1.3rem;opacity:0;transform:translateX(-10px);transition:all 0.3s ease;z-index:1}
.series-card:hover .card-arrow{opacity:0.5;transform:translateX(0)}
.series-footer{text-align:center;padding:40px 0 20px}
.footer-quote{font-style:italic;font-size:1rem;opacity:0.5;margin:0 0 6px}
.footer-attribution{font-size:0.82rem;opacity:0.35;margin:0}
[data-user-color-scheme="dark"] .series-card{background:rgba(255,255,255,0.04);border-color:rgba(255,255,255,0.08)}
[data-user-color-scheme="dark"] .series-card:hover{background:rgba(255,255,255,0.07)}
[data-user-color-scheme="dark"] .series-card h2{color:#e1e5eb!important}
[data-user-color-scheme="dark"] .series-card p{color:#e1e5eb!important;opacity:1}
[data-user-color-scheme="dark"] .card-count{color:#e1e5eb!important}
[data-user-color-scheme="dark"] .card-arrow{color:#e1e5eb}
.card-icon{display:none!important}
@media(max-width:768px){.series-title{font-size:2rem}.series-grid{grid-template-columns:1fr;gap:16px}.series-card{padding:24px 20px 20px}}
.series-grid .series-card{opacity:0;transform:translateY(30px);animation:reveal-card 0.6s ease forwards}
.series-grid .series-card:nth-child(1){animation-delay:0.1s}
.series-grid .series-card:nth-child(2){animation-delay:0.2s}
.series-grid .series-card:nth-child(3){animation-delay:0.3s}
.series-grid .series-card:nth-child(4){animation-delay:0.4s}
.series-grid .series-card:nth-child(5){animation-delay:0.5s}
@keyframes reveal-card{to{opacity:1;transform:translateY(0)}}
</style>`
    },
    layout: 'page'
  };
});
