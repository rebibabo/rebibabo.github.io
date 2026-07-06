---
title: synchronized
tags:
  - wiki
  - glossary
  - concurrency
  - synchronized
type: glossary
source_series: concurrency
status: seed
---

# synchronized

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`synchronized` 是 Java 内置的互斥锁关键字。它可以修饰方法或代码块，保证同一时刻只有一个线程能进入该同步区域。

## 上下文

`synchronized` 的实现基于对象头中的 Monitor（管程）。JDK 1.6 之后做了大量优化：偏向锁（无竞争时直接使用，不 CAS）、轻量级锁（CAS 竞争，自旋）、重量级锁（挂起线程）。这个过程称为锁升级——从低开销逐步升级到高开销，不可逆降级。

和 `ReentrantLock` 对比：`synchronized` 是语言级内置机制，语法简洁，JVM 自动优化；但缺少 `tryLock()`、`lockInterruptibly()`、多 Condition 等灵活能力。

## 相关术语

- [[wiki/glossary/concurrency/Monitor|Monitor]] — synchronized 的底层实现
- [[wiki/glossary/concurrency/Lock-Upgrade|锁升级]] — 偏向→轻量→重量的升级过程
- [[wiki/glossary/concurrency/ReentrantLock|ReentrantLock]] — 功能更丰富的显式锁

## 深入阅读

- [[wiki/concepts/concurrency/synchronized|synchronized 概念页（完整版）]]
- [[_posts/concurrency/03-synchronized为什么能够保证线程安全|03-synchronized]]
