---
title: BlockingQueue
tags:
  - wiki
  - glossary
  - concurrency
  - blockingqueue
type: glossary
source_series: concurrency
status: seed
---

# BlockingQueue

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`BlockingQueue` 是带等待语义的线程安全队列。普通队列只回答元素如何进出，BlockingQueue 额外回答队列空或满时线程应该怎么办——阻塞等待、超时等待、抛异常或返回特殊值。

## 上下文

线程池的任务队列就是 BlockingQueue——队列类型决定任务的调度倾向。主要实现：`ArrayBlockingQueue`（固定数组+单锁，容量明确）、`LinkedBlockingQueue`（链表+双锁，并发度更高，默认近似无界需指定容量）、`SynchronousQueue`（不缓存元素，直接交接）、`PriorityBlockingQueue`（按优先级出队，无界）、`DelayQueue`（按到期时间出队，队列非空也可能阻塞）。

注意：线程池提交用 `offer()` 而非 `put()`——满了返回 false 而非阻塞，触发线程池扩容或拒绝策略。

## 相关术语

- [[wiki/glossary/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]] — BlockingQueue 是线程池的任务队列
- [[wiki/glossary/concurrency/Condition|Condition]] — 内部用 Condition 管理空满等待
- [[wiki/glossary/concurrency/Bounded-Queue|有界/无界队列]] — 容量设计决定系统边界

## 深入阅读

- [[wiki/concepts/concurrency/BlockingQueue|BlockingQueue 概念页（完整版）]]
- [[_posts/concurrency/23-BlockingQueue 如何协调生产者和消费者|23-BlockingQueue]]
