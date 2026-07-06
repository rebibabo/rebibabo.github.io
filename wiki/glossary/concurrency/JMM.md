---
title: JMM
tags:
  - wiki
  - glossary
  - concurrency
  - jmm
type: glossary
source_series: concurrency
status: seed
---

# JMM（Java Memory Model，Java 内存模型）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

JMM 是 Java 语言规范中定义的一套多线程内存可见性规则。它不描述"内存硬件怎么工作"，而是规定：一个线程对共享变量做了修改，另一个线程什么时候一定能看到。

## 上下文

JMM 的核心是 **Happens-Before 规则**——它不靠猜测判断可见性，而是靠程序中的特定动作（锁释放、volatile 写、线程启动/join 等）建立偏序关系。程序员只需满足 Happens-Before 条件，JVM 保证相应的可见性。

JMM 最关键的三个承诺：`synchronized` 释放锁前所有修改对后续获取同一锁的线程可见；`volatile` 写对后续 volatile 读可见；`Thread.start()` 前所有修改对新线程可见。

## 相关术语

- [[wiki/glossary/concurrency/Happens-Before|Happens-Before]] — JMM 的核心规则体系
- [[wiki/glossary/concurrency/volatile|volatile]] — 基于 JMM 的轻量同步
- [[wiki/glossary/concurrency/内存屏障|Memory Barrier]] — JMM 在硬件层的实现手段

## 深入阅读

- [[wiki/concepts/concurrency/Java内存模型|JMM 概念页（完整版）]]
- [[_posts/concurrency/08-Java内存到底规定什么|08-Java 内存模型]]
