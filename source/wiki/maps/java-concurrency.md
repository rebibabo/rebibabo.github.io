---
title: Java 并发学习路径
tags:
  - wiki
  - map
  - concurrency
  - learning-path
type: map
status: seed
---

# Java 并发学习路径

[[wiki/index|返回 Wiki 首页]]

这是一张按**依赖关系**组织的学习地图——每一层概念是上一层的基础，建议从下往上阅读。

## 概念依赖图

```mermaid
graph TD
    subgraph L7["Layer 7 任务系统"]
        WM["Worker Model"] --> TT["数据库任务表"]
        TT --- MQ
        MQ --> ID["幂等"]
    end

    subgraph L6["Layer 6 故障与排查"]
        DL["死锁"]
        LL["活锁"]
        STV["线程饥饿"]
        RC["竞态条件"]
        TI["线程中断"]
    end

    subgraph L5["Layer 5 线程与执行"]
        TPE["ThreadPoolExecutor"] --> FJP["ForkJoinPool"]
        FT["Future/FutureTask"] --> CF["CompletableFuture"]
    end

    subgraph L4["Layer 4 无锁与并发工具"]
        CAS2["CAS"] --> ABA["ABA"]
        CAS2 --> LA["LongAdder"]
        CHM["ConcurrentHashMap"]
        BQ["BlockingQueue"]
        TL["ThreadLocal"]
    end

    subgraph L3["Layer 3 高级同步器"]
        AQS2["AQS"] --> RWL["ReentrantReadWriteLock"]
        AQS2 --> SL["StampedLock"]
        AQS2 --> CDL["CountDownLatch"]
        AQS2 --> SEM["Semaphore"]
        AQS2 --> COND["Condition"]
    end

    subgraph L2["Layer 2 同步原语"]
        SYN["synchronized"]
        MON["Monitor"]
        LUP["锁升级"]
        CAS1["CAS"] --> RL["ReentrantLock"] --> LS["LockSupport"]
    end

    subgraph L1["Layer 1 内存模型"]
        JMM["JMM"]
        HB["Happens-Before"]
        VOL["volatile"]
        IR["指令重排序"]
        MB["内存屏障"]
    end

    subgraph L0["Layer 0 硬件基础"]
        EM["CPU 执行模型"]
        CL["Cache Line"]
        MESI
    end

    L0 --> L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> L7
```

## 推荐阅读路线

### 路线 A：系统学习（从底向上）

| 阶段   | 主题               | 核心概念                                                                  | 原始文章                       |
| ---- | ---------------- | --------------------------------------------------------------------- | -------------------------- |
| 0 硬件 | CPU 如何执行 Java 程序 | 执行模型、Cache Line、MESI                                                  | post 01, 06                |
| 1 内存 | Java 内存模型        | JMM、Happens-Before、volatile、重排序                                       | post 02, 07, 08            |
| 2 同步 | 锁与同步原语           | synchronized、Monitor、锁升级、ReentrantLock、AQS、LockSupport                | post 03-04, 09, 13, 19, 25 |
| 3 高级 | 高级同步器            | Condition、CountDownLatch、Semaphore、ReentrantReadWriteLock、StampedLock | post 10-12, 20             |
| 4 无锁 | 无锁与并发工具          | CAS、ABA、LongAdder、ConcurrentHashMap、BlockingQueue、ThreadLocal         | post 05, 18, 21-23         |
| 5 执行 | 线程池与异步           | ThreadPoolExecutor、Future/CompletableFuture、ForkJoinPool              | post 14-17, 26             |
| 6 故障 | 故障排查             | 死锁/活锁/饥饿、线程中断、jstack                                                  | post 24, 27                |
| 7 系统 | 任务系统设计           | Worker Model、有界队列、任务表、MQ、幂等                                           | post 28-29                 |

### 路线 B：问题驱动（按痛点跳读）

| 遇到的问题 | 直接跳到 |
| --- | --- |
| `count++` 结果不对 | [[wiki/concepts/concurrency/丢失更新\|Lost Update]] → [[wiki/glossary/concurrency/CAS\|CAS]] |
| 程序莫名卡住 | [[wiki/concepts/concurrency/死锁活锁与饥饿\|死锁/活锁/饥饿]] |
| 线程池怎么配都不对 | [[wiki/concepts/concurrency/ThreadPoolExecutor\|ThreadPoolExecutor]] → [[wiki/concepts/concurrency/BlockingQueue\|BlockingQueue]] |
| 服务重启后任务丢了 | [[wiki/concepts/concurrency/可靠任务系统\|可靠任务系统]] |
| 并发容器选哪个 | [[wiki/concepts/concurrency/ConcurrentHashMap\|ConcurrentHashMap]] → [[wiki/concepts/concurrency/BlockingQueue\|BlockingQueue]] |
| 异步任务怎么编排 | [[wiki/concepts/concurrency/CompletableFuture\|CompletableFuture]] |
| volatile 到底管不管用 | [[wiki/glossary/concurrency/volatile\|volatile]] → [[wiki/glossary/concurrency/JMM\|JMM]] |
| AQS 是什么为什么重要 | [[wiki/concepts/concurrency/AQS\|AQS]] |
| synchronized 和 ReentrantLock 怎么选 | [[wiki/glossary/concurrency/synchronized\|synchronized]] vs [[wiki/glossary/concurrency/ReentrantLock\|ReentrantLock]] |

## 同步机制层

```mermaid
graph TD
    AQS["AQS 框架<br/>state · CLH 队列 · park/unpark"]

    AQS --> EX["独占模式<br/>ReentrantLock"]
    AQS --> SH["共享模式<br/>Semaphore · CountDownLatch"]
    AQS --> COND["Condition<br/>条件队列 · await/signal"]

    EX --> RWL["ReentrantReadWriteLock<br/>读共享 · 写独占"]
    RWL --> SL["StampedLock<br/>乐观读 · stamp 校验"]
```

## 执行与任务层

```mermaid
graph LR
    REQ["请求线程"] -->|提交 Task| BQ["有界队列<br/>ArrayBlockingQueue"]
    BQ --> WPSUB

    subgraph WPSUB["Worker Pool"]
        W1["Worker-1"]
        W2["Worker-2"]
        W3["Worker-N"]
    end

    WPSUB --> PROC["Processor<br/>业务逻辑"]
    WPSUB --> FH["FailureHandler<br/>重试 · 死信"]

    BQ -->|升级方案| DB["数据库任务表<br/>可恢复 · 可追踪"]
    BQ -->|升级方案| MQ["MQ<br/>削峰 · 分布式投递"]
```

## 故障排查速查

```mermaid
graph TD
    STUCK["程序 '卡住'"] --> CPU{"CPU 高？"}

    CPU -->|是| HIGH["top -Hp → jstack nid → 业务代码<br/>可能: 死循环 · 活锁 · 大量计算"]
    CPU -->|否| LOW["看线程状态"]

    LOW --> BLOCKED["大量 BLOCKED<br/>→ 锁竞争 / 死锁"]
    LOW --> WAITING["大量 WAITING<br/>→ 线程池 / 队列 / 条件等待"]

    STUCK --> TASK["任务不执行？"]
    TASK --> METRICS["activeCount · queueSize · completedTaskCount<br/>可能: Worker 打满 · 队列堆积 · 长任务占坑"]
```

## 相关入口

- [[wiki/series/concurrency\|Java 高并发系列（原始文章）]]
- [[wiki/glossary/concurrency/index\|Java 并发词汇表]]
- [[wiki/concepts/concurrency/并发总图\|并发概念总图]]

