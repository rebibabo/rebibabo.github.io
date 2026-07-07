/* global hexo */
'use strict';

hexo.extend.filter.register('after_init', function() {
  // Sort all posts by source file path in Hexo's model
  hexo.model('Post').sort('source');
});
