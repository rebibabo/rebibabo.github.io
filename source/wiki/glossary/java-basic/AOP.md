---
title: AOP
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

# AOP（面向切面编程）

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

AOP（Aspect-Oriented Programming）将横切关注点（如日志、事务、权限校验）从核心业务逻辑中分离出来，以"切面"的形式统一管理和织入，避免代码重复。

## 上下文

Spring AOP 基于动态代理实现：有接口时使用 JDK 动态代理（`java.lang.reflect.Proxy`），无接口时使用 CGLIB 字节码生成代理子类。核心概念包括：切面（Aspect，切点和通知的组合）、通知（Advice：@Before / @After / @Around / @AfterReturning / @AfterThrowing）、切入点（Pointcut：基于 execution / annotation 表达式指定拦截位置）、连接点（JoinPoint：方法执行点）。@Around 是最强大的通知类型，可控制目标方法的执行与否和参数修改，但必须手动调用 `ProceedingJoinPoint.proceed()`。AOP 最常见的应用场景是声明式事务（`@Transactional`）——Spring 通过 AOP 在方法执行前后管理事务。常见坑点：同类内部方法调用不会触发 AOP（代理对象而非目标对象调用自身方法时绕过代理）、@Async 和 @Transactional 自调用失效同理。

## 相关术语

- [[wiki/glossary/java-basic/IoC|IoC]] — AOP 切面的织入由 IoC 容器在 Bean 初始化阶段完成
- [[wiki/glossary/java-basic/动态代理|动态代理]] — Spring AOP 的底层实现机制（JDK 动态代理 / CGLIB）
- [[wiki/glossary/java-basic/事务|事务]] — AOP 最经典的应用场景，通过 `@Transactional` 声明式管理事务

## 深入阅读

- [[_posts/Java-basic/16-spring-ioc-aop|Java基础(16) | Spring 核心思想：IoC 与 AOP 到底解决了什么问题]]
