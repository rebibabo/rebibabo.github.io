---
title: HashMap
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# HashMap

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

HashMap 是基于哈希表实现的 Map，底层为数组（桶）+ 链表 + 红黑树（JDK 8+），通过 `hashCode()` 定位桶、`equals()` 比较 key，增删查平均 O(1)。

## 上下文

HashMap 是 Java 中最常用的键值映射结构。put 流程：计算 key 的 hash（扰动函数 `h ^ (h >>> 16)` 让高低位参与运算）-> 通过 `hash & (capacity - 1)` 定位桶下标 -> 若桶为空直接放入，若冲突则遍历链表或红黑树判断覆盖还是追加。当链表长度超过 8 且数组容量 >= 64 时链表转为红黑树（阈值 8 基于泊松分布，概率约百万分之六，几乎不会正常触发）；退化回链表的阈值是 6（留缓冲避免反复树化）。负载因子默认 0.75 是时间与空间的折中，数组容量始终是 2 的幂使得位运算等价于取模。扩容时容量翻倍，元素的新位置只有两种可能（原下标或原下标+旧容量）。**HashMap 不是线程安全的**：JDK 7 扩容头插法可能死循环，JDK 8 多线程 put 可能导致数据覆盖，多线程用 ConcurrentHashMap。

## 相关术语

- [[wiki/glossary/java-basic/HashSet|HashSet]] — 基于 HashMap 的 Set 实现，利用 key 唯一性去重
- [[wiki/glossary/java-basic/LinkedHashMap|LinkedHashMap]] — 在 HashMap 基础上维护插入/访问顺序的双向链表
- [[wiki/glossary/java-basic/红黑树|红黑树]] — HashMap 链表过长时转为红黑树以优化 O(n) 到 O(log n)
- [[wiki/glossary/java-basic/负载因子|负载因子]] — 默认 0.75，触发扩容的容量阈值，时间与空间的折中
- [[wiki/glossary/java-basic/哈希冲突|哈希冲突]] — 不同 key 映射到同一桶下标，通过链表/红黑树解决
- [[wiki/glossary/java-basic/扩容|扩容]] — 容量翻倍，元素重新分布到原下标或原下标+旧容量

## 深入阅读

- [[_posts/Java-basic/03-collections|Java基础(3) 集合框架：List、Set、Map 与队列全梳理]]
- [[_posts/Java-basic/32-data-structure-internals|Java基础(番外) 集合的底层原理：HashMap、ArrayList 与红黑树]]
