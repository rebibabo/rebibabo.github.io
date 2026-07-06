---
title: FutureTask
tags:
  - wiki
  - glossary
  - concurrency
  - futuretask
type: glossary
source_series: concurrency
status: seed
---

# FutureTask

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`FutureTask` 是 `Future` 和 `Runnable` 的结合体——既可以作为 Runnable 提交给线程池执行，又可以通过 Future 接口获取结果、取消任务。

## 上下文

FutureTask 用 CAS 管理状态：NEW → COMPLETING → NORMAL（正常完成）/ EXCEPTIONAL（异常）/ CANCELLED（取消）/ INTERRUPTED（中断）。`get()` 阻塞时线程进入等待链表，任务完成后唤醒所有等待者。

和 `CompletableFuture` 的不同：FutureTask 是"执行 + 结果"一体，偏向直接执行某个任务；CompletableFuture 是"编排 + 结果"，偏向表达任务之间的依赖和组合关系。

## 相关术语

- [[wiki/glossary/concurrency/Future|Future]] — FutureTask 实现了 Future 接口
- [[wiki/glossary/concurrency/CompletableFuture|CompletableFuture]] — 更强大的异步编排替代
- [[wiki/glossary/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]] — 执行 FutureTask

## 深入阅读

- [[wiki/concepts/concurrency/FutureTask|FutureTask 概念页（完整版）]]
- [[_posts/concurrency/15-Future 如何获取异步任务的执行结果|15-Future]]
