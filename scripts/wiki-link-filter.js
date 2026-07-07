/* global hexo */
'use strict';

// Map: source path (relative to source/) → final URL path
// e.g., "_posts/concurrency/05-CAS.md" → "/categories/java-concurrency/05/"
let sourceToUrl = {};

// Build source→url mapping from all posts at generate time
hexo.extend.filter.register('before_generate', function() {
  const posts = hexo.locals.get('posts');
  if (!posts) return;

  posts.forEach(function(post) {
    if (post.source && post.path) {
      // post.source: "_posts/concurrency/05-CAS.md"
      // post.path: "categories/java-concurrency/05/index.html"
      const url = '/' + post.path.replace(/index\.html$/, '');
      sourceToUrl[post.source] = url;
      // Also map without extension
      sourceToUrl[post.source.replace(/\.md$/, '')] = url;
    }
  });
}, 0);

// Convert [[wiki/...]] Obsidian links to Hexo links during markdown rendering
hexo.extend.filter.register('before_post_render', function(data) {
  if (!data.source || !data.raw) return data;

  const sourcePath = data.source;
  const isWiki = sourcePath.startsWith('wiki/');

  if (isWiki) {
    // Inject layout for wiki pages that don't have one
    if (!data.layout) {
      data.layout = 'page';
    }

    // Convert Obsidian wikilinks
    data.raw = convertWikilinks(data.raw, data);
  }

  if (sourcePath.startsWith('_posts/')) {
    data.raw = convertWikilinks(data.raw, data);
  }

  return data;
}, 9);

function convertWikilinks(content, data) {
  // [[wiki/path|text]] → [text](/wiki/path/)
  content = content.replace(/\[\[wiki\/([^\]|]+?)(?:\|([^\]]+?))?\]\]/g, function(match, path, text) {
    const display = text || path.split('/').pop();
    // Remove .md extension if present
    const cleanPath = path.replace(/\.md$/, '');
    // Handle wiki/index → wiki/
    const url = cleanPath === 'index' ? '/wiki/' : '/wiki/' + cleanPath + '/';
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
