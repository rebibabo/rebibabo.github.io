/* global hexo */
'use strict';

hexo.extend.filter.register('before_generate', function() {
  var posts = hexo.locals.get('posts');
  if (!posts || !posts.data || posts.data.length < 2) return;

  // Sort by source file path
  posts.data.sort(function(a, b) {
    return a.source.localeCompare(b.source);
  });

  // Rebuild prev/next chain to follow sorted order
  for (var i = 0; i < posts.data.length; i++) {
    posts.data[i].prev = i > 0 ? posts.data[i - 1] : null;
    posts.data[i].next = i < posts.data.length - 1 ? posts.data[i + 1] : null;
  }
});
