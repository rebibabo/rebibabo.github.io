/* global hexo */
'use strict';

// Get sibling posts in the same categories, sorted by source file ascending
function getSiblings(post) {
  var all = hexo.model('Post').toArray();
  if (!all.length) return [];

  var catNames = [];
  if (post.categories && post.categories.length) {
    catNames = post.categories.map(function(c) { return c.name; });
  }
  if (!catNames.length) return [];

  return all
    .filter(function(p) {
      if (p._id === post._id) return false;
      if (!p.categories || !p.categories.length) return false;
      var pCats = p.categories.map(function(c) { return c.name; });
      return catNames.some(function(cn) { return pCats.indexOf(cn) !== -1; });
    })
    .sort(function(a, b) {
      return a.source.localeCompare(b.source);
    });
}

hexo.extend.helper.register('prev_post', function(post) {
  var sibs = getSiblings(post);
  for (var i = 0; i < sibs.length; i++) {
    if (sibs[i].source.localeCompare(post.source) >= 0) {
      return i > 0 ? sibs[i - 1] : null;
    }
  }
  return sibs.length ? sibs[sibs.length - 1] : null;
});

hexo.extend.helper.register('next_post', function(post) {
  var sibs = getSiblings(post);
  for (var i = sibs.length - 1; i >= 0; i--) {
    if (sibs[i].source.localeCompare(post.source) <= 0) {
      return i < sibs.length - 1 ? sibs[i + 1] : null;
    }
  }
  return sibs.length ? sibs[0] : null;
});
