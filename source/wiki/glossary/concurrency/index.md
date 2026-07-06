---
title: Java 并发词汇表
tags:
  - wiki
  - glossary
  - concurrency
type: glossary
source_series: concurrency
status: seed
---

# Java 并发词汇表

[[wiki/index|返回 Wiki 首页]]  
[[wiki/series/concurrency|返回 Java 高并发系列]]

Java 并发领域有大量底层术语、同步原语缩写和工程概念。这个词汇表提供每个术语的**简短定义**和**快速索引**，不做深度展开——想深入了解任何术语，请跳转到对应的概念页或原始文章。

## 内存模型与底层

| 术语 | 全称 | 一句话 |
|------|------|--------|
| [[wiki/glossary/concurrency/JMM\|JMM]] | Java Memory Model | Java 内存模型，规定多线程下内存可见性的规则 |
| [[wiki/glossary/concurrency/Happens-Before\|Happens-Before]] | — | 判断两个操作是否具有可见性保证的偏序规则 |
| [[wiki/glossary/concurrency/volatile\|volatile]] | — | 保证变量写后读线程立即可见的轻量级同步关键字 |
| [[wiki/glossary/concurrency/Cache-Line\|Cache Line]] | — | CPU 缓存加载数据的最小单位，常见为 64 字节 |
| [[wiki/glossary/concurrency/MESI\|MESI]] | — | 多核 CPU 缓存一致性协议 |
| [[wiki/glossary/concurrency/内存屏障\|内存屏障]] | Memory Barrier | 强制 CPU 刷新缓存或禁止指令重排序的硬件指令 |
| [[wiki/glossary/concurrency/Instruction-Reordering\|指令重排序]] | — | CPU/JIT 为优化性能调整指令执行顺序，可能破坏并发语义 |

## 同步原语

| 术语 | 全称 | 一句话 |
|------|------|--------|
| [[wiki/glossary/concurrency/synchronized\|synchronized]] | — | Java 内置的互斥锁，基于对象 Monitor 实现 |
| [[wiki/glossary/concurrency/Monitor\|Monitor]] | 管程 | Java 对象头中维护的锁机制，也是 wait/notify 的基础 |
| [[wiki/glossary/concurrency/Lock-Upgrade\|锁升级]] | — | 偏向锁 → 轻量级锁 → 重量级锁的逐步升级过程 |
| [[wiki/glossary/concurrency/CAS\|CAS]] | Compare-And-Set | 比较并替换，无锁并发的基础原子操作 |
| [[wiki/glossary/concurrency/AQS\|AQS]] | AbstractQueuedSynchronizer | 构建同步器的底层框架，统一排队与唤醒逻辑 |
| [[wiki/glossary/concurrency/SIGNAL\|SIGNAL]] | — | AQS 中前驱节点标记，表示释放后要唤醒后继 |
| [[wiki/glossary/concurrency/ReentrantLock\|ReentrantLock]] | — | 可重入的显式锁，支持公平/非公平和条件队列 |
| [[wiki/glossary/concurrency/ReentrantReadWriteLock\|ReentrantReadWriteLock]] | — | 读写锁，读读共享、读写互斥、写写互斥 |
| [[wiki/glossary/concurrency/StampedLock\|StampedLock]] | — | 支持乐观读的凭证式读写锁，不可重入 |
| [[wiki/glossary/concurrency/Condition\|Condition]] | — | 锁的条件队列，await/signal 替代 wait/notify |
| [[wiki/glossary/concurrency/LockSupport\|LockSupport]] | — | 底层线程阻塞原语：park/unpark |
| [[wiki/glossary/concurrency/CountDownLatch\|CountDownLatch]] | — | 倒计数门闩，等待一组操作全部完成 |
| [[wiki/glossary/concurrency/Semaphore\|Semaphore]] | — | 信号量，控制同时访问资源的线程数量 |
| [[wiki/glossary/concurrency/Fair-Lock\|公平锁 / 非公平锁]] | — | 公平锁尊重排队顺序，非公平锁允许新线程插队竞争 |

## 并发工具

