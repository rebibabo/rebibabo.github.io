---
title: Stream API
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Stream API

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Stream API 是 Java 8 引入的对集合数据进行声明式处理的管道抽象，将数据处理描述为"要做什么"而非"怎么做"，替代传统命令式的 for 循环和临时变量。

## 上下文

Stream 操作分为三个阶段：数据源（集合、数组等）到中间操作（惰性求值，返回新 Stream）到终端操作（触发整个管道执行并产生结果）。中间操作不会立即执行，只有终端操作被调用时整个管道才会真正运行，这种惰性求值机制支持短路优化和更好的性能。Stream 不存储数据、不修改数据源，且流只能被消费一次。并行流 `parallelStream()` 可以自动利用多核处理数据，但需要注意线程安全问题。

## 相关术语
- [[wiki/glossary/java-basic/中间操作|中间操作]] — Stream 管道中惰性求值的操作，返回新 Stream
- [[wiki/glossary/java-basic/终端操作|终端操作]] — 触发 Stream 管道执行并产生最终结果
- [[wiki/glossary/java-basic/Collectors|Collectors]] — 配合 collect() 终端操作，提供丰富的数据收集功能
- [[wiki/glossary/java-basic/Optional|Optional]] — 常与 Stream 的 findFirst/findAny 等终端操作配合使用

## 深入阅读

- [[_posts/Java-basic/08-lambda-and-stream|java-basics(8) | Lambda 与 Stream API：函数式编程核心工具]]
