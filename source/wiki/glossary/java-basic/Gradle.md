---
title: Gradle
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - gradle
type: glossary
source_series: Java-basic
status: seed
---

# Gradle

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Gradle 是基于 Groovy/Kotlin DSL 的现代化构建工具，支持增量构建、构建缓存和按需配置，比 Maven 更灵活高效。

## 上下文

Gradle 使用 `build.gradle`（Groovy DSL）或 `build.gradle.kts`（Kotlin DSL）作为构建脚本，比 XML 更简洁。其核心优势在于增量构建——只重新执行输入输出发生变化的 task，大幅缩短构建时间。Gradle Wrapper（`gradlew`）确保团队使用统一 Gradle 版本，无需预装 Gradle。依赖管理使用 `implementation`、`api`、`compileOnly` 等配置来区分传递性。Android 开发默认使用 Gradle 作为官方构建工具。常见坑点：DSL 灵活性高但学习曲线陡、构建脚本逻辑过多时难以维护、多模块项目配置需要理解 `subprojects`/`allprojects` 闭包的执行时机。

## 相关术语

- [[wiki/glossary/java-basic/Maven|Maven]] — Apache 旗下的 Java 项目构建和依赖管理工具，基于 XML 配置
- [[wiki/glossary/java-basic/依赖传递|依赖传递]] — 构建工具自动引入间接依赖的机制，Gradle 通过 `api`/`implementation` 控制传递性

## 深入阅读

- [[_posts/Java-basic/15-maven-and-gradle|Java基础(15) | 构建工具：Maven vs Gradle，依赖管理与项目结构]]
