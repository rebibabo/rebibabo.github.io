---
title: AQS
tags:
  - wiki
  - concept
  - concurrency
  - aqs
type: concept
source_series: concurrency
status: seed
---

# AQS

[[wiki/concepts/concurrency/同步机制|返回同步机制]]

## 定义

`AQS`，也就是 `AbstractQueuedSynchronizer`，是一套构建同步器的基础框架。

它解决的核心问题不是"锁是什么"，而是：

> 当线程获取资源失败之后，如何排队、阻塞、再被正确唤醒。

## 它为什么重要

很多看上去不同的并发工具，底层其实共享一套排队与唤醒骨架，比如：

- `ReentrantLock`
- `Semaphore`
- `CountDownLatch`
- `ReentrantReadWriteLock`

这也是为什么理解 AQS 后，很多同步器会突然变得"像一个家族"。

## 核心组件

### state：同步状态

AQS 内部维护一个 `int state`，表示同步状态，但具体语义由子类决定：
- `ReentrantLock`：`state = 0` 锁空闲，`state > 0` 被持有并记录重入次数
- `Semaphore`：`state` 表示剩余许可证数量
- `CountDownLatch`：`state` 表示倒计数

### CLH 风格等待队列

获取失败的线程被包装成 `Node`，通过 CAS 插入队尾形成双向链表。队列第一次初始化时先创建 dummy head，真正等待的节点接在后面：

```
head(dummy) <-> Node B <-> Node C
                  |           |
               Thread B    Thread C
```

`head` 不是普通等待节点，而是队列已经推进到的位置。只有前驱是 `head` 的节点才有资格尝试获取资源。

### 独占与共享两种模式

| 模式 | 获取入口 | 释放入口 | 子类规则 |
|---|---|---|---|
| 独占 | `acquire()` | `release()` | `tryAcquire()` / `tryRelease()` |
| 共享 | `acquireShared()` | `releaseShared()` | `tryAcquireShared()` / `tryReleaseShared()` |

独占模式同一时刻只有一个线程能通过；共享模式允许多个线程同时通过。`Semaphore` 和 `CountDownLatch` 都使用共享模式，但一个围绕许可证数量变化，一个围绕倒计时是否归零。

### park / unpark 阻塞与唤醒

AQS 基于 `LockSupport.park/unpark` 完成线程的挂起和唤醒。`park` 让线程暂时挂起不占 CPU，`unpark` 让被挂起线程有机会醒来。被唤醒的线程不会直接获得锁，而是回到获取循环重新调用 `tryAcquire()`。

## 独占模式的核心流程

### acquire：先尝试获取，失败再排队

```java
public final void acquire(int arg) {
    if (!tryAcquire(arg)) {
        acquireQueued(addWaiter(Node.EXCLUSIVE), arg);
    }
}
```

先调用 `tryAcquire()` 直接尝试一次；成功就不需要排队；失败才包装成 `Node` 入队。

### SIGNAL：park 前必须建立唤醒关系

`SIGNAL` 是标在前驱节点上的，不是标在当前节点自己身上。含义是：前驱节点有责任在释放后唤醒后继。

| `waitStatus` | 值 | 含义 |
|---|---:|---|
| `SIGNAL` | `-1` | 后继节点需要被唤醒 |
| `CANCELLED` | `1` | 节点已取消等待 |
| `0` | `0` | 初始状态 |

线程睡下去之前，必须先把前驱改成 `SIGNAL`，确保将来有人负责叫醒它。

### release：释放资源后才唤醒后继

```java
public final boolean release(int arg) {
    if (tryRelease(arg)) {
        // 从 head 出发找到有效后继并 unpark
        return true;
    }
    return false;
}
```

只有 `tryRelease()` 确认资源释放干净（如 `ReentrantLock` 的 `state` 减到 `0`），AQS 才会从 `head` 出发，跳过取消节点，找到有效后继并 `unpark`。

### 完整链路

