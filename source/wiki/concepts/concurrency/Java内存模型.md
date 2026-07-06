---
title: Java Memory Model
tags:
  - wiki
  - concept
  - concurrency
  - jmm
type: concept
source_series: concurrency
status: seed
---

# Java Memory Model

[[wiki/concepts/concurrency/并发总图|返回并发总图]]

## 定义

Java Memory Model，通常简称 `JMM`，关注的是：

> 一个线程的写入，在什么条件下必须被另一个线程看到；哪些重排序结果被允许，哪些不被允许。

## 这一层解释什么

- `count++` 为什么会出错
- `volatile` 到底保证了什么
- `happens-before` 在语言层面规定了什么顺序
- 可见性、原子性、有序性为什么要分开看

## JMM 不是物理结构图

JMM 最容易被误会成“线程工作内存 + 主内存”的一张结构图。

这个类比可以帮助入门，但它不是要你把 Java 运行时真的想成某种固定硬件布局。JMM 真正关心的是：

> 某次读允许看到哪次写，哪些重排结果是合法的，哪些必须被排除。

也就是说，JMM 描述的是并发语义规则，不是寄存器、Cache、DRAM 的实物图纸。

## 它为什么必须存在

Java 程序最终会跑在不同 CPU 和 JVM 上：

- 不同 CPU 的内存顺序保证不同
- JIT 会做优化
- CPU 自己也会做乱序执行、写缓冲、缓存回写等处理

如果语言层没有统一规则，那么同一段并发代码换一台机器就可能出现完全不同的行为。

JMM 的作用，就是在这些底层差异之上，给 Java 程序员一个可以依赖的统一约定。

## 它在协调哪三层东西

可以把 JMM 看成三层之间的对齐器：

- 上层：Java 程序希望表达的并发语义
- 中层：JVM 和 JIT 如何生成、优化指令
- 下层：CPU / Cache / Store Buffer / 内存系统真实怎么执行

它并不禁止所有优化，而是规定：

> 哪些优化不能破坏线程之间本该成立的可见性和顺序关系。

## program order 为什么不够

单个线程内部当然有自己的代码顺序，这通常叫 `program order`。

例如线程 A 里先写 `data`，再写 `ready`，这是它自己的程序顺序；但这个事实本身，并不会自动推出另一个线程必须按同样顺序观察到这两个写入。

所以并发里很关键的一点是：

- 线程内部顺序存在
- 但线程之间默认没有自动拼成一条全局顺序

这就是为什么“源码明明先写了 data，再写 ready”，另一个线程仍然可能只看到后者、没看到前者。

## 它和硬件的关系

JMM 不是物理内存结构图，而是 Java 在不同 CPU 和 JVM 实现之上定义的一套统一并发语义。

它站在：

- 上层语言语义
- 下层 CPU / Cache / 编译器优化

之间，负责把“底层允许做的事”和“Java 程序员能依赖的结果”对齐起来。

## 它最核心的几个词

### 可见性

一个线程写入的结果，另一个线程什么时候必须能看到。

### 有序性

多个操作对其他线程暴露时，要遵守什么顺序约束。

### 原子性

一个操作能不能被拆成多步，并在中间被其他线程插入。

这三件事经常一起出现，但不是一回事。

例如：

- `volatile` 主要解决可见性和部分有序性
- `count++` 的问题主要是原子性
- 锁通常同时提供可见性和互斥

## JMM 怎么连接两个线程

JMM 不会默认让所有线程彼此同步，它依赖特定规则建立“跨线程连接”。

这些连接包括：

- `volatile` 写与后续对同一变量的读
- 同一把锁的解锁与后续加锁
- `Thread.start()`
- 线程结束与 `join()`

这些规则最终会汇总到 [[wiki/concepts/concurrency/Happens-Before|happens-before]] 这个统一框架里。

## 什么叫数据竞争

如果两个线程访问同一个变量，并且至少有一个是写，而且这两个操作之间没有 happens-before，那么就存在数据竞争。

一旦进入数据竞争区间，Java 往往就不再承诺你期望中的那种稳定结果。

这也是为什么：

- 某段代码跑很多次都“看起来没事”
- 也不能证明它真的是线程安全的

## 它回答的不是“现实里先后”，而是“语义上能依赖什么”

JMM 里的顺序规则，并不等于墙上时钟的真实先后顺序。

它更像是在说：

- 哪些结果必须对别的线程可见
- 哪些重排结果必须被排除
- 程序员到底能安全依赖哪些事实

所以学 JMM，本质上是在学：

> 写并发代码时，哪些观察结果是受保证的，哪些只是“碰巧现在跑出来了”。

## 在系列里的位置

它是执行模型和同步机制之间的桥梁。

很多同步原语之所以成立，最终都要回到 JMM 对可见性和顺序的规定。

## 推荐回看原文

- [[_posts/concurrency/02-为什么count++会出错|02-为什么 count++ 会出错]]
- [[_posts/concurrency/07-volatile到底解决了什么问题|07-volatile 到底解决了什么问题]]
- [[_posts/concurrency/08-Java内存到底规定什么|08-Java 内存模型到底规定了什么]]

## 相关概念

- [[wiki/concepts/concurrency/执行模型|执行模型]]
- [[wiki/concepts/concurrency/Happens-Before|happens-before]]
- [[wiki/concepts/concurrency/缓存一致性|缓存一致性]]
- [[wiki/concepts/concurrency/volatile|volatile]]
- [[wiki/concepts/concurrency/CAS|CAS]]
- [[wiki/concepts/concurrency/同步机制|同步机制]]
- [[wiki/concepts/concurrency/故障模式|故障模式与安全停止]]
