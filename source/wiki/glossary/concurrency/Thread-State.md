---
title: Thread State
tags:
  - wiki
  - glossary
  - concurrency
  - thread-state
type: glossary
source_series: concurrency
status: seed
---

# Thread State（线程状态）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

Java 线程有六种状态：NEW（刚创建未启动）、RUNNABLE（正在执行或等待 CPU 调度）、BLOCKED（等待进入 synchronized 临界区）、WAITING（无限期等待 notify/park/join）、TIMED_WAITING（限时等待 sleep/wait(timeout)）、TERMINATED（执行完毕）。

## 上下文

排查时怎么读状态：
- `BLOCKED`：线程在等 `synchronized` 锁——看 `waiting to lock` 和 `locked` 关系排查死锁或锁竞争
- `WAITING (parking)`：通常是 `LockSupport.park()` 或 `Condition.await()`——可能是空闲等待任务队列也可能是等待条件
- `WAITING (on object monitor)`：`Object.wait()`——看谁负责 notify
- `TIMED_WAITING`：`sleep()`、带超时的 `wait/join/park`——可能是正常的定时等待，也可能是超时过短
- `RUNNABLE` 但 CPU 高：可能是死循环、大量计算或活锁

## 相关术语

- [[wiki/glossary/concurrency/死锁|Deadlock]] — BLOCKED 状态是排查死锁的关键
- [[wiki/glossary/concurrency/LockSupport|LockSupport]] — park() 导致 WAITING 状态

## 深入阅读

- [[wiki/concepts/concurrency/死锁活锁与饥饿|死锁、活锁与饥饿]]
- [[_posts/concurrency/27-死锁、活锁与线程饥饿是如何发生的|27-死锁、活锁与线程饥饿]]
