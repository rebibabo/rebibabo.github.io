---
title: ThreadPoolExecutor
tags:
  - wiki
  - concept
  - concurrency
  - threadpool
type: concept
source_series: concurrency
status: seed
---

# ThreadPoolExecutor

[[wiki/concepts/concurrency/异步执行|返回任务执行与异步编排]]

## 定义

`ThreadPoolExecutor` 是 Java 线程池执行模型最核心的实现。

## 它解决什么问题

它回答的是：

> 为什么任务不应该每次都自己 new Thread，以及线程池到底怎样复用线程、缓存任务、限制并发上限？

## 它最核心的思想：任务和线程分离

没有线程池时，常见做法是：

```java
new Thread(() -> handleRequest()).start();
```

这里“任务来了”和“创建一个新线程”几乎绑定在一起。

线程池做的第一件大事，就是把这两件事拆开：

- 任务：要做什么
- 线程：由谁来做

线程可以被复用，任务不断变化。这样系统就不用为每个任务反复创建和销毁线程。

## 为什么不能每个任务都 new Thread

原文这一章其实是在反复强调一个现实：

- 线程创建有成本
- 线程销毁有成本
- 线程太多会占内存
- 线程远多于 CPU Core 时，会带来大量上下文切换

所以线程池的目标不是“开更多线程”，而是：

> 用有限的工作线程，稳定处理持续到来的任务。

## 可以先把线程池看成三样东西

- 工作线程：真正执行任务
- 任务队列：暂时没人执行的任务先放这里
- 并发上限：线程最多可以扩到多大

这三者一起决定系统在高峰期如何表现。

## 新任务到来时，线程池不是只会入队

`ThreadPoolExecutor` 的调度顺序非常关键，可以先记成：

1. 先尝试创建核心线程执行任务
2. 核心线程都忙时，任务先入队
3. 队列满了，再尝试创建非核心线程
4. 线程数也到上限后，执行拒绝策略

也就是说，它不是简单的“先开满线程”或者“先全都排队”，而是一种分阶段扩容模型。

## 队列为什么会直接改变线程池行为

这一点特别容易被忽略。

同样的核心线程数和最大线程数，换一个队列，线程池行为可能完全不同：

- 大队列：任务更容易先堆积，线程数不容易长到最大值
- 小队列：更容易扩线程，也更早触发拒绝
- `SynchronousQueue`：根本不缓存任务，更容易直接推动线程扩容

所以配置线程池时，不能只看线程数，还要把队列类型和容量一起看。

## Worker 为什么是复用的关键

线程池里真正反复工作的不是“任务对象”，而是内部的 `Worker`。

可以把 `Worker` 先理解成：

- 挂着一个真实 Java 线程
- 先执行创建时交给它的 `firstTask`
- 执行完以后，再不断从队列里 `getTask()`

所以线程池复用的本质是：

> 同一个工作线程，在生命周期里连续执行多个任务。

## 为什么拒绝策略不是附属配置

线程池一旦进入“线程数到上限 + 队列也满”的状态，就必须决定系统怎么退让。

这不是边角问题，而是容量设计的一部分。

常见策略本质上是在不同代价间取舍：

- 明确失败
- 拖慢提交方
- 丢弃任务
- 丢弃更早的任务

也就是说，拒绝策略决定的是：

> 系统过载时，哪一侧来承担代价。

## 线程池大小为什么一定要看任务类型

线程池配置没有一个固定万能值，因为任务类型不同：

- CPU 密集型：线程太多反而增加切换成本
- IO 密集型：可以比 CPU Core 数更多，但又会受下游资源限制

真正要看的不只是 CPU，还包括：

- 数据库连接数
- 外部服务并发上限
- 单任务平均耗时
- 队列最多允许堆多久

所以线程池本质上也是一个“对下游施压的闸门”。

## 它和后面几个节点怎么接

线程池只负责把任务跑起来，不负责保存任务结果本身。

后面几张卡是接在它后面的：

- [[wiki/concepts/concurrency/FutureTask|FutureTask]]：结果和异常存在哪里
- [[wiki/concepts/concurrency/CompletableFuture|CompletableFuture]]：多个异步阶段怎么自动接力
- [[wiki/concepts/concurrency/ThreadLocal|ThreadLocal]]：线程被复用后，线程上下文会留下什么副作用

## 为什么它重要

很多更高层异步工具最终都要落回线程池调度：

- `FutureTask`
- `CompletableFuture`
- 很多业务任务执行框架

所以它是“任务怎么跑起来”的地基。

## 它的关键部件

- 工作线程
- 任务队列
- 核心线程数 / 最大线程数
- 拒绝策略

## 在系列里的位置

它位于异步执行层的起点，是后面所有“拿结果、编排任务、控制并发”能力的基础运行时。

## 推荐回看原文

- [[_posts/concurrency/14-线程池如何复用和调度线程|14-线程池如何复用和调度线程]]
- [[_posts/concurrency/15-Future 如何获取异步任务的执行结果|15-FutureTask 如何保存异步任务的结果和异常]]

## 相关概念

- [[wiki/concepts/concurrency/异步执行|任务执行与异步编排]]
- [[wiki/concepts/concurrency/Future|Future]]
- [[wiki/concepts/concurrency/FutureTask|FutureTask]]
- [[wiki/concepts/concurrency/CompletableFuture|CompletableFuture]]
- [[wiki/concepts/concurrency/BlockingQueue|BlockingQueue]]
- [[wiki/concepts/concurrency/ThreadLocal|ThreadLocal]]
- [[wiki/concepts/concurrency/任务系统|任务系统与系统边界]]
