---
title: volatile
tags:
  - wiki
  - concept
  - concurrency
  - volatile
type: concept
source_series: concurrency
status: seed
---

# volatile

[[wiki/concepts/concurrency/Java内存模型|返回 Java Memory Model]]

## 定义

`volatile` 是 Java 提供的一种内存语义，用来为单个变量建立可见性和有序性规则。

## 它解决什么问题

它回答的是：

> 一个线程改了某个标志位或状态位，另一个线程什么时候必须看到？

典型场景是：

- 停止标志
- 发布完成标志
- 配置状态同步

## 它的第一价值：可见性

最经典的场景就是停止标志：

```java
private static volatile boolean running = true;
```

一个线程反复读取 `running`，另一个线程把它改成 `false`。`volatile` 的核心要求是：

> 对这个变量的写入，后续读取它的线程必须能够看到。

它解决的是“看不看得到”的问题，而不是“谁先执行”的问题。

## 它的第二价值：有序性

`volatile` 不只是在单个变量上做“最新值可见”，还会建立一条发布顺序。

一个典型模式是：

```java
data = 42;
ready = true;
```

如果 `ready` 是 `volatile`，那么它表达的是：

- `ready = true` 之前的普通写，不能被挪到这个 volatile 写之后
- 另一个线程一旦读到 `ready == true`，后面的普通读就必须能看到前面已经发布出去的结果

所以 `volatile` 常被用来做“发布标志”，而不只是“状态位”。

## 它不是“每次都绕过缓存”

一个常见但不够准确的说法是：

> volatile 每次读都直接读主内存，每次写都直接刷回主内存。

更准确的理解是：

- JVM 会在合适位置使用带有内存语义的读写指令或屏障
- CPU 仍然可能使用寄存器和 Cache
- Java 规定的是观察结果必须满足什么语义，而不是要求你脑中必须想象成“完全不用缓存”

所以 `volatile` 是语言层语义，不是“关闭硬件优化”的关键字。

## 它保证什么

- 对同一个 `volatile` 变量的写，对后续读这个变量的线程可见
- 它会限制相关读写的重排序

更具体地说，它适合建立一种“发布-读取”关系：

- 写线程先写普通数据
- 再写 volatile 标志
- 读线程先读 volatile 标志
- 再读普通数据

## 它不保证什么

`volatile` 不会把一段代码变成临界区。

所以它不能单独解决：

- `count++`
- 复合读改写
- 多个变量之间的一致更新

例如：

```java
private volatile int count = 0;

public void increment() {
    count++;
}
```

这里的 `count++` 仍然会被拆成读、算、写三步，所以照样可能发生 [[wiki/concepts/concurrency/丢失更新|丢失更新]]。

这些问题通常还要回到 [[wiki/concepts/concurrency/CAS|CAS]]、锁或更高层同步器。

## 它最适合什么场景

`volatile` 最适合下面这类模式：

- 一个线程写，其他线程读
- 写入不依赖旧值
- 变量本身承担“状态发布”或“完成信号”的作用

常见例子：

- 线程停止标志
- 配置引用切换
- 初始化完成标志

## 它和 happens-before 的关系

`volatile` 真正站得住脚，不是因为“感觉上更快看到值”，而是因为 JMM 规定：

> 对一个 volatile 变量的写，happens-before 随后对同一个变量的读。

所以想彻底理解 `volatile`，最好连着 [[wiki/concepts/concurrency/Happens-Before|happens-before]] 一起看。

## 在系列里的位置

它是 `JMM` 里最容易被直接用到、也最容易被误解的关键点。

## 推荐回看原文

- [[_posts/concurrency/07-volatile到底解决了什么问题|07-volatile 到底解决了什么问题]]
- [[_posts/concurrency/08-Java内存到底规定什么|08-Java 内存模型到底规定了什么]]
- [[_posts/concurrency/02-为什么count++会出错|02-为什么 count++ 会出错]]

## 相关概念

- [[wiki/concepts/concurrency/Java内存模型|Java Memory Model]]
- [[wiki/concepts/concurrency/Happens-Before|happens-before]]
- [[wiki/concepts/concurrency/缓存一致性|缓存一致性]]
- [[wiki/concepts/concurrency/丢失更新|count++ 与丢失更新]]
- [[wiki/concepts/concurrency/CAS|CAS]]
- [[wiki/concepts/concurrency/同步机制|同步机制]]
- [[wiki/concepts/concurrency/故障模式|故障模式与安全停止]]
