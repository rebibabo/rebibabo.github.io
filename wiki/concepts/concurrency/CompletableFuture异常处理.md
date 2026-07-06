---
title: CompletableFuture 异常处理
tags:
  - wiki
  - concept
  - concurrency
  - completablefuture
  - exception
type: concept
source_series: concurrency
status: seed
---

# CompletableFuture 异常处理

[[wiki/concepts/concurrency/CompletableFuture|返回 CompletableFuture]]

## 定义

这一页关注的是：

> 异步任务链失败以后，异常如何保存、传播、恢复，以及调用线程最后怎么感知这次失败。

## 它解决什么问题

同步代码里异常会顺着当前调用栈往上抛。

但异步任务通常跑在别的线程上，所以异常不能直接跳回调用线程，必须先保存到结果对象里，再通过：

- `exceptionally`
- `handle`
- `whenComplete`
- `get / join`

这些路径重新暴露出来。

## 为什么异步异常不能直接抛回调用线程

这条线的根因和 `FutureTask` 很像：

- 调用线程负责创建异步阶段
- 工作线程负责真正执行阶段代码

异常只能沿当前线程调用栈传播，不能直接从工作线程“跳回”调用线程。

所以异常必须先被保存到 `CompletableFuture` 对象里，再在后续阶段或最终消费时重新暴露。

## 这一页真正要区分的是三种事情

### 1. 定义任务时怎么处理受检异常

例如 `Supplier.get()` 本身不能直接声明受检异常，所以很多时候需要先在 Lambda 里捕获，再包装成运行时异常继续抛出。

### 2. 任务链中怎么观察、恢复或转换异常

这对应：

- `exceptionally()`
- `handle()`
- `whenComplete()`

### 3. 最终消费结果时怎么感知失败

这对应：

- `get()`
- `join()`

把这三层分开看，异常语义就会清楚很多。

## 三个常用方法到底怎么选

### `exceptionally`

只在失败时执行，通常用于：

- 给默认值
- 做降级兜底

如果前一步成功，它不会介入。

### `handle`

成功和失败都会执行，而且可以统一映射成一个新结果。

它适合：

- 无论成败，都要转成一个可继续流动的新值
- 成功时转换结果，失败时兜底

### `whenComplete`

成功和失败都会执行，但重点更偏观察，不偏恢复。

它适合：

- 打日志
- 做埋点
- 释放资源

默认情况下，它不会把失败自动恢复成成功。

## 一条非常实用的判断线

可以先这样记：

- 想兜底并继续往下走：`exceptionally`
- 想无论成败都统一转一个新值：`handle`
- 想看一眼结果或异常，但不改主语义：`whenComplete`

## `get()` 和 `join()` 的差别

这两个方法都能在最后拿结果，但异常暴露方式不同：

- `get()` 更接近传统 `Future`，会用受检异常包装等待中断和执行失败
- `join()` 更贴近 `CompletableFuture` 自己的用法，不强制你写受检异常捕获

所以很多链式异步代码最后更常见的是 `join()`，而不是反复 `try-catch get()`。

## 为什么这一页和上一页最好连着看

上一页是在讲：

- 阶段之间怎么接力
- 结果怎么往下流

这一页是在讲：

- 如果中途失败了，结果流会怎么变形
- 哪一层负责观察、恢复或继续失败

把两页合起来看，`CompletableFuture` 才算完整。

## 为什么它重要

很多异步代码真正难的不是“怎么并发跑”，而是：

- 哪里恢复默认值
- 哪里只记录日志
- 哪里应该让任务链继续失败

## 在系列里的位置

它是 `CompletableFuture` 的重要子主题，也是异步执行层和故障处理层交叉的地方。

## 推荐回看原文

- [[_posts/concurrency/17-CompletableFuture 如何处理异步结果与异常|17-CompletableFuture 如何处理异步结果与异常]]
- [[_posts/concurrency/16-CompletableFuture 如何编排多个异步任务|16-CompletableFuture 如何编排多个异步任务]]

## 相关概念

- [[wiki/concepts/concurrency/CompletableFuture|CompletableFuture]]
- [[wiki/concepts/concurrency/FutureTask|FutureTask]]
- [[wiki/concepts/concurrency/Future|Future]]
- [[wiki/concepts/concurrency/Happens-Before|happens-before]]
- [[wiki/concepts/concurrency/故障模式|故障模式与安全停止]]
