---
title: ThreadLocal
tags:
  - wiki
  - concept
  - concurrency
  - threadlocal
type: concept
source_series: concurrency
status: seed
---

# ThreadLocal

[[wiki/concepts/concurrency/异步执行|返回任务执行与异步编排]]

## 定义

`ThreadLocal` 不是用来“让共享对象线程安全”，而是把数据改造成线程私有。

## 它解决什么问题

它回答的是：

> 既然共享会带来竞争，那能不能让每个线程都有自己的上下文副本？

这适合：

- 用户上下文
- trace 信息
- 数据库连接上下文
- 一次请求内的局部状态

## 它的核心思路不是“修复共享”，而是“绕开共享”

前面的锁、CAS、volatile 都是在共享状态已经存在的前提下，想办法把并发访问约束正确。

`ThreadLocal` 走的是另一条路：

> 不让多个线程碰同一份数据，而是让每个线程各自持有一份。

这样线程之间天然没有读写竞争，也就不需要围绕这份数据再做互斥。

## 数据其实不存在线程局部变量对象里，而是挂在线程身上

这点很值得在 wiki 里单独写清。

从 API 表面看，好像是：

```java
tl.set(user);
tl.get();
```

容易让人以为数据存在 `ThreadLocal` 对象本身里。

真实结构更接近：

- 每个 `Thread` 对象内部有一个 `ThreadLocalMap`
- `ThreadLocal` 实例只是 key
- 真正的业务对象是 value

所以不同线程即使共享同一个 `ThreadLocal` 实例，也会因为查的是各自线程自己的 `ThreadLocalMap`，拿到不同数据。

## 为什么在线程池里会出问题

`ThreadLocal` 这个模型有一个隐含前提：

> 线程生命周期最好接近任务生命周期。

如果线程执行完任务就结束，那挂在线程上的数据也会跟着线程结束而自然消失。

但线程池不是这样：

- 任务结束了
- 线程没结束
- 线程会被下一个任务继续复用

于是上一个任务留下的 `ThreadLocal` 数据，也可能被下一个任务看见。

## 线程池里最典型的两个风险

### 数据串用

上一个任务写入的用户 ID、TraceId、租户信息，如果没清理，下一个任务在同一工作线程里 `get()` 时，可能直接读到旧值。

### 生命周期错位

本来只该跟随单次请求存活的对象，结果因为被挂在线程上，生命周期被延长到了线程池工作线程的生命周期。

如果 value 比较大，还会带来持续内存占用。

## 为什么要强调 remove()

`set()` 只是把当前线程这把 key 对应的 value 放进去。

任务结束后，如果不主动 `remove()`：

- 当前线程里的 Entry 还在
- 后续复用这个线程的任务还能读到旧值
- value 也会继续被这条引用链保留

所以在线程池里，一个最重要的工程习惯就是：

```java
try {
    THREAD_LOCAL.set(value);
    // use it
} finally {
    THREAD_LOCAL.remove();
}
```

这不是“代码洁癖”，而是线程复用模型下的必要清理动作。

## 为什么 key 是弱引用、value 仍可能残留

原文后半段一个非常关键的点是：

- `ThreadLocalMap.Entry` 的 key 是弱引用
- value 是强引用

这样设计是为了避免 `ThreadLocal` 实例本身被线程内部的 Map 强行长期保留。

但这不等于 value 一定会自动没问题，因为：

- key 失效后，value 仍然可能暂时留在 Entry 上
- 线程如果长期存活，残留 value 的生命周期也可能被拖长

所以不能把“key 是弱引用”误解成“我不用 remove 也没事”。

## 它最适合什么，不适合什么

它适合：

- 线程内上下文传递
- 一次请求内的用户/链路/租户上下文
- 避免层层手动传参的线程私有信息

它不适合：

- 跨线程共享业务数据
- 在线程池里长期偷懒不清理的上下文缓存
- 把它当成“万能的隐式全局变量”

## 在系列里的位置

它处在异步执行层，但同时又和系统稳定性强相关，是“线程复用”带来隐藏副作用的代表案例。

## 推荐回看原文

- [[_posts/concurrency/18-ThreadLocal 的线程隔离与线程池问题|18-ThreadLocal 的线程隔离与线程池问题]]
- [[_posts/concurrency/14-线程池如何复用和调度线程|14-线程池如何复用和调度线程]]

## 相关概念

- [[wiki/concepts/concurrency/异步执行|任务执行与异步编排]]
- [[wiki/concepts/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]]
- [[wiki/concepts/concurrency/ForkJoinPool|ForkJoinPool]]
- [[wiki/concepts/concurrency/故障模式|故障模式与安全停止]]
- [[wiki/concepts/concurrency/任务系统|任务系统与系统边界]]
