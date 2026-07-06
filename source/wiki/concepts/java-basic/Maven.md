---
title: Maven
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Maven

[[wiki/concepts/java-basic/构建工具|返回构建工具]]

## 这一层回答什么问题

> pom.xml 里的坐标和 scope 各管什么？依赖冲突了怎么办？mvn clean install 做了哪些步骤？

Maven 是基于 `pom.xml` 的声明式构建工具。它不编译代码——它管理编译、测试、打包、依赖的整个生命周期。

## GAV 坐标

`groupId:artifactId:version` 三者唯一确定一个依赖。Maven 通过坐标从仓库（本地 `.m2` → 私服 → Maven Central）拉依赖。

## 依赖范围（Scope）

| scope | 编译 | 测试 | 运行时 | 典型 |
|-------|------|------|--------|------|
| compile（默认） | ✓ | ✓ | ✓ | spring-core |
| provided | ✓ | ✓ | ✗ | servlet-api |
| runtime | ✗ | ✓ | ✓ | mysql-connector |
| test | ✗ | ✓ | ✗ | junit |

**关键理解**：`provided` 的 jar 编译时有，但运行时不打包——Tomcat 容器自己提供 servlet-api。`runtime` 的 jar 编译时不需要，运行时才需要——JDBC 驱动由 `Class.forName` 动态加载。

## 依赖传递与冲突

A 依赖 B(v1)，B 依赖 C(v2) → A 自动依赖 C(v2)。如果 A 也直接依赖 C(v1)，Maven 选**最短路径**——v1 覆盖 v2。

`<exclusion>` 明确排除某个传递依赖。`dependencyManagement` 统一管理版本——子模块只写 groupId:artifactId，版本从父 POM 继承。

## 生命周期

`validate → compile → test → package → verify → install → deploy`。后一个阶段自动执行前面所有的阶段。

`mvn clean install` = clean（删除 target/）+ install（打 jar 装到本地仓库）。

## 在系列里的位置

post 15。

## 推荐回看原文

- [[_posts/Java-basic/15-maven-and-gradle|15-构建工具]]

## 相关概念

- [[wiki/concepts/java-basic/Gradle|Gradle]]
