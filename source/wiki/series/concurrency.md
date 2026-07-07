---
title: Java 高并发底层原理
tags:
  - wiki
  - series
  - java
  - concurrency
type: series
source_series: concurrency
status: seed
---

# Java 高并发底层原理

[[wiki/index|返回 Wiki 首页]]

## 系列定位

这组文章不是“并发 API 使用手册”，而是从计算机执行模型、内存可见性、锁与无锁同步、线程调度到并发容器和任务系统，一层层往下钻的底层原理系列。

它和 `Java-basic/10-concurrency` 的关系可以理解为：

- `Java-basic` 给的是全景入门
- `concurrency` 给的是专题深挖

## 这个系列回答什么问题

- CPU、JVM、内存模型到底如何共同决定并发行为
- `synchronized`、`volatile`、CAS、AQS、LockSupport 这些机制为什么成立
- 线程池、Future、CompletableFuture、ForkJoinPool 的执行模型是什么
- 并发容器和同步工具类为什么能安全工作
- 从单机并发走向任务系统、消息队列时，架构边界怎么判断

## 核心概念入口

- [[wiki/concepts/concurrency/并发总图|并发总图]]
- [[wiki/concepts/concurrency/执行模型|执行模型]]
- [[wiki/concepts/concurrency/Java内存模型|Java Memory Model]]
- [[wiki/concepts/concurrency/同步机制|同步机制]]
- [[wiki/concepts/concurrency/AQS|AQS]]
- [[wiki/concepts/concurrency/异步执行|任务执行与异步编排]]
- [[wiki/concepts/concurrency/并发容器|并发容器与数据结构]]
- [[wiki/concepts/concurrency/任务系统|任务系统与系统边界]]
- [[wiki/concepts/concurrency/故障模式|故障模式与安全停止]]

## 第二层关键节点

- [[wiki/concepts/concurrency/CAS|CAS]]
- [[wiki/concepts/concurrency/volatile|volatile]]
- [[wiki/concepts/concurrency/ReentrantLock|ReentrantLock]]
- [[wiki/concepts/concurrency/ThreadLocal|ThreadLocal]]
- [[wiki/concepts/concurrency/ConcurrentHashMap|ConcurrentHashMap]]
- [[wiki/concepts/concurrency/ForkJoinPool|ForkJoinPool]]
- [[wiki/concepts/concurrency/对象监视器|Object Monitor]]
- [[wiki/concepts/concurrency/Condition|Condition]]
- [[wiki/concepts/concurrency/CountDownLatch|CountDownLatch]]
- [[wiki/concepts/concurrency/Semaphore|Semaphore]]
- [[wiki/concepts/concurrency/BlockingQueue|BlockingQueue]]
- [[wiki/concepts/concurrency/LockSupport|LockSupport]]

## 骨架补齐节点

- [[wiki/concepts/concurrency/丢失更新|count++ 与丢失更新]]
- [[wiki/concepts/concurrency/锁竞争与性能开销|锁竞争与性能开销]]
- [[wiki/concepts/concurrency/缓存一致性|缓存一致性]]
- [[wiki/concepts/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]]
- [[wiki/concepts/concurrency/Future|Future]]
- [[wiki/concepts/concurrency/CompletableFuture异常处理|CompletableFuture 异常处理]]
- [[wiki/concepts/concurrency/ABA|ABA]]
- [[wiki/concepts/concurrency/线程中断|线程中断与安全停止]]
- [[wiki/concepts/concurrency/死锁活锁与饥饿|死锁、活锁与饥饿]]
- [[wiki/concepts/concurrency/Worker执行模型|Worker 执行模型]]
- [[wiki/concepts/concurrency/可靠任务系统|可靠任务系统]]

## 推荐阅读顺序

