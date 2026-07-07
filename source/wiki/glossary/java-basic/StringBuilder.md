---
title: StringBuilder
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - stringbuilder
type: glossary
source_series: Java-basic
status: seed
---

# StringBuilder

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

`StringBuilder` 是可变的字符序列类，底层维护一个可扩容的 `byte[]` 数组，通过 `append`、`insert`、`delete` 等方法直接在原数组上修改，避免了 String 每次操作都创建新对象的开销。它是单线程下字符串拼接的首选。

## 上下文

`StringBuilder` 非线程安全（方法没有 synchronized），因此性能优于 `StringBuffer`。在循环中拼接字符串时，用 `StringBuilder` 可以将 O(n^2) 降为 O(n)。典型使用模式是 `StringBuilder` 单次使用（方法内局部变量），不涉及多线程访问，所以绝大多数场景用 `StringBuilder` 而非 `StringBuffer`。

`StringBuilder` 默认初始容量为 16，扩容时大约翻倍（`oldCapacity * 2 + 2`）。如果已知最终长度，可以通过构造参数指定容量以避免多次扩容。Java 5 引入 `StringBuilder` 替代了 `StringBuffer` 在单线程场景的使用。

## 相关术语

- [[wiki/glossary/java-basic/String|String]] — 不可变字符序列，频繁拼接时产生大量临时对象，应改用 StringBuilder
- [[wiki/glossary/java-basic/String-Pool|String Pool]] — String 的常量池机制，StringBuilder 拼接结果通过 toString() 创建新 String 对象

## 深入阅读

- [[_posts/Java-basic/02-basic-types|java-basics(2) | 基本数据类型：八大原始类型与那些必踩的坑]]
