---
title: SIGNAL
tags:
  - wiki
  - glossary
  - concurrency
  - signal
type: glossary
source_series: concurrency
status: seed
---

# SIGNAL

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

SIGNAL 是 AQS 中 Node 的状态常量（`waitStatus = -1`），含义是：当前节点的后继节点已经（或即将）被阻塞，当当前节点释放或取消时，有责任唤醒后继。

## 上下文

SIGNAL 是标在前驱节点上的，不是标在当前节点自己身上。一个线程在 `park()` 前，必须先尝试把前驱节点的状态改成 SIGNAL，意思是"我要睡了，你释放时记得叫醒我"。

三种情况的处理：前驱已经是 SIGNAL → 安全 park；前驱是 0 → 先 CAS 改成 SIGNAL，本轮不睡回到循环重新判断；前驱 > 0（CANCELLED）→ 跳过取消节点，重新接到有效前驱后面。这个机制保证了 AQS 等待队列中不会有线程睡下去后没人唤醒。

## 相关术语

- [[wiki/glossary/concurrency/AQS|AQS]] — SIGNAL 是 AQS 唤醒链的核心机制
- [[wiki/glossary/concurrency/LockSupport|LockSupport]] — SIGNAL 建立后才调用 park()
- [[wiki/glossary/concurrency/Condition|Condition]] — 条件队列用不同的等待语义

## 深入阅读

- [[wiki/concepts/concurrency/AQS|AQS 概念页]]
- [[_posts/concurrency/19-AQS 独占与共享模式如何完成排队与唤醒|19-AQS]]
