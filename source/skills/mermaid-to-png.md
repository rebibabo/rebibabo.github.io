# Skill：Mermaid 流程图 → PNG 图片

> 从生成 Mermaid 代码到渲染 PNG 并替换 Markdown 的完整工作流。

---

## 什么时候用 Mermaid

适合用 Mermaid 画图的内容：

| 场景 | 示例 |
|------|------|
| 流程/步骤链 | 登录流程、请求处理流程、状态机 |
| 架构关系 | 单体 vs 微服务、组件分层、调用链 |
| 对比/并列 | VM vs Container、Session vs JWT |
| 时序关系 | A 调用 B → B 调用 C |

不适合：
- **超过 6~7 个节点**的长链（图会非常宽）
- 复杂网状结构（Mermaid 布局容易乱）
- 纯数据表格（用 Markdown 表格更合适）

**最佳节点数：3~6 个步骤。**

---

## Mermaid 代码生成规范

### 1. 必须用横向布局 `graph LR`

竖排（`graph TB`）会让高瘦图被 CSS 拉宽撑满页面，非常难看。

```
# ✅ 正确
graph LR
    A[步骤一] --> B[步骤二] --> C[步骤三]

# ❌ 错误
graph TB
    A[步骤一] --> B[步骤二] --> C[步骤三]
```

### 2. 每行只写一条连接

Mermaid 解析器要求每条连接独占一行。

```
# ✅ 正确
    A -->|label| B
    C --> D

# ❌ 错误 —— 会报 Parse error
    A -->|label| B    C --> D
```

### 3. 子图也用横向布局

```
# ✅ 正确
    subgraph 写入["写入线程"]
        direction LR
        D[data = 42] --> VR[volatile write]
    end

# ❌ 错误
    subgraph 写入["写入线程"]
        direction TB          ← 竖排
        D[data = 42] --> VR[volatile write]
    end
```

### 4. 多个子图需要跨子图连接

两个子图如果没有连在一起，会被竖向叠放。

```
    subgraph A[...] ... end
    subgraph B[...] ... end
    A_end_node ~~~ B_start_node    ← 用 ~~~ 隐性连接让它们横排
```

### 5. 不要用菱形节点

菱形 `{...}` 在某些版本有兼容问题，统一用方框 `[...]`。

```
# ✅
    Decision["判断条件"]

# ❌
    Decision{"判断条件"}
```

### 6. 避免在边缘标签中用 `( )`

括号在 Mermaid 中是圆角矩形的语法标记，会触发解析错误。

```
# ✅
    A -->|BillingClient.charge 调用| B

# ❌
    A -->|BillingClient.charge(...)| B
```

### 7. 节点文本用 `<br/>` 换行

```
    Node["第一行内容<br/>第二行内容"]
```

---

## 转换脚本

脚本位置：`bin/mermaid-to-image.js`

### 用法

```bash
# 干跑预览
node bin/mermaid-to-image.js --dir Java-advanced --dry-run

# 转换指定分类
node bin/mermaid-to-image.js --dir Java-advanced --concurrency 17

# 转换全部
node bin/mermaid-to-image.js --concurrency 17
```

### 工作流程

1. 扫描 `source/_posts/<category>/` 下的 `.md` 文件
2. 提取所有 ` ```mermaid ` 代码块
3. 自动规范化（TB→LR、菱形→方框、子图方向修正、单行拆多行等）
4. 用 `mmdc`（Mermaid CLI v11.16.0+）渲染为 PNG（`--scale 2` 保证清晰度）
5. 图片保存到 `source/images/<category>/IMG-xxx.png`
6. Mermaid 源码保存为 `IMG-xxx.mmd` 与 PNG 并列
7. Markdown 中的 ` ```mermaid ` 块替换为 `![](/images/<category>/IMG-xxx.png)`

### 自动规范化规则（`normalizeMermaid`）

脚本内置以下自动修正：

| 规则 | 说明 |
|------|------|
| `graph TB/TD` → `graph LR` | 竖排变横排 |
| `flowchart TB/TD` → `flowchart LR` | 竖排变横排 |
| `direction TB/TD` → `direction LR` | 子图内方向修正 |
| 子图无 `direction` → 自动插入 `direction LR` | 补充子图方向 |
| `Node{"text"}` → `Node["text"]` | 菱形变方框 |
| `&#40;`/`&#41;` → `(`/`)` | 修复 HTML 转义 |
| 同一行多个 `-->` → 拆成多行 | 防止解析错误 |
| 子图内孤立节点 → `---` 串链 | 让节点横排 |
| 多子图无连接 → `~~~` 隐性连接 | 让子图横排 |

### 依赖

- **mmdc**（Mermaid CLI）：全局安装 `npm install -g @mermaid-js/mermaid-cli@latest`
- **Node.js** v24+

---

## CSS 控制图片显示

`source/css/custom.css` 中的关键规则：

```css
.markdown-body pre[style*="display:none"] + p > img {
  display: block;
  width: auto !important;
  max-width: min(760px, 100%) !important;
  max-height: 700px;
  height: auto !important;
  margin: 1.5rem auto;
  object-fit: contain;
}
```

通过 `<pre style="display:none">` 保存 Mermaid 源码后紧跟的 `![]()` 图片，自动限制最大宽度 760px、最大高度 700px，居中显示，保持比例。

---

## 图片 Alt Text 清理规则

Obsidian 会自动给图片引用加上数字或尺寸信息：

```
![374](/images/Java-advanced/IMG-xxx.png)     ← 纯数字 → 清空
![|295](/images/Java-advanced/IMG-xxx.png)    ← 以 | 开头 → 清空
```

脚本生成时始终使用 `![]()` （空 alt text）。

---

## 踩坑记录

| 问题 | 原因 | 解决 |
|------|------|------|
| 图片撑满页面 | Fluid 主题 `min-width: 100%` | CSS `min-width: auto !important` |
| 竖排图被拉宽 | TB 图高瘦但 CSS 撑满宽度 | 统一用 LR 横排 |
| mmdc 8.x 渲染错误 | 不支持菱形+emoji+`<br/>` 组合 | 升级到 mmdc 11.16.0 |
| 同一行两个 `-->` 报错 | Mermaid 每行只允许一条连接 | 拆分到多行 |
| `&#40;` 解析失败 | Obsidian 把 `()` 转义为 HTML 实体 | 脚本自动还原 |
| 图片模糊 | `sips` 缩小了像素 | 只用 CSS 控制显示，保留 `--scale 2` |
| 脚本被 Hexo 自动加载 | `scripts/` 目录是 Hexo 约定 | 脚本放在 `bin/` 目录 |
| 并发渲染崩溃 | 异步 runner 竞态 | 加空值保护 |
| 并发失败后 markdown 残留 | 失败的块未替换 | 逐个手动修复 |
