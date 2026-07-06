---
title: volatile
tags:
  - wiki
  - glossary
  - concurrency
  - volatile
type: glossary
source_series: concurrency
status: seed
---

# volatile

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`volatile` 是 Java 中最轻量级的同步机制。它声明的变量保证：一个线程写入后，其他线程立即可见；同时禁止指令重排序，保证写之前的操作不会被重排到写之后。

## 上下文

`volatile` 的两大作用：**可见性**——一个线程写 volatile 变量后，另一个线程读该变量一定能看到最新值；**禁止重排序**——volatile 写之前的所有操作不会被重排序到写之后，读之后的操作不会被重排到读之前。

`volatile` 不能替代 `synchronized` 的地方：它不保证原子性。`count++` 即使 `count` 是 volatile 也不安全——因为读、加、写是三步，volatile 只保证每步看到最新值，不保证三步整体原子。

适合用 `volatile` 的场景：状态标志位（`running = false`）、一次性安全发布（构造完成后发布引用）、独立观察（一个线程写多个线程读）。

## 相关术语

- [[wiki/glossary/concurrency/JMM|JMM]] — volatile 的语义由 JMM 定义
- [[wiki/glossary/concurrency/Happens-Before|Happens-Before]] — volatile 写 Happens-Before 后续读
- [[wiki/glossary/concurrency/内存屏障|Memory Barrier]] — volatile 在硬件层的实现

## 深入阅读

- [[wiki/concepts/concurrency/volatile|volatile 概念页（完整版）]]
- [[_posts/concurrency/07-volatile到底解决了什么问题|07-volatile 到底解决了什么问题]]
