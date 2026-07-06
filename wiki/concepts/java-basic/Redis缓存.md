---
title: Redis 缓存
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Redis 缓存

[[wiki/concepts/java-basic/数据访问|返回数据访问]]

## 这一层回答什么问题

> Redis 的五种数据结构分别解决什么？缓存穿透、击穿、雪崩怎么防？Cache Aside 模式为什么删缓存而不是更新？

Redis 是基于内存的键值存储。它不只是一个"快一点的数据库"——它的数据结构和原子操作让它能做分布式锁、计数器、排行榜、消息队列，远不止缓存。

## 五种数据结构

| 类型 | 底层 | 场景 |
|------|------|------|
| String | SDS | 缓存、计数器（INCR）、分布式锁（SETNX） |
| Hash | 哈希表 | 对象缓存（用户信息） |
| List | 双向链表 | 消息队列（LPUSH/BRPOP） |
| Set | 哈希表 | 去重、交集（共同好友） |
| ZSet | 跳跃表 | 排行榜（按分数排序） |

## 缓存三大问题

**穿透**：查一个不存在的数据 → 缓存没有 → 每请求都打 DB。

解决方案：布隆过滤器（直接拒绝不存在的 key），或者缓存空值设短过期。

**击穿**：热点 key 过期瞬间 → 大量请求同时打到 DB。

解决方案：互斥锁（只让一个请求去查 DB、重建缓存），或者逻辑过期（缓存永不过期，后台异步刷新）。

**雪崩**：大量 key 同时过期，或 Redis 宕机 → 所有请求打到 DB。

解决方案：TTL 加随机值（`setex key 3600+random`, 避免同时过期）、Redis 集群/哨兵做高可用、多级缓存。

## Cache Aside 模式

```
读：查缓存 → 有则返回 → 没有查 DB → 写缓存 → 返回
写：更新 DB → 删除缓存（不是更新缓存！）
```

**为什么是删缓存不是更新缓存？** 更新操作可能被并发覆盖——A 更新缓存后、B 又更新缓存，中间的 DB 更新丢失。删缓存后，下次读自然加载最新数据。

## Spring Cache 注解

```java
@Cacheable(value = "users", key = "#id")    // 查缓存
@CachePut(value = "users", key = "#user.id")  // 更新缓存
@CacheEvict(value = "users", key = "#id")    // 删缓存
```

声明式缓存——不用写 RedisTemplate。但注意：`@Cacheable` 的 AOP 也同样受 `this` 调用失效的限制。

## 在系列里的位置

post 21。

## 推荐回看原文

- [[_posts/Java-basic/21-redis|21-Redis 实战]]

## 相关概念

- [[wiki/concepts/java-basic/MySQL事务与索引|MySQL 事务与索引]]
- [[wiki/concepts/java-basic/MyBatis|MyBatis]]
