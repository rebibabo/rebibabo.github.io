---
title: PriorityQueue
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# PriorityQueue

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

PriorityQueue 是基于二叉堆（默认最小堆）实现的优先队列，每次 `poll()` 取出当前最小（或按 Comparator 定义的优先级最高）的元素，入队和出队 O(log n)。

## 上下文

PriorityQueue 底层是一个数组表示的完全二叉树，通过上浮（siftUp）和下沉（siftDown）维护堆性质。默认是最小堆，可通过 `Comparator.reverseOrder()` 转为最大堆，也支持自定义 Comparator 定义优先级。不允许 null 元素，元素必须可比较（自然排序或提供 Comparator）。常用于 Top K 问题、任务调度、Dijkstra 最短路径等算法场景。和普通 Queue 不同，PriorityQueue 的遍历顺序不等于优先级顺序，只有通过 `poll()` 才能按优先级取出。

## 相关术语

- [[wiki/glossary/java-basic/LinkedList|LinkedList]] — 同时实现 List 和 Deque，可作为双端队列使用
- [[wiki/glossary/java-basic/TreeMap|TreeMap]] — 红黑树实现的有序结构，同样支持自定义 Comparator 排序

## 深入阅读

- [[_posts/Java-basic/03-collections|Java基础(3) 集合框架：List、Set、Map 与队列全梳理]]
