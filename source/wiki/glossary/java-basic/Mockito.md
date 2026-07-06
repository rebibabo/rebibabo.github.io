---
title: Mockito
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Mockito

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Mockito 是 Java 主流的 Mock 框架，通过 `@Mock` 创建假对象替代真实依赖，`when().thenReturn()` 预设行为，`verify()` 验证方法调用，实现单元测试中被测对象与外部依赖的隔离。

## 上下文

核心用法：`@Mock` 创建 Mock 对象（所有方法默认返回 null/0/空），`@InjectMocks` 创建真实的被测对象并自动注入 Mock 依赖，`when(x.method()).thenReturn(value)` 设定"当某个方法被调用时返回什么"，`verify(x).method()` 事后检查"这个方法是否被调用过"。`when()` 还可以返回异常（`thenThrow`）、动态计算（`thenAnswer`，根据传入参数动态返回值）、连续调用不同值（`thenReturn(a, b, c)`）。参数匹配器 `any()`、`eq()`、`argThat()` 让规则不限于特定参数值——注意所有参数要么全用匹配器，要么全用字面值，不能混用。`verify()` 支持 `times(n)`、`atLeast(n)`、`atMost(n)`、`never()` 等次数控制，`InOrder` 验证调用顺序，`verifyNoMoreInteractions` 确认没有意外的额外调用。`@Spy` 保留真实实现，只覆盖部分方法。在 Spring 容器测试中用 `@MockBean` 替代 `@Mock`。

## 相关术语

- [[wiki/glossary/java-basic/JUnit-5|JUnit 5]] — Java 主流单元测试框架，Mockito 的标准搭档

## 深入阅读

- [[_posts/Java-basic/20-unit-testing|Java基础(20) 单元测试：JUnit 5 + Mockito 实战]]
