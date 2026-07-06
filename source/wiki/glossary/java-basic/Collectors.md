---
title: Collectors
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Collectors

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Collectors 是 `java.util.stream.Collectors` 工具类，提供了一系列静态方法返回 Collector 实例，配合 Stream 的 `collect()` 终端操作将流中元素收集为集合、字符串、Map 或进行分组统计。

## 上下文

常用收集器：`toList()` 收集为 List、`toSet()` 收集为 Set（去重）、`toCollection(TreeSet::new)` 指定具体集合实现；`toMap(keyMapper, valueMapper, mergeFunction)` 收集为 Map，key 冲突时需提供合并函数否则抛异常；`joining(delimiter, prefix, suffix)` 将 Stream<String> 拼接为字符串；`groupingBy(classifier)` 按条件分成多组，返回 `Map<K, List<T>>`，支持下游收集器（如 groupingBy 后再 counting 统计每组数量）；`partitioningBy(predicate)` 按条件分成 true/false 恰好两组；`summarizingInt` 等统计类收集器可一次性获取 count、sum、min、max、average。`groupingBy` 适合任意多组分类，`partitioningBy` 适合按布尔条件分成两组的场景。

## 相关术语
- [[wiki/glossary/java-basic/Stream-API|Stream API]] — Collectors 配合 Stream 的 collect() 终端操作使用
- [[wiki/glossary/java-basic/终端操作|终端操作]] — collect() 是最常用的终端操作，参数来自 Collectors 工具类
- [[wiki/glossary/java-basic/中间操作|中间操作]] — 中间操作对数据做预处理，Collectors 负责最终收集

## 深入阅读

- [[_posts/Java-basic/08-lambda-and-stream|Java基础(8) | Lambda 与 Stream API：函数式编程核心工具]]
