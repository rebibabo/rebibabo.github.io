---
title: Gradle
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Gradle

[[wiki/concepts/java-basic/构建工具|返回构建工具]]

## 这一层回答什么问题

> Gradle 比 Maven 快在哪？`implementation` 和 `api` 有什么区别？什么时候选 Gradle？

Gradle 是基于 Groovy/Kotlin DSL 的构建工具。核心差异不是"XML vs DSL"——而是**增量编译**和**构建缓存**。

## 增量编译

Maven 每次 `mvn compile` 重新编译所有文件。Gradle 只编译改过的文件和依赖它的文件——其他部分直接用上次编译结果。大项目从几十秒降到几秒。

## implementation vs api

```kotlin
dependencies {
    implementation("com.google.guava:guava:33.0.0")  // 只在模块内部用
    api("com.fasterxml.jackson:jackson-databind")     // 暴露给下游模块
}
```

| 配置 | 编译时→下游 | 运行时→下游 |
|------|------------|------------|
| `implementation` | 不可见 | 可见 |
| `api` | 可见 | 可见 |
| `compileOnly` | 可见 | 不可见 |
| `runtimeOnly` | 不可见 | 可见 |

`implementation` 的依赖只在本模块内编译时可用，下游模块编译时看不到——修改内部依赖不用触发下游重新编译。Maven 没有这个区分，所有 compile 依赖都会暴露。

## 版本目录（Version Catalog）

`libs.versions.toml` 集中管理所有依赖版本——多模块项目不用在十几个 build.gradle 里重复写版本号。类似 Maven 的 `dependencyManagement`，但更直观。

## Maven vs Gradle 选型

| | Maven | Gradle |
|------|-------|--------|
| 构建速度 | 每次都全量 | 增量+缓存 |
| 配置 | XML（啰嗦但明确） | DSL（灵活） |
| 学习成本 | 低 | 中 |
| Spring 官方 | 支持 | 已迁移到 Gradle |
| 推荐 | 简单项目、遗留项目 | 新项目、多模块项目 |

## 在系列里的位置

post 15。

## 推荐回看原文

- [[_posts/Java-basic/15-maven-and-gradle|15-构建工具]]

## 相关概念

- [[wiki/concepts/java-basic/Maven|Maven]]
