---
title: ForkJoinPool
tags:
  - wiki
  - glossary
  - concurrency
  - forkjoinpool
type: glossary
source_series: concurrency
status: seed
---

# ForkJoinPool

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`ForkJoinPool` 是面向递归拆分任务的分治型线程池。每个 Worker 有自己的本地双端队列，当前 Worker 拆出的子任务放本地队列，优先处理本地任务，空闲时从其他 Worker 队列偷任务——这就是工作窃取。

## 上下文

核心使用模式：`left.fork()` 把左任务放入本地队列（可被窃取），`right.compute()` 当前 Worker 继续执行右任务，`left.join()` 需要结果时再获取。`join()` 不是简单阻塞——任务没被偷走就自己执行，被偷走但没执行完就帮其他 Worker 推进任务。

适用场景：可递归拆分、主要消耗 CPU、子任务间尽量少共享状态。不适用：大量阻塞 I/O（Worker 被卡住无法窃取）、任务粒度太小（调度成本超过计算收益）。注意 `commonPool()` 是 JVM 全局共享的，`parallelStream()` 和 `CompletableFuture` 默认可能使用它，阻塞任务会拖慢公共池。

## 相关术语

- [[wiki/glossary/concurrency/Work-Stealing|Work-Stealing]] — ForkJoinPool 的核心调度策略
- [[wiki/glossary/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]] — 通用任务型线程池

## 深入阅读

- [[wiki/concepts/concurrency/ForkJoinPool|ForkJoinPool 概念页（完整版）]]
- [[_posts/concurrency/26-ForkJoinPool 如何通过工作窃取执行任务|26-ForkJoinPool]]
