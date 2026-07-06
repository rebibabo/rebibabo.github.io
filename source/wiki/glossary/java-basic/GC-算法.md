---
title: GC 算法
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# GC 算法

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

GC 算法是垃圾回收器回收堆内存的核心策略，主要包括标记-清除、标记-复制、标记-整理三种基本算法，分别适用于不同的内存区域。

## 上下文

**标记-清除（Mark-Sweep）**：先标记所有可达对象，再清除未标记的对象。实现简单但会产生内存碎片，导致大对象分配困难。**标记-复制（Copying）**：将内存分为两块，每次只用一块；GC 时将存活对象复制到另一块，清空当前块。无碎片且分配快（指针碰撞），但可用内存减半。新生代使用此算法的优化版（Eden + S0 + S1，大部分对象都是垃圾，需要复制的很少）。**标记-整理（Mark-Compact）**：标记后不直接清除，而是将存活对象向一端移动，清理边界外内存。无碎片但移动对象开销大，老年代使用此算法。不同垃圾回收器对算法的应用不同：G1 综合使用复制和整理，ZGC 使用着色指针和读屏障实现并发整理。

## 相关术语
- [[wiki/glossary/java-basic/垃圾回收|垃圾回收]] — GC 算法是垃圾回收器回收内存的核心策略
- [[wiki/glossary/java-basic/新生代|新生代]] — 使用标记-复制算法，适合"朝生夕死"的对象
- [[wiki/glossary/java-basic/老年代|老年代]] — 使用标记-整理算法，适合长期存活的对象

## 深入阅读

- [[_posts/Java-basic/11-jvm|Java基础(11) | JVM 基础：内存结构、类加载与垃圾回收]]
