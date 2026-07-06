---
title: HashMap
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# HashMap

[[wiki/concepts/java-basic/集合框架|返回集合框架]]

## 这一层回答什么问题

> HashMap 底层数组 + 链表 + 红黑树到底怎么配合的？扰动函数、负载因子、扩容、树化——每个设计在解决什么问题？

HashMap 是 Java 里使用频率最高的数据结构之一。理解它的底层不是为了应付面试——是在实际场景里知道"为什么 put 的时候突然 CPU 飙高"、"为什么内存占用一直在涨"。

## 数据结构：为什么是三层

```
数组(桶) → 链表(Node) → 红黑树(TreeNode)
```

- **数组**：通过 key 的 hash 快速定位桶，O(1)
- **链表**：不同 key 落在同一个桶时，拉链法解决冲突
- **红黑树**：链表太长时（≥8），O(n) 退化到 O(log n)

## put 的完整流程

1. 计算 key 的 `hashCode()`
2. 扰动函数 `(h = key.hashCode()) ^ (h >>> 16)` —— 让高位也参与运算，减少低位相同时的碰撞
3. `(n - 1) & hash` 定位桶下标 —— 等价 `hash % n`，但位运算更快
4. 桶为空 → 直接放
5. 桶不为空 → 遍历链表/树，比较 hash 和 equals。找到相同 key → 更新 value；没找到 → 尾插法插入
6. 链表长度 ≥ 8 且容量 ≥ 64 → 链表转红黑树

## 关键参数

| 参数 | 默认值 | 为什么是这个值 |
|------|--------|---------------|
| 初始容量 | 16 | 2 的幂，方便位运算取模 |
| 负载因子 | 0.75 | 时间（冲突率）与空间（利用率）的折中 |
| 树化阈值 | 8 | 泊松分布：8 的概率约百万分之六 |
| 退化阈值 | 6 | 与 8 之间留 2 的缓冲，避免反复树化 |

**为什么容量必须是 2 的幂？** `(n - 1) & hash` 这个 trick 只有在 n 是 2 的幂时才等价于取模。同时保证低位掩码均匀分布。

## 扩容

元素数量 > 容量 × 负载因子 → 容量翻倍。JDK 8 优化了 rehash：元素只分两种——留在原位置，或移到原位置 + 旧容量。不再需要重新计算 hash。

## JDK 7 → 8 的关键变化

JDK 7 并发 resize 时头插法可能形成**环形链表**导致死循环。JDK 8 改用尾插法解决了死循环问题——但 HashMap 仍然不是线程安全的。并发场景下仍会数据覆盖和丢失。

## 为什么重写 equals 就必须重写 hashCode

HashMap 用 hashCode 找桶，用 equals 在桶内匹配。如果两个对象 equals 相等但 hashCode 不同，它们落在不同桶——HashMap 找不到。

## 在系列里的位置

post 03 和 post 32。

## 推荐回看原文

- [[_posts/Java-basic/03-collections|03-集合框架]]
- [[_posts/Java-basic/32-data-structure-internals|32-集合的底层原理]]

## 相关概念

- [[wiki/concepts/java-basic/ConcurrentHashMap|ConcurrentHashMap]]
- [[wiki/concepts/java-basic/ArrayList与LinkedList|ArrayList 与 LinkedList]]
