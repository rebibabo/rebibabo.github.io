---
title: MyBatis
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - mybatis
  - database
type: glossary
source_series: Java-basic
status: seed
---

# MyBatis

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

MyBatis 是一款半自动的 ORM（对象关系映射）框架，将 SQL 语句与 Java 代码解耦，通过 XML 映射文件或注解定义 SQL，支持动态 SQL 和结果集自动映射。

## 上下文

与全自动 ORM（如 Hibernate/JPA）不同，MyBatis 将 SQL 控制权完全交给开发者，不自动生成 SQL，因此更适合复杂查询和对 SQL 有精确优化需求的场景。核心组件：SqlSessionFactory（会话工厂，全局唯一）、SqlSession（数据库会话，线程不安全）、Mapper 接口（定义数据库操作的方法签名）、映射文件（XML 或注解，定义 SQL 与 Java 对象的映射关系）。MyBatis-Plus 是其增强工具，提供通用 CRUD（BaseMapper）、条件构造器（QueryWrapper / UpdateWrapper）和分页插件，大幅减少样板代码。常见坑点：Mapper XML 的 namespace 与接口路径不一致、resultType 和 resultMap 混淆导致映射失败、参数类型为基本类型时 XML 中只能用 `_parameter` 引用。

## 相关术语

- [[wiki/glossary/java-basic/动态SQL|动态SQL]] — MyBatis 核心特性，通过 XML 标签根据参数条件动态拼接 SQL
- [[wiki/glossary/java-basic/事务|事务]] — 数据库事务管理，MyBatis 配合 `@Transactional` 实现声明式事务
- [[wiki/glossary/java-basic/SpringBoot|SpringBoot]] — MyBatis 通常通过 `mybatis-spring-boot-starter` 集成到 Spring Boot 中

## 深入阅读

- [[_posts/Java-basic/18-mybatis|java-basics(18) | MyBatis 数据访问：SQL 映射、动态 SQL 与 MyBatis-Plus]]
