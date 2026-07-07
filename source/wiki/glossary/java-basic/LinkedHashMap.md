---
title: LinkedHashMap
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# LinkedHashMap

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

LinkedHashMap 继承 HashMap，额外维护一条双向链表记录元素插入顺序（或访问顺序），遍历时按链表顺序输出，增删查 O(1)。

## 上下文

LinkedHashMap 在 HashMap 的数组+链表+红黑树基础上增加双向链表，每个节点额外维护 before/after 指针。默认按插入顺序遍历（`accessOrder=false`），设置 `accessOrder=true` 后每次 get 操作将该元素移到链表末尾，配合重写 `removeEldestEntry` 方法可以实现 LRU 缓存：当 size 超过阈值时自动淘汰链表头部（最久未访问）的元素。这是 LeetCode 146（LRU Cache）的标准解法之一，无需手动维护双向链表。允许一个 null key。

## 相关术语

- [[wiki/glossary/java-basic/HashMap|HashMap]] — LinkedHashMap 的父类，提供哈希表基础能力
- [[wiki/glossary/java-basic/TreeMap|TreeMap]] — 按 key 排序的 Map，需要排序场景时替代 LinkedHashMap

## 深入阅读

- [[_posts/Java-basic/03-collections|java-basics(3) 集合框架：List、Set、Map 与队列全梳理]]
