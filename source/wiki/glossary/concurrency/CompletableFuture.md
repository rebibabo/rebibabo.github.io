---
title: CompletableFuture
tags:
  - wiki
  - glossary
  - concurrency
  - completablefuture
type: glossary
source_series: concurrency
status: seed
---

# CompletableFuture

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`CompletableFuture` 不是线程池，而是异步任务编排工具。它表达任务之间的依赖、组合和回调关系——上一个任务完成后自动触发下一个任务，组合多个异步结果，处理异常链路。

## 上下文

核心方法链：`supplyAsync()` 异步执行 → `thenApply()` 结果转换 → `thenAccept()` 消费结果 → `thenCombine()` 组合两个结果 → `exceptionally()` 异常处理。如果未显式指定 Executor，默认可能使用 `ForkJoinPool.commonPool()`。

和 Future 的区别：Future 只能 `get()` 等待结果，CompletableFuture 可以链式编排回调。和线程池的关系：CompletableFuture 负责编排异步流程，Executor 负责执行任务——两者职责不同。

## 相关术语

- [[wiki/glossary/concurrency/Future|Future]] — CompletableFuture 的低配版
- [[wiki/glossary/concurrency/ForkJoinPool|ForkJoinPool]] — 默认可能使用 commonPool
- [[wiki/glossary/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]] — 显式指定 Executor 时

## 深入阅读

- [[wiki/concepts/concurrency/CompletableFuture|CompletableFuture 概念页（完整版）]]
- [[_posts/concurrency/16-CompletableFuture 如何编排多个异步任务|16-CompletableFuture]]
