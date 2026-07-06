---
title: AtomicLong
tags:
  - wiki
  - glossary
  - concurrency
  - atomiclong
type: glossary
source_series: concurrency
status: seed
---

# AtomicLong / AtomicInteger

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`AtomicLong` 和 `AtomicInteger` 是基于 CAS 的原子变量。提供 `get()`、`set()`、`compareAndSet()`、`getAndIncrement()` 等方法，每次调用都是原子操作，不需要加锁。

## 上下文

和普通 `long count++` 的区别：`count++` 分读-加-写三步，多线程下不是原子的。`AtomicLong.getAndIncrement()` 将这三步合并为一个不可分割的 CAS 操作。但如果多个线程同时竞争同一个变量，CAS 失败的线程会重试——竞争激烈时 CPU 空转会很高。

高竞争统计场景可以考虑 `LongAdder`（分散竞争，但其 `sum()` 不是强一致快照）。需要强一致（如余额、库存）的场景适合 `AtomicLong`。

## 相关术语

- [[wiki/glossary/concurrency/CAS|CAS]] — AtomicLong 的底层实现
- [[wiki/glossary/concurrency/LongAdder|LongAdder]] — 高并发统计场景的替代方案
- [[wiki/glossary/concurrency/ABA|ABA]] — 基于 CAS 的边界问题

## 深入阅读

- [[wiki/concepts/concurrency/CAS|CAS 概念页]]
- [[_posts/concurrency/05-CAS为什么能够在不加锁的情况下更新共享数据|05-CAS]]
