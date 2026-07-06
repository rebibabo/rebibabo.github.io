---
title: Happens-Before
tags:
  - wiki
  - glossary
  - concurrency
  - happens-before
type: glossary
source_series: concurrency
status: seed
---

# Happens-Before（先行发生）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

Happens-Before 是 JMM 判断两个操作之间是否具有可见性保证的偏序规则。如果操作 A Happens-Before 操作 B，那么 A 对共享变量的所有修改，B 都能看到。

## 上下文

JMM 提供了以下关键 Happens-Before 规则：程序次序规则（同一线程内前面的操作 Happens-Before 后面的）、锁规则（unlock Happens-Before 后续的 lock）、volatile 规则（volatile 写 Happens-Before 后续的 volatile 读）、传递性（A Happens-Before B 且 B Happens-Before C，则 A Happens-Before C）、线程启动规则（start() Happens-Before 线程内操作）、线程终止规则（线程内操作 Happens-Before join() 返回）。

不需要死记这些规则——核心逻辑是：通过锁、volatile、线程操作这些"同步动作"，JMM 定义了修改传播的边界。

## 相关术语

- [[wiki/glossary/concurrency/JMM|JMM]] — Happens-Before 是 JMM 的核心
- [[wiki/glossary/concurrency/volatile|volatile]] — volatile 读写之间建立 Happens-Before
- [[wiki/glossary/concurrency/内存屏障|Memory Barrier]] — 硬件层实现 Happens-Before 的手段

## 深入阅读

- [[wiki/concepts/concurrency/Happens-Before|Happens-Before 概念页（完整版）]]
- [[_posts/concurrency/08-Java内存到底规定什么|08-Java 内存模型]]
