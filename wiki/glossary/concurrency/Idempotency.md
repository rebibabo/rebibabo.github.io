---
title: 幂等
tags:
  - wiki
  - glossary
  - concurrency
  - idempotency
type: glossary
source_series: concurrency
status: seed
---

# 幂等（Idempotency）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

幂等指的是同一个任务/消息即使被执行多次，最终业务结果应与执行一次保持一致。这是分布式系统中补偿重复投递、重试和故障恢复的安全兜底。

## 上下文

为什么并发系统需要幂等：消息可能重复投递（MQ 至少一次语义）、任务状态抢占不能完全保证唯一执行（抢到后宕机）、网络超时重试导致重复请求。实现方式：用 `task_id` 或 `biz_id` 作为幂等键，处理前检查是否已处理过。

幂等不是性能优化，而是正确性保障。它和任务状态抢占是两层防护：抢占尽量减重复，幂等兜底重复。两者解决的问题不同，缺一不可。

## 相关术语

- [[wiki/glossary/concurrency/Task-Table|数据库任务表]] — 状态抢占减少重复，幂等兜底
- [[wiki/glossary/concurrency/MQ|MQ]] — MQ 的至少一次投递需要幂等
- [[wiki/glossary/concurrency/丢失更新|Lost Update]] — 幂等防止的也是"重复操作导致不一致"

## 深入阅读

- [[wiki/concepts/concurrency/可靠任务系统|可靠任务系统概念页]]
- [[_posts/concurrency/29-从内存队列到可靠任务系统：数据库任务表与 MQ 如何选择|29-可靠任务系统]]
