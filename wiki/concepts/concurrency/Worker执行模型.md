---
title: Worker 执行模型
tags:
  - wiki
  - concept
  - concurrency
  - worker
type: concept
source_series: concurrency
status: seed
---

# Worker 执行模型

[[wiki/concepts/concurrency/任务系统|返回任务系统与系统边界]]

## 定义

这一页关注的是：

> 当任务不再只是"扔给线程池就完了"，Worker 模型到底怎么组织任务获取、执行、重试和退出。

## 它解决什么问题

它把单机并发和系统级任务处理之间那一层结构补出来：

- 任务怎么被取走
- Worker 怎么循环执行
- 失败后怎么处理
- 怎么停机、怎么回收

## 基本 Worker 模型

Worker 的基本职责：等待任务 → 取出任务 → 交给 Processor 执行 → 继续等待下一个。

```java
while (true) {
    Task task = taskQueue.take();   // 空了就阻塞等待
    processor.process(task);        // 交给 Processor 执行业务逻辑
}
```

Worker 用 `take()`，和提交端的 `offer()` 形成对应：

| 方法 | 使用方 | 队列满/空时的行为 |
| --- | --- | --- |
| `offer(task)` | 提交线程 | 满了马上返回失败 |
| `take()` | Worker 线程 | 空了阻塞等待 |

Worker 本身不包含业务逻辑——业务逻辑放在 `TaskProcessor` 中。职责分离：

| 对象 | 关心的问题 |
| --- | --- |
| Worker | 如何从队列取任务、如何循环执行 |
| Processor | 某类任务具体怎么处理 |
| Task | 当前任务是谁、是什么状态 |

## 失败处理：从 Worker 中拆出来

Worker 只负责取任务和调用 Processor。任务失败后，是否重试、是否进入死信，由独立的 `TaskFailureHandler` 决定：

```
task failed → record error → should retry?
  → yes: increase retry count → requeue
  → no:  mark dead → save dead task
```

### 重试必须分类

| 失败类型 | 是否适合重试 | 例子 |
| --- | --- | --- |
| 临时失败 | 适合 | 网络抖动、HTTP 超时 |
| 资源繁忙 | 适合延迟重试 | 下游限流、连接池满 |
| 参数错误 | 不适合 | 文件 ID 不存在 |
| 业务规则失败 | 不适合 | 当前状态不允许处理 |
| 代码 Bug | 不适合盲目重试 | 空指针、类型转换错误 |

延迟重试比立刻重试更合理——第一次失败后 5 秒，第二次 30 秒，第三次 2 分钟。

## Worker 数量和队列容量设计

- CPU 密集型：Worker 数接近 CPU 核数
- I/O 密集型：可大于 CPU 核数，但受下游资源限制
- 混合型：从保守值开始压测调整

队列容量从业务可接受等待时间倒推：
```
queue capacity ≈ (workerCount / avgTaskCost) × acceptableWaitTime
```

## 优雅关闭

Worker 循环从永久 `take()` 改成带超时的 `poll()`，周期性检查关闭状态：

```java
while (pool.isRunning() || !taskQueue.isEmpty()) {
    Task task = taskQueue.poll(1, SECONDS);
    if (task == null) continue;
    processor.process(task);
}
```

关闭流程：停止接收新任务 → 中断空闲 Worker → 排空已有队列 → 超时等待。

## 监控指标

核心指标：队列长度、队列容量使用率、任务等待时间（`startTime - createTime`）、任务执行时间（`finishTime - startTime`）、成功数、失败数、重试次数、死信数量、Worker 存活数。

等待时间变长但执行时间正常 → 处理能力可能不足或提交速度升高。执行时间变长 → 业务逻辑或下游资源变慢。

## 为什么它重要

很多可靠任务系统并不是直接从 MQ 长出来的，而是先从一个清晰的 Worker 执行模型长出来。Worker 模型是单机内存任务系统和可靠任务系统之间的共通骨架。

## 在系列里的位置

它位于 `ThreadPoolExecutor` 和 [[wiki/concepts/concurrency/可靠任务系统|可靠任务系统]] 之间，是任务系统层的中间骨架。

## 推荐回看原文

- [[_posts/concurrency/28-并发任务处理系统如何设计：从任务模型到 Worker 执行|28-并发任务处理系统如何设计：从任务模型到 Worker 执行]]
- [[_posts/concurrency/14-线程池如何复用和调度线程|14-线程池如何复用和调度线程]]

## 相关概念

- [[wiki/concepts/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]]
- [[wiki/concepts/concurrency/BlockingQueue|BlockingQueue]]
- [[wiki/concepts/concurrency/任务系统|任务系统]]
- [[wiki/concepts/concurrency/可靠任务系统|可靠任务系统]]
