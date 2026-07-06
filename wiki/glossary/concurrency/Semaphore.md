---
title: Semaphore
tags:
  - wiki
  - glossary
  - concurrency
  - semaphore
type: glossary
source_series: concurrency
status: seed
---

# Semaphore

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`Semaphore（信号量）` 用于控制同时访问某个资源的线程数量。它维护一组许可证：线程通过 `acquire()` 获取许可证后才能执行，用完通过 `release()` 归还。当许可证为 0 时，后续线程阻塞等待。

## 上下文

`Semaphore` 基于 AQS 的共享模式实现：`state` 表示剩余许可证数量。`acquire()` 尝试扣减一个许可证，扣减成功直接通过，失败则入队等待。由于是共享模式，释放许可证后可能触发传播——如果还有剩余，后续共享节点可以继续被唤醒。

典型场景：数据库连接池限制（许可证数=连接数）、接口限流（许可证数=最大并发数）。注意 `Semaphore` 不是基于"谁持有"概念的——任何线程都可以 `release()`，不要求一定是之前 `acquire()` 的线程。

## 相关术语

- [[wiki/glossary/concurrency/CountDownLatch|CountDownLatch]] — 同样是共享模式，但计数只能减不能增
- [[wiki/glossary/concurrency/AQS|AQS]] — Semaphore 基于 AQS 共享模式

## 深入阅读

- [[wiki/concepts/concurrency/Semaphore|Semaphore 概念页（完整版）]]
- [[_posts/concurrency/12-Semaphore 如何控制并发线程数量|12-Semaphore]]
