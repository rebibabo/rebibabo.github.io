---
title: Semaphore
tags:
  - wiki
  - concept
  - concurrency
  - semaphore
type: concept
source_series: concurrency
status: seed
---

# Semaphore

[[wiki/concepts/concurrency/同步机制|返回同步机制]]

## 定义

`Semaphore` 是一种基于许可证数量控制并发度的同步器。

## 它解决什么问题

它回答的是：

> 这些线程可以并发跑，但同一时刻最多只能有多少个继续执行？

## 可以把它先看成“许可证池”

`Semaphore(3)` 表示初始有 3 张许可证。

线程执行：

- `acquire()`：尝试拿走一张许可证
- `release()`：归还一张许可证

如果许可证还有剩余，线程就能继续执行；如果已经没有剩余，就需要等待。

所以它本质上控制的是：

> 同时被放行的线程数量上限。

## AQS 的 state 在这里表示什么

在 `Semaphore` 里，`state` 表示当前剩余许可证数量。

例如：

- `state = 3`：还剩 3 张
- `state = 0`：没有许可证了

这和 `ReentrantLock`、`CountDownLatch` 用的是同一个 AQS 字段，但语义完全不同。AQS 提供的是骨架，具体含义由同步器自己定义。

## 为什么 acquire 和 release 都要用 CAS

两个方向都可能发生并发更新：

- 多个线程同时申请许可证
- 多个线程同时归还许可证

如果只是普通加减，就会出现更新丢失。

所以：

- `acquire()` 需要 CAS 保证“同一张许可证不会被两个人同时拿走”
- `release()` 需要 CAS 保证“多个归还动作不会只记住其中一个”

这和 `CountDownLatch` 只需要递减不同，`Semaphore` 是一个可循环变化的共享计数。

## 它为什么属于共享模式

`ReentrantLock` 是独占的，一次只能有一个线程通过。

`Semaphore` 不是。只要许可证还够，多个线程都可以先后成功通过：

- 第一个线程把 `3` 减成 `2`
- 第二个线程把 `2` 减成 `1`
- 第三个线程把 `1` 减成 `0`

所以它不是“锁”，而是“允许最多 N 个线程同时进入”的共享放行器。

## 它和 CountDownLatch 的根本区别

这两个名字很容易一起出现，但语义完全不同：

- `CountDownLatch`：关注“什么时候全部完成”
- `Semaphore`：关注“同时最多允许多少个继续执行”

前者像一次性闸门，后者像反复流转的通行证池。

## 它为什么可以重复使用

`Semaphore` 的许可证不是一次性耗尽就结束，而是在：

- 获取时减少
- 归还时增加

这个循环里持续流动。

所以它很适合长期在线的工程场景：

- 限制外部服务并发访问数
- 控制数据库连接使用数
- 约束某类昂贵资源的并发度

## 它不记录“许可证属于谁”

这一点和锁很不一样。

`ReentrantLock` 会记录 owner，只有持锁线程才能正确 `unlock()`。

但 `Semaphore` 不关心是哪一个线程申请的许可证，也不验证由谁归还。它只维护数量。

这意味着：

- 业务上必须自己保证 `acquire()` / `release()` 配对
- 如果多 `release()`，许可证数量甚至可能超过初始值

所以它是灵活的，但也更依赖正确使用。

## 为什么也要写 finally

如果线程已经成功 `acquire()`，但后续异常退出却没 `release()`，许可证就会泄漏。

泄漏一段时间后，系统表现就会像“莫名其妙越来越卡”，因为可用许可证越来越少，最后所有后续线程都可能被堵住。

所以标准写法同样是：

```java
semaphore.acquire();
try {
    doWork();
} finally {
    semaphore.release();
}
```

## 它能提供什么，不能提供什么

它能提供：

- 并发上限控制
- release 之前写入到后续 acquire 成功之后的可见性边界

它不能提供：

- 自动结果汇总
- 复合状态互斥更新
- 多线程访问非线程安全对象时的完整保护

例如 `Semaphore(3)` 允许 3 个线程同时进入，如果这 3 个线程还会一起改同一个非线程安全对象，照样可能出错。

## 为什么它重要

它不是互斥锁，而是“并发上限控制器”。

这类能力在：

- 限流
- 连接池
- 资源访问并发控制

里非常常见。

## 它和 CountDownLatch 的区别

- `CountDownLatch` 关心的是“什么时候全部完成”
- `Semaphore` 关心的是“同时最多放行多少个”

两者都基于 `AQS` 共享模式，但同步语义完全不同。

## 在系列里的位置

它是 `AQS` 共享模式落到实际工程控制的典型例子，也和线程池、外部资源访问等场景关系很强。

## 推荐回看原文

- [[_posts/concurrency/12-Semaphore 如何控制并发线程数量|12-Semaphore 如何控制并发线程数量]]
- [[_posts/concurrency/19-AQS 独占与共享模式如何完成排队与唤醒|19-AQS 独占与共享模式如何完成排队与唤醒]]

## 相关概念

- [[wiki/concepts/concurrency/AQS|AQS]]
- [[wiki/concepts/concurrency/CountDownLatch|CountDownLatch]]
- [[wiki/concepts/concurrency/ReentrantLock|ReentrantLock]]
- [[wiki/concepts/concurrency/Happens-Before|happens-before]]
- [[wiki/concepts/concurrency/异步执行|任务执行与异步编排]]
- [[wiki/concepts/concurrency/任务系统|任务系统与系统边界]]
