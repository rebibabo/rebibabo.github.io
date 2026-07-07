---
title: HashSet
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# HashSet

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

HashSet 是基于 HashMap 实现的 Set，内部用一个 HashMap 存储元素（所有 key 映射到同一个虚拟 value），利用 HashMap 的 key 唯一性保证元素不可重复，增删查 O(1)。

## 上下文

HashSet 是最常用的 Set 实现，元素无序，允许一个 null 值。由于底层就是 HashMap，放入 HashSet 的元素必须正确重写 `equals()` 和 `hashCode()` 且保持一致，否则会出现"逻辑上相同的元素被重复添加"的问题。遍历顺序不确定。如果需要保留插入顺序用 `LinkedHashSet`，需要元素排序用 `TreeSet`（底层红黑树，O(log n)）。支持集合运算：`retainAll`（交集）、`addAll`（并集）、`removeAll`（差集），均为原地操作。

## 相关术语

- [[wiki/glossary/java-basic/HashMap|HashMap]] — HashSet 底层实现，所有元素作为 HashMap 的 key 存储
- [[wiki/glossary/java-basic/TreeMap|TreeMap]] — 基于红黑树的有序 Map，其 Set 版本 TreeSet 提供排序去重

## 深入阅读

- [[_posts/Java-basic/03-collections|java-basics(3) 集合框架：List、Set、Map 与队列全梳理]]
