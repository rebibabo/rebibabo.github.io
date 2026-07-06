---
title: Unchecked Exception
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Unchecked Exception

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Unchecked Exception（非受检异常）是继承自 `RuntimeException` 的异常，编译器不强制要求处理，可以不 try-catch 也不声明 throws，代表程序逻辑错误（bug）。

## 上下文

常见的 Unchecked Exception 包括 `NullPointerException`、`ArrayIndexOutOfBoundsException`、`ClassCastException`、`IllegalArgumentException`、`ArithmeticException`、`NumberFormatException`、`UnsupportedOperationException` 等。设计理念是"程序员写了 bug"——这些异常不应该通过 try-catch 掩盖，而应该在开发阶段修复代码逻辑。自定义业务异常通常继承 `RuntimeException`，这是现代 Java 开发的主流倾向。注意不要用异常控制普通流程（如用 `NumberFormatException` 判断字符串是否为数字），异常机制开销大且意图不清。

## 相关术语

- [[wiki/glossary/java-basic/Checked-Exception|Checked Exception]] — 编译器强制处理的异常，代表可预见的外部问题
- [[wiki/glossary/java-basic/Throwable|Throwable]] — 异常体系根类，RuntimeException 和 Error 都继承自它

## 深入阅读

- [[_posts/Java-basic/07-exception|Java基础(7) 异常体系：Checked vs Unchecked 与 try-with-resources]]