1. [[_posts/concurrency/01-计算机是如何执行Java程序的|java-concurrency（一）—— 计算机是如何执行 Java 程序的]]
2. [[_posts/concurrency/02-为什么count++会出错|java-concurrency（二）—— 为什么 count++ 会出错]]
3. [[_posts/concurrency/03-synchronized为什么能够保证线程安全|java-concurrency（三）—— synchronized 为什么能够保证线程安全]]
4. [[_posts/concurrency/04-synchronized为什么会影响性能|java-concurrency（四）—— synchronized 为什么会影响性能]]
5. [[_posts/concurrency/05-CAS为什么能够在不加锁的情况下更新共享数据|java-concurrency（五）—— CAS 为什么能够在不加锁的情况下更新共享数据]]
6. [[_posts/concurrency/06-多核CPU如何保持缓存一致|java-concurrency（六）—— 多核 CPU 如何保持缓存一致]]
7. [[_posts/concurrency/07-volatile到底解决了什么问题|java-concurrency（七）—— volatile 到底解决了什么问题]]
8. [[_posts/concurrency/08-Java内存到底规定什么|java-concurrency（八）—— Java 内存模型到底规定了什么]]
9. [[_posts/concurrency/09-ReentrantLock 为什么能够实现互斥|java-concurrency（九）—— ReentrantLock 为什么能够实现互斥]]
10. [[_posts/concurrency/10-Condition 如何实现线程等待与通知|java-concurrency（十）—— Condition 如何实现线程等待与通知]]
11. [[_posts/concurrency/11-CountDownLatch 如何等待多个线程完成|java-concurrency（十一）—— CountDownLatch 如何等待多个线程完成]]
12. [[_posts/concurrency/12-Semaphore 如何控制并发线程数量|java-concurrency（十二）—— Semaphore 如何控制并发线程数量]]
13. [[_posts/concurrency/13-Object Monitor 如何实现对象锁与线程等待|java-concurrency（十三）—— Object Monitor 如何实现对象锁与线程等待]]
14. [[_posts/concurrency/14-线程池如何复用和调度线程|java-concurrency（十四）—— 线程池如何复用和调度线程]]
15. [[_posts/concurrency/15-Future 如何获取异步任务的执行结果|java-concurrency（十五）—— FutureTask 如何保存异步任务的结果和异常]]
16. [[_posts/concurrency/16-CompletableFuture 如何编排多个异步任务|java-concurrency（十六）—— CompletableFuture 如何编排多个异步任务]]
17. [[_posts/concurrency/17-CompletableFuture 如何处理异步结果与异常|java-concurrency（十七）—— CompletableFuture 如何处理异步结果与异常]]
18. [[_posts/concurrency/18-ThreadLocal 的线程隔离与线程池问题|java-concurrency（十八）—— ThreadLocal 的线程隔离与线程池问题]]
19. [[_posts/concurrency/19-AQS 独占与共享模式如何完成排队与唤醒|java-concurrency（十九）—— AQS 独占与共享模式如何完成排队与唤醒]]
20. [[_posts/concurrency/20-ReentrantReadWriteLock 与 StampedLock|java-concurrency（二十）—— ReentrantReadWriteLock 与 StampedLock]]
21. [[_posts/concurrency/21-无锁设计、ABA 与 LongAdder|java-concurrency（二十一）—— 无锁设计、ABA 与 LongAdder]]
22. [[_posts/concurrency/22-ConcurrentHashMap 为什么能支持高并发访问|java-concurrency（二十二）—— ConcurrentHashMap 为什么能支持高并发访问]]
23. [[_posts/concurrency/23-BlockingQueue 如何协调生产者和消费者|java-concurrency（二十三）—— BlockingQueue 如何协调生产者和消费者]]
24. [[_posts/concurrency/24-线程中断如何让任务安全停止|java-concurrency（二十四）—— 线程中断如何让任务安全停止]]
25. [[_posts/concurrency/25-LockSupport 如何挂起和唤醒线程|java-concurrency（补充）—— LockSupport 如何挂起和唤醒线程]]
26. [[_posts/concurrency/26-ForkJoinPool 如何通过工作窃取执行任务|java-concurrency—— ForkJoinPool 如何通过工作窃取执行任务]]
27. [[_posts/concurrency/27-死锁、活锁与线程饥饿是如何发生的|死锁、活锁与线程饥饿是如何发生的]]
28. [[_posts/concurrency/28-并发任务处理系统如何设计：从任务模型到 Worker 执行|并发任务处理系统如何设计：从任务模型到 Worker 执行]]
29. [[_posts/concurrency/29-从内存队列到可靠任务系统：数据库任务表与 MQ 如何选择|从内存队列到可靠任务系统：数据库任务表与 MQ 如何选择]]

## 结构脉络

### 1. 运行基础与内存语义

