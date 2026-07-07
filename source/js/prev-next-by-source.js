/* global hexo */
'use strict';

// Regenerate post prev/next based on same-category + source order
// This runs after the built-in post generator and overrides its prev/next
hexo.extend.generator.register('prev-next-fix', function(locals) {
  var posts = locals.posts.sort('source').toArray();
  var length = posts.length;

  return posts.map(function(post, i) {
    var path = post.path;
    var layout = post.layout;
    if (!layout || layout === 'false') return;

    // Find prev: same-category, source order
    var prev = null;
    for (var j = i - 1; j >= 0; j--) {
      if (sameCat(post, posts[j])) { prev = posts[j]; break; }
    }
    post.prev = prev;

    // Find next: same-category, source order
    var next = null;
    for (var k = i + 1; k < length; k++) {
      if (sameCat(post, posts[k])) { next = posts[k]; break; }
    }
    post.next = next;

    return {
      path: path,
      data: post
    };
  });

  function sameCat(a, b) {
    if (!a.categories || !b.categories) return false;
    var aNames = a.categories.map(function(c) { return c.name; });
    var bNames = b.categories.map(function(c) { return c.name; });
    return aNames.some(function(n) { return bNames.indexOf(n) !== -1; });
  }
});
