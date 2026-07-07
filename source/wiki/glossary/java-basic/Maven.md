---
title: Maven
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - maven
type: glossary
source_series: Java-basic
status: seed
---

# Maven

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Maven 是 Apache 旗下的 Java 项目构建和依赖管理工具，通过 `pom.xml` 文件描述项目的 GAV 坐标（groupId、artifactId、version）、依赖关系和构建生命周期。

## 上下文

Maven 采用"约定优于配置"原则，规定标准目录结构（`src/main/java`、`src/main/resources`、`src/test/java`），并提供 clean、compile、test、package、install、deploy 等标准生命周期阶段。依赖从中央仓库（Maven Central）下载到本地仓库 `~/.m2`，通过 GAV 坐标唯一定位。插件体系（如 maven-compiler-plugin、spring-boot-maven-plugin）扩展了各生命周期的行为。常见坑点：依赖版本冲突不易排查、pom.xml 随着项目规模膨胀变得冗长、需要理解 scope（compile/provided/runtime/test）对传递性的影响。

## 相关术语

- [[wiki/glossary/java-basic/Gradle|Gradle]] — 基于 Groovy/Kotlin DSL 的现代化构建工具，比 Maven 更灵活高效
- [[wiki/glossary/java-basic/依赖传递|依赖传递]] — 构建工具自动引入间接依赖的机制，Maven 通过 scope 控制传递性
- [[wiki/glossary/java-basic/依赖冲突|依赖冲突]] — 传递依赖引入不同版本的同一库，需通过排除和版本锁定解决

## 深入阅读

- [[_posts/Java-basic/15-maven-and-gradle|java-basics(15) | 构建工具：Maven vs Gradle，依赖管理与项目结构]]
