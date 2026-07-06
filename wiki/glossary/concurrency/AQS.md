---
title: AQS
tags:
  - wiki
  - glossary
  - concurrency
  - aqs
type: glossary
source_series: concurrency
status: seed
---

# AQS（AbstractQueuedSynchronizer）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

AQS 是 Java 并发包里构建同步器的底层框架。它不是一把具体的锁，而是一套解决"线程获取资源失败后如何排队、阻塞、再被正确唤醒"的通用骨架。

## 上下文

AQS 提供三个核心机制：`int state`（同步状态，语义由子类定义）、CLH 风格的双向等待队列（失败线程包装成 Node 入队）、`park/unpark` 阻塞与唤醒（基于 LockSupport）。同步器只需实现 `tryAcquire/tryRelease`（独占）或 `tryAcquireShared/tryReleaseShared`（共享）来定义"什么时候能获取/释放"。

`ReentrantLock`、`Semaphore`、`CountDownLatch`、`ReentrantReadWriteLock` 都基于 AQS——它们各自只定义 state 的含义和获取/释放规则，排队、阻塞、唤醒全部复用 AQS。理解 AQS 后这些同步器会突然变得"像一个家族"。

## 相关术语

- [[wiki/glossary/concurrency/SIGNAL|SIGNAL]] — AQS 队列中前驱节点唤醒后继的关键标记
- [[wiki/glossary/concurrency/Condition|Condition]] — AQS 中的条件队列
- [[wiki/glossary/concurrency/LockSupport|LockSupport]] — AQS 底层使用的 park/unpark

## 深入阅读

- [[wiki/concepts/concurrency/AQS|AQS 概念页（完整版）]]
- [[_posts/concurrency/19-AQS 独占与共享模式如何完成排队与唤醒|19-AQS]]
