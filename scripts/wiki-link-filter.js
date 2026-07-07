/* global hexo */
'use strict';

// Map: source path (relative to source/) → final URL path
// e.g., "_posts/concurrency/05-CAS.md" → "/categories/java-concurrency/05/"
let sourceToUrl = {};

// Build source→url mapping from all posts at generate time
hexo.extend.filter.register('before_generate', function() {
  // Build post URL mappings
  const posts = hexo.locals.get('posts');
  if (posts) {
    posts.forEach(function(post) {
      if (post.source && post.path) {
        const url = '/' + post.path.replace(/index\.html$/, '');
        sourceToUrl[post.source] = url;
        sourceToUrl[post.source.replace(/\.md$/, '')] = url;
      }
    });
  }

}, 0);

// Convert [[wiki/...]] Obsidian links to Hexo links during markdown rendering
hexo.extend.filter.register('before_post_render', function(data) {
  if (!data.source || !data.raw) return data;

  const sourcePath = data.source;

  if (sourcePath.indexOf('_posts') !== -1) {
    data.raw = convertWikilinks(data.raw, data);
  }

  return data;
}, 9);

// For wiki pages (rendered as pages not posts), use after_render:html
hexo.extend.filter.register('after_render:html', function(html, data) {
  if (!data.path || !/^wiki\//.test(data.path)) return html;

  // Only process body content (avoid breaking meta tags in <head>)
  const bodyMatch = html.match(/([\s\S]*<body[^>]*>)([\s\S]*)(<\/body>[\s\S]*)/i);
  if (!bodyMatch) return html;

  let head = bodyMatch[1];
  let body = bodyMatch[2];
  let foot = bodyMatch[3];

  // Wrap page content in markdown-body for proper styling (tables, headings, etc.)
  body = body.replace(
    /(<article class="page-content">)([\s\S]*?)(<\/article>)/,
    '$1<div class="markdown-body">$2</div>$3'
  );

  // Convert [[wiki/...]] links — only within body content
  body = body.replace(/\[\[wiki(?:&#x2F;|\/)([^\]|]+?)(?:\|([^\]]+?))?\]\]/g, function(match, path, text) {
    const cleanPath = path.replace(/&#x2F;/g, '/').replace(/\.md$/, '');
    const display = text || cleanPath.split('/').pop();
    const url = cleanPath === 'index' ? '/wiki/' : '/wiki/' + cleanPath + '.html';
    return '<a href="' + url + '" class="wiki-link">' + display + '</a>';
  });

  // Convert mermaid click directives: .md → .html, make URLs absolute
  body = body.replace(/(click\s+\w+\s+(?:&quot;|"))(wiki\/[^"&]+)\.md((?:&quot;|"))/g, function(m, prefix, path, suffix) {
    return prefix + '/' + path + '.html' + suffix;
  });

  // Convert [[_posts/...]] links — only within body content
  body = body.replace(/\[\[_posts(?:&#x2F;|\/)([^\]|]+?)(?:\|([^\]]+?))?\]\]/g, function(match, path, text) {
    const key = '_posts/' + path;
    const keyNoExt = key.replace(/\.md$/, '');
    const url = sourceToUrl[key] || sourceToUrl[keyNoExt];
    if (url) {
      const display = text || url.split('/').filter(Boolean).pop();
      return '<a href="' + url + '">' + display + '</a>';
    }
    const display = text || path.split('/').pop().replace(/\.md$/, '');
    return '<a href="/wiki/">' + display + ' (unresolved)</a>';
  });

  return head + body + foot;
}, 15);

function convertWikilinks(content, data) {
  // [[wiki/path|text]] → [text](/wiki/path/)
  content = content.replace(/\[\[wiki\/([^\]|]+?)(?:\|([^\]]+?))?\]\]/g, function(match, path, text) {
    const display = text || path.split('/').pop();
    // Remove .md extension if present
    const cleanPath = path.replace(/\.md$/, '');
    // Handle wiki/index → wiki/
    const url = cleanPath === 'index' ? '/wiki/' : '/wiki/' + cleanPath + '.html';
    return '[' + display + '](' + url + ')';
  });

  // [[_posts/path/to/file|text]] → [text](post-url)
  content = content.replace(/\[\[_posts\/([^\]|]+?)(?:\|([^\]]+?))?\]\]/g, function(match, path, text) {
    const key = '_posts/' + path;
    const keyNoExt = key.replace(/\.md$/, '');
    const url = sourceToUrl[key] || sourceToUrl[keyNoExt];

    if (url) {
      // Extract post title from the display text or use default
      const display = text || (url.split('/').filter(Boolean).pop());
      return '[' + display + '](' + url + ')';
    }

    // Fallback: link to the raw source path in wiki
    const display = text || path.split('/').pop().replace(/\.md$/, '');
    return '[' + display + '](/wiki/_posts/' + path.replace(/\.md$/, '') + '/)';
  });

  return content;
}

// Add "返回 Wiki" button to wiki detail pages
hexo.extend.filter.register('after_render:html', function(html, data) {
  if (!data.path || !/^wiki\/(concepts|glossary|maps|series)\//.test(data.path)) return html;

  // Add back-to-wiki button
  const btn = '<a href="/wiki/" class="back-to-wiki-btn">← 返回 Wiki</a>';
  let bodyEnd = btn + '\n';

  // Add mermaid (same CDN & init as Fluid theme, wait for script load)
  if (/class="[^"]*mermaid[^"]*"/.test(html)) {
    bodyEnd += `<script>
(function(){
  var s = document.createElement('script');
  s.src = 'https://lib.baomitu.com/mermaid/8.14.0/mermaid.min.js';
  s.onload = function() {
    mermaid.initialize({"theme":"default"});
    mermaid.init(undefined, '.mermaid');
  };
  document.body.appendChild(s);
})();
</script>\n`;
  }

  bodyEnd += '</body>';
  html = html.replace('</body>', bodyEnd);

  // Add CSS for the button
  const style = `<style>
.back-to-wiki-btn {
  position: fixed;
  left: 24px;
  bottom: 32px;
  z-index: 9999;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(102,126,234,0.9);
  color: #fff !important;
  font-size: 14px;
  text-decoration: none !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.18);
}
.back-to-wiki-btn:hover {
  background: rgba(118,75,162,0.95);
  color: #fff !important;
}
@media (max-width: 768px) {
  .back-to-wiki-btn { left: 16px; bottom: 20px; font-size: 13px; padding: 7px 12px; }
}
</style>`;

  html = html.replace('</head>', style + '\n</head>');
  return html;
}, 20);
