---
title: ConcurrentHashMap
tags:
  - wiki
  - concept
  - concurrency
  - concurrenthashmap
type: concept
source_series: concurrency
status: seed
---

# ConcurrentHashMap

[[wiki/concepts/concurrency/并发容器|返回并发容器与数据结构]]

## 定义

`ConcurrentHashMap` 是 Java 里最典型的高并发 Map，用来在多线程读写下保持结构安全，并尽量减少全局锁竞争。

## 它解决什么问题

它回答的是：

> 多线程同时写 Map 时，怎样既不把结构写坏，又不要像 Hashtable 那样一把锁锁整张表？

普通 `HashMap` 并发写不安全——多个线程同时修改同一个桶时，可能互相覆盖或破坏链表结构。`Hashtable` 用全局 `synchronized` 保证安全，但即使两个线程操作不同桶也必须串行。

## 核心思路：从 Segment 到桶级锁

JDK 1.7 使用 `Segment` 分段锁——把整张 Map 拆成多个小区域，每个 Segment 有自己的锁。不同线程落到不同 Segment 可并发执行。

JDK 1.8 进一步下沉到桶级别：

| 桶状态 | 写入方式 |
| --- | --- |
| 桶为空 | CAS 放入新节点 |
| 桶非空 | 锁住桶头节点，再修改桶内结构 |

**能用 CAS 完成的写入就不加锁；必须修改桶内链表或红黑树时，只锁当前桶。**

## 为什么 get 大多数时候不用加锁

`get` 不修改结构，只是沿着已发布的结构向下查找。节点字段设计支持无锁读取：

- `key` 和 `hash` 初始化后不变
- `val` 和 `next` 是 `volatile`，保证可见性

新增节点时，JDK 1.8 在链表尾部追加——先把新节点构造完成，再通过一次 `volatile next` 写接入链表。对读线程来说，结构只有两种可能：旧链表（没有新节点），或新链表（已接入新节点），不会看到半成品。删除同理——通过前驱节点跳过被删节点，读线程可能看到旧路径或新路径，但不会看到断裂链表。

**`get` 不保证读到全局最新状态，但保证不会读到被破坏的半截结构。**

## 扩容：多线程协助迁移

当数组容量不足时，创建更大的 `nextTable`。扩容不是停住所有线程等单线程慢慢搬，而是由执行 `put` 等操作的业务线程顺手参与迁移：

- 通过 CAS 分配迁移范围（transferIndex），不同线程领取不同段
- 每个桶迁移完成后放入 `ForwardingNode`（通往新表的路标）
- 扩容期间，未迁移桶仍可在旧表处理；已迁移桶通过 `ForwardingNode` 转向新表
- 扩容完成后，最后一个完成迁移的线程把 `table = nextTable`

## 计数：分散计数如 LongAdder

`size()` 不能用普通 `int size++`（非原子）。JDK 1.8 使用类似 `LongAdder` 的分散计数：低竞争时更新 `baseCount`，竞争激烈时分散到多个 `CounterCell`。`size()` 统计时求和，但不是强一致快照。

## 为什么不允许 null

禁止 `null value`：如果允许，`get(key)` 返回 `null` 时有两种可能（key 不存在 vs value 就是 null），并发下两次观察之间 Map 可能已被修改，无法可靠区分。

## 复合操作要使用原子方法

```java
// 错误：非原子
if (!map.containsKey(key)) {
    map.put(key, value);
}

// 正确
map.putIfAbsent(key, value);
map.computeIfAbsent(key, k -> loadFromDb(k));
```

| 方法 | 语义 |
| --- | --- |
| `putIfAbsent(key, value)` | key 不存在时才放入 |
| `remove(key, value)` | 当前 value 匹配时才删除 |
| `replace(key, oldValue, newValue)` | 旧值匹配时才替换 |
| `computeIfAbsent(key, function)` | key 不存在时计算并放入 |

## 为什么它重要

它是"同步原语如何长成高级数据结构"的代表例子。理解它之后，会更容易看清：为什么桶级并发比全局锁更强；为什么 `volatile` 和 CAS 可以一起工作；为什么并发容器不是简单给 `HashMap` 套一把锁。

## 在系列里的位置

它位于并发容器层的中心节点，也是同步机制、无锁更新和局部加锁三者交汇的地方。

## 推荐回看原文

- [[_posts/concurrency/22-ConcurrentHashMap 为什么能支持高并发访问|22-ConcurrentHashMap 为什么能支持高并发访问]]
- [[_posts/concurrency/21-无锁设计、ABA 与 LongAdder|21-无锁设计、ABA 与 LongAdder]]

## 相关概念

- [[wiki/concepts/concurrency/CAS|CAS]]
- [[wiki/concepts/concurrency/volatile|volatile]]
- [[wiki/concepts/concurrency/LongAdder|LongAdder]]
- [[wiki/concepts/concurrency/并发容器|并发容器与数据结构]]
