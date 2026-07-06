---
title: Work-Stealing
tags:
  - wiki
  - glossary
  - concurrency
  - work-stealing
type: glossary
source_series: concurrency
status: seed
---

# Work-Stealing（工作窃取）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

Work-Stealing 是 ForkJoinPool 的核心调度策略：Worker 优先执行自己本地队列中的任务（LIFO 从 top 端 pop）；空闲 Worker 从其他 Worker 本地队列的 base 端偷任务执行（FIFO）。

## 上下文

双端操作的设计意图：当前 Worker 从 top 端操作保持局部性（最近产生的任务离 CPU Cache 更近），窃取者从 base 端偷到较早的大粒度任务（可继续拆分产生新的本地工作量）。两端操作也减少了队列拥有者和窃取者之间的竞争。

和普通线程池的区别：普通线程池是所有线程竞争同一个共享队列，工作窃取让竞争分散到每个 Worker 的本地队列。这让递归拆分的任务更容易实现负载均衡。

## 相关术语

- [[wiki/glossary/concurrency/ForkJoinPool|ForkJoinPool]] — 使用工作窃取策略的线程池
- [[wiki/glossary/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]] — 不使用工作窃取的通用线程池

## 深入阅读

- [[wiki/concepts/concurrency/ForkJoinPool|ForkJoinPool 概念页]]
- [[_posts/concurrency/26-ForkJoinPool 如何通过工作窃取执行任务|26-ForkJoinPool]]
