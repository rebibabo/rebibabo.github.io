---
title: 公平锁 / 非公平锁
tags:
  - wiki
  - glossary
  - concurrency
  - fair-lock
type: glossary
source_series: concurrency
status: seed
---

# 公平锁 / 非公平锁

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

公平锁和非公平锁没有改变 AQS 同步队列本身，区别只发生在新线程刚来抢锁时：公平锁先检查队列前面是否已有等待者，有则排队；非公平锁允许新线程直接 CAS 抢一次，抢不到再排队。

## 上下文

公平锁的核心逻辑在 `hasQueuedPredecessors()`：如果当前线程前面已有等待者，放弃直接竞争，进入同步队列。非公平锁则先执行 `compareAndSetState(0, 1)`——只要刚好看到 state==0 并 CAS 成功，就可以直接获取锁。

| 选择 | 优点 | 代价 |
| --- | --- | --- |
| 非公平锁 | 吞吐量通常更好 | 个别线程可能等待较久 |
| 公平锁 | 等待顺序更稳定 | 调度成本更高，吞吐量可能下降 |

`ReentrantLock` 默认非公平锁。当业务特别关心等待顺序或饥饿风险时，用公平锁。`ReentrantReadWriteLock` 也支持公平/非公平选择。

## 相关术语

- [[wiki/glossary/concurrency/ReentrantLock|ReentrantLock]] — 可通过构造参数选择公平/非公平
- [[wiki/glossary/concurrency/AQS|AQS]] — 公平/非公平差在 tryAcquire 实现
- [[wiki/glossary/concurrency/线程饥饿|Thread Starvation]] — 非公平锁可能导致饥饿

## 深入阅读

- [[wiki/concepts/concurrency/ReentrantLock|ReentrantLock 概念页]]
- [[_posts/concurrency/19-AQS 独占与共享模式如何完成排队与唤醒|19-AQS]]
