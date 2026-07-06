---
title: 有界队列 / 无界队列
tags:
  - wiki
  - glossary
  - concurrency
  - queue
type: glossary
source_series: concurrency
status: seed
---

# 有界队列 / 无界队列

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

有界队列容量固定——队列满后生产者必须等待或被告知失败，形成反压信号。无界队列容量理论上无限（如 `Integer.MAX_VALUE`）——生产者几乎永远不会被阻塞，但压力被隐藏到内存中。

## 上下文

在任务系统中，有界队列是反压的第一道防线——队列满意味着处理能力不足，必须触发拒绝策略或扩容。无界队列看起来方便，但会隐藏问题直到内存耗尽。线程池中队列选择是调度策略的一部分：无界队列让 `maximumPoolSize` 难以发挥作用，`SynchronousQueue` 让线程池更积极创建新线程。

设计原则：队列容量 ≈ 处理速度 × 可接受等待时间。不是为了无限缓存，而是提供有限缓冲并暴露过载信号。

## 相关术语

- [[wiki/glossary/concurrency/BlockingQueue|BlockingQueue]] — 有界/无界队列的实现
- [[wiki/glossary/concurrency/Rejection-Policy|Rejection Policy]] — 有界队列满后的自保策略
- [[wiki/glossary/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]] — 队列类型决定线程池行为

## 深入阅读

- [[wiki/concepts/concurrency/任务系统|任务系统概念页]]
- [[_posts/concurrency/28-并发任务处理系统如何设计：从任务模型到 Worker 执行|28-任务系统设计]]
