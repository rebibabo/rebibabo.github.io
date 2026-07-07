---
title: Optional
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Optional

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Optional 是 Java 8 引入的容器类，表示一个值可能存在也可能不存在，用于替代 null 返回值，从 API 层面强制调用方处理空值情况，减少 NullPointerException。

## 上下文

创建方式：`Optional.of(value)`（值不能为 null）、`Optional.ofNullable(value)`（值可为 null）、`Optional.empty()`（空容器）。安全获取：`orElse(default)` 提供默认值、`orElseGet(supplier)` 惰性计算默认值、`orElseThrow(exceptionSupplier)` 抛自定义异常。链式操作：`map` 转换内部值、`flatMap` 当映射函数本身返回 Optional 时使用、`filter` 条件不满足时变为空 Optional。使用原则：只用作方法返回值（提示调用方结果可能为空），不用作方法参数、不用作类的字段（未实现 Serializable）、不包装集合（空集合优于 Optional<List>），避免用 `isPresent() + get()` 代替 null 检查。

## 相关术语
- [[wiki/glossary/java-basic/Stream-API|Stream API]] — Stream 的 findFirst/findAny 等终端操作返回 Optional
- [[wiki/glossary/java-basic/Lambda|Lambda]] — Optional 的 map/flatMap/filter 等方法接受 Lambda 参数

## 深入阅读

- [[_posts/Java-basic/08-lambda-and-stream|java-basics(8) | Lambda 与 Stream API：函数式编程核心工具]]
