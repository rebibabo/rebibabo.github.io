---
title: LongAdder
tags:
  - wiki
  - concept
  - concurrency
  - longadder
type: concept
source_series: concurrency
status: seed
---

# LongAdder

[[wiki/concepts/concurrency/并发容器|返回并发容器与数据结构]]

## 定义

`LongAdder` 是一种通过分散热点竞争来提高高并发累加吞吐量的计数器。它把单点 CAS 拆成多个 Cell 上的分散 CAS。

## 它解决什么问题

它回答的是：

> 如果很多线程都在争抢同一个计数器位置，单个 CAS 热点扛不住了，怎么办？

`AtomicLong` 的模型是所有线程 CAS 同一个 `value`——多个核心同时修改同一个变量时，变量所在的 cache line 会在不同核心之间反复失效和转移。`LongAdder` 的思路是把一个热点拆成多个槽：

```
Thread A → cell[0]
Thread B → cell[1]
Thread C → cell[2]
Thread D → cell[3]
```

最后求和时再把 `base` 和所有 `Cell` 加起来。

## 为什么它重要

它说明了一个非常关键的并发设计思路：

> 问题不一定是"原子性不够"，也可能是"所有线程都在打同一个热点"。

`LongAdder` 的方向不是换一把更大的锁，而是把竞争拆散。

## 核心结构

```
LongAdder
├─ base       (低竞争时优先 CAS 更新)
└─ cells[]
   ├─ cell[0].value
   ├─ cell[1].value
   ├─ cell[2].value
   └─ cell[3].value
```

### 分层处理竞争

| 操作 | 频率 | 处理方式 |
|---|---:|---|
| 更新 `base` | 高频 | CAS |
| 更新 `Cell.value` | 高频 | 分散 CAS |
| 初始化 `cells[]` | 低频 | `cellsBusy` 协调 |
| 扩容 `cells[]` | 低频 | `cellsBusy` 协调 |

一次 `add(1)` 的简化流程：先 CAS `base` → 失败则按 probe 选 Cell → CAS Cell.value → 冲突则 rehash 或扩容。

## 两重优化：CAS 分散 + 缓存行隔离

`LongAdder` 的优化有两层：

| 层次 | 解决的问题 |
|---|---|
| 拆分 Cell | 避免所有线程 CAS 同一个变量 |
| 缓存行隔离 | 避免不同 Cell 在缓存层面重新互相干扰 |

如果多个 `Cell.value` 落在同一条 cache line 上，表面上线程更新不同变量，但缓存层面仍然在争抢——这叫伪共享（False Sharing）。因此 Cell 需要填充来隔离缓存行。

## 它和 AtomicLong 的区别

- `AtomicLong`：单点原子更新，每次 `get()` 返回精确值
- `LongAdder`：分片累加后汇总，`sum()` 不是强一致快照

`LongAdder.sum()` 不是原子快照——它逐个读取 `base` 和各 Cell 后相加，求和过程中可能仍有线程在执行 `add()`。因此适合请求计数、QPS、监控指标等可接受短暂不精确的场景，不适合账户余额、库存扣减等强一致场景。

**本质：不是比 `AtomicLong` 更原子，而是在更新路径上更会分散竞争。用读取时的弱一致，换取高并发写入时的低冲突。**

## 在系列里的位置

它位于 `CAS` 和并发容器之后，是"无锁设计如何继续应对热点争用"的代表节点。

## 推荐回看原文

- [[_posts/concurrency/21-无锁设计、ABA 与 LongAdder|21-无锁设计、ABA 与 LongAdder]]
- [[_posts/concurrency/05-CAS为什么能够在不加锁的情况下更新共享数据|05-CAS 为什么能够在不加锁的情况下更新共享数据]]

## 相关概念

- [[wiki/concepts/concurrency/CAS|CAS]]
- [[wiki/concepts/concurrency/ConcurrentHashMap|ConcurrentHashMap]]
- [[wiki/concepts/concurrency/ABA|ABA]]
- [[wiki/concepts/concurrency/StampedLock|StampedLock]]
- [[wiki/concepts/concurrency/并发容器|并发容器与数据结构]]
