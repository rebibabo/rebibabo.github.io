/* global hexo */
'use strict';

var through2 = require('through2');

// Hook into Hexo's Router to inject prev/next URLs based on source order
hexo.extend.filter.register('before_generate', function() {
  // Get all posts sorted by source
  var posts = hexo.locals.get('posts').data;
  if (!posts || posts.length < 2) return;

  posts.sort(function(a, b) {
    return a.source.localeCompare(b.source);
  });

  // Directly set prev/next on each post so the theme's helpers pick them up
  for (var i = 0; i < posts.length; i++) {
    if (i > 0) posts[i].prev = posts[i - 1];
    else posts[i].prev = null;

    if (i < posts.length - 1) posts[i].next = posts[i + 1];
    else posts[i].next = null;
  }
});
