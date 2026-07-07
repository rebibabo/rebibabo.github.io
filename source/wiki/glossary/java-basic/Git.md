---
title: Git
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Git

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Git 是一种分布式版本控制系统，追踪文件变更并支持多人协作，代码在提交过程中依次经过工作区（Working Directory）、暂存区（Staging Area）、本地仓库（Local Repository）和远程仓库（Remote Repository）四个区域。

## 上下文

理解"三个区域"是使用 Git 的关键：工作区是你编辑文件的地方，`git add` 将改动放入暂存区（精确挑选本次提交包含哪些文件），`git commit` 将暂存区内容写入本地仓库，`git push` 同步到远程仓库。核心操作包括：分支管理（`git switch -c` 创建并切换）、合并（fast-forward 快进 vs merge commit 产生汇合节点）、冲突解决（手动编辑冲突标记后 `git add` + `git commit`）、撤销（未 add 用 `restore`，未 push 用 `reset --soft/mixed/hard`，已 push 用 `revert`）。rebase vs merge 的金原则：自己的、还没分享出去的历史可以 rebase 整理成直线；已经分享给别人的历史用 merge，别 rebase。`git reflog` 是误操作后的救命命令，记录了 HEAD 曾经指向过的每一个位置。

## 相关术语

- [[wiki/glossary/java-basic/Maven|Maven]] — Java 项目构建与依赖管理工具，常与 Git 配合管理项目版本
- [[wiki/glossary/java-basic/Gradle|Gradle]] — 新一代 Java 构建工具，替代 Maven 的现代选择

## 深入阅读

- [[_posts/Java-basic/28-git-essentials|java-basics(番外) Git 日常操作实战：从提交到协作全流程]]
