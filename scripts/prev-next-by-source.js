/* global hexo */
'use strict';

hexo.extend.filter.register('after_init', function() {
  // After init, replace the built-in post generator to sort by source
  // The original post.js generator does: locals.posts.sort('-date').toArray()
  // We re-register and rely on our version running after the built-in one

  // Actually, directly monkey-patch the built-in post generator module
  // to change '-date' to 'source'
  try {
    var postGenPath = require.resolve('hexo/dist/plugins/generator/post');
    delete require.cache[postGenPath];
    var genModule = require(postGenPath);
    // We can't easily patch this, so let's try another way
  } catch(e) {}
});

// Cleanest approach: intercept at the locals level
// Override how locals.posts.sort works to always sort by source
hexo.extend.filter.register('before_generate', function() {
  var origGet = hexo.locals.get.bind(hexo.locals);

  // Store sorted posts array so everyone gets the same order
  var sortedPosts = null;

  // Monkey-patch hexo.locals.get to wrap 'posts'
  hexo.locals.get = function(name) {
    var result = origGet(name);
    if (name === 'posts' && result) {
      if (!sortedPosts) {
        sortedPosts = result.sort('source');
      }
      return sortedPosts;
    }
    return result;
  };
});
