---
title: ReentrantLock
tags:
  - wiki
  - glossary
  - concurrency
  - reentrantlock
type: glossary
source_series: concurrency
status: seed
---

# ReentrantLock

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`ReentrantLock` 是基于 AQS 实现的显式互斥锁，支持可重入、公平/非公平模式、`lockInterruptibly()` 中断等锁、以及多 Condition 条件队列。

## 上下文

和 `synchronized` 相比，`ReentrantLock` 多了三个重要能力：`tryLock()`（尝试获取，失败立即返回而不是阻塞）、`lockInterruptibly()`（等锁期间可被中断）、多 `Condition`（一个锁可以有多个条件队列）。代价是需要显式 `lock()` 和 `finally { unlock() }`，不能像 `synchronized` 那样自动释放。

默认是非公平锁（允许新线程插队竞争，吞吐更高）。构造时传 `true` 使用公平锁（尊重排队顺序，降低饥饿风险但吞吐下降）。

## 相关术语

- [[wiki/glossary/concurrency/synchronized|synchronized]] — 内置锁 vs 显式锁
- [[wiki/glossary/concurrency/AQS|AQS]] — ReentrantLock 的底层实现
- [[wiki/glossary/concurrency/Condition|Condition]] — ReentrantLock 的条件队列
- [[wiki/glossary/concurrency/Fair-Lock|公平锁 / 非公平锁]]

## 深入阅读

- [[wiki/concepts/concurrency/ReentrantLock|ReentrantLock 概念页（完整版）]]
- [[_posts/concurrency/09-ReentrantLock 为什么能够实现互斥|09-ReentrantLock]]
