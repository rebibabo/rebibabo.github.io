---
title: String
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# String

[[wiki/concepts/java-basic/数据类型|返回数据类型]]

## 这一层回答什么问题

> String 为什么是不可变的？`"hello"` 和 `new String("hello")` 有什么区别？循环拼接字符串为什么用 StringBuilder？

String 不是基本类型，但在 Java 里使用频率极高。它的不可变性、常量池、Compact Strings 优化，每一个都直接影响日常代码的性能和正确性。

## 不可变性：最核心的设计

String 底层是 `final byte[] value`（Java 9+ Compact Strings，之前是 `final char[]`）。`final` 意味着引用不可变，数组内容也不对外暴露——任何"修改"操作都返回一个新的 String 对象。

这样做的好处：
- **安全**：作为 HashMap 的 key、数据库连接 URL、文件路径时，不用担心被意外修改
- **线程安全**：不可变对象天然线程安全
- **常量池**：编译期就能确定的内容可以复用

代价：频繁拼接会产生大量临时对象。所以有了 StringBuilder。

## 字符串常量池

```java
String a = "hello";           // 从常量池取（没有就创建）
String b = "hello";           // 常量池已有，直接返回同一个引用
a == b;                       // true

String c = new String("hello"); // 强制在堆上新建对象
a == c;                       // false
```

`intern()` 方法可以手动把一个堆上的 String 放入常量池。但不要滥用——常量池在 Java 7+ 也放在堆上，大量 intern 会增加 GC 压力。

## StringBuilder：可变的字符串

```java
// ❌ 循环中用 +：每次循环创建新 String 对象，O(n²) 时间 + O(n²) 内存分配
String result = "";
for (int i = 0; i < 10000; i++) {
    result += i;  // 实际上转换成 StringBuilder → append → toString，每次循环一个
}

// ✅ 循环外用 StringBuilder：只有同一个对象反复 append，O(n)
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);
}
String result = sb.toString();
```

`StringBuffer` 是线程安全版（方法加 `synchronized`），单线程下用 `StringBuilder`，性能更好。

## 常用操作

`equals()` 比较内容、`length()`、`charAt()`、`substring()`、`split()`、`trim()`、`toLowerCase()`、`indexOf()`、`startsWith()`、`replace()`、`join()`、`format()`——这些方法全部返回新 String，原 String 不变。

## 在系列里的位置

post 02 的核心内容。

## 推荐回看原文

- [[_posts/Java-basic/02-basic-types|02-基本数据类型]]

## 相关概念

- [[wiki/concepts/java-basic/基本类型与包装类|基本类型与包装类]]
- [[wiki/concepts/java-basic/面向对象|面向对象]] — String 的 equals 和 hashCode 重写是 OOP 的经典案例
