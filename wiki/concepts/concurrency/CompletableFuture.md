---
title: CompletableFuture
tags:
  - wiki
  - concept
  - concurrency
  - completablefuture
type: concept
source_series: concurrency
status: seed
---

# CompletableFuture

[[wiki/concepts/concurrency/异步执行|返回任务执行与异步编排]]

## 定义

`CompletableFuture` 是 Java 里用来编排异步任务关系的核心工具。

## 它解决什么问题

它回答的是：

> 如果一个异步任务完成后，还要自动推动后续异步步骤，能不能不用调用线程一次次 `get()`、再手动提交下一步？

## 它和 Future 的根本区别

`Future` 更像“单个异步结果凭证”。

`CompletableFuture` 更像“异步阶段关系图”。

也就是说，它真正改变的不是“能不能拿结果”，而是：

> 能不能提前把后续步骤登记好，让前一个阶段完成后自动推动下一步。

所以调用线程的角色，从“反复等待并手工推进”变成了“先把任务关系描述出来”。

## 起点怎么创建

这一层最常见的两个起点是：

- `runAsync()`：没有业务返回值
- `supplyAsync()`：有业务返回值

它们表达的是：

- 先把第一步异步跑起来
- 返回一个后续可以继续接链的 `CompletableFuture`

## 单阶段完成后，下一步通常有三种形态

原文这里拆得很清楚，可以直接保留成判断模板：

- `thenApply()`：用上一步结果，产出新结果
- `thenAccept()`：用上一步结果，但不再产出业务结果
- `thenRun()`：只关心上一步已经结束，不关心结果

所以不要先背方法名，先问两个问题：

1. 下一步要不要上一步结果？
2. 下一步还要不要产出新结果？

## `thenCompose` 为什么重要

它是这张卡里最关键的一个“会不会嵌套”的分界点。

如果下一步本身已经返回 `CompletableFuture<R>`，那就不能再把它当普通结果直接套一层，否则会变成：

```text
CompletableFuture<CompletableFuture<R>>
```

`thenCompose()` 的价值，就是把“依赖上一步结果再启动一个异步阶段”展平成一层。

所以它适合：

- 前后依赖
- 且下一步本身也是异步任务

## `thenCombine` 代表的是另一类关系

不是所有任务都前后依赖。

如果两个任务彼此独立，可以同时启动，最后再汇合，就更适合 `thenCombine()`。

所以可以先把这两个关系分开记：

- `thenCompose()`：A 完成后，才能决定如何启动 B
- `thenCombine()`：A 和 B 可以并行跑，最后合并结果

这也是 `CompletableFuture` 真正比 `Future` 更强的地方之一，因为它开始能表达“关系”，而不只是“结果”。

## `allOf` 和 `anyOf` 解决的是批量等待

当任务变多时，不再适合一层层硬编码拼接。

- `allOf()`：等全部完成
- `anyOf()`：等任意一个先完成

其中一个很值得保留下来的点是：

> `allOf()` 只表示“它们都结束了”，不会自动把业务结果帮你收集成列表。

结果仍然各自保存在原来的 `CompletableFuture` 里。

## 普通版和 Async 版的区别不要只理解成“是不是异步”

`thenApply()` 和 `thenApplyAsync()` 等名字很像，但真正差别在于：

- 后续动作由谁来调度
- 是否显式切换到异步执行器

也就是说，`Async` 更多是在表达“后续阶段的执行调度方式”，而不只是一个笼统的“更异步”。

## 它最适合什么场景

`CompletableFuture` 最适合这几类任务编排：

- 多阶段顺序依赖
- 多任务并行汇合
- 结果转换和透传
- 异常恢复与降级

如果只是提交一个单任务、以后拿结果，[[wiki/concepts/concurrency/Future|Future]] / [[wiki/concepts/concurrency/FutureTask|FutureTask]] 往往已经够用。

## 为什么它重要

它把异步编程从“等待单个结果”推进到了“描述整个任务链”。

所以它最擅长的不是保存单个结果，而是表达：

- 顺序依赖
- 并行汇合
- 结果转换
- 异常恢复

## 它和 FutureTask 的关系

- [[wiki/concepts/concurrency/FutureTask|FutureTask]] 更像单个异步任务结果对象
- `CompletableFuture` 更像异步任务编排图

## 在系列里的位置

它位于 `FutureTask` 之后，是异步执行层里最重要的编排节点之一。

## 推荐回看原文

- [[_posts/concurrency/16-CompletableFuture 如何编排多个异步任务|16-CompletableFuture 如何编排多个异步任务]]
- [[_posts/concurrency/17-CompletableFuture 如何处理异步结果与异常|17-CompletableFuture 如何处理异步结果与异常]]

## 相关概念

- [[wiki/concepts/concurrency/异步执行|任务执行与异步编排]]
- [[wiki/concepts/concurrency/Future|Future]]
- [[wiki/concepts/concurrency/FutureTask|FutureTask]]
- [[wiki/concepts/concurrency/CompletableFuture异常处理|CompletableFuture 异常处理]]
- [[wiki/concepts/concurrency/ForkJoinPool|ForkJoinPool]]
- [[wiki/concepts/concurrency/故障模式|故障模式与安全停止]]
