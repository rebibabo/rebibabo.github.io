---
title: Object.wait / notify
tags:
  - wiki
  - glossary
  - concurrency
  - wait-notify
type: glossary
source_series: concurrency
status: seed
---

# Object.wait / notify

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`Object.wait()`、`notify()`、`notifyAll()` 是 Java 内置的线程等待/通知机制。它们必须写在 `synchronized` 块内——调用者必须先持有对象的 Monitor 锁。

## 上下文

`wait()` 让当前线程释放锁并进入 Monitor 的 Wait Set 等待；`notify()` 唤醒 Wait Set 中的一个等待线程，但它不会立即获得锁——要先进入 Entry Set 重新竞争锁。因此 `wait()` 外面必须用 `while` 而不是 `if`：醒来不等于是第一个拿到锁的。

和 `Condition.await/signal` 相比：`wait/notify` 是语言内置机制，每个对象只有一个条件队列；`Condition` 可以为一个锁创建多个条件队列（`notEmpty`、`notFull`），唤醒更精确。

## 相关术语

- [[wiki/glossary/concurrency/Monitor|Monitor]] — wait/notify 的底层实现
- [[wiki/glossary/concurrency/Condition|Condition]] — 更灵活的显式条件队列
- [[wiki/glossary/concurrency/synchronized|synchronized]] — wait/notify 必须在 synchronized 内

## 深入阅读

- [[wiki/concepts/concurrency/对象监视器|Object Monitor 概念页]]
- [[_posts/concurrency/13-Object Monitor 如何实现对象锁与线程等待|13-Object Monitor]]
