---
title: CountDownLatch
tags:
  - wiki
  - concept
  - concurrency
  - countdownlatch
type: concept
source_series: concurrency
status: seed
---

# CountDownLatch

[[wiki/concepts/concurrency/同步机制|返回同步机制]]

## 定义

`CountDownLatch` 是一种一次性等待协调器，用来让一个或多个线程等待一批完成事件发生。

## 它解决什么问题

它回答的是：

> 这些任务不一定互斥，但我必须等它们都做完，才能继续往下走。

## 它等的不是“线程锁”，而是“完成事件”

`CountDownLatch(3)` 最重要的不是数字 3 本身，而是它表示：

> 还需要 3 次完成事件发生，等待方才能继续执行。

所以：

- `countDown()` 是报告“又完成了一次”
- `await()` 是等待“剩余次数变成 0”

它关注的是协作进度，不是临界区互斥。

## AQS 里的 state 在这里代表什么

在 `CountDownLatch` 里，AQS 的 `state` 不再表示锁是否占用，而是表示：

- 还剩多少次完成事件没有发生

也就是说：

- `3 -> 2 -> 1 -> 0`

一旦减到 `0`，闸门就打开了。

## 为什么 `countDown()` 也要用 CAS

很多人第一次看到这里会直觉上觉得：不就是减一吗？

但多个工作线程可能同时完成。如果只是普通 `state--`，就会出现和 `count++` 相反方向但本质类似的问题：

- 两个线程都读到同一个旧值
- 都各自减一
- 最后只生效一次

所以每一次成功的 `countDown()`，都必须对应一次真实递减，这也是它要用 CAS 的原因。

## 为什么它是“一次性闸门”

`CountDownLatch` 的计数只会往下减，不会再加回去。

这意味着：

- 计数没到 `0` 时，`await()` 的线程继续等
- 一旦到 `0`，后续所有 `await()` 都直接通过
- 它不会重新关闭，也没有 reset 能力

所以它非常适合“一批任务完成后统一放行”的场景，但不适合多轮反复会合。

## 它不保存结果，只负责“都结束了吗”

`CountDownLatch` 很容易被误会成“任务结果收集器”，但它不是。

它只回答一件事：

> 所有需要等待的完成事件，是否都已经发生了？

至于：

- 每个任务成没成功
- 返回值是什么
- 异常是谁抛的

这些都必须由别的结构自己保存。

## 为什么 `countDown()` 往往放 finally

如果某个工作线程抛异常后直接退出，却没有执行 `countDown()`，等待方可能就永远卡住。

所以更稳妥的语义通常是：

- 任务不管成功还是失败
- 只要这一份“结束事件”发生了
- 就应该报告一次 `countDown()`

这也是它常被放在 `finally` 里的原因。

## `await()` 返回后为什么能看见结果

`CountDownLatch` 不只是个计数器，它还有同步语义。

一个工作线程在调用 `countDown()` 之前做过的写入，对另一个线程从对应 `await()` 成功返回之后的读取是可见的。

所以常见模式才会成立：

- 工作线程先写结果
- 再 `countDown()`
- 主线程 `await()` 返回后再统一读取结果

这也是它作为“汇总前等待点”非常好用的原因。

## 它为什么重要

它把“等待多个任务完成”这件事从手工 `join()` 或手工计数里抽出来，变成了标准同步器。

同时它也是理解 `AQS` 共享模式的一个非常好的例子。

## 它的边界

- 它只关心“还有多少事件没发生”
- 它不保存任务结果
- 它不能复位
- 它不是限流器，也不是锁

所以它更像一次性闸门，而不是循环栅栏。

## 在系列里的位置

它位于 `Condition` 之后，说明并发协作已经从“单个条件等待”推进到“多任务完成等待”。

## 推荐回看原文

- [[_posts/concurrency/11-CountDownLatch 如何等待多个线程完成|11-CountDownLatch 如何等待多个线程完成]]
- [[_posts/concurrency/19-AQS 独占与共享模式如何完成排队与唤醒|19-AQS 独占与共享模式如何完成排队与唤醒]]

## 相关概念

- [[wiki/concepts/concurrency/AQS|AQS]]
- [[wiki/concepts/concurrency/Semaphore|Semaphore]]
- [[wiki/concepts/concurrency/Happens-Before|happens-before]]
- [[wiki/concepts/concurrency/任务系统|任务系统与系统边界]]
