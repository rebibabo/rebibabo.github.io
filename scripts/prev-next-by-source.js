/* global hexo */
'use strict';

// Override prev_post helper — find previous post by source file order
hexo.extend.helper.register('prev_post', function(post) {
  var all = hexo.model('Post');
  if (!all) return null;

  var posts = all.toArray();
  if (posts.length < 2) return null;

  posts.sort(function(a, b) {
    return a.source.localeCompare(b.source);
  });

  var idx = posts.indexOf(post);
  if (idx <= 0) return null;

  var prev = posts[idx - 1];
  if (prev && prev.hide) return null;
  return prev;
});

// Override next_post helper — find next post by source file order
hexo.extend.helper.register('next_post', function(post) {
  var all = hexo.model('Post');
  if (!all) return null;

  var posts = all.toArray();
  if (posts.length < 2) return null;

  posts.sort(function(a, b) {
    return a.source.localeCompare(b.source);
  });

  var idx = posts.indexOf(post);
  if (idx < 0 || idx >= posts.length - 1) return null;

  var next = posts[idx + 1];
  if (next && next.hide) return null;
  return next;
});
