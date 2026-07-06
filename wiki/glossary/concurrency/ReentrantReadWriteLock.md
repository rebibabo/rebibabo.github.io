---
title: ReentrantReadWriteLock
tags:
  - wiki
  - glossary
  - concurrency
  - reentrantreadwritelock
type: glossary
source_series: concurrency
status: seed
---

# ReentrantReadWriteLock

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`ReentrantReadWriteLock` 是支持读读并发的读写锁。读操作可共享（多个读线程同时持有），写操作独占（读写互斥、写写互斥）。写锁可重入且支持锁降级。

## 上下文

读写锁的核心价值：如果大部分时间都在读数据，让读线程之间不互斥可以大幅提升并发吞吐。底层通过将 AQS 的 `int state` 拆分成高 16 位（读锁总数）和低 16 位（写锁重入次数），用同一个状态值编码两类信息。

锁降级：线程持写锁 → 先获取读锁 → 再释放写锁，平滑从"独占写"过渡到"共享读"。关键顺序是先拿读锁再放写锁——避免中间无锁空档被其他写线程插入。

## 相关术语

- [[wiki/glossary/concurrency/StampedLock|StampedLock]] — 比 ReentrantReadWriteLock 更激进，支持乐观读
- [[wiki/glossary/concurrency/ReentrantLock|ReentrantLock]] — 普通互斥锁
- [[wiki/glossary/concurrency/AQS|AQS]] — 底层框架，共享模式和独占模式的组合应用

## 深入阅读

- [[wiki/concepts/concurrency/ReentrantReadWriteLock|ReentrantReadWriteLock 概念页（完整版）]]
- [[_posts/concurrency/20-ReentrantReadWriteLock 与 StampedLock|20-ReentrantReadWriteLock]]
