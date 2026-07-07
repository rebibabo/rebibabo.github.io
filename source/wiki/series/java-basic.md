---
title: Java 基础系列
tags:
  - wiki
  - series
  - java
  - java-basic
type: series
source_series: Java-basic
status: seed
---

# Java 基础系列

[[wiki/index|返回 Wiki 首页]]
[[wiki/maps/java-basic|📖 Java 基础学习路径图]]
[[wiki/glossary/java-basic/index|📗 Java 基础词汇表]]

## 系列定位

这组文章是面向 Java 学习路径的主干系列，覆盖从语言基础、运行时、常用框架到工程实践的完整路线。

它不是按“面试题词条”拆开的，而是按“从会写到会理解，再到会做项目”的节奏推进。

## 这个系列回答什么问题

- Java 程序到底是怎么从源码走到运行的
- 语言层面的类、泛型、异常、集合、Lambda、I/O 应该怎么系统理解
- JVM、并发、注解、反射、构建工具在工程里分别解决什么问题
- Spring、Spring Boot、MyBatis、Redis、HTTP 调用这些常见基础设施怎么串起来
- 团队开发、测试、Git、消息队列、Tomcat 这些工程问题应该怎么建立整体认知

## 推荐阅读顺序

1. [[_posts/Java-basic/01-introduction|java-basics(1) | 从源码到运行：理解Java程序的一生]]
2. [[_posts/Java-basic/02-basic-types|java-basics(2) | 基本数据类型：八大原始类型与那些必踩的坑]]
3. [[_posts/Java-basic/03-collections|java-basics(3) | 集合框架：List、Set、Map 与队列全梳理]]
4. [[_posts/Java-basic/04-basic-class|java-basics(4) | 类与对象：构造方法、访问控制、static 与 final]]
5. [[_posts/Java-basic/05-advanced-class|java-basics(5) | 继承与多态：extends、重写、抽象类与接口]]
6. [[_posts/Java-basic/06-genrics|java-basics(6) | 泛型：类型擦除、通配符与 PECS 原则]]
7. [[_posts/Java-basic/07-exception|java-basics(7) | 异常体系：Checked vs Unchecked 与 try-with-resources]]
8. [[_posts/Java-basic/08-lambda-and-stream|java-basics(8) | Lambda 与 Stream API：函数式编程核心工具]]
9. [[_posts/Java-basic/09-io|java-basics(9) | I/O 与文件操作：从 BIO 到 NIO 与 Files 工具类]]
10. [[_posts/Java-basic/10-concurrency|java-basics(10) | 并发编程：线程、锁、线程池与 CompletableFuture]]
11. [[_posts/Java-basic/11-jvm|java-basics(11) | JVM 基础：内存结构、类加载与垃圾回收]]
12. [[_posts/Java-basic/12-annotation-and-reflection|java-basics(12) | 注解与反射：框架背后的魔法]]
13. [[_posts/Java-basic/13-enum|java-basics(13) | 枚举：不只是常量，还能做策略模式和单例]]
14. [[_posts/Java-basic/14-datetime|java-basics(14) | 日期时间 API：java.time 全梳理]]
15. [[_posts/Java-basic/15-maven-and-gradle|java-basics(15) | 构建工具：Maven vs Gradle，依赖管理与项目结构]]
16. [[_posts/Java-basic/16-spring-ioc-aop|java-basics(16) | Spring 核心思想：IoC 与 AOP 到底解决了什么问题]]
17. [[_posts/Java-basic/17-springboot|java-basics(17) | Spring Boot 快速上手：自动配置与 REST 服务实战]]
18. [[_posts/Java-basic/18-mybatis|java-basics(18) | MyBatis 数据访问：SQL 映射、动态 SQL 与 MyBatis-Plus]]
19. [[_posts/Java-basic/19-design-patterns|java-basics(19) | 设计模式：Java 中最常见的几种模式实战]]
20. [[_posts/Java-basic/20-unit-testing|java-basics(20) | 单元测试：JUnit 5 + Mockito 实战]]
21. [[_posts/Java-basic/21-redis|java-basics(21) | Redis 实战：Spring Data Redis 与缓存策略]]
22. [[_posts/Java-basic/22-http-client|java-basics(22) | HTTP 客户端：RestTemplate、WebClient 与远程调用]]
23. [[_posts/Java-basic/23-sql-advanced-syntax|java-basics(23) | SQL 进阶语法：常用函数、CTE 与窗口函数]]
24. [[_posts/Java-basic/24-mysql-internals|java-basics(24) | MySQL 原理与优化：事务、存储引擎、索引与锁]]
25. [[_posts/Java-basic/25-claude-code|Claude Code 入门：日常对话、Skills 与 Subagents]]
26. [[_posts/Java-basic/26-dev-conventions|java-basics(番外) | 开发规范全集：命名、代码、目录、文档、Git 一站式速查]]
27. [[_posts/Java-basic/27-dev-workflow|java-basics(番外) | 团队开发全流程：从需求到上线的完整链路]]
28. [[_posts/Java-basic/28-git-essentials|java-basics(番外) | Git 日常操作实战：从提交到协作全流程]]
29. [[_posts/Java-basic/29-tomcat-servlet|java-basics(番外) | Tomcat 与 Servlet：Spring Boot 背后的请求处理流程]]
30. [[_posts/Java-basic/30-RabbitMQ|java-basics(番外) | 消息队列入门：为什么用、怎么用、踩坑点]]
31. [[_posts/Java-basic/31-kafka|java-basics(番外) | Kafka 入门：分区、副本与消费者组原理]]
32. [[_posts/Java-basic/32-data-structure-internals|java-basics(番外) | 集合的底层原理：HashMap、ArrayList 与红黑树]]

