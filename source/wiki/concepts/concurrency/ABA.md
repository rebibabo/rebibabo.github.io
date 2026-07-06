---
title: ABA
tags:
  - wiki
  - concept
  - concurrency
  - aba
type: concept
source_series: concurrency
status: seed
---

# ABA

[[wiki/concepts/concurrency/CAS|返回 CAS]]

## 定义

`ABA` 问题描述的是：

> 一个位置的值从 A 变成 B，又变回 A，CAS 看起来像"没变过"，但语义上其实已经发生过变化。

## 它解决什么问题

它提醒我们：

- CAS 只比较当前值
- 但某些场景真正关心的是"中间是否发生过变化"

## 为什么它重要

它是 CAS 体系里最经典的边界问题之一。CAS 能保证原子比较替换，不等于它天然能表达完整历史。

## 经典场景：无锁栈的 ABA 陷阱

初始结构：`head → A → B → C`

线程 1 想弹出 A，读到 `oldHead = A, next = B`。在执行 CAS 之前，线程 2 插入执行：`pop A → pop B → push A`。此时结构变成 `head → A → C`——`head` 又回到 A，但 A 后面已经不是 B。

线程 1 继续执行 `CAS(head, A, B)`，CAS 成功（因为 `head` 确实还是 A），结果变成 `head → B → C`。问题是 B 已经被线程 2 弹出，却被线程 1 基于旧的 `next = B` 重新接回栈中。危险的不是 A 回来了本身，而是线程 1 基于旧结构做了决策，CAS 只检查了 head 是否还是 A，没有检查 A 后面的结构是否仍然有效。

## 解决思路：版本号

把比较对象从单个值升级成"值 + 版本"：

```
(A, 1) → (B, 2) → (A, 3)
```

虽然值又回到 A，但版本号已变化。Java 中对应工具是 `AtomicStampedReference<T>`：

```java
AtomicStampedReference<Node> head =
    new AtomicStampedReference<>(nodeA, 1);
head.compareAndSet(oldNode, newNode, oldStamp, oldStamp + 1);
```

它比较的不只是引用，还包括 stamp。这样就能识别"值虽然相同，但中间已经变化过"的情况。

## 和乐观读的共通思想

| 思路 | 检查时机 | 检查内容 |
|---|---|---|
| CAS | 写入时检查 | 当前值是否仍然等于旧值 |
| 乐观读 | 读取后检查 | 读取期间版本是否变化 |
| 版本号/ABA | 写入时检查 | 当前值+版本是否仍然匹配 |

三者都是同一类乐观思想：先假设无事发生，最后再校验。

## 在系列里的位置

它位于无锁设计线条里，是从"CAS 能工作"走向"CAS 有什么盲区"的关键节点。

## 推荐回看原文

- [[_posts/concurrency/21-无锁设计、ABA 与 LongAdder|21-无锁设计、ABA 与 LongAdder]]
- [[_posts/concurrency/05-CAS为什么能够在不加锁的情况下更新共享数据|05-CAS 为什么能够在不加锁的情况下更新共享数据]]

## 相关概念

- [[wiki/concepts/concurrency/CAS|CAS]]
- [[wiki/concepts/concurrency/LongAdder|LongAdder]]
- [[wiki/concepts/concurrency/StampedLock|StampedLock]]
