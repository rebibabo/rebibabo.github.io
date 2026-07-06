---
title: CountDownLatch
tags:
  - wiki
  - glossary
  - concurrency
  - countdownlatch
type: glossary
source_series: concurrency
status: seed
---

# CountDownLatch

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`CountDownLatch` 是一个倒计数门闩——初始化一个计数值，等待线程在计数归零前阻塞，其他线程通过 `countDown()` 减少计数，最终归零时所有等待线程被同时释放。

## 上下文

`CountDownLatch` 基于 AQS 的共享模式实现：`state` 表示剩余计数，等待线程调用 `await()` 时 `tryAcquireShared()` 检查计数是否归零——未归零则入队阻塞；其他线程调用 `countDown()` 减少计数，最后一次归零时触发共享唤醒，排队线程陆续放行。

典型场景：主线程等待多个子任务完成（`CountDownLatch(n)` → 每个任务完成后 `countDown()` → 主线程 `await()` 继续）；多个线程统一开始（`CountDownLatch(1)` → 所有线程 `await()` → 主控线程 `countDown()` 一声令下）。

## 相关术语

- [[wiki/glossary/concurrency/Semaphore|Semaphore]] — 同样是共享模式，但管理许可证数量
- [[wiki/glossary/concurrency/AQS|AQS]] — CountDownLatch 基于 AQS 共享模式

## 深入阅读

- [[wiki/concepts/concurrency/CountDownLatch|CountDownLatch 概念页（完整版）]]
- [[_posts/concurrency/11-CountDownLatch 如何等待多个线程完成|11-CountDownLatch]]
