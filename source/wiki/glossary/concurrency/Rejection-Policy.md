---
title: 拒绝策略
tags:
  - wiki
  - glossary
  - concurrency
  - rejection-policy
type: glossary
source_series: concurrency
status: seed
---

# 拒绝策略（Rejection Policy）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

拒绝策略是线程池或任务队列过载时的自保方式。当线程数达到 `maximumPoolSize` 且队列已满，新任务无法接收时，由拒绝策略决定如何处理。

## 上下文

JDK 内置四种策略：**AbortPolicy**（抛 `RejectedExecutionException`，拒绝信号明确）、**CallerRunsPolicy**（提交线程自己执行任务，形成反压减速）、**DiscardPolicy**（静默丢弃，适合日志/监控等允许丢失的场景）、**DiscardOldestPolicy**（丢弃队列中最旧的任务，适合对新任务时效性要求高的场景）。

选择取决于任务类型：核心状态同步不能丢、文件解析可以让用户重试、日志可以采样丢弃。拒绝策略不是一定要选"永不丢弃"——关键是根据任务重要性选择匹配的过载行为。

## 相关术语

- [[wiki/glossary/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]] — 拒绝策略的使用场景
- [[wiki/glossary/concurrency/Bounded-Queue|有界队列]] — 队列满才触发拒绝策略
- [[wiki/glossary/concurrency/Worker-Model|Worker Model]] — 任务系统的过载设计

## 深入阅读

- [[wiki/concepts/concurrency/任务系统|任务系统概念页]]
- [[_posts/concurrency/28-并发任务处理系统如何设计：从任务模型到 Worker 执行|28-任务系统设计]]