```
lock() → tryAcquire() 失败 → 入队 → 循环等待
  → 前驱标记 SIGNAL → park()
  
unlock() → tryRelease() 成功 → 清理 SIGNAL → unpark 后继
  → 后继醒来 → 回到获取循环 → tryAcquire() 成功 → setHead()
```

## 共享模式的传播机制

共享模式复用同一条 AQS 同步队列，区别在于入队节点是 `SHARED` 模式。核心差异在于 `tryAcquireShared()` 返回 `int`：

| 返回值 | 含义 |
|---:|---|
| `< 0` | 获取失败，需要入队 |
| `= 0` | 获取成功，但后续共享节点不一定能继续 |
| `> 0` | 获取成功，后续共享节点可能也能继续 |

共享节点获取成功后，会调用 `setHeadAndPropagate()`：当前节点变成新 `head`，同时根据返回值决定是否继续唤醒后面的共享节点。这就是共享模式和独占模式最核心的区别——独占强调"一个成功后其他人继续等"，共享强调"一个成功后可能要继续传播"。

## 公平锁和非公平锁

两者没有改变同步队列，区别只发生在新线程刚来抢锁时：

| 类型 | 获取策略 | 特点 |
|---|---|---|
| 非公平锁 | 新线程先 CAS 抢一次，失败再排队 | 吞吐通常更高，但可能插队 |
| 公平锁 | 先检查队列，前面没人才能抢 | 更尊重等待顺序，但吞吐可能下降 |

普通业务场景 `ReentrantLock` 默认非公平锁；当业务特别关心等待顺序或饥饿风险时，才用公平锁。

## Condition：从"等锁"扩展到"等条件"

AQS 同步队列解决的是"线程想获取锁但暂时获取不到"。`Condition` 解决的是另一个问题：线程已经拿到锁，但发现业务条件不满足，需要暂时等待。

`await()` 让线程从"持锁执行"进入"条件等待"并释放锁，进入 Condition 条件队列。`signal()` 只负责把它从条件队列转回 AQS 同步队列，真正继续执行还要等它重新获得锁。

因此 `await()` 外面必须用 `while` 而不是 `if`——线程从 `await()` 返回只能说明重新拿到了锁，不能说明业务条件一定仍然满足。

## 中断的不同响应方式

| 方法 | 等待期间被中断 | 结果 |
|---|---|---|
| `lock()` | 可被唤醒但不退出 | 继续排队，最终拿到锁后恢复中断标记 |
| `lockInterruptibly()` | 响应中断 | 退出等锁，直接抛 `InterruptedException` |
| `Condition.await()` | 响应中断 | 退出条件等待，但重新拿到锁后才抛异常 |

## 在系列里的位置

它是同步机制层里的总装配框架，位于 `ReentrantLock`、`Condition` 等具体同步器之下。

## 推荐回看原文

- [[_posts/concurrency/19-AQS 独占与共享模式如何完成排队与唤醒|19-AQS 独占与共享模式如何完成排队与唤醒]]
- [[_posts/concurrency/09-ReentrantLock 为什么能够实现互斥|09-ReentrantLock 为什么能够实现互斥]]
- [[_posts/concurrency/10-Condition 如何实现线程等待与通知|10-Condition 如何实现线程等待与通知]]
- [[_posts/concurrency/11-CountDownLatch 如何等待多个线程完成|11-CountDownLatch 如何等待多个线程完成]]
- [[_posts/concurrency/12-Semaphore 如何控制并发线程数量|12-Semaphore 如何控制并发线程数量]]

## 相关概念

- [[wiki/concepts/concurrency/同步机制|同步机制]]
- [[wiki/concepts/concurrency/ReentrantLock|ReentrantLock]]
- [[wiki/concepts/concurrency/Condition|Condition]]
- [[wiki/concepts/concurrency/CountDownLatch|CountDownLatch]]
- [[wiki/concepts/concurrency/Semaphore|Semaphore]]
- [[wiki/concepts/concurrency/LockSupport|LockSupport]]
- [[wiki/concepts/concurrency/线程中断|线程中断]]
- [[wiki/concepts/concurrency/ReentrantReadWriteLock|ReentrantReadWriteLock]]
