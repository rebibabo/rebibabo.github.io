---
title: StampedLock
tags:
  - wiki
  - concept
  - concurrency
  - stampedlock
type: concept
source_series: concurrency
status: seed
---

# StampedLock

[[wiki/concepts/concurrency/并发容器|返回并发容器与数据结构]]

## 定义

`StampedLock` 是一种面向读多写少场景的高级锁，提供写锁、悲观读锁和乐观读三种模式。

## 它解决什么问题

它回答的是：

> 如果读线程大多数时候只是快速查看数据，能不能先便宜地读，只有发现冲突时再回退？

`ReentrantReadWriteLock` 已经允许多个读线程并发，但读线程仍然需要真正加锁（修改读锁计数）。对于读多写少且读操作很短的场景，这部分同步成本可能变得明显。

## 为什么它重要

它比普通读写锁更激进，因为它把"乐观读"这种策略直接做成了标准模型。这让我们能更清楚看到：锁不只有"加或不加"两种形态，一致性和吞吐量之间可以继续细调。

## 三种模式

| 模式 | 方法 | 是否真正加锁 | 典型用途 |
| --- | --- | --- | --- |
| 写锁 | `writeLock()` | 是 | 修改共享数据 |
| 悲观读锁 | `readLock()` | 是 | 稳定读取，阻止写线程 |
| 乐观读 | `tryOptimisticRead()` | 否 | 先读取局部快照，再校验中途有没有写 |

## stamp：状态版本凭证

`StampedLock` 的方法返回 `long` 类型的 `stamp`——可以粗略理解成"版本时间戳"，但不是物理时间，而是锁状态的版本凭证。不同来源的 `stamp` 有不同用途：

| 来源 | stamp 的作用 |
| --- | --- |
| `tryOptimisticRead()` | 用于后续 `validate(stamp)` 校验 |
| `readLock()` | 作为读锁凭证，用于释放读锁 |
| `writeLock()` | 作为写锁凭证，用于释放写锁 |

## 乐观读的正确写法

乐观读的核心原则：**先拿 stamp → 复制共享字段到局部变量 → 再 validate**。校验成功后只能使用已复制出来的局部变量。

```java
double distanceFromOrigin() {
    long stamp = lock.tryOptimisticRead();
    double currentX = x;
    double currentY = y;
    if (!lock.validate(stamp)) {
        // 退回悲观读锁重新读取
        stamp = lock.readLock();
        try {
            currentX = x;
            currentY = y;
        } finally {
            lock.unlockRead(stamp);
        }
    }
    return Math.sqrt(currentX * currentX + currentY * currentY);
}
```

常见错误写法：先 `validate()` 再读取共享字段——`validate()` 通过后写线程仍可能立刻修改共享字段。另一个错误：复制了局部变量也完成了校验，但最后又重新访问共享字段。

## 它和 ReentrantReadWriteLock 的关键区别

| 维度 | `ReentrantReadWriteLock` | `StampedLock` |
| --- | --- | --- |
| 可重入 | 支持（写锁可重入） | 不可重入 |
| `Condition` | 写锁支持 | 不支持 |
| 乐观读 | 不支持 | 支持 |
| 实现风格 | 围绕 AQS state 和重入计数 | 围绕 stamp 凭证 |
| 代码复杂度 | 较低，符合常见锁模型 | 较高，需要正确管理 stamp |

`StampedLock` 不可重入——不要在同一线程里对已持有写锁的状态再次调用 `writeLock()`。需要锁模式转换时使用 `tryConvertToWriteLock(stamp)` 等非阻塞转换方法。

## 两者如何选择

| 场景 | 更适合 |
| --- | --- |
| 需要可重入 | `ReentrantReadWriteLock` |
| 需要 `Condition` | `ReentrantReadWriteLock` 的写锁 |
| 希望代码简单、稳定、易维护 | `ReentrantReadWriteLock` |
| 读很多、写很少，且读操作短小 | `StampedLock` 乐观读 |
| 读取的是一组相关字段的快照 | `StampedLock` 乐观读 |
| 读取过程较长或逻辑复杂 | 悲观读锁 |

实际选择：先考虑 `ReentrantReadWriteLock`；只有当读操作非常频繁、写操作很少，且读逻辑能清晰写成"复制局部快照 + validate 校验"时，再考虑 `StampedLock`。

## 在系列里的位置

它是读写锁这条线上的进阶节点，也和无锁、快照、乐观校验这些思想有相通之处。

## 推荐回看原文

- [[_posts/concurrency/20-ReentrantReadWriteLock 与 StampedLock|20-ReentrantReadWriteLock 与 StampedLock]]
- [[_posts/concurrency/21-无锁设计、ABA 与 LongAdder|21-无锁设计、ABA 与 LongAdder]]

## 相关概念

- [[wiki/concepts/concurrency/ReentrantReadWriteLock|ReentrantReadWriteLock]]
- [[wiki/concepts/concurrency/LongAdder|LongAdder]]
- [[wiki/concepts/concurrency/CAS|CAS]]
- [[wiki/concepts/concurrency/ABA|ABA]]
- [[wiki/concepts/concurrency/并发容器|并发容器与数据结构]]
