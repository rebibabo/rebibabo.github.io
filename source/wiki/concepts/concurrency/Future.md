---
title: Future
tags:
  - wiki
  - concept
  - concurrency
  - future
type: concept
source_series: concurrency
status: seed
---

# Future

[[wiki/concepts/concurrency/异步执行|返回任务执行与异步编排]]

## 定义

`Future` 可以理解为异步任务结果的凭证。

## 它解决什么问题

它回答的是：

> 任务已经交给别的线程去跑了，那我之后用什么对象来等待它、取消它、取结果？

## 它把“提交任务”和“取得结果”拆开了

这是 `Future` 最核心的价值。

提交任务时，调用线程先拿到的不是最终结果，而是一个“以后再来取结果”的凭证。

所以它代表的是：

- 结果可能还没出来
- 任务可能还在执行
- 任务也可能已经失败或被取消
- 但调用线程已经有了一个统一入口去等待和查询

## 它能提供哪几类动作

围绕一个异步任务，`Future` 主要暴露四类能力：

- 等待结果：`get()`
- 超时等待：`get(timeout, unit)`
- 取消任务：`cancel(boolean)`
- 查询状态：`isDone()` / `isCancelled()`

也就是说，`Future` 关心的是“异步结果的生命周期管理”，而不是“任务怎么执行”。

## 为什么它还不够表达任务链

`Future` 很适合单个异步任务：

- 提交一个任务
- 将来等它
- 然后拿结果

但一旦任务之间有前后依赖，调用线程就容易变成：

1. 提交 A
2. `get()` 等 A
3. 取到 A 的结果后，再提交 B
4. 再 `get()` 等 B

所以它擅长的是“单结果等待”，不擅长的是“多阶段自动编排”。这也是后面为什么会走向 [[wiki/concepts/concurrency/CompletableFuture|CompletableFuture]]。

## `isDone()` 为什么不等于“成功了”

这是一个很容易误用的点。

`isDone()` 只表示任务已经进入最终状态，但这个最终状态可能是：

- 正常完成
- 执行失败
- 被取消

所以它更像是“任务结束没结束”，而不是“任务成没成功”。

## 超时和取消也不是一回事

- `get(timeout, unit)` 超时：表示当前等待方不想再继续等了
- `cancel(true/false)`：表示尝试让任务进入取消状态

尤其是超时，并不自动意味着后台任务已经停止。任务可能还在工作线程里继续跑。

这一点对工程上特别重要，因为：

> 调用方不等了，不代表资源已经自动释放。

## 为什么它重要

它把“任务提交”和“结果取得”分开了。

所以它是异步编程里很基础的一步，但它更偏：

- 单个任务结果
- 主动等待
- 主动查询

## 它和 FutureTask 的关系

- `Future` 是接口层语义
- [[wiki/concepts/concurrency/FutureTask|FutureTask]] 是把执行和结果状态合起来的具体实现模型

可以先简单记成：

- `Future` 定义“外面的人怎么查结果”
- `FutureTask` 负责“里面的人怎么执行并保存结果”

## 在系列里的位置

它位于线程池之后、CompletableFuture 之前，是异步结果模型的基础抽象。

## 推荐回看原文

- [[_posts/concurrency/15-Future 如何获取异步任务的执行结果|15-FutureTask 如何保存异步任务的结果和异常]]
- [[_posts/concurrency/16-CompletableFuture 如何编排多个异步任务|16-CompletableFuture 如何编排多个异步任务]]

## 相关概念

- [[wiki/concepts/concurrency/异步执行|任务执行与异步编排]]
- [[wiki/concepts/concurrency/FutureTask|FutureTask]]
- [[wiki/concepts/concurrency/CompletableFuture|CompletableFuture]]
- [[wiki/concepts/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]]
