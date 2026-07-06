---
title: Throwable
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Throwable

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Throwable 是 Java 异常体系的根类，所有可被抛出和捕获的异常对象都继承自它，下分 `Error`（系统级错误，不应捕获）和 `Exception`（程序级异常）。

## 上下文

异常体系层次：`Throwable` -> `Error`（OutOfMemoryError、StackOverflowError 等 JVM 级别问题，不应捕获也处理不了）和 `Exception`（程序可处理的异常）。`Exception` 又分为 `RuntimeException`（Unchecked，程序 bug，不强制处理）和其他 Exception（Checked，编译器强制处理）。实际开发中不应该 catch `Throwable` 或 `Error`——这些大多是不可恢复的 JVM 错误，捕获后也无法正常继续运行。最上层捕获到 `Exception` 一般就够了。Throwable 提供 `getMessage()`、`getCause()`、`printStackTrace()` 等基础方法。

## 相关术语

- [[wiki/glossary/java-basic/Checked-Exception|Checked Exception]] — Exception 下非 RuntimeException 的分支，编译器强制处理
- [[wiki/glossary/java-basic/Unchecked-Exception|Unchecked Exception]] — RuntimeException 分支，代表程序 bug，不强制处理
- [[wiki/glossary/java-basic/异常链|异常链]] — 通过 Throwable 的 cause 参数串联原始异常，排查根因的关键

## 深入阅读

- [[_posts/Java-basic/07-exception|Java基础(7) 异常体系：Checked vs Unchecked 与 try-with-resources]]
