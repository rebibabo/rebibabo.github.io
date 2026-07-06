---
title: DI
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - spring
type: glossary
source_series: Java-basic
status: seed
---

# DI（依赖注入）

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

DI（Dependency Injection）是 IoC 的具体实现方式，由容器自动将依赖对象注入到需要它们的目标对象中，而非由目标对象自行创建或查找依赖。

## 上下文

Spring 支持三种注入方式：构造器注入（推荐，强制依赖不缺失、方便单元测试）、Setter 注入（可选依赖、可在运行时修改）和字段注入（`@Autowired` 加在字段上，简洁但难以测试且隐藏了依赖关系）。构造器注入因为不依赖反射、支持 final 字段、显式声明依赖而成为官方推荐方式。DI 的核心价值在于解耦——业务代码只依赖接口抽象，具体实现由容器装配，方便切换和 Mock。常见坑点：字段注入导致测试时必须启动 Spring 容器、多个构造器时需显式标注 `@Autowired`、`@Autowired(required = false)` 可构造可选注入。

## 相关术语

- [[wiki/glossary/java-basic/IoC|IoC]] — 控制反转设计原则，DI 是其具体实现方式
- [[wiki/glossary/java-basic/Bean|Bean]] — Spring IoC 容器管理的对象，通过 DI 完成依赖装配
- [[wiki/glossary/java-basic/AOP|AOP]] — 面向切面编程，依赖注入同样适用于切面中的依赖管理

## 深入阅读

- [[_posts/Java-basic/16-spring-ioc-aop|Java基础(16) | Spring 核心思想：IoC 与 AOP 到底解决了什么问题]]
