# Playwright 自动化 — 通用模式、踩坑与最佳实践

## 一、登录态持久化

### 保存与加载
```python
# 保存
context.storage_state(path="auth.json")

# 加载（跳过登录）
context = browser.new_context(storage_state="auth.json")
```

### 过期检测
不要依赖特定 class 名（网站改版会变）。最可靠的方式：
```python
# 1. 访问需要登录的页面
page.goto("https://xxx.com/dashboard")
# 2. 检查是否被重定向到了登录页
if "login" in page.url:
    return False  # 过期
# 3. 兜底：检查关键元素
return page.evaluate("() => !!document.querySelector('.user-avatar')")
```

### 登录流程
- 登录页必须 `headless=False`，用户要看到页面
- 登录成功自动检测优于 `input()` 手动按回车：
  ```python
  for _ in range(150):  # 最多等 5 分钟
      time.sleep(2)
      try:
          if "login" not in page.url:
              break  # 已跳转 = 登录成功
          page.evaluate("() => !!document.querySelector('.avatar')")
      except Exception:
          # 页面跳转中 evaluate 会报 Execution context was destroyed
          # 这恰恰说明登录成功了
          if "login" not in page.url:
              break
  ```
- 登录态检测**不要嵌套 `sync_playwright()`**，应复用外层已有的 playwright 实例

## 二、多标签页 / 弹窗处理

```python
# 新标签页
with page.expect_popup() as popup_info:
    page.locator("a.target-blank").click()
new_page = popup_info.value

# 新窗口
with page.expect_popup() as popup_info:
    page.locator("button.open-window").click()
```

⚠️ `expect_popup` 必须在触发点击的**同一行代码前**声明，否则可能丢失。

## 三、内容填入

### 三种方式，选对场景

| 方式 | 适用场景 | 缺点 |
|---|---|---|
| `locator.fill(text)` | textarea、input | 不适用于富文本/contenteditable |
| `keyboard.insert_text(text)` | 模拟打字 | 逐字输入慢，**丢失 markdown 格式** |
| 剪贴板粘贴 | 富文本/Markdown 编辑器 | 需要剪贴板权限 |

### 剪贴板粘贴（推荐用于 Markdown 编辑器）
```python
# 1. 创建 context 时授权
context = browser.new_context(
    permissions=["clipboard-read", "clipboard-write"]
)

# 2. 写入剪贴板 + 粘贴
page.evaluate("(content) => navigator.clipboard.writeText(content)", body)
page.keyboard.press("ControlOrMeta+v")
```

### CodeMirror / Monaco 编辑器 API
```python
# CodeMirror
page.evaluate("""
    document.querySelector('.CodeMirror').CodeMirror.setValue(content)
""")

# Monaco
page.evaluate("""
    window.monaco.editor.getModels()[0].setValue(content)
""")
```
先检测编辑器类型再选方案，避免无脑 fallback。

## 四、选择器策略

### 优先级
1. **CSS 选择器** → `.class-name`、`#id`、`[data-xxx="yyy"]`（最稳定）
2. **placeholder 匹配** → `[placeholder*="搜索"]`（较稳定）
3. **role 选择器** → `get_by_role("button", name="提交")`（一般，UI 改版易失效）
4. **text 匹配** → `get_by_text("确 定", exact=True)`（最不稳定）

### 常见问题与解法

**元素不可点击（嵌套太深/Vue 组件）**
```python
# 方案 A：force click
page.locator(".deeply-nested").click(force=True)

# 方案 B：直接 DOM 点击（终极方案）
page.evaluate("document.querySelector('.btn').click()")
```

**`:has-text()` 是 Playwright 专属伪类**
不能在 `document.querySelector()` 里使用，会报 `not a valid selector`：
```javascript
// ❌ 错误
document.querySelector('a:has-text("提交")')
// ✅ 正确
document.querySelectorAll('a').find(a => a.textContent.includes('提交'))
```

**循环删除列表项**
```python
items = page.locator(".delete-btn")
for _ in range(items.count()):
    items.nth(0).click()  # 删掉后索引前移，始终点第一个
    page.wait_for_timeout(300)
```

**条件点击（元素可能存在也可能不存在）**
```python
def safe_click(page, selector, timeout=2000):
    try:
        page.locator(selector).wait_for(timeout=timeout)
        page.locator(selector).click()
    except Exception:
        pass  # 不存在就跳过
```
适用：广告弹窗、引导跳过、可选的关闭按钮。

**多选匹配（遍历列表按文本匹配）**
```python
items = page.locator(".item").all()
for name in TARGET_NAMES:
    found = next((i for i in items if i.text_content().strip() == name), None)
    if found:
        found.click()
    else:
        print(f"未找到: {name}")
```

## 五、下拉 / 弹窗 / 面板

```python
# 打开面板
page.locator("#panel .open-btn").click()
page.wait_for_timeout(500)

# 操作面板内的元素
page.locator(".panel-item").first.click()

# 关闭面板
page.locator(".modal .close-btn").click()
```

