---
title: Stream API
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Stream API

[[wiki/concepts/java-basic/Lambda与Stream|返回 Lambda 与 Stream]]

## 这一层回答什么问题

> Stream 和集合有什么区别？中间操作和终端操作怎么区分？map、flatMap、reduce、collect 各做什么？

Stream 不是数据结构——它是一条描述"对数据做什么"的流水线。它把 Java 的数据处理从命令式变成了声明式。

## Stream 是什么（不是什么）

- **不是数据结构**：不存储数据，只描述操作
- **不是集合的替代品**：集合关注"数据在哪"，Stream 关注"对数据做什么"
- **惰性**：在终端操作触发之前，什么都不执行
- **一次性**：一个 Stream 只能消费一次，再消费需要重新创建

## 三阶段流水线

```
数据源 → 中间操作（0~N 个，惰性） → 终端操作（1 个，触发执行）
         filter/map/sorted/...       collect/forEach/reduce/...
```

中间操作返回 Stream，不会触发执行。终端操作返回非 Stream 的结果（或 void），触发整个流水线。

## 核心操作

**中间操作**：

| 操作 | 作用 |
|------|------|
| `filter` | 保留满足条件的 |
| `map` | 转换每个元素 |
| `flatMap` | 展平嵌套结构（`List<List<T>>` → `Stream<T>`） |
| `distinct` | 去重（基于 equals） |
| `sorted` | 排序（自然序或 Comparator） |
| `limit` / `skip` | 截断 / 跳过 |

**终端操作**：

| 操作 | 作用 |
|------|------|
| `collect(Collectors.toList())` | 收集成 List |
| `forEach` | 遍历（不要在里面改外部状态） |
| `reduce` | 归约（累加、求最值） |
| `count` | 计数 |
| `findFirst` / `findAny` | 找第一个 / 任意一个 |
| `anyMatch` / `allMatch` / `noneMatch` | 判断 |

## Collectors 工具箱

```java
collect(Collectors.toList())
collect(Collectors.toSet())
collect(Collectors.toMap(User::getId, Function.identity()))
collect(Collectors.groupingBy(User::getDepartment))
collect(Collectors.partitioningBy(u -> u.getAge() > 18))
collect(Collectors.joining(", "))
```

`groupingBy` 支持 downstream collector——比如 `groupingBy(Dept, counting())` 按部门统计人数。

## 并发流

`list.parallelStream()` 用 ForkJoinPool 并行执行。适合 CPU 密集型、数据量大、操作独立无状态、无 I/O 阻塞的场景。不是所有 Stream 都值得并行。

## 在系列里的位置

post 08。

## 推荐回看原文

- [[_posts/Java-basic/08-lambda-and-stream|08-Lambda 与 Stream API]]

## 相关概念

- [[wiki/concepts/java-basic/Lambda与函数式接口|Lambda 与函数式接口]]
- [[wiki/concepts/java-basic/Optional|Optional]]
- [[wiki/concepts/java-basic/集合框架|集合框架]] — Stream 的数据源通常是集合