- [[_posts/concurrency/01-计算机是如何执行Java程序的|01]]
- [[_posts/concurrency/02-为什么count++会出错|02]]
- [[_posts/concurrency/03-synchronized为什么能够保证线程安全|03]]
- [[_posts/concurrency/04-synchronized为什么会影响性能|04]]
- [[_posts/concurrency/05-CAS为什么能够在不加锁的情况下更新共享数据|05]]
- [[_posts/concurrency/06-多核CPU如何保持缓存一致|06]]
- [[_posts/concurrency/07-volatile到底解决了什么问题|07]]
- [[_posts/concurrency/08-Java内存到底规定什么|08]]

### 2. 锁、条件队列与同步工具

- [[_posts/concurrency/09-ReentrantLock 为什么能够实现互斥|09]]
- [[_posts/concurrency/10-Condition 如何实现线程等待与通知|10]]
- [[_posts/concurrency/11-CountDownLatch 如何等待多个线程完成|11]]
- [[_posts/concurrency/12-Semaphore 如何控制并发线程数量|12]]
- [[_posts/concurrency/13-Object Monitor 如何实现对象锁与线程等待|13]]

### 3. 任务执行与异步编排

- [[_posts/concurrency/14-线程池如何复用和调度线程|14]]
- [[_posts/concurrency/15-Future 如何获取异步任务的执行结果|15]]
- [[_posts/concurrency/16-CompletableFuture 如何编排多个异步任务|16]]
- [[_posts/concurrency/17-CompletableFuture 如何处理异步结果与异常|17]]
- [[_posts/concurrency/18-ThreadLocal 的线程隔离与线程池问题|18]]

### 4. AQS、容器与高级并发原语

- [[_posts/concurrency/19-AQS 独占与共享模式如何完成排队与唤醒|19]]
- [[_posts/concurrency/20-ReentrantReadWriteLock 与 StampedLock|20]]
- [[_posts/concurrency/21-无锁设计、ABA 与 LongAdder|21]]
- [[_posts/concurrency/22-ConcurrentHashMap 为什么能支持高并发访问|22]]
- [[_posts/concurrency/23-BlockingQueue 如何协调生产者和消费者|23]]
- [[_posts/concurrency/24-线程中断如何让任务安全停止|24]]
- [[_posts/concurrency/25-LockSupport 如何挂起和唤醒线程|25]]
- [[_posts/concurrency/26-ForkJoinPool 如何通过工作窃取执行任务|26]]

### 5. 故障、系统边界与架构延伸

- [[_posts/concurrency/27-死锁、活锁与线程饥饿是如何发生的|27]]
- [[_posts/concurrency/28-并发任务处理系统如何设计：从任务模型到 Worker 执行|28]]
- [[_posts/concurrency/29-从内存队列到可靠任务系统：数据库任务表与 MQ 如何选择|29]]

## 当前这页的作用

这页现在不只是原文目录，也已经是 `wiki` 里的并发总入口。

你可以把它理解成两层导航：

- 想按文章顺序系统学习：走“推荐阅读顺序”
- 想按概念关系拆开理解：走“核心概念入口”

## 当前细化进度

这次已经先按原文 01-18 做了第一轮实质补充，不再只是挂骨架：

