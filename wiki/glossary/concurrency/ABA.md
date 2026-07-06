---
title: ABA
tags:
  - wiki
  - glossary
  - concurrency
  - aba
type: glossary
source_series: concurrency
status: seed
---

# ABA 问题

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

ABA 是 CAS 的经典边界问题：一个位置的值从 A 变成 B 又变回 A，CAS 只看到"还是 A"就允许更新，却没有察觉中间发生过变化。危险的是操作基于旧结构做了决策，而 CAS 没有检查结构是否仍然有效。

## 上下文

经典场景在无锁栈中：线程 1 准备 pop A（记录 next=B），线程 2 抢先 pop A → pop B → push A。线程 1 的 CAS 仍然成功（head 还是 A），但 B 已经被弹出却被重新接入栈中。

解决思路：将比较对象从单个值升级为"值 + 版本号"。`(A,1) → (B,2) → (A,3)`，版本号变化让 CAS 能够识别中间变化。Java 对应工具是 `AtomicStampedReference<T>`。

## 相关术语

- [[wiki/glossary/concurrency/CAS|CAS]] — ABA 是 CAS 的边界
- [[wiki/glossary/concurrency/StampedLock|StampedLock]] — 类似的版本号/乐观校验思想

## 深入阅读

- [[wiki/concepts/concurrency/ABA|ABA 概念页（完整版）]]
- [[_posts/concurrency/21-无锁设计、ABA 与 LongAdder|21-ABA]]
