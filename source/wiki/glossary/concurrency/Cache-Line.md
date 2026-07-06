---
title: Cache Line
tags:
  - wiki
  - glossary
  - concurrency
  - cache-line
type: glossary
source_series: concurrency
status: seed
---

# Cache Line（缓存行）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

Cache Line 是 CPU 缓存加载数据的最小单位，通常在 64 字节（桌面/服务器处理器）。即使程序只读一个 `int`（4 字节），CPU 也会把包含它的整条 64 字节数据块一并加载到缓存。

## 上下文

理解并发为什么需要关注 Cache Line：多个核心同时修改不同变量时，如果这些变量落在同一条 Cache Line 上，表面上互不干扰，但缓存层面会因为 MESI 协议导致该 Cache Line 在不同核心间反复失效和转移——这就是 False Sharing（伪共享）。

JDK 中 `LongAdder` 的 Cell 填充、`@Contended` 注解，本质上都是在利用 Cache Line 隔离来避免伪共享。

## 相关术语

- [[wiki/glossary/concurrency/MESI|MESI]] — 缓存一致性协议，定义 Cache Line 在不同核心间的状态转换
- [[wiki/glossary/concurrency/伪共享|False Sharing]] — Cache Line 粒度过大导致的缓存争抢
- [[wiki/glossary/concurrency/LongAdder|LongAdder]] — 通过 Cache Line 隔离优化高并发累加

## 深入阅读

- [[wiki/concepts/concurrency/缓存一致性|Cache Coherence 概念页]]
- [[_posts/concurrency/06-多核CPU如何保持缓存一致|06-多核 CPU 如何保持缓存一致]]
