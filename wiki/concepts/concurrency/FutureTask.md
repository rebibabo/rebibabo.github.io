---
title: FutureTask
tags:
  - wiki
  - concept
  - concurrency
  - futuretask
type: concept
source_series: concurrency
status: seed
---

# FutureTask

[[wiki/concepts/concurrency/异步执行|返回任务执行与异步编排]]

## 定义

`FutureTask` 把“可被工作线程执行的任务”和“可被提交线程查询结果的异步凭证”合到同一个对象里。

## 它解决什么问题

它回答的是：

> 线程池里执行的任务，如果有返回值、异常、取消状态，应该放到哪里保存，之后又怎么取出来？

## 它为什么是关键桥梁

线程池里的工作线程最终更习惯执行的是：

```java
task.run();
```

但有返回值的任务更自然写成 `Callable`：

```java
V call() throws Exception
```

所以这里天然有个落差：

- 工作线程想执行 `Runnable`
- 调用线程想拿到 `Future`
- 业务任务本身却更像 `Callable`

`FutureTask` 的价值，就是把这三件事拼到同一个对象里。

## 可以把它先理解成一个“二合一对象”

同一个 `FutureTask` 同时扮演两种身份：

- `Runnable`：给工作线程执行
- `Future`：给提交线程等待和取结果

所以原文里那条很重要的主线可以概括成：

> 工作线程执行的对象，和提交线程之后查询的对象，通常是同一个堆对象。

## 为什么结果必须保存在堆对象里

异步任务运行在工作线程里，提交线程和它不是同一个调用栈。

这意味着：

- `Callable.call()` 的返回值不会直接“跨线程 return”回提交线程
- 工作线程里抛出的异常，也不会直接跳回提交线程调用 `submit()` 的地方

所以结果、异常、取消状态都必须先保存到一个共享对象里。`FutureTask` 就是这个共享结果容器。

## 它内部至少要保存两类信息

### state

任务当前处于什么完成状态，例如：

- 还没完成
- 正常完成
- 异常完成
- 已取消

### outcome

任务完成后真正产出的内容：

- 正常返回值
- 异常对象

这两类信息必须分开看，因为：

- `outcome == null` 不代表任务一定失败
- 任务也可能正常返回 `null`

真正决定怎么解释结果的，是状态。

## `submit()` 为什么能同时返回 Future 又让线程池执行

原文很值得保留下来的一点是这条简化链路：

1. `Callable` 先被包装成 `FutureTask`
2. `FutureTask` 作为 `Runnable` 提交给线程池
3. 同一个 `FutureTask` 又作为 `Future` 返回给调用线程

所以调用线程拿到的 `future`，和工作线程 later 执行的 `task`，通常指向同一个对象。

## `get()` 真正等的是什么

调用 `get()` 时，如果任务还没到最终状态，等待线程就会阻塞；如果任务已经完成，`get()` 再根据状态解释结果：

- 正常完成：返回值
- 执行失败：抛出包装异常
- 被取消：抛出取消异常

所以 `get()` 等的不是“某个方法返回”，而是：

> 这个共享结果对象进入最终完成状态。

## 为什么它是走向 CompletableFuture 的前一站

`FutureTask` 已经解决了“单个异步任务结果怎么存活在堆里”的问题。

但它仍然更偏单任务：

- 一个任务执行
- 一个结果对象保存结果
- 一个等待方之后去取

如果还想表达“上一步完成后自动接下一步”，就要继续走到 [[wiki/concepts/concurrency/CompletableFuture|CompletableFuture]]。

## 为什么它重要

它是从 `Runnable` 走向“异步结果对象”的关键桥梁。

理解它之后，`Future`、`get()`、超时等待、取消、异常回传这些语义就能连成一条线。

## 它的关键角色

- `Callable` 负责定义有返回值的任务
- `Future` 负责暴露等待和查询接口
- `FutureTask` 负责把执行态和结果态装在一起

## 在系列里的位置

它位于线程池之后、`CompletableFuture` 之前，是“异步结果如何存活在堆对象里”的核心节点。

## 推荐回看原文

- [[_posts/concurrency/15-Future 如何获取异步任务的执行结果|15-FutureTask 如何保存异步任务的结果和异常]]
- [[_posts/concurrency/14-线程池如何复用和调度线程|14-线程池如何复用和调度线程]]

## 相关概念

- [[wiki/concepts/concurrency/异步执行|任务执行与异步编排]]
- [[wiki/concepts/concurrency/Future|Future]]
- [[wiki/concepts/concurrency/CompletableFuture|CompletableFuture]]
- [[wiki/concepts/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]]
- [[wiki/concepts/concurrency/任务系统|任务系统与系统边界]]
