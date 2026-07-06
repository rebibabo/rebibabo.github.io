---
title: InterruptedException
tags:
  - wiki
  - glossary
  - concurrency
  - interruptedexception
type: glossary
source_series: concurrency
status: seed
---

# InterruptedException

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`InterruptedException` 是可中断阻塞方法（`Thread.sleep()`、`Object.wait()`、`BlockingQueue.take()`、`Condition.await()`、`ReentrantLock.lockInterruptibly()`）被外部 `interrupt()` 唤醒时抛出的受检异常。

## 上下文

关键行为：方法抛出 `InterruptedException` 后通常会清除线程的中断标记。因此 catch 里如果不恢复标记，上层调用者就无法感知线程曾被中断。

正确的处理模式：要么传播（`throw` 给调用方），要么恢复中断标记后退出（`Thread.currentThread().interrupt() + return`）。最坏的做法是空 catch 什么都不做——中断信号被吞掉，外部停止请求丢失。

## 相关术语

- [[wiki/glossary/concurrency/线程中断|线程中断]] — InterruptedException 的触发来源
- [[wiki/glossary/concurrency/LockSupport|LockSupport]] — park() 不抛 InterruptedException，需要手动检查

## 深入阅读

- [[wiki/concepts/concurrency/线程中断|线程中断概念页]]
- [[_posts/concurrency/24-线程中断如何让任务安全停止|24-线程中断]]
