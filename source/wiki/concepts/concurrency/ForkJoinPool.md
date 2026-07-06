---
title: ForkJoinPool
tags:
  - wiki
  - concept
  - concurrency
  - forkjoinpool
type: concept
source_series: concurrency
status: seed
---

# ForkJoinPool

[[wiki/concepts/concurrency/异步执行|返回任务执行与异步编排]]

## 定义

`ForkJoinPool` 是面向可拆分任务的一种执行框架，核心特征是**工作窃取（Work-Stealing）**。

普通线程池适合独立任务：任务提交到共享队列，Worker 从队列中取任务执行。ForkJoinPool 面向的是另一类任务：一个大任务可以递归拆成多个子任务，子任务继续拆分，最后把结果合并。

## 它解决什么问题

它回答的是：

> 当一个大任务会不断拆出子任务时，怎样让多个 Worker 在不频繁竞争同一个全局队列的前提下协同执行？

如果所有子任务都放进一个共享队列，所有线程会频繁竞争同一个队列。ForkJoinPool 的核心思路是：**每个 Worker 有自己的本地双端队列**；当前 Worker 拆出来的子任务先放到自己队列；当前 Worker 优先执行自己的任务；其他 Worker 空闲时可以从别人队列中偷任务执行。

## 四个核心角色

| 角色 | 作用 |
| --- | --- |
| ForkJoinPool | 管理 Worker、接收外部提交、协调窃取 |
| Worker | 真正执行任务的工作线程 |
| 本地双端队列 | Worker 的"私有任务缓冲区" |
| ForkJoinTask | 被执行的任務對象，记录完成状态和结果 |

## 两条不同的提交路径

| 场景 | 调用线程 | 调用方式 | 任务进入 |
| --- | --- | --- | --- |
| 外部提交根任务 | 外部线程 | `pool.invoke()` / `submit()` / `execute()` | ForkJoinPool 的外部提交路径 |
| Worker 内部 fork | ForkJoin Worker | `task.fork()` | 当前 Worker 的本地队列 |

`invoke()` 同步等待结果；`submit()` 异步提交返回 `ForkJoinTask`；`execute()` 不关心结果。**根任务应通过 Pool 级别方法进入池子；`fork()` 主要用于 Worker 内部拆分子任务。**

## 核心执行模式：fork 一个，compute 一个，最后 join

```java
left.fork();              // 把左任务放入本地队列，可被窃取
long rightResult = right.compute();  // 当前 Worker 继续执行右任务
long leftResult = left.join();       // 需要结果时再获取
```

原则：把一部分任务暴露给其他 Worker（fork），同时让当前 Worker 继续干活（compute），不轻易闲置。

## 本地双端队列的两端操作

```
base                                  top
 ↓                                     ↓
[task-1] [task-2] [task-3] [task-4]
 ↑                                     ↑
steal (other worker)              push/pop (owner)
```

- 当前 Worker 从 `top` 端 push/pop（LIFO，保持局部性）
- 其他 Worker 从 `base` 端 steal（偷较早的、粒度较大的任务）

同时解决两个问题：当前 Worker 保持局部性，空闲 Worker 获得足够大的任务。

## join 不是简单阻塞等待

`join()` 有三种可能：
1. 任务已被偷走并执行完成 → 直接返回结果
2. 任务还在本地队列 → 取出来自己执行
3. 任务被偷走但还没执行完 → 尝试寻找其他可执行任务帮助推进

Worker 在等待结果时不会轻易闲置，而是尽量参与任务推进。

## 工作循环

```
check local deque → check submissions → steal from others → wait if no work
```

Worker 优先处理本地任务，空闲后才扩展到外部提交和其他 Worker 的队列。

## parallelism 控制的是目标并行度

`new ForkJoinPool(4)` 中的 4 不是严格最大线程数，而是期望维持的目标并行工作线程数。ForkJoinPool 有阻塞补偿机制，当某些 Worker 因特殊原因阻塞时可能临时补充线程。

## commonPool 容易互相影响

`ForkJoinPool.commonPool()` 是 JVM 进程级别共享的。`parallelStream()` 和 `CompletableFuture.supplyAsync()` 在没有显式指定 Executor 时可能默认使用 commonPool。如果其中混入了阻塞 I/O 任务，会拖慢整个公共池。对于阻塞 I/O，应显式使用独立线程池。

## 使用边界

| 问题 | 表现 | 后果 |
| --- | --- | --- |
| 任务粒度太小 | 子任务数量过多 | 调度成本超过计算收益（需要 THRESHOLD） |
| 阻塞 I/O | Worker 卡在外部调用 | 工作窃取无法发挥作用 |
| 共享状态竞争 | 多任务频繁修改同一变量 | CAS 或锁竞争抵消并行收益 |

ForkJoinPool 适合：可拆分、主要消耗 CPU、子任务之间尽量少共享状态的任务。

## RecursiveTask vs RecursiveAction

| 类型 | 是否有返回值 | 完成方式 |
| --- | --- | --- |
| `RecursiveTask<V>` | 是 | 子任务返回结果，父任务 `join()` 后合并 |
| `RecursiveAction` | 否 | 子任务完成即可，父任务等待结束 |

## 在系列里的位置

它位于线程池和任务系统之间，是"任务结构影响调度结构"的代表案例。

## 推荐回看原文

- [[_posts/concurrency/26-ForkJoinPool 如何通过工作窃取执行任务|26-ForkJoinPool 如何通过工作窃取执行任务]]
- [[_posts/concurrency/14-线程池如何复用和调度线程|14-线程池如何复用和调度线程]]
- [[_posts/concurrency/28-并发任务处理系统如何设计：从任务模型到 Worker 执行|28-并发任务处理系统如何设计]]

## 相关概念

- [[wiki/concepts/concurrency/异步执行|任务执行与异步编排]]
- [[wiki/concepts/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]]
- [[wiki/concepts/concurrency/任务系统|任务系统与系统边界]]
- [[wiki/concepts/concurrency/故障模式|故障模式与安全停止]]
