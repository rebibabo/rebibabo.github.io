---
title: ConcurrentHashMap
tags:
  - wiki
  - glossary
  - concurrency
  - concurrenthashmap
type: glossary
source_series: concurrency
status: seed
---

# ConcurrentHashMap

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`ConcurrentHashMap` 是 Java 中最常用的高并发 Map。JDK 1.8 采用桶级并发控制：空桶插入用 CAS，非空桶修改只锁当前桶头节点，读操作无锁。不支持 null key/value。

## 上下文

核心设计原则：对外可见的结构变化缩成一次安全发布。新增节点先构造完成再接入链表（尾插），删除节点通过改变可见路径绕过旧节点——读线程不会看到半成品结构。扩容时多线程协助迁移，用 `ForwardingNode` 引导读写线程到新表。

计数采用类似 `LongAdder` 的分散机制。复合操作要使用原子方法（`putIfAbsent`、`computeIfAbsent`、`remove(key,value)` 等）而非先判断后修改。

## 相关术语

- [[wiki/glossary/concurrency/CAS|CAS]] — 空桶插入的原子操作
- [[wiki/glossary/concurrency/BlockingQueue|BlockingQueue]] — 另一个重要的并发容器
- [[wiki/glossary/concurrency/LongAdder|LongAdder]] — 计数机制的相似思路

## 深入阅读

- [[wiki/concepts/concurrency/ConcurrentHashMap|ConcurrentHashMap 概念页（完整版）]]
- [[_posts/concurrency/22-ConcurrentHashMap 为什么能支持高并发访问|22-ConcurrentHashMap]]