## 结构脉络

### 1. 语言与基础语法

- [[_posts/Java-basic/01-introduction|01-introduction]]
- [[_posts/Java-basic/02-basic-types|02-basic-types]]
- [[_posts/Java-basic/03-collections|03-collections]]
- [[_posts/Java-basic/04-basic-class|04-basic-class]]
- [[_posts/Java-basic/05-advanced-class|05-advanced-class]]
- [[_posts/Java-basic/06-genrics|06-genrics]]
- [[_posts/Java-basic/07-exception|07-exception]]
- [[_posts/Java-basic/08-lambda-and-stream|08-lambda-and-stream]]
- [[_posts/Java-basic/09-io|09-io]]

### 2. 运行时与核心机制

- [[_posts/Java-basic/10-concurrency|10-concurrency]]
- [[_posts/Java-basic/11-jvm|11-jvm]]
- [[_posts/Java-basic/12-annotation-and-reflection|12-annotation-and-reflection]]
- [[_posts/Java-basic/13-enum|13-enum]]
- [[_posts/Java-basic/14-datetime|14-datetime]]
- [[_posts/Java-basic/15-maven-and-gradle|15-maven-and-gradle]]

### 3. 框架与后端工程

- [[_posts/Java-basic/16-spring-ioc-aop|16-spring-ioc-aop]]
- [[_posts/Java-basic/17-springboot|17-springboot]]
- [[_posts/Java-basic/18-mybatis|18-mybatis]]
- [[_posts/Java-basic/21-redis|21-redis]]
- [[_posts/Java-basic/22-http-client|22-http-client]]
- [[_posts/Java-basic/23-sql-advanced-syntax|23-sql-advanced-syntax]]
- [[_posts/Java-basic/24-mysql-internals|24-mysql-internals]]
- [[_posts/Java-basic/29-tomcat-servlet|29-tomcat-servlet]]
- [[_posts/Java-basic/30-RabbitMQ|30-RabbitMQ]]
- [[_posts/Java-basic/31-kafka|31-kafka]]

### 4. 设计、测试与开发工作流

- [[_posts/Java-basic/19-design-patterns|19-design-patterns]]
- [[_posts/Java-basic/20-unit-testing|20-unit-testing]]
- [[_posts/Java-basic/25-claude-code|25-claude-code]]
- [[_posts/Java-basic/26-dev-conventions|26-dev-conventions]]
- [[_posts/Java-basic/27-dev-workflow|27-dev-workflow]]
- [[_posts/Java-basic/28-git-essentials|28-git-essentials]]
- [[_posts/Java-basic/32-data-structure-internals|32-data-structure-internals]]

## 当前这页的作用

这页是 Java 基础系列的“路线图”，帮你决定先读哪一块、某篇文章在整套体系里处于什么位置。

## Wiki 概念页

本系列的 wiki 概念层已拆分为 **15 个一级概念 + 39 个二级概念**，共 55 个页面。

入口：[[wiki/concepts/java-basic/Java-Basic-概念总图|Java-Basic 概念总图]]

### 一级概念
1. [[wiki/concepts/java-basic/Java-程序如何运行|Java 程序如何运行]]
2. [[wiki/concepts/java-basic/数据类型|数据类型]]
3. [[wiki/concepts/java-basic/面向对象|面向对象]]
4. [[wiki/concepts/java-basic/泛型|泛型]]
5. [[wiki/concepts/java-basic/集合框架|集合框架]]
6. [[wiki/concepts/java-basic/异常|异常]]
7. [[wiki/concepts/java-basic/Lambda与Stream|Lambda 与 Stream]]
8. [[wiki/concepts/java-basic/IO|I/O]]
9. [[wiki/concepts/java-basic/并发|并发]] → [[wiki/concepts/concurrency/并发总图|并发概念总图]]
10. [[wiki/concepts/java-basic/JVM|JVM]]
11. [[wiki/concepts/java-basic/注解与反射|注解与反射]]
12. [[wiki/concepts/java-basic/构建工具|构建工具]]
13. [[wiki/concepts/java-basic/Spring|Spring]]
14. [[wiki/concepts/java-basic/数据访问|数据访问]]
15. [[wiki/concepts/java-basic/工程实践|工程实践]]

### 快速参考
- [[wiki/glossary/java-basic/index|Java 基础词汇表]] — 110+ 术语速查
- [[wiki/maps/java-basic|Java 基础学习路径图]] — Mermaid 7 层依赖图
- [[wiki/maps/java-concurrency|Java 并发学习路径]] — 外部知识库
