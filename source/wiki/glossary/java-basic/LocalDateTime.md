---
title: LocalDateTime
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# LocalDateTime

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

LocalDateTime 是 Java 8 `java.time` 包中表示日期+时间的不可变对象（如 `2026-06-16T14:30:00`），不包含时区信息，线程安全。

## 上下文

LocalDateTime 由 LocalDate 和 LocalTime 组合而成，可通过 `LocalDateTime.now()`、`LocalDateTime.of(year, month, day, hour, minute)`、`LocalDateTime.parse("2026-06-16T14:30:00")` 创建。支持 `toLocalDate()` / `toLocalTime()` 拆分，以及 `plusDays()` / `minusHours()` / `withMonth()` 等方法，所有"修改"操作返回新对象，原对象不变。适用于不需要时区的本地事件场景（如会议提醒记录、日志记录），但跨时区业务（如全球用户系统）必须使用 ZonedDateTime。与旧 Date API 互转需经过 Instant 作为桥梁。注意 LocalDateTime 不存储时区，无法直接表示时间线上的精确时刻，需要配合 ZoneId 才能转为 Instant。

## 相关术语
- [[wiki/glossary/java-basic/ZonedDateTime|ZonedDateTime]] — 带时区的完整日期时间，跨时区业务应使用 ZonedDateTime
- [[wiki/glossary/java-basic/Instant|Instant]] — 时间线上的精确时刻，LocalDateTime 配合 ZoneId 才能转为 Instant
- [[wiki/glossary/java-basic/DateTimeFormatter|DateTimeFormatter]] — 线程安全的日期时间格式化器

## 深入阅读

- [[_posts/Java-basic/14-datetime|Java基础(14) | 日期时间 API：java.time 全梳理]]
