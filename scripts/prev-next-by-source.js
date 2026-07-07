/* global hexo */
'use strict';

// Override prev_post and next_post helpers to use source file order
hexo.extend.helper.register('prev_post', function(orig) {
  return function(post) {
    var posts = hexo.locals.get('posts').data;
    if (!posts || posts.length < 2) return null;

    // Sort by source (file path) ascending
    var sorted = posts.slice().sort(function(a, b) {
      return a.source.localeCompare(b.source);
    });

    var idx = sorted.indexOf(post);
    if (idx <= 0) return null;

    var prev = sorted[idx - 1];
    while (prev && prev.hide) {
      idx--;
      if (idx <= 0) return null;
      prev = sorted[idx - 1];
    }
    return prev;
  };
}(hexo.extend.helper.get('prev_post')));

hexo.extend.helper.register('next_post', function(orig) {
  return function(post) {
    var posts = hexo.locals.get('posts').data;
    if (!posts || posts.length < 2) return null;

    // Sort by source (file path) ascending
    var sorted = posts.slice().sort(function(a, b) {
      return a.source.localeCompare(b.source);
    });

    var idx = sorted.indexOf(post);
    if (idx < 0 || idx >= sorted.length - 1) return null;

    var next = sorted[idx + 1];
    while (next && next.hide) {
      idx++;
      if (idx >= sorted.length - 1) return null;
      next = sorted[idx + 1];
    }
    return next;
  };
}(hexo.extend.helper.get('next_post')));
