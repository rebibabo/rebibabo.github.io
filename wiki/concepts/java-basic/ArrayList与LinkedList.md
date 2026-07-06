---
title: ArrayList 与 LinkedList
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# ArrayList 与 LinkedList

[[wiki/concepts/java-basic/集合框架|返回集合框架]]

## 这一层回答什么问题

> ArrayList 和 LinkedList 什么时候用哪个？扩容是怎么做的？为什么官方说 ArrayDeque 比 LinkedList 好？

这两个是最常用的 List 实现。选对的场景差别不大——但在对性能敏感的代码里，选错可能让 O(1) 变 O(n)。

## ArrayList：动态数组

底层是一个 `Object[]`。默认容量 10，插入时不够用了就扩容——增加到原容量的 **1.5 倍**，通过 `System.arraycopy` 把旧数组整体复制到新数组。

- 随机访问 `get(i)`：O(1)
- 尾部插入 `add(e)`：均摊 O(1)（扩容不是每次都发生）
- 中间插入/删除：O(n)（要移动后面的元素）
- 内存：紧凑，一个元素只占一个引用

**预知数据量时**：`new ArrayList<>(expectedSize)` 指定初始容量，避免多次扩容。

## LinkedList：双向链表

每个节点存前后指针 + 数据引用。

- 随机访问 `get(i)`：O(n)（从头/尾开始数）
- 头部/尾部插入删除：O(1)
- 内存：每个节点多两个指针（24 字节开销 vs ArrayList 的 4 字节）

**LinkedList 很少是正确答案**。大多数场景下随机访问比头尾操作更频繁，O(n) 的 get 是性能杀手。即使需要头尾操作，官方推荐 **ArrayDeque**——循环数组实现，没有指针开销，缓存更友好。

## CPU 缓存的视角

ArrayList 的元素在内存上连续排列——遍历时 CPU 能一次加载一整条缓存行（64 字节）的数据，命中率极高。LinkedList 的节点在内存上分散——每次跳到下一个节点几乎必然 cache miss。

## 选型速查

| 场景 | 选什么 |
|------|--------|
| 需要索引访问 | ArrayList |
| 经常在尾部追加 | ArrayList |
| 频繁在头部/中间插入删除 | 重新考虑数据结构（ArrayDeque?） |
| 需要队列 | ArrayDeque，不要 LinkedList |
| 需要栈 | ArrayDeque，不要 Stack |

## 在系列里的位置

post 03 和 post 32。

## 推荐回看原文

- [[_posts/Java-basic/03-collections|03-集合框架]]
- [[_posts/Java-basic/32-data-structure-internals|32-集合的底层原理]]

## 相关概念

- [[wiki/concepts/java-basic/HashMap|HashMap]]
- [[wiki/concepts/java-basic/ConcurrentHashMap|ConcurrentHashMap]]
