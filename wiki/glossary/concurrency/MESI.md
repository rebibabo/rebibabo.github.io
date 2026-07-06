---
title: MESI
tags:
  - wiki
  - glossary
  - concurrency
  - mesi
type: glossary
source_series: concurrency
status: seed
---

# MESI（缓存一致性协议）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

MESI 是多核 CPU 保持各核心缓存数据一致的核心协议。它将每条 Cache Line 标记为四种状态之一：**M**odified（已修改，独占）、**E**xclusive（独占未修改）、**S**hared（多核共享）、**I**nvalid（失效）。

## 上下文

当一个 Core 修改其缓存中的变量时，MESI 协议通过总线广播让其他 Core 中同一 Cache Line 失效（标记为 Invalid），迫使它们下次读取时从主内存或修改者缓存中获取最新值。

这也是为什么 CAS 在高竞争时性能下降——多个核心同时 CAS 同一个变量，该变量所在的 Cache Line 在不同核心间反复失效和转移（"缓存乒乓"）。无锁设计的性能瓶颈不是 CAS 指令本身慢，而是缓存一致性开销。

## 相关术语

- [[wiki/glossary/concurrency/Cache-Line|Cache Line]] — MESI 操作的单位
- [[wiki/glossary/concurrency/伪共享|False Sharing]] — MESI 协议下不同变量同 Cache Line 导致的性能问题
- [[wiki/glossary/concurrency/CAS|CAS]] — CAS 竞争导致 MESI 缓存乒乓

## 深入阅读

- [[wiki/concepts/concurrency/缓存一致性|Cache Coherence 概念页]]
- [[_posts/concurrency/06-多核CPU如何保持缓存一致|06-多核 CPU 如何保持缓存一致]]
