---
title: Checked Exception
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Checked Exception

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Checked Exception（受检异常）是继承自 `Exception` 但不属于 `RuntimeException` 的异常，编译器强制要求调用者必须通过 `try-catch` 或 `throws` 声明来处理，否则编译不通过。

## 上下文

Checked Exception 的设计初衷是"可以预见并应该处理的外部问题"——文件不存在（`IOException`）、数据库连接失败（`SQLException`）、类未找到（`ClassNotFoundException`）等。核心争议在于它强制调用者面对问题，但过度使用会导致代码充斥样板化的 try-catch 或 throws 层层上抛。选择 Checked 还是 Unchecked 的判断标准：调用者可以合理恢复处理的用 Checked，程序错误（参数非法、状态异常）用 Unchecked。现代 Java 和 Spring 生态的倾向是优先使用 Unchecked，因为大多数异常在业务层面无法恢复，层层声明 throws 反而增加噪音。

## 相关术语

- [[wiki/glossary/java-basic/Unchecked-Exception|Unchecked Exception]] — 继承自 RuntimeException，不强制处理，代表程序 bug
- [[wiki/glossary/java-basic/Throwable|Throwable]] — 异常体系根类，Checked 和 Unchecked 都继承自 Exception -> Throwable
- [[wiki/glossary/java-basic/try-with-resources|try-with-resources]] — 自动关闭资源的语法糖，常用于处理 Checked Exception（如 IOException）

## 深入阅读

- [[_posts/Java-basic/07-exception|java-basics(7) 异常体系：Checked vs Unchecked 与 try-with-resources]]
