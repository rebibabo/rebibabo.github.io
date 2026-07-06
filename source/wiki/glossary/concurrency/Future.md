---
title: Future
tags:
  - wiki
  - glossary
  - concurrency
  - future
type: glossary
source_series: concurrency
status: seed
---

# Future / FutureTask

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`Future` 是表示异步计算结果的句柄接口。提交任务后立即返回 Future，后续可以通过 `get()` 等待结果、`cancel()` 取消任务、`isDone()` 检查是否完成。`FutureTask` 是同时实现了 `Runnable` 和 `Future` 的具体类。

## 上下文

`Future.get()` 有两个版本：无参版本无限等待，带超时版本最多等指定时间后抛 `TimeoutException`。`cancel(true)` 尝试中断执行线程，但不保证任务一定停止——取决于任务代码是否响应中断。

`FutureTask` 内部用 AQS 或类似的 CAS 机制记录任务状态流转：NEW → COMPLETING → NORMAL/EXCEPTIONAL/CANCELLED/INTERRUPTED。`get()` 线程通过阻塞等待状态完成，完成时被唤醒返回结果。

局限性：多个 Future 之间有依赖关系时，手动编排会比较麻烦——这是 `CompletableFuture` 要解决的问题。

## 相关术语

- [[wiki/glossary/concurrency/CompletableFuture|CompletableFuture]] — 更强大的异步编排工具
- [[wiki/glossary/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]] — submit() 返回 Future
- [[wiki/glossary/concurrency/线程中断|线程中断]] — Future.cancel(true) 的基础

## 深入阅读

- [[wiki/concepts/concurrency/Future|Future 概念页]]
- [[wiki/concepts/concurrency/FutureTask|FutureTask 概念页]]
- [[_posts/concurrency/15-Future 如何获取异步任务的执行结果|15-Future]]
