---
title: ZonedDateTime
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# ZonedDateTime

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

ZonedDateTime 是 Java 8 `java.time` 包中带时区的完整日期时间对象（如 `2026-06-16T14:30+08:00[Asia/Shanghai]`），不可变且线程安全。

## 上下文

ZonedDateTime 由 LocalDateTime + ZoneId + ZoneOffset 组成，可通过 `ZonedDateTime.now(ZoneId.of("Asia/Shanghai"))` 或 `ZonedDateTime.of(LocalDateTime, ZoneId)` 创建。核心操作是 `withZoneSameInstant(ZoneId)` ——将同一时刻转换为另一时区的表示（如北京时间 14:00 = 东京时间 15:00）。时区 ID 使用 `ZoneId.of("区域/城市")` 格式，如 "Asia/Shanghai"、"UTC"、"America/New_York"。最佳实践：存储/传输/日志统一使用 UTC（或时间戳），展示给用户时转换为用户所在时区。数据库建议使用 TIMESTAMP WITH TIME ZONE 或存 UTC 时间戳。这在广告系统中尤其重要——投放按用户当地时间控制，但竞价和计费使用 UTC 时间戳。

## 相关术语
- [[wiki/glossary/java-basic/LocalDateTime|LocalDateTime]] — ZonedDateTime 由 LocalDateTime + ZoneId + ZoneOffset 组成
- [[wiki/glossary/java-basic/Instant|Instant]] — 通过 toInstant() / atZone() 互相转换，表示同一时刻的不同时区表示

## 深入阅读

- [[_posts/Java-basic/14-datetime|Java基础(14) | 日期时间 API：java.time 全梳理]]