| 术语 | 全称 | 一句话 |
|------|------|--------|
| [[wiki/glossary/concurrency/ThreadPoolExecutor\|ThreadPoolExecutor]] | — | 通用线程池，管理核心/最大线程数和任务队列 |
| [[wiki/glossary/concurrency/ForkJoinPool\|ForkJoinPool]] | — | 分治任务执行器，核心特征是工作窃取 |
| [[wiki/glossary/concurrency/Work-Stealing\|Work-Stealing]] | 工作窃取 | 空闲 Worker 从其他 Worker 队列偷任务执行的调度策略 |
| [[wiki/glossary/concurrency/Future\|Future]] | — | 表示异步计算结果的句柄，支持取消和等待 |
| [[wiki/glossary/concurrency/FutureTask\|FutureTask]] | — | 结合 Runnable 和 Future 的可执行异步任务 |
| [[wiki/glossary/concurrency/CompletableFuture\|CompletableFuture]] | — | 异步任务编排工具，支持链式组合和异常处理 |
| [[wiki/glossary/concurrency/ConcurrentHashMap\|ConcurrentHashMap]] | — | 桶级并发控制的哈希表，读无锁写局部加锁 |
| [[wiki/glossary/concurrency/BlockingQueue\|BlockingQueue]] | — | 带等待语义的线程安全队列，支持空满阻塞 |
| [[wiki/glossary/concurrency/ThreadLocal\|ThreadLocal]] | — | 线程本地变量，每个线程持有独立副本 |
| [[wiki/glossary/concurrency/AtomicLong\|AtomicLong]] | — | 基于 CAS 的原子长整型，保证单变量原子更新 |
| [[wiki/glossary/concurrency/LongAdder\|LongAdder]] | — | 分散竞争的高并发累加器，适合统计场景 |
| [[wiki/glossary/concurrency/ABA\|ABA]] | — | CAS 的经典边界问题：值回到 A 不代表中间没变化 |

## 线程基础

| 术语 | 全称 | 一句话 |
|------|------|--------|
| [[wiki/glossary/concurrency/线程中断\|线程中断]] | — | 协作式停止机制：通知线程该停了，不强制终止 |
| [[wiki/glossary/concurrency/InterruptedException\|InterruptedException]] | — | 可中断阻塞方法被唤醒时抛出的受检异常 |
| [[wiki/glossary/concurrency/Object-Wait-Notify\|Object.wait/notify]] | — | Java 内置的线程等待/通知机制，基于对象 Monitor |
| [[wiki/glossary/concurrency/Thread-State\|Thread State]] | — | RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED |
| [[wiki/glossary/concurrency/上下文切换\|上下文切换]] | Context Switch | CPU 从一个线程切换到另一个线程的开销 |

## 故障与排查

| 术语 | 全称 | 一句话 |
|------|------|--------|
| [[wiki/glossary/concurrency/死锁\|死锁]] | Deadlock | 多线程互相持有对方所需资源，等待关系成环 |
| [[wiki/glossary/concurrency/活锁\|活锁]] | Livelock | 线程一直在让步重试但没有实质性进展 |
| [[wiki/glossary/concurrency/线程饥饿\|线程饥饿]] | Thread Starvation | 部分线程长期得不到 CPU/锁/连接等资源 |
| [[wiki/glossary/concurrency/竞态条件\|竞态条件]] | Race Condition | 多线程执行顺序不确定导致结果不一致 |
| [[wiki/glossary/concurrency/丢失更新\|丢失更新]] | Lost Update | 两个线程同时读写共享变量导致一次更新丢失 |

## 系统设计

| 术语 | 全称 | 一句话 |
|------|------|--------|
| [[wiki/glossary/concurrency/伪共享\|伪共享]] | False Sharing | 不同变量落在同一条 Cache Line 上导致缓存争抢 |
| [[wiki/glossary/concurrency/Worker-Model\|Worker Model]] | — | Worker 从队列取任务→执行→继续等待的循环模型 |
| [[wiki/glossary/concurrency/Bounded-Queue\|有界/无界队列]] | — | 有界队列形成反压，无界队列隐藏过载风险 |
| [[wiki/glossary/concurrency/Rejection-Policy\|拒绝策略]] | Rejection Policy | 线程池/任务队列过载时的自保方式 |
| [[wiki/glossary/concurrency/Task-Table\|数据库任务表]] | Task Table | 让任务持久化和可恢复的方案，任务状态存 DB |
| [[wiki/glossary/concurrency/MQ\|MQ]] | Message Queue | 分布式任务投递通道，支持削峰和消费扩展 |
| [[wiki/glossary/concurrency/Idempotency\|幂等]] | Idempotency | 同一任务执行多次，最终业务结果与执行一次一致 |

## 使用说明

- 每个词条都是**快速参考**，1-2 分钟读完
- 想看完整上下文：跳到词条末尾的"深入阅读"链接
- 想看原始文章：从 [[wiki/series/concurrency|系列主页]] 按推荐顺序阅读
- 想看概念关系图：在 Obsidian 里筛选 `path:"wiki/concepts/concurrency"`
