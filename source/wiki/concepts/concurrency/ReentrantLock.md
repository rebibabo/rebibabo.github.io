---
title: ReentrantLock
tags:
  - wiki
  - concept
  - concurrency
  - reentrantlock
type: concept
source_series: concurrency
status: seed
---

# ReentrantLock

[[wiki/concepts/concurrency/同步机制|返回同步机制]]

## 定义

`ReentrantLock` 是 Java 里最常见的显式锁之一，提供互斥、可重入、公平策略、可中断等待和超时获取等能力。

## 它解决什么问题

它回答的是：

> 不用 `synchronized`，怎么也能把临界区安全地串行化？

## 它是怎么做到互斥的

原文里最核心的一条主线是：

> `ReentrantLock` 不是靠语法块天然互斥，而是靠一组同步状态规则来决定谁能进入临界区。

可以先把它拆成几个关键部件：

- `state`：记录锁当前是否空闲，后面也承担重入计数
- `owner`：记录当前持锁线程是谁
- CAS：在线程首次竞争空闲锁时，原子地把状态从空闲改成占用
- 等待队列：获取失败的线程先排队，再等待被唤醒

也就是说，`ReentrantLock` 的互斥并不是“魔法”，而是：

- 先原子地决定谁抢到锁
- 再记录是谁持有锁
- 失败者不一直空转，而是进入等待队列

## 为什么获取锁要用 CAS

如果两个线程只是普通地判断：

```java
if (state == 0) {
    state = 1;
}
```

那么它们都可能先看到 `state == 0`，最后都以为自己拿到了锁。

CAS 的价值就在这里：

```java
compareAndSet(0, 1)
```

只有一个线程能成功把锁从“空闲”改成“占用”。这一步决定了互斥的入口。

## 什么是可重入

`ReentrantLock` 的“reentrant”不是附属特性，而是它名字里最重要的一半。

如果同一个线程已经持有锁，又在临界区里调用了另一个也要获取同一把锁的方法，它不应该把自己卡死。

所以：

- 第一次拿锁时，线程成为 `owner`
- 再次拿同一把锁时，如果还是这个 `owner`，允许继续进入
- 同时把 `state` 从“是否占用”扩展成“持有了几次”

这就是可重入的本质：同一线程可以重复进入，但必须按相同次数成对释放。

## 为什么 unlock 要写在 finally 里

`ReentrantLock` 和 `synchronized` 的一个工程差别非常大：

- `synchronized` 退出代码块时会自动释放
- `ReentrantLock` 必须显式 `unlock()`

如果线程已经成功拿到锁，但临界区抛异常后没有执行 `unlock()`，那么：

- `state` 不会回到 `0`
- `owner` 不会清空
- 等待队列里的线程可能一直过不去

所以标准写法必须是：

```java
lock.lock();
try {
    // critical section
} finally {
    lock.unlock();
}
```

## 它和 AQS 的关系

`ReentrantLock` 是理解 AQS 最好的具体入口之一，因为它把 AQS 的几个抽象件全都落到了真实场景里：

- `state` 不再是抽象整数，而是锁状态和重入计数
- 队列不再是抽象等待结构，而是“没抢到锁的线程”
- 唤醒不再是抽象动作，而是“释放锁后让等待线程重新竞争”

所以看 `ReentrantLock` 时，最好把它理解成：

> AQS 在“独占锁”这个场景下的一次具体落地。

## 公平和非公平到底差在哪

它们都能保证互斥，差别不在“安全性”，而在“新线程能不能插队”。

- 非公平锁：新来的线程可以先直接尝试抢锁
- 公平锁：如果队列里已经有人等着，新线程通常不能绕过它们

非公平模式通常吞吐更好，因为它减少了严格排队带来的调度成本；公平模式更强调等待顺序，但不代表绝对按现实时间严格执行。

## 为什么它重要

它是理解 `AQS` 最好的入口之一，因为它把很多抽象机制都落到了一个具体同步器上：

- `state`
- `owner`
- 可重入计数
- 等待队列
- `park / unpark`

## 它和 synchronized 的关系

- 两者都能实现互斥
- `synchronized` 更偏语言内置监视器
- `ReentrantLock` 更偏可编程同步器
- 两者都提供可见性与互斥，但可扩展能力不同

所以它不是“替代一切”的锁，而是显式同步模型的代表。

## 在系列里的位置

它位于 `CAS` 和 [[wiki/concepts/concurrency/AQS|AQS]] 之间，是“具体锁”如何站在底层同步框架之上的关键例子。

## 推荐回看原文

- [[_posts/concurrency/09-ReentrantLock 为什么能够实现互斥|09-ReentrantLock 为什么能够实现互斥]]
- [[_posts/concurrency/10-Condition 如何实现线程等待与通知|10-Condition 如何实现线程等待与通知]]
- [[_posts/concurrency/19-AQS 独占与共享模式如何完成排队与唤醒|19-AQS 独占与共享模式如何完成排队与唤醒]]

## 相关概念

- [[wiki/concepts/concurrency/CAS|CAS]]
- [[wiki/concepts/concurrency/AQS|AQS]]
- [[wiki/concepts/concurrency/Condition|Condition]]
- [[wiki/concepts/concurrency/synchronized|synchronized]]
- [[wiki/concepts/concurrency/volatile|volatile]]
- [[wiki/concepts/concurrency/故障模式|故障模式与安全停止]]
