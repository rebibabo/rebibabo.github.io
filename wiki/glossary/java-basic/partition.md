---
title: partition
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# partition

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Kafka Partition（分区）是 Topic 的物理存储单元，每个分区是一个独立的、只追加（append-only）的日志文件，是 Kafka 并行处理和顺序性保证的基本单位。

## 上下文

Producer 通过 `hash(key) % 分区数` 决定消息写入哪个分区——相同的 key 永远落到同一个分区，从而保证同一业务实体（如同一个 orderId）的消息在分区内严格有序。如果不指定 key，Kafka 轮询各分区以均匀分布数据。分区数决定了一个 Consumer Group 内的最大并行消费能力——一个分区只能被组内一个消费者消费，消费者数超过分区数会导致闲置。因此创建 Topic 时建议分区数略多于当前消费者数，为未来扩容留出空间（分区数创建后很难修改，改了会打乱 key->分区的映射）。分区内有序、分区间不保证顺序，这是 Kafka 顺序性的核心结论。

## 相关术语

- [[wiki/glossary/java-basic/Kafka|Kafka]] — 分布式消息系统，Topic 由多个 partition 组成
- [[wiki/glossary/java-basic/消费者组|消费者组]] — 组内消费者数超过分区数时，多出的消费者闲置

## 深入阅读

- [[_posts/Java-basic/31-kafka|Java基础(番外) Kafka 入门：分区、副本与消费者组原理]]
