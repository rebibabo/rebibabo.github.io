---
title: Java 程序如何运行
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Java 程序如何运行

[[wiki/concepts/java-basic/Java-Basic-概念总图|返回概念总图]]

## 这一层回答什么问题

> 一个 `.java` 文件是怎么变成运行中的程序的？JDK、JRE、JVM 各负责什么？

这是 Java 知识体系的入口。在理解任何具体语法之前，先看清楚一条代码从"写出来"到"跑起来"的完整路径。

## 核心流程

```
.java 源码 → javac 编译 → .class 字节码 → JVM 加载执行
```

- **javac**：把你写的 `.java` 编译成 `.class` 字节码。字节码不是机器码，是给 JVM 看的一种中间表示。
- **JVM**：把字节码转成机器指令跑起来。HotSpot 采用"解释 + JIT 编译"的混合模式。
- **为什么不直接编译成机器码？** — 一份字节码可以在任何安装了 JVM 的平台上跑。C++ 需要为 Windows / Linux / Mac 各编译一次。

## JDK ⊃ JRE ⊃ JVM

```
┌─────────────────────────────────┐
│ JDK                             │
│  ┌───────────────────────────┐  │
│  │ JRE                       │  │
│  │  ┌─────────────────────┐  │  │
│  │  │ JVM                 │  │  │
│  │  │ 类加载 · 执行引擎 · GC │  │  │
│  │  └─────────────────────┘  │  │
│  │  核心类库 (rt.jar / modules)│  │
│  └───────────────────────────┘  │
│  javac · jar · jshell · jdb ... │
└─────────────────────────────────┘
```

| 缩写 | 全称 | 角色 |
|------|------|------|
| JVM | Java Virtual Machine | 执行字节码 |
| JRE | Java Runtime Environment | JVM + 核心类库，运行环境 |
| JDK | Java Development Kit | JRE + 编译器等开发工具 |

Java 11 之后 Oracle 不再单独发布 JRE，JDK 自带运行时。

## 与其他语言的关键差异

| 维度 | Java | C++ | Python |
|------|------|-----|--------|
| 编译产物 | 字节码（跨平台） | 机器码（平台相关） | 不编译（.pyc 是缓存） |
| 运行依赖 | JVM | 操作系统 | 解释器 |
| 内存管理 | GC 自动 | 手动 new / delete | GC 自动 |
| 速度 | 较快（JIT） | 很快 | 较慢 |

## 在系列里的位置

这是整个 Java 知识树的根节点。后续所有内容——基本类型、OOP、JVM——都从这里展开。

## 推荐回看原文

- [[_posts/Java-basic/01-introduction|01-从源码到运行：理解Java程序的一生]]

## 相关概念

- [[wiki/concepts/java-basic/JVM|JVM]]
- [[wiki/concepts/java-basic/构建工具|构建工具]] — javac 只是编译，Maven/Gradle 管理整个构建流程
