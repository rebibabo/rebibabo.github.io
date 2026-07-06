---
title: BlockingQueue
tags:
  - wiki
  - concept
  - concurrency
  - blockingqueue
type: concept
source_series: concurrency
status: seed
---

# BlockingQueue

[[wiki/concepts/concurrency/并发容器|返回并发容器与数据结构]]

## 定义

`BlockingQueue` 是带等待语义的线程安全队列。普通 `Queue` 只回答"元素如何进出"，`BlockingQueue` 额外回答"队列暂时不能操作时，线程应该怎么办"。

## 它解决什么问题

它回答的是：

> 队列空了消费者怎么办，队列满了生产者怎么办，而且这些等待逻辑能不能不要每次都手写？

生产者消费者模型中，两边速度不一致是常态——`BlockingQueue` 把"存取元素"和"空满等待"合并成统一接口。

## 方法差异本质是失败策略差异

| 失败策略 | 插入 | 获取并移除 | 查看队首 | 队列满/空时的行为 |
|---|---|---|---|---|
| 抛异常 | `add(e)` | `remove()` | `element()` | 无法操作时抛异常 |
| 返回特殊值 | `offer(e)` | `poll()` | `peek()` | 插入失败返回 false，获取失败返回 null |
| 一直等待 | `put(e)` | `take()` | 无 | 满了就等，空了就等 |
| 超时等待 | `offer(e,time,unit)` | `poll(time,unit)` | 无 | 等一段时间后返回失败 |

## 主要实现对比

### ArrayBlockingQueue：固定数组 + 单锁

内部结构：固定数组 `items[]`、`putIndex`、`takeIndex`、`count`、一把 `ReentrantLock`、两个 `Condition`（`notEmpty`、`notFull`）。数组循环使用，下标走到末尾回 0。用 `count` 区分 `putIndex == takeIndex` 是空还是满。

**特点：容量明确、内存稳定、实现简单，但 `put()` 和 `take()` 不能真正并行**（同一把锁）。

### LinkedBlockingQueue：链表 + 双锁

入队和出队拆成两把锁：`putLock`（保护尾部追加）、`takeLock`（保护头部摘取）。`count` 用 `AtomicInteger` 协调两把锁之间的计数变化。内部是带头哨兵的单链表——`head` 永远是哨兵（不存有效元素），`head.next` 是第一个真实元素。

**特点：生产消费并发度更高，但节点对象开销更大。** 需要跨边通知：生产者放完元素后如果队列从空变非空，需要临时获取 `takeLock` 再 `signalNotEmpty()`。

默认无参构造容量是 `Integer.MAX_VALUE`（近似无界），实际使用应显式指定容量。

### SynchronousQueue：零容量直接交接

不缓存元素——生产者和消费者必须直接配对，元素不进入中间缓冲区。生产者先到就等消费者，消费者先到就等生产者。支持公平（FIFO 队列）和非公平（LIFO 栈）模式。

在线程池中，使用 `SynchronousQueue` 意味着任务没有地方缓存，只能直接交给空闲 Worker——如果没有空闲线程，就倾向创建新线程直到 `maximumPoolSize`。

### PriorityBlockingQueue：按优先级出队

出队顺序由元素优先级决定（底层小顶堆），不是按入队时间。无界队列，`put()` 通常不阻塞，`take()` 在队列空时阻塞。同优先级元素不保证 FIFO 顺序。

### DelayQueue：按到期时间出队

元素必须实现 `Delayed` 接口。**队列非空，`take()` 也可能继续阻塞**——只有堆顶元素的延迟时间 ≤ 0 时才能取出。内部用 leader 优化避免多个消费者同时等待同一到期时间。适合延迟任务、订单超时关闭、缓存过期清理。

## 在线程池中的作用

`ThreadPoolExecutor` 的 `workQueue` 就是 `BlockingQueue`。不同队列让线程池表现不同倾向：

| 队列 | 行为倾向 | 主要风险 |
|---|---|---|
| `ArrayBlockingQueue` | 核心满后先排队，满后扩容 | 队列太小易拒绝 |
| 有界 `LinkedBlockingQueue` | 类似先排队，并发度更高 | 节点对象多，GC 压力 |
| 无界 `LinkedBlockingQueue` | 几乎一直排队 | 任务堆积，可能 OOM |
| `SynchronousQueue` | 不缓存，倾向直接交接或创建新线程 | 线程数可能快速增长 |

队列选择本身就是线程池调度策略的一部分。

## 为什么它重要

它把两件事标准化封装：队列存取 + 空/满时的阻塞协作。内部依赖锁、条件队列、可见性规则和局部结构并发控制，是 `Condition` 和并发容器设计的一次合流。

## 在系列里的位置

它是并发容器层和任务系统层之间非常重要的桥梁。

## 推荐回看原文

- [[_posts/concurrency/23-BlockingQueue 如何协调生产者和消费者|23-BlockingQueue 如何协调生产者和消费者]]
- [[_posts/concurrency/10-Condition 如何实现线程等待与通知|10-Condition 如何实现线程等待与通知]]
- [[_posts/concurrency/14-线程池如何复用和调度线程|14-线程池如何复用和调度线程]]

## 相关概念

- [[wiki/concepts/concurrency/Condition|Condition]]
- [[wiki/concepts/concurrency/并发容器|并发容器与数据结构]]
- [[wiki/concepts/concurrency/任务系统|任务系统与系统边界]]
- [[wiki/concepts/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]]
