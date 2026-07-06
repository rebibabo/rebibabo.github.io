---
title: try-with-resources
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# try-with-resources

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

try-with-resources 是 Java 7 引入的语法糖，实现了 `AutoCloseable` 接口的资源在 `try(资源声明)` 代码块结束后会自动调用 `close()`，无需手动在 finally 中关闭。

## 上下文

Java 7 之前关闭资源需要在 finally 块中手写嵌套的 try-catch，代码冗长且容易遗漏 close。try-with-resources 解决了这个问题：将资源声明放在 try 括号中（多个用分号分隔），作用域结束时按声明逆序自动关闭。所有实现了 `AutoCloseable` 接口的类都可以使用，包括 InputStream/OutputStream、Reader/Writer、JDBC Connection/Statement/ResultSet、Socket/ServerSocket、Scanner 等。关闭顺序与声明顺序相反（后声明的先关），即使 close 方法本身抛异常也能正确处理，原异常不会被吞掉。

## 相关术语

- [[wiki/glossary/java-basic/Checked-Exception|Checked Exception]] — try-with-resources 最常处理的异常类型，如 IOException
- [[wiki/glossary/java-basic/字节流|字节流]] — InputStream/OutputStream 是实现 AutoCloseable 的典型资源类

## 深入阅读

- [[_posts/Java-basic/07-exception|Java基础(7) 异常体系：Checked vs Unchecked 与 try-with-resources]]
