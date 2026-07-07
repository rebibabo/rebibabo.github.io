---
title: String
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - string
type: glossary
source_series: Java-basic
status: seed
---

# String

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

`String` 是 Java 中最常用的不可变字符序列类（final 类，底层使用 `byte[]` 数组存储）。它不是基本类型，但使用频率和重要性堪比基本类型，拥有字符串常量池和运算符重载（`+` 拼接）等特殊支持。

## 上下文

String 的不可变性意味着每次拼接、替换、截取都会产生新对象，原对象不变。因此在循环中大量字符串拼接会导致 O(n^2) 的时间复杂度和大量临时对象，应改用 `StringBuilder`。

字符串字面量（如 `"hello"`）优先从常量池获取，`new String("hello")` 则直接在堆上创建新对象。比较字符串内容永远用 `.equals()` 而非 `==`。Java 9 后底层从 `char[]` 改为 `byte[]`（Compact Strings），纯 ASCII 字符只占 1 字节。Java 11 引入了 `isBlank()`、`lines()`、`strip()` 等实用方法。

## 相关术语

- [[wiki/glossary/java-basic/String-Pool|String Pool]] — JVM 字符串常量池，字面量字符串优先从池中获取，避免重复创建
- [[wiki/glossary/java-basic/StringBuilder|StringBuilder]] — 可变字符序列，频繁拼接时替代 String 避免产生大量临时对象
- [[wiki/glossary/java-basic/equals-和-==|equals 和 ==]] — 字符串内容比较必须用 equals()，== 只比较引用地址

## 深入阅读

- [[_posts/Java-basic/02-basic-types|java-basics(2) | 基本数据类型：八大原始类型与那些必踩的坑]]
