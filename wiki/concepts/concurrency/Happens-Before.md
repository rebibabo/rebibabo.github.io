---
title: happens-before
tags:
  - wiki
  - concept
  - concurrency
  - jmm
  - happens-before
type: concept
source_series: concurrency
status: seed
---

# happens-before

[[wiki/concepts/concurrency/Java内存模型|返回 Java Memory Model]]

## 定义

`happens-before` 是 Java 内存模型里用来表达可见性和顺序保证的核心关系。

## 它解决什么问题

它回答的是：

> 一个线程前面做过的写入，什么时候必须对另一个线程后面的读取可见？

## 它可以先理解成“语义上的先于”

`happens-before` 不等于现实时间里谁真的先跑完，也不等于两个操作紧挨着发生。

它更像一种语言层承诺：

- 前一个操作的结果必须对后一个操作可见
- 编译器和 CPU 不能制造出违背这个关系的执行结果

所以它不是在描述“时钟上的先后”，而是在描述“程序员能不能依赖这条顺序”。

## 为什么它重要

很多并发结论其实都能统一还原到这一句话：

- 为什么 `volatile` 有效
- 为什么加同一把锁能建立可见性
- 为什么线程启动、结束、join 会带来同步语义

`happens-before` 就是把这些“规则”装进同一个框架里的名字。

## 它是怎么建立出来的

单独一个 `happens-before` 关系，往往不是凭空出现的，而是由几类规则拼起来：

- 同一个线程里的 `program order`
- 跨线程的同步关系
- 传递性

最常见的跨线程同步关系包括：

- volatile 写 -> 后续对同一变量的 volatile 读
- unlock -> 后续对同一把锁的 lock
- `Thread.start()` -> 新线程中的动作
- 线程中的动作 -> 另一个线程 `join()` 成功返回

## 一个最典型的例子

```java
data = 42;
ready = true;
```

如果 `ready` 是 `volatile`，另一个线程这样读：

```java
if (ready) {
    System.out.println(data);
}
```

那么链路是这样的：

1. 写线程里，`data = 42` 先于 `ready = true`
2. `ready = true` 和另一个线程读到 `ready` 建立同步关系
3. 读线程里，先读 `ready`，后读 `data`

通过传递性，`data = 42` 的结果就被带到了另一个线程后续的 `read data`。

这也是为什么很多“发布-读取”模式能成立。

## 它不等于什么

它不等于“现实时间上一定先发生”。

它更像一种内存语义约束：

- 前一个操作的结果对后一个操作可见
- 前一个操作在同步语义上排在后一个操作之前

它也不等于“结果唯一”。即使某个写 happens-before 某个读，读操作有时仍然可能在合法范围内看到其他并发写入的结果。它的作用更像是排除不合法结果，而不是永远指定唯一答案。

## 为什么它特别适合拿来判断并发代码

遇到一段并发代码时，一个高价值问题是：

> 这两个线程之间，到底有没有建立 happens-before？

如果没有，就应该默认它们之间的可见性和顺序没有被可靠保证。

这比“我本地跑了几次没出错”更靠谱，因为 happens-before 分析的是语义保证，不是偶然时序。

## 在系列里的位置

它是 `JMM` 里最核心的抽象层，很多后续同步器的正确性都可以最终追到这里。

## 推荐回看原文

- [[_posts/concurrency/08-Java内存到底规定什么|08-Java 内存模型到底规定了什么]]
- [[_posts/concurrency/07-volatile到底解决了什么问题|07-volatile 到底解决了什么问题]]

## 相关概念

- [[wiki/concepts/concurrency/Java内存模型|Java Memory Model]]
- [[wiki/concepts/concurrency/volatile|volatile]]
- [[wiki/concepts/concurrency/synchronized|synchronized]]
- [[wiki/concepts/concurrency/CountDownLatch|CountDownLatch]]
