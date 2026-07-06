---
title: LockSupport
tags:
  - wiki
  - glossary
  - concurrency
  - locksupport
type: glossary
source_series: concurrency
status: seed
---

# LockSupport

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`LockSupport` 是 Java 并发包中最底层的线程阻塞与唤醒工具。提供两个基础原语：`park()` 让当前线程暂停，`unpark(thread)` 唤醒指定线程。AQS、Condition、FutureTask 的底层阻塞都依赖它。

## 上下文

每个线程关联一个最多为 1 的 permit（许可证）。`park()` 尝试获取 permit，没有则阻塞；`unpark(thread)` 发放 permit，如果线程正在 park 中则唤醒。

关键特性：`unpark()` 可以先于 `park()` 发生（permit 提前留存）——和 `wait/notify` 不同，wait 必须在 notify 之前。permit 不累加——多次 unpark 也只保留一个。`park()` 遇到中断会返回但不抛异常也不清除中断标记。

职责分离：LockSupport 只负责线程如何停、如何醒；条件判断和排队顺序由上层（AQS、锁、同步器）负责。

## 相关术语

- [[wiki/glossary/concurrency/AQS|AQS]] — AQS 基于 LockSupport 实现队列的阻塞唤醒
- [[wiki/glossary/concurrency/Object-Wait-Notify|Object.wait/notify]] — 更上层但更受限的等待机制
- [[wiki/glossary/concurrency/线程中断|线程中断]] — 中断也会让 park() 返回

## 深入阅读

- [[wiki/concepts/concurrency/LockSupport|LockSupport 概念页（完整版）]]
- [[_posts/concurrency/25-LockSupport 如何挂起和唤醒线程|25-LockSupport]]
