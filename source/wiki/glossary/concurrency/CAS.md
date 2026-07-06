---
title: CAS
tags:
  - wiki
  - glossary
  - concurrency
  - cas
type: glossary
source_series: concurrency
status: seed
---

# CAS（Compare-And-Set / Compare-And-Swap）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

CAS 是无锁并发的基础原子操作。它的语义是：修改共享变量前，先确认它还是不是我之前看到的旧值——如果是就替换成新值，如果不是说明期间已被人改过、本次更新失败。"比较旧值"和"替换新值"在底层是一个不可分割的 CPU 原子指令。

## 上下文

CAS 是 `AtomicInteger`、`AtomicReference`、`LongAdder`、`ConcurrentHashMap` 的无锁插入等所有乐观更新的底层原语。典型的 CAS 使用模式是循环重试：读当前值 → 计算新值 → CAS 提交 → 失败则重新读、重新算、重新提交。

CAS 适合可以重试的短操作（计数器累加、状态位切换、引用替换），但不适合复杂逻辑——竞争激烈时大量线程失败重试会形成 CPU 空转浪费。

## 相关术语

- [[wiki/glossary/concurrency/ABA|ABA]] — CAS 只能判断值相同，不能判断中间是否变化过
- [[wiki/glossary/concurrency/AtomicLong|AtomicLong]] — 基于 CAS 的原子变量
- [[wiki/glossary/concurrency/LongAdder|LongAdder]] — 分散 CAS 竞争的高并发累加器

## 深入阅读

- [[wiki/concepts/concurrency/CAS|CAS 概念页（完整版）]]
- [[_posts/concurrency/05-CAS为什么能够在不加锁的情况下更新共享数据|05-CAS]]
