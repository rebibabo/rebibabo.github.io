---
title: JUnit 5
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# JUnit 5

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

JUnit 5（Jupiter）是 Java 主流单元测试框架，通过 `@Test`、生命周期注解和丰富的断言 API 提供结构化的测试编写方式。

## 上下文

核心注解包括：`@Test` 标记测试方法，`@BeforeEach`/`@AfterEach` 在每个测试前后执行（用于初始化和清理），`@BeforeAll`/`@AfterAll` 在所有测试前后执行一次（必须是 static）。断言方面，JUnit 5 提供 `assertEquals`、`assertTrue`、`assertThrows`、`assertTimeout`、`assertAll`（分组断言，全部失败都报出来）等。`@ParameterizedTest` 配合 `@ValueSource`、`@CsvSource`、`@MethodSource` 让同一段测试逻辑跑多组数据。`@DisplayName` 用于给测试写中文描述，`@Disabled` 跳过测试。Spring Boot 项目中 `spring-boot-starter-test` 一次引入就包含 JUnit 5、Mockito、AssertJ 等全套测试依赖。

## 相关术语

- [[wiki/glossary/java-basic/Mockito|Mockito]] — Java 主流 Mock 框架，配合 JUnit 5 隔离外部依赖

## 深入阅读

- [[_posts/Java-basic/20-unit-testing|Java基础(20) 单元测试：JUnit 5 + Mockito 实战]]
