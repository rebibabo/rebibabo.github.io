---
title: Worker Model
tags:
  - wiki
  - glossary
  - concurrency
  - worker-model
type: glossary
source_series: concurrency
status: seed
---

# Worker Model（Worker 执行模型）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

Worker Model 是单机任务处理系统的核心执行骨架：Worker 线程在循环中从队列取任务 → 交给 Processor 执行业务逻辑 → 继续等待下一个任务。任务失败由独立的 FailureHandler 处理，不在 Worker 主循环中散落异常处理。

## 上下文

核心职责分离：Worker 只管取任务和执行循环，Processor 封装具体业务逻辑，Task 记录任务身份和状态，FailureHandler 决定失败后是否重试，队列负责缓冲速度差。

Worker 数量和队列容量一起设计：Worker 太少处理跟不上，Worker 太多打满下游资源。队列容量 ≈ (workerCount / avgTaskCost) × acceptableWaitTime。优雅关闭时 Worker 循环从 `take()` 变 `poll(timeout)`，周期性检查关闭状态。

## 相关术语

- [[wiki/glossary/concurrency/BlockingQueue|BlockingQueue]] — Worker 的任务来源
- [[wiki/glossary/concurrency/Bounded-Queue|有界/无界队列]] — 队列容量决定缓冲边界
- [[wiki/glossary/concurrency/Task-Table|Task Table]] — 从内存 Worker 模型升级到持久化任务

## 深入阅读

- [[wiki/concepts/concurrency/Worker执行模型|Worker 执行模型概念页（完整版）]]
- [[_posts/concurrency/28-并发任务处理系统如何设计：从任务模型到 Worker 执行|28-任务系统设计]]