- [[wiki/concepts/concurrency/执行模型|执行模型]]：补了源码到 CPU 的执行链、Heap / Stack、线程调度与共享状态来源
- [[wiki/concepts/concurrency/丢失更新|count++ 与丢失更新]]：补了原子性、竞态条件和“三问判断法”
- [[wiki/concepts/concurrency/synchronized|synchronized]]：补了临界区、三种写法和“锁对象而不是锁代码”
- [[wiki/concepts/concurrency/锁竞争与性能开销|锁竞争与性能开销]]：补了竞争、阻塞、唤醒、上下文切换与临界区大小
- [[wiki/concepts/concurrency/CAS|CAS]]：补了三值模型、CAS 循环和与 `synchronized` 的区别
- [[wiki/concepts/concurrency/缓存一致性|缓存一致性]]：补了 Cache Line、副本失效、MESI 理解模型和 CAS 的硬件竞争背景
- [[wiki/concepts/concurrency/volatile|volatile]]：补了可见性、有序性、发布模式和它不能解决 `count++` 的边界
- [[wiki/concepts/concurrency/Java内存模型|Java Memory Model]]：补了 JMM 的定位、program order、数据竞争和它与底层硬件的分工
- [[wiki/concepts/concurrency/ReentrantLock|ReentrantLock]]：补了 state、owner、CAS、重入、等待队列和公平/非公平差异
- [[wiki/concepts/concurrency/Condition|Condition]]：补了 await/signal 语义、条件队列和锁等待队列的区别、以及多 Condition 的业务拆分
- [[wiki/concepts/concurrency/CountDownLatch|CountDownLatch]]：补了一次性闸门模型、countDown 的 CAS 递减、结果汇总边界和 await 可见性
- [[wiki/concepts/concurrency/Semaphore|Semaphore]]：补了许可证模型、共享模式、重复使用语义和 finally 释放边界
- [[wiki/concepts/concurrency/对象监视器|Object Monitor]]：补了 Monitor 与对象的关系、wait/notify 语义和与 Condition 的平行关系
- [[wiki/concepts/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]]：补了任务与线程分离、调度分流顺序、队列差异和拒绝策略含义
- [[wiki/concepts/concurrency/Future|Future]]：补了结果凭证语义、等待/超时/取消边界和它为什么不擅长任务链
- [[wiki/concepts/concurrency/FutureTask|FutureTask]]：补了 Runnable/Future 二合一模型、state/outcome 分工和 submit 后的共享对象语义
- [[wiki/concepts/concurrency/CompletableFuture|CompletableFuture]]：补了起点创建、阶段接力、thenCompose/thenCombine、allOf/anyOf 和 Async 调度差异
- [[wiki/concepts/concurrency/CompletableFuture异常处理|CompletableFuture 异常处理]]：补了异常保存、传播、恢复，以及 exceptionally/handle/whenComplete 的选择边界
- [[wiki/concepts/concurrency/ThreadLocal|ThreadLocal]]：补了 ThreadLocalMap 存储模型、线程池复用风险、remove 习惯和弱引用边界

## 当前 Wiki 覆盖范围

第一版没有急着把 29 篇文章拆成 29 个零散概念，而是先建立 9 个主骨架页面：

- 并发总图：所有知识层次的总入口
- 执行模型：CPU / JVM / 缓存 / 调度
- Java Memory Model：可见性、有序性、happens-before
- 同步机制：锁、无锁、阻塞、唤醒
- AQS：同步器的统一排队框架
- 任务执行与异步编排：线程池、Future、CompletableFuture、ForkJoinPool
- 并发容器与数据结构：ConcurrentHashMap、BlockingQueue、LongAdder
- 任务系统与系统边界：Worker、数据库任务表、MQ、可靠任务系统
- 故障模式与安全停止：死锁、活锁、饥饿、中断

这一轮已经优先拆出了 12 个第二层关键节点：

- [[wiki/concepts/concurrency/CAS|CAS]]
- [[wiki/concepts/concurrency/volatile|volatile]]
- [[wiki/concepts/concurrency/ReentrantLock|ReentrantLock]]
- [[wiki/concepts/concurrency/ThreadLocal|ThreadLocal]]
- [[wiki/concepts/concurrency/ConcurrentHashMap|ConcurrentHashMap]]
- [[wiki/concepts/concurrency/ForkJoinPool|ForkJoinPool]]
- [[wiki/concepts/concurrency/对象监视器|Object Monitor]]
- [[wiki/concepts/concurrency/Condition|Condition]]
- [[wiki/concepts/concurrency/CountDownLatch|CountDownLatch]]
- [[wiki/concepts/concurrency/Semaphore|Semaphore]]
- [[wiki/concepts/concurrency/BlockingQueue|BlockingQueue]]
- [[wiki/concepts/concurrency/LockSupport|LockSupport]]

这一轮也继续补上了 7 个第三层进阶节点：

- [[wiki/concepts/concurrency/synchronized|synchronized]]
- [[wiki/concepts/concurrency/Happens-Before|happens-before]]
- [[wiki/concepts/concurrency/FutureTask|FutureTask]]
- [[wiki/concepts/concurrency/CompletableFuture|CompletableFuture]]
- [[wiki/concepts/concurrency/ReentrantReadWriteLock|ReentrantReadWriteLock]]
- [[wiki/concepts/concurrency/StampedLock|StampedLock]]
- [[wiki/concepts/concurrency/LongAdder|LongAdder]]

这一版把系列主干上的骨架节点已经基本补齐了。后续如果继续扩展，更自然的方向会是：

- AtomicInteger
- ThreadPool 参数与拒绝策略
- CompletableFuture 组合模式
- MQ / 数据库任务表决策树
- AQS 队列节点细节
