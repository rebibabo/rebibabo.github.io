/* global hexo */
'use strict';

// Re-sort posts by source file path so prev/next follow filename order
hexo.extend.filter.register('after_init', function() {
  var Post = hexo.model('Post');

  // Sort by source (file path), same as order_by: source
  Post.sort('source');
});
