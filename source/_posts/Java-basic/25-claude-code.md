---
title: 'Claude Code 入门：日常对话、Skills 与 Subagents'
date: 2026-05-25
tags:
  - Claude Code
  - AI 工具
  - 开发效率
categories:
  - Java基础
---

## 前言

Claude Code 是 Anthropic 的命令行 AI 编程助手，可以直接在终端里读写项目文件、跑命令、调试报错。这篇文章记录从基本对话到 Skills、Subagents 的常用技巧，作为开发 Mini-SSP 时的工具准备。

<!-- more -->

## 1. 基本使用

### 1.1 启动和退出

```bash
# 在项目根目录启动（重要：在哪个目录启动，Claude 就能访问哪个目录的文件）
cd mini-ssp
claude

# 退出
/exit
# 或 Ctrl+C 两次
```

### 1.2 直接对话

进入交互模式后，直接用自然语言描述需求即可：

```
帮我创建 BidController，包含一个 POST /api/v1/bid 接口
```

```
SlotService 里这个方法报 NullPointerException，帮我看看是什么原因
```

Claude Code 会自动读取相关文件、给出修改建议，并在终端里展示 diff。修改前会询问是否确认（除非配置了自动批准）。

### 1.3 文件引用

用 `@` 引用项目里的文件，让 Claude 直接读取内容，不用自己复制粘贴：

```
@src/main/java/com/example/ssp/service/BidService.java 这个类里的竞价逻辑有什么问题？
```

也可以引用具体行号范围（用 `Cmd+Option+K` / `Ctrl+Alt+K` 快捷插入）：

```
@src/main/java/com/example/ssp/service/BidService.java#L20-45 重构这部分代码
```

---

## 2. 常用内置命令（Slash Commands）

输入 `/` 会弹出自动补全菜单，列出所有可用命令。常用的：

| 命令 | 作用 |
|------|------|
| `/help` | 显示所有可用命令 |
| `/clear` | 清空当前对话历史，开始新会话 |
| `/compact` | 压缩对话历史，释放上下文空间（长会话变慢时用） |
| `/model` | 切换模型（如 Sonnet / Opus） |
| `/init` | 扫描项目，生成 `CLAUDE.md` 项目说明文件 |
| `/agents` | 管理 Subagents |
| `/mcp` | 管理 MCP 服务器连接 |
| `/memory` | 编辑长期记忆文件 |
| `/login` | 登录账号 |

### 2.1 `/init`：让 Claude 了解你的项目

第一次在新项目里用，建议先跑一次：

```
/init
```

它会扫描项目结构、依赖、代码风格，生成一个 `CLAUDE.md` 文件放在项目根目录。之后每次启动 Claude Code，都会自动读取这个文件，了解项目背景，不用每次重新解释"这是一个 Spring Boot 项目，用 MyBatis-Plus..."。

```markdown
# CLAUDE.md 示例内容
## 项目概述
Mini-SSP：程序化广告 SSP 练习项目

## 技术栈
- Java 17, Spring Boot 3.x, Maven
- MyBatis-Plus + MySQL
- Redis 缓存

## 代码规范
- Controller 只做参数校验和调用 Service
- 业务逻辑全部在 Service 层
- 统一用 ApiResponse 包装返回值
```

随着项目推进可以手动补充这个文件，比如加入团队的命名规范、踩过的坑等。

---

## 3. Skills：把重复的指令存成命令

### 3.1 为什么需要 Skills

如果你发现自己经常输入类似的长指令：

```
帮我检查这段代码：1. 是否有空指针风险 2. 是否需要加日志
3. 命名是否符合规范 4. 是否需要写注释
```

每次都重新打一遍很麻烦。Skill 就是把这类指令存成文件，之后用 `/命令名` 一键调用。

### 3.2 创建一个 Skill

在项目根目录创建 `.claude/skills/<名字>/SKILL.md`：

```bash
mkdir -p .claude/skills/review
```

```markdown
<!-- .claude/skills/review/SKILL.md -->
---
name: review
description: 按团队规范审查代码
---

请按以下标准审查当前文件：
1. 是否有空指针风险，是否需要加 Optional 或判空
2. 关键方法是否需要加日志
3. 命名是否符合阿里巴巴 Java 规范
4. 复杂逻辑是否需要注释说明

逐项给出问题和修改建议。
```

之后在对话里：

```
@src/main/java/com/example/ssp/service/BidService.java
/review
```

