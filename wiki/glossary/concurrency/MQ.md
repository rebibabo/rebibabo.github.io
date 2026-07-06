---
title: MQ
tags:
  - wiki
  - glossary
  - concurrency
  - mq
type: glossary
source_series: concurrency
status: seed
---

# MQ（Message Queue，消息队列）

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

MQ 是分布式消息中间件，提供跨进程、跨机器的任务投递通道。Producer 发送消息到 Broker，Consumer 接收并消费消息。核心能力：削峰、解耦、多消费者扩展、失败重投、死信隔离。

## 上下文

MQ 消费的关键概念链：Broker 保存并投递消息 → Consumer 接收并执行业务 → Ack 确认消息已完成 → 失败则重试投递 → 多次失败进入死信队列。Ack 必须在业务成功后发送（不能先 ack 再处理——否则处理失败消息已丢失）。

MQ 语义通常是"至少一次投递"——消息可能重复到达，因此幂等不能省略。MQ 和数据库任务表的区别：前者擅长分布式投递和削峰，后者擅长状态追踪和补偿。组合方案（MQ + 业务任务表）在实际中常见但不应该过度设计。

## 相关术语

- [[wiki/glossary/concurrency/Task-Table|数据库任务表]] — 侧重状态管理 vs 侧重投递
- [[wiki/glossary/concurrency/Idempotency|幂等]] — MQ 重复投递的兜底
- [[wiki/glossary/concurrency/Worker-Model|Worker Model]] — Consumer 内部的执行模型

## 深入阅读

- [[wiki/concepts/concurrency/可靠任务系统|可靠任务系统概念页（完整版）]]
- [[_posts/concurrency/29-从内存队列到可靠任务系统：数据库任务表与 MQ 如何选择|29-可靠任务系统]]
