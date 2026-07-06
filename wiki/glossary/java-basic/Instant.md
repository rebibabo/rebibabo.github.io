---
title: Instant
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Instant

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Instant 是 Java 8 `java.time` 包中表示时间线上一个精确点的不可变对象，底层存储 UTC 纪元（1970-01-01T00:00:00Z）以来的秒数加纳秒偏移，用于机器时间和日志记录。

## 上下文

Instant 通过 `Instant.now()` 获取当前时刻（输出如 `2026-06-16T06:30:00.123Z`，Z 代表 UTC），`getEpochSecond()` 获取秒级时间戳，`toEpochMilli()` 获取毫秒级时间戳（等价于 `System.currentTimeMillis()`）。可从时间戳创建：`Instant.ofEpochSecond(seconds)` 或 `Instant.ofEpochMilli(millis)`。与 ZonedDateTime 互转：`instant.atZone(zoneId)` 转为有时区的日期时间，`zonedDateTime.toInstant()` 转回 Instant。Instant 是旧 Date API 与新 java.time API 之间的桥梁：`oldDate.toInstant()` 和 `Date.from(instant)`。适用于存储时间戳到数据库、API 响应中的时间字段、日志记录等场景，避免时区混乱。

## 相关术语
- [[wiki/glossary/java-basic/LocalDateTime|LocalDateTime]] — 本地日期时间，配合 ZoneId 可转为 Instant
- [[wiki/glossary/java-basic/ZonedDateTime|ZonedDateTime]] — 带时区日期时间，通过 toInstant() 转为机器时间

## 深入阅读

- [[_posts/Java-basic/14-datetime|Java基础(14) | 日期时间 API：java.time 全梳理]]
