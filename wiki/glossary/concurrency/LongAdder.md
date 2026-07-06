---
title: LongAdder
tags:
  - wiki
  - glossary
  - concurrency
  - longadder
type: glossary
source_series: concurrency
status: seed
---

# LongAdder

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`LongAdder` 是 JDK 8 引入的高并发累加器。它把单点 CAS 拆成多个 Cell 上的分散 CAS——线程按 probe 选择不同 Cell 更新，低竞争时优先 CAS `base`。求和时逐 Cell 累加，返回的不是强一致快照。

## 上下文

核心优化：拆分 Cell 分散 CAS 竞争 + Cache Line 填充避免伪共享。适合请求计数、QPS、监控指标等可接受短暂不精确的统计场景。不适合账户余额、库存扣减等强一致场景。

本质：不是比 `AtomicLong` 更原子，而是在更新路径上更会分散竞争。用读取时的弱一致换取写入时的低冲突。

## 相关术语

- [[wiki/glossary/concurrency/AtomicLong|AtomicLong]] — 单点 CAS 的原子变量
- [[wiki/glossary/concurrency/CAS|CAS]] — LongAdder 底层仍是 CAS
- [[wiki/glossary/concurrency/伪共享|False Sharing]] — Cell 填充要解决的问题

## 深入阅读

- [[wiki/concepts/concurrency/LongAdder|LongAdder 概念页（完整版）]]
- [[_posts/concurrency/21-无锁设计、ABA 与 LongAdder|21-LongAdder]]
