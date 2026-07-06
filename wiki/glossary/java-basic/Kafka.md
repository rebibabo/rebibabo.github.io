---
title: Kafka
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Kafka

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Kafka 是一种高吞吐的分布式消息系统，底层基于"分布式的、可持久化的日志文件"设计，Producer 将消息写入 Topic 的 Partition（分区日志文件），Consumer 从 Partition 按 Offset 顺序拉取消费，消息消费后不会删除。

## 上下文

Kafka 高吞吐的核心技术：顺序写磁盘（每个 Partition 是 append-only 文件）、页缓存（写入 Page Cache 即返回，不等真正落盘）、零拷贝（sendfile 系统调用直接从 OS 内存发送到网卡）、批量发送与压缩（Producer 本地缓冲区攒批后一次性发送）。与 RabbitMQ 的核心区别：Kafka 消息消费后保留在磁盘（按 retention 配置保留时间），多个 Consumer Group 可各自独立、完整地消费同一份消息流；RabbitMQ 消息 ACK 后即删除，路由更灵活但吞吐量较低。Spring 集成用 `spring-kafka`，通过 `KafkaTemplate.send(topic, key, message)` 发送（key 决定分区），`@KafkaListener(topics, groupId)` 消费。Offset 存储在内部 Topic `__consumer_offsets` 中，自动提交可能丢消息，手动提交更可靠但可能重复消费。

## 相关术语

- [[wiki/glossary/java-basic/RabbitMQ|RabbitMQ]] — 基于 AMQP 的消息中间件，路由更灵活但吞吐量较低
- [[wiki/glossary/java-basic/partition|partition]] — Kafka 的物理存储单元，决定并行处理能力和顺序性
- [[wiki/glossary/java-basic/消费者组|消费者组]] — 共享 groupId 的消费者集合，组内竞争消费、组间广播

## 深入阅读

- [[_posts/Java-basic/31-kafka|Java基础(番外) Kafka 入门：分区、副本与消费者组原理]]
