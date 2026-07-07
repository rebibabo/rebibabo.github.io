---
title: ConcurrentHashMap
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# ConcurrentHashMap

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

ConcurrentHashMap 是线程安全的 HashMap 实现，JDK 7 使用分段锁（Segment，默认 16 段），JDK 8 改为 CAS + synchronized（锁粒度精确到单个桶），支持更高的并发度，是多线程环境下 Map 的首选。

## 上下文

HashMap 不是线程安全的：JDK 7 扩容头插法可能导致死循环，JDK 8 多线程 put 可能导致数据覆盖。ConcurrentHashMap 的用法和 HashMap 完全一样（都实现 Map 接口），区别在于内部实现。JDK 7 的分段锁将数据分成 16 段（默认），每段独立加锁，不同段操作可并行——但并发度上限就是段数（16）。JDK 8 改进：put 时先用 CAS 尝试无锁插入空桶；若桶不为空（有冲突），只对桶的头节点加 synchronized 锁——锁粒度从"段"细化到"桶"，理论上并发度等于数组长度（随扩容增长），且去掉了 Segment 的内存开销。ConcurrentHashMap 还提供原子操作如 `putIfAbsent`、`compute`、`merge`，替代"先 get 再 put"这种非原子的组合操作。注意：单个方法是线程安全的，但组合操作（如 containsKey + put）不是。

## 相关术语

- [[wiki/glossary/java-basic/HashMap|HashMap]] — 非线程安全的 Map 实现，ConcurrentHashMap 的多线程替代
- [[wiki/glossary/java-basic/扩容|扩容]] — JDK 7 扩容头插法死循环，JDK 8 ConcurrentHashMap 用 CAS+synchronized 解决

## 深入阅读

- [[_posts/Java-basic/10-concurrency|java-basics(10) 并发编程：线程、锁、线程池与 CompletableFuture]]
- [[_posts/Java-basic/32-data-structure-internals|java-basics(番外) 集合的底层原理：HashMap、ArrayList 与红黑树]]
