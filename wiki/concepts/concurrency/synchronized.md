---
title: synchronized
tags:
  - wiki
  - concept
  - concurrency
  - synchronized
type: concept
source_series: concurrency
status: seed
---

# synchronized

[[wiki/concepts/concurrency/同步机制|返回同步机制]]

## 定义

`synchronized` 是 Java 内置的互斥同步机制。

更准确地说，它规定了一条最基础的并发规则：

> 访问同一份共享状态的线程，进入临界区之前必须先竞争同一把锁。

## 它解决什么问题

它回答的是：

> 当一组读改写操作必须作为一个整体执行时，怎样让别的线程暂时进不来？

## 临界区是什么

被 `synchronized` 保护起来、同一时刻只允许一个线程进入的那段代码，通常叫临界区。

对于 `count++` 这类问题，重点不是把加法变成单条指令，而是把：

- 读旧值
- 计算新值
- 写回结果

这一整组步骤包成一个不能被别的线程从中间插进来的整体。

所以 `synchronized` 解决的是复合操作的完整性问题。

## 为什么它重要

它是很多并发原理的起点，因为它把“线程安全”第一次落成了非常直观的规则：

- 先竞争同一把锁
- 进入临界区
- 执行完成再释放

## 它锁的是什么

更准确地说，`synchronized` 锁住的不是代码文本，而是某个对象关联的监视器语义。

所以理解它时，必须同时看：

- 锁对象是谁
- 共享状态是谁
- 所有线程是不是都遵守同一把锁

实例同步方法本质上等价于：

```java
public void increment() {
    synchronized (this) {
        count++;
    }
}
```

所以它锁的是 `this`，不是方法名本身。

## 三种常见写法

### 实例同步方法

```java
public synchronized void increment() {
    count++;
}
```

锁的是当前实例 `this`，适合保护这个对象自己的状态。

### 静态同步方法

```java
public static synchronized void increment() {
    count++;
}
```

锁的是 `Class` 对象，也就是类级别的一把锁，适合保护静态共享状态。

### 同步代码块

```java
private final Object lock = new Object();

public void increment() {
    synchronized (lock) {
        count++;
    }
}
```

这种写法可以显式指定锁对象，也能把临界区缩到真正需要保护的几行代码。

## `synchronized` 生效的前提

很多人第一次踩坑，不是因为没写 `synchronized`，而是因为锁对象选错了。

它要生效，至少要满足两件事：

1. 多个线程访问的是同一份共享状态
2. 多个线程竞争的是同一把锁

如果每次调用都临时 `new Object()` 当锁，那么每个线程拿到的都是不同锁对象，互斥就根本没有建立起来。

## 它提供的是互斥，不是免费性能

`synchronized` 的第一目标是正确性，不是吞吐量最大化。

它最适合：

- 需要把多步读改写操作包成整体
- 需要保护多个字段之间的一致性
- 业务判断和状态更新必须放在一起完成

至于它为什么会带来等待、阻塞和性能开销，要继续看 [[wiki/concepts/concurrency/锁竞争与性能开销|锁竞争与性能开销]]。

## 在系列里的位置

它位于 `count++` 之后、[[wiki/concepts/concurrency/CAS|CAS]] 之前，是“先用互斥解决复合操作冲突”的最基础节点。

## 推荐回看原文

- [[_posts/concurrency/03-synchronized为什么能够保证线程安全|03-synchronized 为什么能够保证线程安全]]
- [[_posts/concurrency/04-synchronized为什么会影响性能|04-synchronized 为什么会影响性能]]
- [[_posts/concurrency/13-Object Monitor 如何实现对象锁与线程等待|13-Object Monitor 如何实现对象锁与线程等待]]

## 相关概念

- [[wiki/concepts/concurrency/丢失更新|count++ 与丢失更新]]
- [[wiki/concepts/concurrency/对象监视器|Object Monitor]]
- [[wiki/concepts/concurrency/ReentrantLock|ReentrantLock]]
- [[wiki/concepts/concurrency/CAS|CAS]]
- [[wiki/concepts/concurrency/锁竞争与性能开销|锁竞争与性能开销]]
- [[wiki/concepts/concurrency/Java内存模型|Java Memory Model]]
