---
title: JDK
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - jdk
type: glossary
source_series: Java-basic
status: seed
---

# JDK（Java Development Kit）

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

JDK 是 Java 开发工具包，包含 JRE（JVM + 核心类库）以及编译器（javac）、调试器（jdb）、反编译工具（javap）、打包工具（jar）等开发工具。它是 Java 开发者的必备安装环境。

## 上下文

JDK 是 Java 技术栈的最外层——JDK superset JRE superset JVM，层层包含。从 Java 11 开始，Oracle 不再单独提供 JRE 下载，JDK 成为唯一的发行单元。开发时需要 JDK（编译和调试），生产环境以往只需 JRE，但现在通常也直接部署 JDK。

常见的 JDK 发行版包括 Oracle JDK、OpenJDK、Amazon Corretto、Azul Zulu 等。不同发行版的 JVM 实现和核心类库基本一致，区别主要在更新策略、商业支持和附加工具上。

## 相关术语

- [[wiki/glossary/java-basic/JVM|JVM]] — JDK 内部执行字节码的虚拟机，JDK 包含 JVM 作为其运行时核心
- [[wiki/glossary/java-basic/类加载|类加载]] — JVM 加载 .class 文件的过程，JDK 编译产物由类加载器载入 JVM 执行

## 深入阅读

- [[_posts/Java-basic/01-introduction|java-basics(1) | 从源码到运行：理解Java程序的一生]]
