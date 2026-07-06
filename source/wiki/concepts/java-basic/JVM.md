---
title: JVM
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# JVM

[[wiki/concepts/java-basic/Java-Basic-概念总图|返回概念总图]]

## 这一层回答什么问题

> Java 代码跑起来之后，JVM 内部到底发生了什么？内存怎么分配？类怎么加载？垃圾怎么回收？

这一层关心的是"代码在 JVM 里怎么活"。它不教你写更优雅的 Java，但教你在线上 Full GC 频繁、OOM 崩溃时知道往哪看。

## 这层的主要分支

- [[wiki/concepts/java-basic/类加载|类加载]] — 类的生命周期、双亲委派模型、打破委派的场景
- [[wiki/concepts/java-basic/内存结构|内存结构]] — 堆/栈/方法区/程序计数器、各区域 OOM
- [[wiki/concepts/java-basic/垃圾回收|垃圾回收]] — 可达性分析、三种算法、Serial → ZGC 演进

---

### 内存结构

JVM 把内存分成几个区域，各有各的职责和 OOM 风险：

| 区域 | 存放什么 | 线程 | OOM 表现 |
|------|----------|------|----------|
| 堆 | 对象实例、数组 | 共享 | `Java heap space` |
| 虚拟机栈 | 栈帧（局部变量、操作数栈） | 私有 | `StackOverflowError` |
| 方法区/元空间 | 类信息、常量、静态变量 | 共享 | `Metaspace` |
| 程序计数器 | 当前字节码行号 | 私有 | 不会 OOM |

堆是 GC 的主战场，分新生代（Eden + S0 + S1）和老年代。对象先在 Eden 创建，熬过几次 Minor GC 后晋升到老年代。

### 类加载

`.class` 文件不是一次性全部加载的——按需加载。过程：**加载 → 验证 → 准备 → 解析 → 初始化**。

**双亲委派模型**：一个类加载器收到请求，先问父加载器能不能加载。父加载器能，就不自己加载。这条链（Bootstrap → Extension → Application）保证了核心类（如 `java.lang.String`）不会被自定义类替换。

### 垃圾回收

**怎么判断可以回收？** 可达性分析——从 GC Roots（栈引用、静态变量、常量）出发，不可达的就是垃圾。引用计数法 Java 不用，因为解决不了循环引用。

**三种基本算法：**

| 算法 | 做法 | 代价 |
|------|------|------|
| 标记-清除 | 标记垃圾 → 清除 | 碎片 |
| 标记-复制 | 存活对象移到另一区 → 清空原区 | 浪费一半空间 |
| 标记-整理 | 存活对象移到一端 → 清理边界外 | 耗时 |

新生代用标记-复制（对象朝生夕死），老年代用标记-清除或标记-整理。

**垃圾回收器演进**：Serial → Parallel → CMS → G1（Java 9+ 默认，分区 Region、可预测暂停）→ ZGC（TB 级堆、<1ms STW）。每次升级都在降低"Stop The World"的暂停时间。

## 为什么 JVM 是分水岭

写 CRUD 不需要 JVM 知识。但一旦线上频繁 Full GC、接口响应抖动，或者 OOM 之后分不清是内存泄漏还是正常压力——JVM 知识就从"面试题"变成"排查工具"。

## 在系列里的位置

post 11。在 I/O 之后——理解 I/O 的阻塞模型有助于理解 NIO 在 JVM 层的实现差异。

## 推荐回看原文

- [[_posts/Java-basic/11-jvm|11-JVM 基础]]

## 相关概念

- [[wiki/concepts/java-basic/Java-程序如何运行|Java 程序如何运行]] — JVM 是 Java 程序的运行平台
- [[wiki/concepts/java-basic/注解与反射|注解与反射]] — 反射创建大量动态类会撑爆元空间
- [[wiki/concepts/java-basic/Spring|Spring]] — Spring 容器是在 JVM 堆上管理 Bean
