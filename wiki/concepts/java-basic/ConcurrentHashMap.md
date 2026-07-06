---
title: ConcurrentHashMap
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# ConcurrentHashMap

[[wiki/concepts/java-basic/集合框架|返回集合框架]]

## 这一层回答什么问题

> 多线程下怎么安全地操作 HashMap？ConcurrentHashMap 和 Hashtable 有什么区别？JDK 7 的分段锁和 JDK 8 的 CAS + synchronized 是谁更好？

ConcurrentHashMap 是并发环境下的标准 Map 实现。它解决的不是"怎么用"，而是"怎么做到既安全又不至于把所有线程都卡住"。

## Hashtable 的问题

`Hashtable` 用 `synchronized` 修饰每个方法——全表锁。一个线程在 put，其他所有线程全部阻塞。并发越高，性能越差。

## JDK 7：分段锁（Segment）

把整个 Map 分成 16 个 Segment（默认），每个 Segment 独立加锁。不同 Segment 之间可以并行操作——两个线程 put 不同 Segment 的数据，不阻塞。

问题：Segment 数量固定，不能动态扩展。跨 Segment 操作（size、containsValue）需要锁住所有 Segment。

## JDK 8：CAS + synchronized 按桶加锁

彻底抛弃 Segment，改为**桶级别**的并发控制：

- **读**：不加锁（Node 的 val 和 next 用 volatile 修饰，保证可见性）
- **写（空桶）**：CAS 尝试设置第一个节点，失败说明有竞争，进入 synchronized
- **写（非空桶）**：synchronized 锁住桶的头节点，只锁这一个桶
- **扩容**：多线程协同——正在扩容时，其他线程帮忙迁移数据（不阻塞）

粒度从"整个 Segment"细化到"单个桶"。16 个线程操作 16 个不同桶，完全不阻塞。

## ConcurrentHashMap vs HashMap 的使用差异

- 用法完全相同——同样实现了 `Map` 接口
- ConcurrentHashMap 的 key 和 value 都不能是 null（HashMap 允许一个 null key 和多个 null value）
- `putIfAbsent` / `computeIfAbsent` 是原子操作——ConcurrentHashMap 里这对组合是线程安全的

## 在系列里的位置

post 03 和 post 32。

## 推荐回看原文

- [[_posts/Java-basic/32-data-structure-internals|32-集合的底层原理]]

## 相关概念

- [[wiki/concepts/java-basic/HashMap|HashMap]]
- [[wiki/concepts/java-basic/ArrayList与LinkedList|ArrayList 与 LinkedList]]
