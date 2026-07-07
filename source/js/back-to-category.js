(function () {
  const CATEGORY_PREFIX = "/categories/";
  const SCROLL_KEY_PREFIX = "category-scroll:";

  function isCategoryPage() {
    // /categories/xxx/  (一个子路径) → 分类列表页
    // /categories/xxx/01/ (两个子路径) → 文章页
    return /^\/categories\/[^/]+\/$/.test(location.pathname);
  }

  function isPostPage() {
    return !isCategoryPage() && !!document.querySelector(".markdown-body");
  }

  function scrollKey(pathname) {
    return SCROLL_KEY_PREFIX + pathname;
  }

  // 1. 在分类页：保存滚动位置 + 显示"返回主页"按钮
  if (isCategoryPage()) {
    // 保存和恢复滚动位置
    const key = scrollKey(location.pathname);

    const savedY = sessionStorage.getItem(key);
    if (savedY !== null) {
      setTimeout(function () {
        window.scrollTo(0, Number(savedY));
      }, 80);
    }

    let ticking = false;

    window.addEventListener("scroll", function () {
      if (ticking) {
        return;
      }

      ticking = true;

      requestAnimationFrame(function () {
        sessionStorage.setItem(key, String(window.scrollY));
        ticking = false;
      });
    });

    // 添加"返回主页"按钮
    var homeBtn = document.createElement("a");
    homeBtn.className = "back-to-home-btn";
    homeBtn.href = "/series/";
    homeBtn.innerText = "← 返回主页";
    document.body.appendChild(homeBtn);

    return;
  }

  // 2. 只在文章页显示返回按钮
  if (!isPostPage()) {
    return;
  }

  let target = "/categories/";

  // 优先从页面自身的分类链接获取（文章页一定有 .category-chain-item）
  const catLink = document.querySelector(".category-chain-item");
  if (catLink) {
    target = catLink.getAttribute("href");
  }

  const link = document.createElement("a");
  link.className = "back-to-category-btn";
  link.href = target;
  link.innerText = "← 返回分类列表";

  link.addEventListener("click", function (event) {
    event.preventDefault();
    location.href = target;
  });

  document.body.appendChild(link);
})();