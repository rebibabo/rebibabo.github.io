---
title: Redis
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - redis
  - cache
type: glossary
source_series: Java-basic
status: seed
---

# Redis

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Redis（Remote Dictionary Server）是基于内存的高性能键值存储系统，支持五种核心数据结构——String、Hash、List、Set、Sorted Set——并提供持久化、发布订阅、Lua 脚本等扩展能力。

## 上下文

Redis 将数据存储在内存中，读写速度可达每秒十万级，因此被广泛用作缓存、分布式锁和消息队列。五种数据结构各有典型场景：String 存储简单键值或序列化对象（也可做分布式锁 SETNX）；Hash 存储对象属性（用户信息）；List 实现消息队列（LPUSH/BRPOP）；Set 实现去重、交并集运算（共同好友）；Sorted Set 实现排行榜（score 排序）。持久化方式：RDB（快照，后台执行，可能丢失最后一次快照后的数据）和 AOF（追加写命令日志，更可靠但文件更大）。Java 端最常用 Spring Data Redis 配合 RedisTemplate 进行对象缓存，需注意序列化方案选择（默认 JDK 序列化可读性差，推荐 JSON 序列化）。常见坑点：Big Key 导致阻塞（DEL 大 key 时 Redis 单线程阻塞）、热 Key 导致单节点 CPU 打满、缓存与数据库双写不一致。

## 相关术语

- [[wiki/glossary/java-basic/缓存穿透|缓存穿透]] — 查询不存在的数据导致请求穿透缓存打到数据库，Redis 缓存策略需应对的核心问题之一
- [[wiki/glossary/java-basic/缓存雪崩|缓存雪崩]] — 大量缓存集中过期导致数据库压力骤增，需通过过期时间随机化等策略应对
- [[wiki/glossary/java-basic/事务|事务]] — 缓存与数据库双写时需考虑事务一致性，防止数据不一致

## 深入阅读

- [[_posts/Java-basic/21-redis|Java基础(21) | Redis 实战：Spring Data Redis 与缓存策略]]
