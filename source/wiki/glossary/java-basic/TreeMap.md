---
title: TreeMap
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# TreeMap

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

TreeMap 是基于红黑树（自平衡二叉搜索树）实现的 Map，key 始终有序（自然排序或自定义 Comparator），增删查 O(log n)，不允许 null key。

## 上下文

红黑树是一种近似平衡的二叉搜索树，比 AVL 树旋转次数更少，在读写均衡的场景综合性能更优。TreeMap 特有范围操作：`firstKey`/`lastKey`（最小/最大 key）、`floorKey`/`ceilingKey`（<=或>=某值的最大/最小 key）、`subMap`/`headMap`/`tailMap`（子映射）。遍历时按 key 排序输出，适合需要排序或范围查询的场景。和普通 HashMap 相比，TreeMap 以 O(log n) 的代价换取了有序性和范围操作能力。对应 Set 版本是 TreeSet。

## 相关术语

- [[wiki/glossary/java-basic/HashMap|HashMap]] — 哈希表实现的 Map，O(1) 但不保证顺序
- [[wiki/glossary/java-basic/LinkedHashMap|LinkedHashMap]] — 维护插入顺序的 Map，介于 HashMap 和 TreeMap 之间
- [[wiki/glossary/java-basic/红黑树|红黑树]] — TreeMap 底层数据结构，自平衡二叉搜索树

## 深入阅读

- [[_posts/Java-basic/03-collections|Java基础(3) 集合框架：List、Set、Map 与队列全梳理]]
- [[_posts/Java-basic/32-data-structure-internals|Java基础(番外) 集合的底层原理：HashMap、ArrayList 与红黑树]]
