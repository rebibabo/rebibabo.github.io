---
title: String Pool
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - string-pool
type: glossary
source_series: Java-basic
status: seed
---

# String Pool（字符串常量池）

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

String Pool 是 JVM 中维护的一个特殊内存区域，用于缓存字符串字面量和通过 `intern()` 方法显式加入的字符串。当使用字面量如 `"hello"` 创建字符串时，JVM 会先在池中查找：如果存在则直接返回引用，不存在则创建后放入池中。

## 上下文

String Pool 从 Java 7 开始被移入堆内存（之前在方法区/永久代），因此它也受 GC 管理。`String.intern()` 可以手动将堆上的 String 对象加入常量池，但滥用会导致常量池膨胀，影响性能。

与 Integer 缓存池不同，String Pool 没有固定范围限制，而是基于哈希表动态维护。常见面试题如 `"hello" == "hello"` 为 true（都指向池中同一对象），但 `"hello" == new String("hello")` 为 false（new 在堆上创建新对象，不走池）。

## 相关术语

- [[wiki/glossary/java-basic/String|String]] — String 类的不可变性是常量池存在的前提，同一字面量可以安全共享
- [[wiki/glossary/java-basic/equals-和-==|equals 和 ==]] — 常量池中同一字符串用 == 比较为 true，堆上新对象用 == 为 false，比较内容必须用 equals()

## 深入阅读

- [[_posts/Java-basic/02-basic-types|Java基础(2) | 基本数据类型：八大原始类型与那些必踩的坑]]
