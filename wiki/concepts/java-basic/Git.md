---
title: Git
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Git

[[wiki/concepts/java-basic/工程实践|返回工程实践]]

## 这一层回答什么问题

> Git 的工作区、暂存区、本地仓库、远程仓库怎么配合？merge 和 rebase 什么时候用哪个？操作错了怎么撤销？

Git 的核心不只是记几条命令——是理解四层模型，才能在任何意外情况下知道数据在哪、怎么找回、怎么撤销。

## 四层模型

```
工作区        →  add  →  暂存区  →  commit  →  本地仓库  →  push  →  远程仓库
(你编辑的文件)           (要提交的)            (.git/)              (GitHub/GitLab)
             ←  restore/checkout ←            ←  pull/fetch ←
```

`git status` 告诉你三层之间的差异。`git diff` 看工作区 vs 暂存区，`git diff --staged` 看暂存区 vs 本地仓库。

## merge vs rebase

**merge**：创建合并提交，保留完整的分支历史。安全，但历史分叉多。

**rebase**：把当前分支的提交"移到"目标分支顶端，历史变成一条直线。干净，但改写了提交 SHA。

**黄金原则**：公共分支用 merge，个人分支用 rebase。**不要 rebase 已经 push 且别人可能已拉取的分支**——否则冲突地狱。

## 撤销三件套

| 场景 | 命令 |
|------|------|
| 改错了还没 add | `git restore <file>` |
| add 了但还没 commit | `git restore --staged <file>` |
| commit 了但还没 push | `git reset --soft HEAD^`（保留改动）|
| push 了 | `git revert <hash>`（安全，不破坏历史） |

**`git reflog` 是最后的安全网**——记录了 HEAD 的每一次移动。即使 `reset --hard` 了，也能靠 reflog 找回。

## 在系列里的位置

post 28。

## 推荐回看原文

- [[_posts/Java-basic/28-git-essentials|28-Git 日常操作实战]]

## 相关概念

- [[wiki/concepts/java-basic/构建工具|构建工具]] — Maven/Gradle + Git = CI/CD 的起点
