---
title: ThreadPoolExecutor
tags:
  - wiki
  - glossary
  - concurrency
  - threadpool
type: glossary
source_series: concurrency
status: seed
---

# ThreadPoolExecutor

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`ThreadPoolExecutor` 是 Java 中最通用的线程池实现。它管理核心线程数、最大线程数、任务队列和拒绝策略四个核心参数，决定了任务提交后是先创建线程、先排队、还是被拒绝。

## 上下文

线程池的执行流程：提交任务 → 当前线程数 < corePoolSize？创建核心线程执行 → 队列 offer() 成功？任务入队等待 → 当前线程数 < maximumPoolSize？创建非核心线程执行 → 执行拒绝策略。

核心参数设计必须和队列类型一起看：无界队列会让 maximumPoolSize 很难发挥作用（任务几乎一直排队）；SynchronousQueue 会让线程池更积极创建新线程（不缓存任务、直接交接）。拒绝策略常见四种：AbortPolicy（抛异常）、CallerRunsPolicy（调用者自己执行）、DiscardPolicy（静默丢弃）、DiscardOldestPolicy（丢弃最旧任务）。

## 相关术语

- [[wiki/glossary/concurrency/BlockingQueue|BlockingQueue]] — 线程池的任务队列
- [[wiki/glossary/concurrency/Rejection-Policy|Rejection Policy]] — 队列满后的自保策略
- [[wiki/glossary/concurrency/ForkJoinPool|ForkJoinPool]] — 另一种分治型线程池

## 深入阅读

- [[wiki/concepts/concurrency/ThreadPoolExecutor|ThreadPoolExecutor 概念页（完整版）]]
- [[_posts/concurrency/14-线程池如何复用和调度线程|14-线程池]]
