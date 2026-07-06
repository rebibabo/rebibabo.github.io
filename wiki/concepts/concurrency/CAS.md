---
title: CAS
tags:
  - wiki
  - concept
  - concurrency
  - cas
type: concept
source_series: concurrency
status: seed
---

# CAS

[[wiki/concepts/concurrency/同步机制|返回同步机制]]

## 定义

`CAS`，也就是 `Compare And Swap`，是一种基于“比较旧值是否仍然成立，再尝试写入新值”的原子更新机制。

## 它解决什么问题

它回答的是：

> 不加互斥锁，线程还能不能安全更新共享值？

对于计数器、状态位、链表节点引用这类单点更新，CAS 往往能避免把线程都拉进阻塞等待。

## CAS 的三个值

一次 CAS 更新至少要围绕三个值来理解：

- Current：共享变量此刻的真实值
- Expected：当前线程之前读到并相信仍然成立的旧值
- Update：当前线程基于旧值算出来的新值

它的核心规则是：

```text
如果 Current == Expected
就把 Current 更新成 Update
否则本次更新失败
```

关键不在“比较”本身，而在于：

> 比较旧值是否仍然成立，以及写入新值，必须作为一个原子整体完成。

## 为什么它能避免丢失更新

以 `count++` 为例，两个线程都先读到 `0`，也都算出 `1`。

- 线程 A 执行 `CAS(0, 1)` 成功
- 线程 B 再执行 `CAS(0, 1)` 时，当前值已经变成 `1`

这时线程 B 不能直接把自己算出的 `1` 写回去，因为那样又会把线程 A 的结果覆盖掉。

所以 CAS 的真正价值是：

> 写入之前先验证“我计算时基于的旧值，现在还成立吗”。

如果不成立，就说明当前线程的结果已经过期，必须放弃并重算。

## 最常见的形态：CAS 重试循环

CAS 很少只做一次。更常见的是下面这种 Retry Loop：

1. 读取当前值
2. 基于这个值计算新值
3. 尝试 `compareAndSet`
4. 失败就重新读取并重试

```java
int expected;
int update;

do {
    expected = count.get();
    update = expected + 1;
} while (!count.compareAndSet(expected, update));
```

这就是为什么 `AtomicInteger.incrementAndGet()` 虽然没显式写锁，仍然能正确完成单值更新。

## 它为什么重要

CAS 是 Java 并发里最关键的无锁基础件之一。

很多更高层的能力都建立在它之上，比如：

- `AtomicInteger`
- `ReentrantLock` 获取锁时的状态竞争
- `ConcurrentHashMap` 空桶插入
- `LongAdder`

## 它的代价和边界

CAS 不是“永远比锁好”。

它更适合：

- 更新逻辑短
- 共享状态集中
- 失败后可以重试

但在竞争激烈时，CAS 可能会不断失败重试，还会带出 `ABA` 这类问题。

它更擅长的是：

- 单个值更新
- 状态位切换
- 链表或桶头这类指针替换

而不擅长的是：

- 需要同时修改多个字段
- 需要把业务判断和状态更新绑成一个整体
- 失败重试代价很高的复杂逻辑

## CAS 和 `synchronized` 的直观区别

`synchronized` 的思路是先拿独占权限，再进入临界区。

CAS 的思路是先算结果，提交前再验证旧值是否仍然成立。

所以两者不是简单的“谁更先进”，而是两种不同策略：

- `synchronized`：用互斥换正确性
- CAS：用验证与重试换掉部分阻塞等待

## 在系列里的位置

它位于 `synchronized` 之后、`AQS` 和并发容器之前，是从“加锁同步”走向“无锁同步”的关键节点。

## 推荐回看原文

- [[_posts/concurrency/05-CAS为什么能够在不加锁的情况下更新共享数据|05-CAS 为什么能够在不加锁的情况下更新共享数据]]
- [[_posts/concurrency/21-无锁设计、ABA 与 LongAdder|21-无锁设计、ABA 与 LongAdder]]
- [[_posts/concurrency/09-ReentrantLock 为什么能够实现互斥|09-ReentrantLock 为什么能够实现互斥]]

## 相关概念

- [[wiki/concepts/concurrency/丢失更新|count++ 与丢失更新]]
- [[wiki/concepts/concurrency/锁竞争与性能开销|锁竞争与性能开销]]
- [[wiki/concepts/concurrency/ABA|ABA]]
- [[wiki/concepts/concurrency/Java内存模型|Java Memory Model]]
- [[wiki/concepts/concurrency/同步机制|同步机制]]
- [[wiki/concepts/concurrency/AQS|AQS]]
- [[wiki/concepts/concurrency/ConcurrentHashMap|ConcurrentHashMap]]
