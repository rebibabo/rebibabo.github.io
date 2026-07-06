---
title: equals 和 ==
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - equals
  - comparison
type: glossary
source_series: Java-basic
status: seed
---

# equals 和 ==

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

`==` 是比较运算符，对于原始类型比较的是值是否相等，对于引用类型比较的是两个引用是否指向堆上的同一个对象（内存地址）。`equals()` 是 `Object` 中定义的方法，默认实现就是 `==`，但可以被重写为按内容/值比较。

## 上下文

核心原则：比较对象的内容用 `equals()`，比较引用地址（是否同一个对象）用 `==`。String、Integer 等标准类都重写了 `equals()` 实现值比较。包装类型的缓存池（-128~127）会让 `==` 产生假象——127 之内可能相等（同一对象），128 之外大概率不等（不同对象）——因此永远用 `equals()` 比较包装类型和 String 的值。

对于自定义类，如果没有重写 `equals()`，则继承 `Object` 的默认实现（即 `==`），可能导致 `HashSet`、`HashMap` 等集合行为异常。重写 `equals()` 必须同步重写 `hashCode()`。

## 相关术语

- [[wiki/glossary/java-basic/hashCode|hashCode]] — 与 equals() 存在契约关系：equals() 为 true 则 hashCode() 必须相等，重写 equals() 必须同步重写 hashCode()
- [[wiki/glossary/java-basic/String|String]] — 最常见的 equals() 使用场景，String 重写了 equals() 实现值比较，== 只会比较引用

## 深入阅读

- [[_posts/Java-basic/02-basic-types|Java基础(2) | 基本数据类型：八大原始类型与那些必踩的坑]]
- [[_posts/Java-basic/05-advanced-class|Java基础(5) | 继承与多态：extends、重写、抽象类与接口]]
