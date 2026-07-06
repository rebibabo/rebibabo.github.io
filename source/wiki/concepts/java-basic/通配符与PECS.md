---
title: 通配符与PECS
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# 通配符与 PECS

[[wiki/concepts/java-basic/泛型|返回泛型]]

## 这一层回答什么问题

> 泛型里 `?` 是什么？什么时候用 `? extends`、什么时候用 `? super`？为什么 `List<String>` 不是 `List<Object>` 的子类型？

这些问题的答案都指向一件事：**泛型是不变的（invariant）**。`List<String>` 和 `List<Object>` 之间没有继承关系——即使 `String` 是 `Object` 的子类。通配符就是用来在不变的类型系统里"打洞"的。

## 三种通配符

| 通配符 | 能做什么 | 不能做什么 |
|--------|----------|-----------|
| `?` | 几乎什么都做不了 | — |
| `? extends T` | 读出来是 T | 不能写入 |
| `? super T` | 可以写入 T | 读出来是 Object |

## PECS：这条规则解决一切困惑

**P**roducer **E**xtends, **C**onsumer **S**uper。

如果一个参数是"生产者"——你只从里面读数据——用 `? extends`：

```java
// src 是生产者：只遍历，不往里加东西
public static double sum(List<? extends Number> numbers) {
    double sum = 0;
    for (Number n : numbers) sum += n.doubleValue();  // 能读，读出来是 Number
    // numbers.add(1);  // ❌ 编译错误
    return sum;
}
```

如果一个参数是"消费者"——你只往里写数据——用 `? super`：

```java
// dest 是消费者：只往里放，不往外取特定类型
public static void addNumbers(List<? super Integer> dest) {
    dest.add(1);  // 能写 Integer
    dest.add(2);
    // Integer i = dest.get(0);  // ❌ 编译错误，读出来是 Object
}
```

## 为什么不是"读就 extends，写就 super"

规则比这个更精确：

- `? extends T` 的意思是"这个容器里装的可能是 T 或 T 的子类，但不知道具体是什么"。如果允许写入，你可能把 `Dog` 写进一个实际是 `List<Cat>` 的容器。所以只能读。
- `? super T` 的意思是"这个容器能装 T 或 T 的父类"。所以写一个 T 进去是安全的——它一定能被接收。但读出来时不知道具体类型，只能给 Object。

## 经典例子：Collections.copy

```java
public static <T> void copy(List<? super T> dest, List<? extends T> src) {
    // dest 是消费者（super）→ 往里写
    // src 是生产者（extends）→ 从里读
    for (T item : src) dest.add(item);
}
```

## 在系列里的位置

post 06 最核心的部分。

## 推荐回看原文

- [[_posts/Java-basic/06-genrics|06-泛型]]

## 相关概念

- [[wiki/concepts/java-basic/类型擦除|类型擦除]]
- [[wiki/concepts/java-basic/集合框架|集合框架]] — PECS 规则在 Collections API 中大量使用
