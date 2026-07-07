---
title: JVM
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - jvm
type: glossary
source_series: Java-basic
status: seed
---

# JVM（Java Virtual Machine）

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

JVM 是执行 Java 字节码的虚拟机，是 Java "Write Once, Run Anywhere" 跨平台能力的核心。它负责加载 `.class` 文件、解释执行字节码（配合 JIT 编译优化）、管理内存和垃圾回收。

## 上下文

JVM 本身是平台相关的——macOS 的 JVM 和 Linux 的 JVM 是不同的二进制程序，但它们对上层暴露统一的字节码接口。JVM 内部包含类加载器、字节码解释器、JIT 编译器、垃圾回收器和内存管理模块。

JVM 的内存区域主要包括堆（对象实例）、栈（线程私有，栈帧）、方法区（类信息、常量池、元空间）和程序计数器。此外，JVM 通过 JMM（Java Memory Model）定义了多线程下的内存可见性规则，是理解并发编程的基础。

## 相关术语

- [[wiki/glossary/java-basic/JDK|JDK]] — Java 开发工具包，JVM 是 JDK 的核心组成部分，JDK 还包含编译器等开发工具
- [[wiki/glossary/java-basic/类加载|类加载]] — JVM 加载类的机制，类加载器将字节码读入 JVM 并完成链接和初始化
- [[wiki/glossary/java-basic/垃圾回收|垃圾回收]] — JVM 自动管理堆内存的机制，回收不再被引用的对象

## 深入阅读

- [[_posts/Java-basic/01-introduction|java-basics(1) | 从源码到运行：理解Java程序的一生]]
- [[_posts/Java-basic/11-jvm|java-basics(11) | JVM 内存模型与垃圾回收]]
