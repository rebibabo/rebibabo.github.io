---
title: Condition
tags:
  - wiki
  - glossary
  - concurrency
  - condition
type: glossary
source_series: concurrency
status: seed
---

# Condition

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`Condition` 是显式锁（`ReentrantLock`）的条件队列接口，功能等价于 `Object.wait/notify`，但更灵活：一个锁可以有多个 Condition（如 `notEmpty` 和 `notFull`），每个 Condition 管理一类等待条件。

## 上下文

`await()` 让线程从"持锁执行"进入"条件等待"——先进入 Condition 条件队列，再释放锁，让其他线程有机会修改条件。`signal()` 只负责把等待节点从条件队列转移回 AQS 同步队列——被转移的线程还要重新竞争锁，拿到了才能从 `await()` 返回。

因此 `await()` 外面必须用 `while` 而不是 `if`：线程返回只能说明重新拿到了锁，不能说明条件仍然满足。`signal()` 和 `signalAll()` 的区别：前者转移一个节点，后者转移全部。

## 相关术语

- [[wiki/glossary/concurrency/ReentrantLock|ReentrantLock]] — Condition 必须配合 ReentrantLock 使用
- [[wiki/glossary/concurrency/AQS|AQS]] — Condition 条件队列和 AQS 同步队列的关系
- [[wiki/glossary/concurrency/Object-Wait-Notify|Object.wait/notify]] — 内置条件机制的对应

## 深入阅读

- [[wiki/concepts/concurrency/Condition|Condition 概念页（完整版）]]
- [[_posts/concurrency/10-Condition 如何实现线程等待与通知|10-Condition]]
