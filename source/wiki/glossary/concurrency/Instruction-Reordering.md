---
title: 指令重排序
tags:
  - wiki
  - glossary
  - concurrency
  - reordering
type: glossary
source_series: concurrency
status: seed
---

# 指令重排序（Instruction Reordering）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

指令重排序是 CPU 和 JIT 编译器为优化执行效率，在不改变单线程执行结果的前提下，调整指令的实际执行顺序。在单线程下安全，但在多线程下可能暴露中间状态。

## 上下文

经典例子是单例的 DCL（Double-Checked Locking）：`instance = new Singleton()` 在底层可能是"分配内存 → 初始化对象 → 赋值引用"，但 CPU 可能重排成"分配内存 → 赋值引用 → 初始化对象"。如果另一个线程在引用已赋值但对象未初始化时读取，就会看到半成品对象。

`volatile` 可以禁止这种重排——volatile 写之前的所有操作不会被重排到写之后。这就是为什么 DCL 单例中的 `instance` 必须声明为 `volatile`。

## 相关术语

- [[wiki/glossary/concurrency/volatile|volatile]] — volatile 禁止指令重排序
- [[wiki/glossary/concurrency/内存屏障|Memory Barrier]] — 硬件层禁止重排序的机制
- [[wiki/glossary/concurrency/JMM|JMM]] — JMM 定义了哪些情况下不允许重排序

## 深入阅读

- [[wiki/concepts/concurrency/volatile|volatile 概念页]]
- [[_posts/concurrency/07-volatile到底解决了什么问题|07-volatile 到底解决了什么问题]]
