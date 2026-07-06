---
title: LockSupport
tags:
  - wiki
  - concept
  - concurrency
  - locksupport
type: concept
source_series: concurrency
status: seed
---

# LockSupport

[[wiki/concepts/concurrency/同步机制|返回同步机制]]

## 定义

`LockSupport` 是 Java 并发里最底层的线程阻塞与唤醒工具。它不是一把完整的锁，也不维护等待队列，而是提供两个最基础的原语：`park()`（让当前线程暂停）和 `unpark(thread)`（唤醒指定线程）。

## 它解决什么问题

它回答的是：

> 不讨论锁语义，只看最底层，线程到底怎么停下来，又怎么被叫醒？

完整的锁还需要状态判断、等待队列和唤醒策略；`LockSupport` 只负责其中最底层的一步：线程如何停下、如何被指定线程唤醒。

## 为什么它重要

很多更高层同步器最终都会落到它：`AQS`、`ReentrantLock`、条件等待中的底层阻塞。理解它是理解 AQS 等待唤醒闭环的底座。

## 核心机制：permit（许可证）

每个线程关联一个最多为 1 的 permit：

- `park()`：尝试获取 permit；有则消耗并返回，没有则阻塞等待
- `unpark(thread)`：给指定线程发放 permit；如果线程正在 `park()` 中阻塞就让其返回，如果还没执行到 `park()` 则 permit 先保留

## 关键特点

### unpark 可以先于 park

`LockSupport` 和 `wait/notify` 的重要区别：`unpark()` 可以先于 `park()` 发生。如果主线程先调用了 `unpark(worker)`，子线程后执行 `park()` 可以直接通过——permit 已提前发放。

### permit 不会累加

连续多次 `unpark()` 最多也只是把 permit 设为 1。后续连续调用两次 `park()`，第一次消耗已有 permit 直接返回，第二次没有新 permit 就会阻塞。

### park 返回不代表条件已满足

`park()` 返回可能有三种原因：`unpark()` 发放 permit、`interrupt()` 中断、极少数伪唤醒。因此外面必须用 `while` 反复检查条件：

```java
while (!ready) {
    LockSupport.park();
}
```

职责分离：`park()` 只负责阻塞线程，`ready` 等共享状态才负责表达线程是否真的可以继续。

### 中断也会让 park 返回

`park()` 遇到中断会返回，但**不抛 `InterruptedException`，也不清除中断标记**。如果等待逻辑需要"即使被中断也继续等待"，常见做法是先清除并记录中断标记（避免后续 `park()` 因中断标记存在而立即返回），等条件满足后再恢复：

```java
boolean interrupted = false;
while (!ready) {
    LockSupport.park(this);
    if (Thread.interrupted()) {
        interrupted = true;  // 记录并清除中断标记
    }
}
if (interrupted) {
    Thread.currentThread().interrupt(); // 恢复
}
```

### park(Object blocker) 记录阻塞原因

`LockSupport.park(this)` 中的 `this` 是 blocker——不改变语义，只是把阻塞原因记录下来方便线程 Dump 排查。

## LockSupport 不维护等待队列

`unpark(thread)` 必须明确传入 `Thread`，说明 `LockSupport` 不知道"有哪些线程在等待"。如果需要排队等待，就必须由上层结构（如 AQS）维护等待关系。

职责分层：

| 职责 | 由谁负责 |
| --- | --- |
| 条件是否满足 | 上层状态（锁状态、任务状态、业务标志） |
| 哪些线程在等待 | 上层队列（如 AQS 同步队列） |
| 线程如何暂停和唤醒 | `LockSupport.park/unpark` |

## 在系列里的位置

它是同步机制层里最贴近线程阻塞原语的一层，也是理解 `AQS` 和等待唤醒闭环的重要底座。

## 推荐回看原文

- [[_posts/concurrency/25-LockSupport 如何挂起和唤醒线程|25-LockSupport 如何挂起和唤醒线程]]
- [[_posts/concurrency/19-AQS 独占与共享模式如何完成排队与唤醒|19-AQS 独占与共享模式如何完成排队与唤醒]]

## 相关概念

- [[wiki/concepts/concurrency/AQS|AQS]]
- [[wiki/concepts/concurrency/ReentrantLock|ReentrantLock]]
- [[wiki/concepts/concurrency/线程中断|线程中断]]
- [[wiki/concepts/concurrency/对象监视器|Object Monitor]]
- [[wiki/concepts/concurrency/故障模式|故障模式与安全停止]]
