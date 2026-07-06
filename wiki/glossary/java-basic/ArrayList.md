---
title: ArrayList
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# ArrayList

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

ArrayList 是基于动态数组实现的 List，支持 O(1) 随机访问，底层是一个 `Object[]` 数组，当数组满时以 1.5 倍扩容并整体复制。

## 上下文

ArrayList 是 95% 场景下 List 的默认选择。扩容机制：当元素数达到容量上限，创建旧容量 1.5 倍的新数组（`oldCapacity + oldCapacity >> 1`），通过 `System.arraycopy` 复制全部元素。虽然扩容这一次是 O(n)，但通过均摊分析绝大多数 add 是 O(1)。中间插入和删除需要移动后续元素同样是 O(n)。如果提前知道数据量，用 `new ArrayList<>(initialCapacity)` 指定初始容量可以避免多次扩容复制。相比 LinkedList，ArrayList 内存紧凑且缓存友好，性能几乎全面占优。

## 相关术语

- [[wiki/glossary/java-basic/LinkedList|LinkedList]] — 基于双向链表的 List，O(1) 头尾操作但随机访问 O(n)
- [[wiki/glossary/java-basic/HashMap|HashMap]] — 键值映射的首选，与 ArrayList 同为最常用集合
- [[wiki/glossary/java-basic/扩容|扩容]] — ArrayList 1.5 倍扩容机制，均摊 O(1) 的关键

## 深入阅读

- [[_posts/Java-basic/03-collections|Java基础(3) 集合框架：List、Set、Map 与队列全梳理]]
- [[_posts/Java-basic/32-data-structure-internals|Java基础(番外) 集合的底层原理：HashMap、ArrayList 与红黑树]]
