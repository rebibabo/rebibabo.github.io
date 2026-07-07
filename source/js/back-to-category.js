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

  // 优先从页面自身的分类链接获取（文章页一定有 .category-chain-item）
  const catLink = document.querySelector(".category-chain-item");
  if (catLink) {
    target = catLink.getAttribute("href");
  }

  // 在文章头部注入分类导航条
  var catName = catLink ? catLink.textContent.trim() : "";
  var navDiv = document.createElement("div");
  navDiv.className = "post-category-nav";
  navDiv.innerHTML =
    '<span class="nav-sep">📂</span>' +
    '<a href="/series/">首页</a>' +
    '<span class="nav-sep">/</span>' +
    '<a href="' + target + '">' + catName + '</a>';
  // 插入到标题下方
  var bannerContent = document.querySelector("#banner > div > div > div");
  if (bannerContent) {
    bannerContent.appendChild(navDiv);
  }

  const link = document.createElement("a");
  link.className = "back-to-category-btn";
  link.href = target;
  link.innerText = "← 返回分类列表";

  link.addEventListener("click", function (event) {
    event.preventDefault();

    // 优先用 history.back()，浏览器会恢复滚动位置
    if (history.length > 1) {
      history.back();
      return;
    }

    location.href = target;
  });

  document.body.appendChild(link);
})();