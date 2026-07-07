---
title: RabbitMQ
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# RabbitMQ

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

RabbitMQ 是基于 AMQP 协议的消息中间件，通过 Exchange（交换机）将 Producer 发送的消息按路由规则转发到 Queue（队列），Consumer 从 Queue 中消费消息，实现服务间的异步解耦。

## 上下文

RabbitMQ 的消息流转路径为 Producer -> Exchange -> Queue -> Consumer。Exchange 有三种主要类型：Direct（精确匹配 routing key）、Fanout（广播到所有绑定队列）、Topic（通配符模糊匹配）。核心概念包括：消息确认机制（ACK）——手动 ACK 比自动 ACK 更可靠，消费者处理完业务逻辑后才确认；消息持久化（durable queue + PERSISTENT delivery mode）防止 Broker 重启丢消息；生产者确认（Publisher Confirm）防止发送环节丢消息。消息可靠性需要三段链路一起保证：生产者确认 + 持久化 + 手动 ACK。默认"至少一次"语义意味着业务必须做幂等处理（唯一索引/状态机/Redis 去重）。Spring 集成用 `spring-boot-starter-amqp`，通过 `RabbitTemplate.convertAndSend()` 发送，`@RabbitListener` 监听消费。

## 相关术语

- [[wiki/glossary/java-basic/Kafka|Kafka]] — 高吞吐分布式日志系统，与 RabbitMQ 互补的消息中间件选择
- [[wiki/glossary/java-basic/事务|事务]] — 消息可靠性三段链路中，业务幂等处理依赖事务保证

## 深入阅读

- [[_posts/Java-basic/30-RabbitMQ|java-basics(番外) 消息队列入门：为什么用、怎么用、踩坑点]]
