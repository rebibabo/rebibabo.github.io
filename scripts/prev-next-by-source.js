/* global hexo */
'use strict';

// Replace the Hexo locals.getter for 'posts' to sort by source file path
// This ensures post.prev and post.next are set based on source order
hexo.extend.filter.register('after_init', function() {
  var db = hexo.model('Post');
  if (!db) return;

  // Set default model sort order
  db.sort('source');
});