Claude 就会按这个模板审查代码，不需要每次重新描述要求。

### 3.3 Skill 的作用域

| 位置 | 作用范围 |
|------|---------|
| `.claude/skills/` | 仅当前项目 |
| `~/.claude/skills/` | 所有项目（个人全局） |

团队协作的 Skill 放在项目里（提交到 Git，团队共享）；个人习惯用的 Skill 放在全局目录。

---

## 4. Subagents：专门干一件事的子助手

### 4.1 为什么需要 Subagent

主对话窗口的上下文是共享的——如果你让 Claude 先去翻遍整个代码库找某个 bug，再继续聊别的，前面翻代码的内容会一直占用上下文，拖慢后续对话。

Subagent 是**独立的子任务**，有自己的上下文窗口，做完任务后只把结论汇报给主对话，过程中的细节不会污染主对话。

### 4.2 内置 Subagent

| 类型 | 用途 |
|------|------|
| `Explore` | 只读探索代码库，不会修改文件 |
| `Plan` | 制定计划，不执行 |
| `general-purpose` | 通用任务 |

```
用 Explore agent 帮我找一下项目里所有调用 Redis 的地方，整理成列表
```

Claude 会派出一个 Explore 子任务去搜索代码库，搜索过程中产生的大量中间结果不会进入主对话，最后只返回整理好的列表。

### 4.3 自定义 Subagent

在 `.claude/agents/` 下创建配置文件，可以定义专用的子助手，比如一个专门做 SQL 审查的：

```markdown
<!-- .claude/agents/sql-reviewer.md -->
---
name: sql-reviewer
description: 审查 MyBatis SQL 是否有性能问题
tools: Read, Grep, Glob
---

你是 SQL 性能审查专家。检查 Mapper XML 中的 SQL：
1. 是否有全表扫描风险（缺少索引字段的 WHERE 条件）
2. 是否用了 SELECT *
3. IN 子句是否可能元素过多
4. 是否需要分页但没分页

只读，不要修改文件，给出审查报告即可。
```

`tools: Read, Grep, Glob` 限制这个 Subagent 只能读文件、搜索，不能修改——审查类的 Subagent 建议都设为只读，避免误改代码。

调用：

```
用 sql-reviewer 检查一下 BidLogMapper.xml
```

---

## 5. 实用技巧

### 5.1 后台运行长命令

跑测试、启动服务这类耗时命令，可以让它在后台跑，不阻塞对话：

```
在后台启动 Spring Boot 应用，然后帮我写下一个接口
```

Claude 会用后台模式运行 `mvn spring-boot:run`，运行日志可以随时查看，同时继续对话。

### 5.2 长会话变慢时

对话太长会导致响应变慢、上下文溢出。两种处理方式：

```
/compact   # 压缩历史，保留关键信息
/clear     # 直接清空，开始新会话（CLAUDE.md 仍会被读取）
```

经验：完成一个功能模块后 `/clear`，避免上下文堆积。

### 5.3 让 Claude 自己拆解任务

复杂任务直接让它规划：

```
帮我实现竞价接口的完整链路：接收请求 → 查询广告位 → 并发请求 DSP → 选最高价 → 返回结果
先列出实现步骤，我确认后再开始
```

它会先输出 TODO 列表，确认后逐项实现，过程中可以用 `/todos` 查看当前进度。

### 5.4 文件级精确修改

不想让 Claude 大范围重构时，明确限定范围：

```
只修改 BidService.java 的 processBid 方法，其他文件不要动
```

---

## 6. 小结

| 功能 | 用途 | 存放位置 |
|------|------|---------|
| 对话 + `@文件` | 日常开发主要交互方式 | - |
| `/init` | 生成项目说明，让 Claude 记住项目背景 | `CLAUDE.md` |
| Slash Commands | 内置功能（清空、压缩、切换模型等） | - |
| Skills | 把重复指令存成命令，`/命令名` 调用 | `.claude/skills/` |
| Subagents | 独立子任务，不污染主对话上下文 | `.claude/agents/` |

开发 Mini-SSP 时的建议用法：先 `/init` 让 Claude 了解项目结构，日常用自然语言 + `@文件` 交互，每完成一个模块 `/clear` 一次，代码审查类重复任务可以做成 Skill。

---

> **下一篇预告**：Mini-SSP 实战——用 Claude Code 搭建项目骨架