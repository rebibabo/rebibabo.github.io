---
title: LinkedList
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# LinkedList

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

LinkedList 是基于双向链表实现的 List 和 Deque，每个节点包含数据、prev 指针和 next 指针，支持 O(1) 头尾操作但随机访问为 O(n)。

## 上下文

LinkedList 同时实现了 `List` 和 `Deque` 接口，因此既可以当列表使用，也可以当双端队列或栈使用。每节点额外有约 16 字节的指针开销，且链表节点在内存中分散存储导致 CPU 缓存命中率低。理论上频繁在中间增删时 LinkedList 更合适，但实际上中间增删也需要 O(n) 先遍历定位，因此优势有限。官方推荐栈和队列场景优先使用 `ArrayDeque`（连续数组，缓存友好）。在现代 Java 项目中，LinkedList 的使用场景已经比较少见，仅在频繁头部插入/删除且不需要随机访问时才考虑。

## 相关术语

- [[wiki/glossary/java-basic/ArrayList|ArrayList]] — 基于动态数组的 List，随机访问 O(1)，大多数场景更优
- [[wiki/glossary/java-basic/PriorityQueue|PriorityQueue]] — 基于二叉堆的优先队列，按优先级出队而非 FIFO

## 深入阅读

- [[_posts/Java-basic/03-collections|Java基础(3) 集合框架：List、Set、Map 与队列全梳理]]
- [[_posts/Java-basic/32-data-structure-internals|Java基础(番外) 集合的底层原理：HashMap、ArrayList 与红黑树]]
