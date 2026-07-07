(function () {
  // 只在文章页显示：你的文章 URL 是 /2026/07/02/xxx/ 这种结构
  if (!/^\/\d{4}\/\d{2}\/\d{2}\//.test(location.pathname)) {
    return;
  }

  let target = "/categories/";

  // 如果是从某个分类页点进来的，就返回那个分类页
  if (document.referrer) {
    try {
      const ref = new URL(document.referrer);

      if (
        ref.origin === location.origin &&
        ref.pathname.startsWith("/categories/")
      ) {
        target = ref.pathname;
      }
    } catch (e) {
      target = "/categories/";
    }
  }

  const link = document.createElement("a");
  link.className = "back-to-category-btn";
  link.href = target;
  link.innerText = "← 返回分类列表";

  document.body.appendChild(link);
})();