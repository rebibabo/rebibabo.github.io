---
title: ArrayList 扩容
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# ArrayList 扩容

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

ArrayList 底层基于动态数组，当数组满时自动扩容，新容量为旧容量的 1.5 倍（`oldCapacity + oldCapacity >> 1`），通过 `System.arraycopy` 将旧数组元素复制到新数组。

## 上下文

默认初始容量为 10（第一次 add 时才真正分配数组）。每次扩容都涉及"创建新数组 + 整体复制"，单次扩容是 O(n) 操作。之所以不是每次 add 都触发扩容，是因为 1.5 倍的增长使得扩容频率随数据增长而降低——均摊下来每次 add 的时间复杂度仍是 O(1)（均摊时间复杂度）。1.5 倍是时间与空间的折中：如果每次只扩容 1 个，几乎每次都触发扩容；如果扩容倍数太大（如 2 倍），容易造成内存浪费。如果你提前知道大概要存多少元素，用 `new ArrayList<>(initialCapacity)` 指定初始容量可以避免多次扩容复制。在中间位置插入或删除元素时需要整体移动后续元素（`System.arraycopy`），是 O(n) 操作，频繁中间增删时 LinkedList 理论上更合适。

## 相关术语

- [[wiki/glossary/java-basic/ArrayList|ArrayList]] — 基于动态数组的列表实现，底层触发扩容的核心类
- [[wiki/glossary/java-basic/扩容|扩容（HashMap）]] — HashMap 的扩容机制，容量翻倍而非 1.5 倍

## 深入阅读

- [[_posts/Java-basic/32-data-structure-internals|java-basics(番外) 集合的底层原理：HashMap、ArrayList 与红黑树]]
