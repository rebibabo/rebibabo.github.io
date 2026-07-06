---
title: StampedLock
tags:
  - wiki
  - glossary
  - concurrency
  - stampedlock
type: glossary
source_series: concurrency
status: seed
---

# StampedLock

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`StampedLock` 是比读写锁更激进的凭证式锁，提供三种模式：写锁、悲观读锁、乐观读。主打乐观读——先假设没有写线程干扰，不加锁读取后再用 `stamp` 校验。

## 上下文

乐观读的正确模式：`tryOptimisticRead()` 获取 stamp → 把共享字段复制到局部变量 → `validate(stamp)` 校验 → 成功则用局部变量，失败退化到悲观读锁。关键约束是校验成功后只能使用已复制的局部变量，不能重新读取共享字段。

和 `ReentrantReadWriteLock` 的核心区别：`StampedLock` 不可重入、不支持 Condition、通过 stamp 凭证而非 AQS state 编码状态。适合读极多写极少且读逻辑能清晰写成"快照+校验"的场景。

## 相关术语

- [[wiki/glossary/concurrency/ReentrantReadWriteLock|ReentrantReadWriteLock]] — 更传统的读写锁
- [[wiki/glossary/concurrency/CAS|CAS]] — 乐观读和 CAS 是同一类乐观思想

## 深入阅读

- [[wiki/concepts/concurrency/StampedLock|StampedLock 概念页（完整版）]]
- [[_posts/concurrency/20-ReentrantReadWriteLock 与 StampedLock|20-ReentrantReadWriteLock 与 StampedLock]]
