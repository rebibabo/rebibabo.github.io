---
title: Monitor
tags:
  - wiki
  - glossary
  - concurrency
  - monitor
type: glossary
source_series: concurrency
status: seed
---

# Monitor（管程 / 监视器）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

Monitor（管程）是 Java 中每个对象内部维护的一套锁机制。它是 `synchronized` 和 `Object.wait/notify` 的底层实现基础。一个 Monitor 同时只能有一个 Owner 线程。

## 上下文

Java 对象头中的 Mark Word 指向了该对象的 Monitor。Monitor 内部维护：Entry Set（等待获取锁的线程集合）、Wait Set（调用了 `wait()` 后释放锁等待通知的线程集合）、Owner（当前持有锁的线程）。这就是为什么 `wait/notify` 必须在 `synchronized` 块内调用——调用者必须持有对象的 Monitor。

Monitor 机制是理解 AQS 为什么出现的背景：AQS 本质上是用更灵活的方式（CAS + park/unpark + CLH 队列）重新实现了一套"可定制语义的 Monitor"。

## 相关术语

- [[wiki/glossary/concurrency/synchronized|synchronized]] — 基于 Monitor 实现
- [[wiki/glossary/concurrency/Object-Wait-Notify|Object.wait/notify]] — 基于 Monitor 的等待/通知
- [[wiki/glossary/concurrency/AQS|AQS]] — 用更灵活的方式重新实现的 Monitor 式框架

## 深入阅读

- [[wiki/concepts/concurrency/对象监视器|Object Monitor 概念页（完整版）]]
- [[_posts/concurrency/13-Object Monitor 如何实现对象锁与线程等待|13-Object Monitor]]