⚠️ 面板/弹窗打开后要等一小段时间 DOM 渲染完成，否则 click 可能落空。

## 六、URL 编码

```python
from urllib.parse import quote

# 路径含中文时需要编码
encoded = "/".join(quote(part, safe="") for part in path.split("/"))

# markdown 中保留原始中文（浏览器会自动处理）
raw_url = f"https://cdn.example.com/{path}"        # 有中文
check_url = f"https://cdn.example.com/{encoded}"   # 编码后
```
⚠️ 某些后端图片抓取服务处理不好编码后的中文 URL → markdown 中保留原始路径更安全。

## 七、外部 API 调用

```python
import ssl, json, urllib.request

# macOS Python SSL 问题
ctx = ssl._create_unverified_context()

data = json.dumps({
    "model": "gpt-4",
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.3,
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.example.com/chat/completions",
    data=data,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    },
)
with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
    result = json.loads(resp.read().decode("utf-8"))
```

⚠️ API 调用必须有 fallback，失败时自动降级到本地兜底策略。

## 八、git 操作在 subprocess 中

```python
import subprocess

# ❌ 不推荐：capture_output 吞掉错误
subprocess.run(["git", "push"], capture_output=True)

# ✅ 推荐：打印 stderr
result = subprocess.run(
    ["git", "push", "origin", "main"],
    capture_output=True, text=True,
)
if result.returncode != 0:
    print(f"git push 失败: {result.stderr}")
```

⚠️ subprocess 环境里拿不到终端的 SSH agent / Git credential helper。优先让用户手动 git 操作，脚本只检测不自动推送。

## 九、macOS 定时任务（合盖可执行）

### 架构
```
pmset (唤醒) → launchd (定时触发) → shell wrapper → caffeinate -s python3 script.py
```

### pmset：睡眠唤醒
```bash
# 每天 23:58 唤醒
sudo pmset repeat wakeorpoweron MTWRFSU 23:58:00

# 查看
pmset -g sched

# 取消
sudo pmset repeat cancel
```

### launchd：定时执行
plist 路径：`~/Library/LaunchAgents/com.xxx.plist`

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key><integer>0</integer>
    <key>Minute</key><integer>0</integer>
</dict>
<key>EnvironmentVariables</key>
<dict>
    <key>PATH</key><string>/usr/local/bin:/usr/bin:/bin</string>
    <key>HOME</key><string>/Users/xxx</string>
    <key>YOUR_API_KEY</key><string>xxx</string>
</dict>
```

```bash
# 加载
launchctl load ~/Library/LaunchAgents/com.xxx.plist
# 查看
launchctl list | grep com.xxx
# 卸载
launchctl unload ~/Library/LaunchAgents/com.xxx.plist
```

### caffeinate：防休眠
```bash
# ❌ -i：防空闲休眠，但合盖必睡
caffeinate -i python3 script.py

# ✅ -s：防系统休眠，合盖也能跑（需接电源）
caffeinate -s python3 script.py
```

⚠️ 电池模式合盖**必睡**，苹果不提供配置选项。定时任务场景必须接电源。

### 停止脚本模板
```bash
# 卸载 launchd
launchctl unload ~/Library/LaunchAgents/com.xxx.plist

# 取消唤醒
sudo pmset repeat cancel

# 清理残留进程
pkill -f "script_name.py"
pkill -f "chromium.*playwright"
```

## 十、调试与测试

### 有头模式
```python
browser = playwright.chromium.launch(headless=False)  # 看着浏览器操作
```

### 变量化 headless
```python
HEADLESS = os.environ.get("HEADLESS", "true") == "true"
browser = playwright.chromium.launch(headless=HEADLESS)
```

### 干跑测试
写一个 dummy 脚本，只打印不实际操作，验证调度链路：
```python
for i, article in enumerate(articles):
    print(f"({i+1}/{total}) 模拟发布: {article['path']}")
    time.sleep(5)
```

### 日志
所有 print 加 `flush=True`，避免缓冲延迟：
```python
print(f"[{datetime.now()}] 开始发布...", flush=True)
```
用文件日志 + 终端双写。

---

## 速查表

| 场景 | 方案 |
|---|---|
| 元素不可点击 | `click(force=True)` 或 `evaluate("el.click()")` |
| 页面跳转中报错 | catch Exception，检查 page.url |
| 列表逐项删除 | `nth(0).click()` 循环 |
| markdown 内容填入 | 剪贴板粘贴，不用 insert_text |
| 多标签页 | `expect_popup()` |
| 条件点击 | `safe_click()` 包装 |
| SSL 证书错误 | `ssl._create_unverified_context()` |
| git push 失败 | 不要自动 push，提示用户手动 |
| 合盖还要跑 | `caffeinate -s` + 必须接电源 |
| API 失败 | 必须 fallback，不能阻断主流程 |
