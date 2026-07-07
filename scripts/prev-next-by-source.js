/* global hexo */
'use strict';

hexo.extend.helper.register('prev_post', function(post) {
  var posts = hexo.locals.get('posts').data;
  if (!posts || posts.length < 2) return null;

  var sorted = posts.slice().sort(function(a, b) {
    return a.source.localeCompare(b.source);
  });

  var idx = sorted.indexOf(post);
  if (idx <= 0) return null;
  var prev = sorted[idx - 1];
  if (prev && prev.hide) return null;
  return prev;
});

hexo.extend.helper.register('next_post', function(post) {
  var posts = hexo.locals.get('posts').data;
  if (!posts || posts.length < 2) return null;

  var sorted = posts.slice().sort(function(a, b) {
    return a.source.localeCompare(b.source);
  });

  var idx = sorted.indexOf(post);
  if (idx < 0 || idx >= sorted.length - 1) return null;
  var next = sorted[idx + 1];
  if (next && next.hide) return null;
  return next;
});
