---
title: Optional
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Optional

[[wiki/concepts/java-basic/Lambda与Stream|返回 Lambda 与 Stream]]

## 这一层回答什么问题

> 为什么要用 Optional 替代 null？`map` 和 `flatMap` 在 Optional 里怎么用？什么时候不该用 Optional？

null 的问题是它不告诉你"为什么没有值"——只能靠层层判 null。Optional 是一个容器，它强制调用者面对"可能没有值"的情况。

## 不用 vs 用 Optional

```java
// ❌ 层层判断
public String getCity(User user) {
    if (user != null) {
        Address addr = user.getAddress();
        if (addr != null) return addr.getCity();
    }
    return "未知";
}

// ✅ Optional 链式
public String getCity(User user) {
    return Optional.ofNullable(user)
        .map(User::getAddress)
        .map(Address::getCity)
        .orElse("未知");
}
```

## 核心方法

| 方法 | 作用 |
|------|------|
| `ofNullable(x)` | 可能为 null 的值包装 |
| `of(x)` | 确定不为 null（为 null 会抛 NPE） |
| `empty()` | 空 Optional |
| `map(Function)` | 转换内部值 |
| `flatMap(Function)` | 转换并展平（Function 返回 Optional） |
| `orElse(default)` | 为空时返回默认值 |
| `orElseGet(Supplier)` | 为空时惰性计算默认值 |
| `orElseThrow()` | 为空时抛异常 |
| `ifPresent(Consumer)` | 不为空时消费 |

`orElse` vs `orElseGet`：`orElse(default)` **总是**计算默认值；`orElseGet(() -> expensive())` 只在为空时才计算。默认值昂贵时，用 `orElseGet`。

## 使用原则

- **适合用作方法返回值**来表达"可能没有结果"
- **不适合**：作为字段类型、方法参数、集合元素
- **不要** `opt.isPresent()` → `opt.get()`——这跟判 null 没区别，用 `orElse` `ifPresent` `map` 等链式方法

## 在系列里的位置

post 08。

## 推荐回看原文

- [[_posts/Java-basic/08-lambda-and-stream|08-Lambda 与 Stream API]]

## 相关概念

- [[wiki/concepts/java-basic/Lambda与函数式接口|Lambda 与函数式接口]]
- [[wiki/concepts/java-basic/Stream-API|Stream API]]
