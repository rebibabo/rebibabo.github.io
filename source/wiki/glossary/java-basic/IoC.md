---
title: IoC
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

# IoC（控制反转）

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

IoC（Inversion of Control）是一种设计原则，将对象创建、依赖管理和生命周期控制的职责从调用方转移给容器（如 Spring IoC 容器），实现"谁调用谁控制"到"容器统一控制"的翻转。

## 上下文

在传统编程中，对象直接通过 `new` 创建依赖，导致代码强耦合、难以测试。IoC 容器接管了对象的创建和装配——开发者只需声明依赖关系，由容器在运行时注入。Spring 的 ApplicationContext 是最常用的 IoC 容器实现，通过读取配置（XML、注解、Java Config）完成 Bean 的实例化和依赖注入。IoC 是实现 DI 的前提，依赖注入是 IoC 的具体实现方式。常见坑点：循环依赖、Bean 作用域理解不透（singleton vs prototype）、容器启动慢（Bean 数量过多时）。

## 相关术语

- [[wiki/glossary/java-basic/DI|DI]] — IoC 的具体实现方式，容器自动将依赖注入到目标对象中
- [[wiki/glossary/java-basic/Bean|Bean]] — Spring IoC 容器管理的对象实例，由容器控制其全生命周期
- [[wiki/glossary/java-basic/AOP|AOP]] — 面向切面编程，Spring 通过 IoC 容器管理切面的织入

## 深入阅读

- [[_posts/Java-basic/16-spring-ioc-aop|java-basics(16) | Spring 核心思想：IoC 与 AOP 到底解决了什么问题]]
