---
title: Condition
tags:
  - wiki
  - concept
  - concurrency
  - condition
type: concept
source_series: concurrency
status: seed
---

# Condition

[[wiki/concepts/concurrency/同步机制|返回同步机制]]

## 定义

`Condition` 是和 `ReentrantLock` 绑定使用的条件等待机制。

## 它解决什么问题

它回答的是：

> 线程已经拿到锁了，但业务条件还不满足，接下来该怎么办？

这时线程不能一直占着锁空转，而应该：

- 释放锁
- 进入条件等待
- 被通知后再回来重新竞争锁

## 为什么有了锁还不够

锁只解决“谁能进入临界区”，不解决“进去以后条件是否已经满足”。

最典型的例子就是生产者消费者：

- 消费者已经拿到锁
- 但队列还是空的
- 它不能一直占着锁等，因为生产者也需要同一把锁来放数据

所以这里真正需要的是：

> 条件不满足时，先释放锁，再等待条件变化。

这就是 `Condition` 的位置。

## `await()` 到底做了什么

`await()` 不能简单理解成“当前线程睡一会儿”。

它至少做了三件事：

1. 当前线程进入这个 `Condition` 对应的条件等待队列
2. 释放当前持有的 `ReentrantLock`
3. 暂停执行，直到后续被通知并重新拿回锁

所以 `await()` 返回时，一个很关键的事实是：

> 线程已经重新获得了那把锁。

这也是为什么外层通常还能安全继续访问共享状态。

## 为什么必须在持锁状态下调用

`await()` 不是一个脱离锁独立存在的 API。

必须先持有与它绑定的那把 `ReentrantLock`，否则就会有经典问题：

- 线程先检查到条件不满足
- 还没真正进入等待
- 另一个线程已经修改条件并发送通知
- 当前线程随后才开始等待，结果把这次通知错过去了

所以 `await()` 必须和同一把锁绑定在一起，才能把“检查条件”“进入等待”“释放锁”衔接成一个可靠过程。

## 为什么要用 while，而不是 if

正确写法通常是：

```java
while (queue.isEmpty()) {
    notEmpty.await();
}
```

而不是：

```java
if (queue.isEmpty()) {
    notEmpty.await();
}
```

原因不是语法偏好，而是语义上：

- 收到通知不等于条件一定满足
- 线程被唤醒后还要重新竞争锁
- 等它真正重新拿到锁时，条件可能又被别的线程改掉了

所以每次从 `await()` 返回，都要重新检查业务条件。

## `signal()` 不是“直接把锁给你”

`signal()` 的作用是：

> 通知一个等待线程，条件可能已经变化，可以回来重新竞争锁。

它不表示：

- 等待线程立刻开始执行
- 锁已经直接交过去了
- 条件一定已经满足

通知线程调用 `signal()` 时，通常还在持锁状态里，所以等待线程即使收到通知，也得等对方真正 `unlock()` 之后，才有机会继续推进。

## 条件队列和锁等待队列不是一回事

这一点很容易混。

- 锁等待队列：线程想拿 `ReentrantLock`，但还没拿到
- 条件队列：线程已经拿到过锁，但因为业务条件不成立，主动 `await()`

线程在 `Condition` 上等待时，不是在“等锁空闲”，而是在“等条件变化”。等收到 `signal()` 后，它才会再回到锁竞争这条线上。

## 为什么一把锁可以有多个 Condition

同一把锁下，可能同时存在多个不同业务条件。

例如有界队列里：

- 消费者等的是“队列非空”
- 生产者等的是“队列未满”

如果都塞进同一个等待队列，就会有很多无效唤醒。把它们拆成多个 `Condition`，本质上就是把“等待原因”按业务条件分类。

## 它为什么重要

`Condition` 把“互斥”和“等待条件成立”拆成了两件事：

- `ReentrantLock` 负责谁能进入临界区
- `Condition` 负责条件不满足时怎么等

这也是很多阻塞队列、同步器和任务协作模型的重要基础。

## 它和 Object Monitor 的关系

- `Object Monitor` 对应 `synchronized + wait/notify`
- `Condition` 对应 `ReentrantLock + await/signal`
- 两者都遵循“等待时释放锁，被通知后重新竞争锁”

两者解决的是很相似的问题，但编程模型不同。

## 在系列里的位置

它位于 [[wiki/concepts/concurrency/ReentrantLock|ReentrantLock]] 之后、[[wiki/concepts/concurrency/BlockingQueue|BlockingQueue]] 之前，是“条件协作”这条线的关键桥梁。

## 推荐回看原文

- [[_posts/concurrency/10-Condition 如何实现线程等待与通知|10-Condition 如何实现线程等待与通知]]
- [[_posts/concurrency/09-ReentrantLock 为什么能够实现互斥|09-ReentrantLock 为什么能够实现互斥]]
- [[_posts/concurrency/23-BlockingQueue 如何协调生产者和消费者|23-BlockingQueue 如何协调生产者和消费者]]

## 相关概念

- [[wiki/concepts/concurrency/ReentrantLock|ReentrantLock]]
- [[wiki/concepts/concurrency/对象监视器|Object Monitor]]
- [[wiki/concepts/concurrency/BlockingQueue|BlockingQueue]]
- [[wiki/concepts/concurrency/AQS|AQS]]
- [[wiki/concepts/concurrency/LockSupport|LockSupport]]
