(function () {
  const CATEGORY_PREFIX = "/categories/";
  const SCROLL_KEY_PREFIX = "category-scroll:";

  function isCategoryPage() {
    return location.pathname.startsWith(CATEGORY_PREFIX);
  }

  function isPostPage() {
    return /^\/\d{4}\/\d{2}\/\d{2}\//.test(location.pathname);
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
  let canBackToCategory = false;

  if (document.referrer) {
    try {
      const ref = new URL(document.referrer);

      if (
        ref.origin === location.origin &&
        ref.pathname.startsWith(CATEGORY_PREFIX)
      ) {
        target = ref.pathname;
        canBackToCategory = true;
      }
    } catch (e) {
      target = "/categories/";
    }
  }

  const link = document.createElement("a");
  link.className = "back-to-category-btn";
  link.href = target;
  link.innerText = "← 返回分类列表";

  link.addEventListener("click", function (event) {
    event.preventDefault();

    // 从分类页点进文章时，优先 history.back()
    // 浏览器通常会自动恢复原来的滚动位置
    if (canBackToCategory && history.length > 1) {
      history.back();
      return;
    }

    // 不是从分类页进入的，就跳到分类总页或 referrer 分类页
    location.href = target;
  });

  document.body.appendChild(link);
})();