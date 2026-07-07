---
title: DateTimeFormatter
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# DateTimeFormatter

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

DateTimeFormatter 是 Java 8 `java.time` 包中的线程安全日期时间格式化器，用于将日期时间对象格式化为字符串或从字符串解析为日期时间对象。

## 上下文

创建方式：预定义格式（`DateTimeFormatter.ISO_LOCAL_DATE`、`ISO_LOCAL_DATE_TIME` 等）和自定义格式（`DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")`）。常用 pattern 符号：yyyy（年）、MM（月）、dd（日）、HH（24小时制时）、hh（12小时制时）、mm（分）、ss（秒）、SSS（毫秒）、Z（时区偏移如 +0800）、VV（时区ID如 Asia/Shanghai）。与旧 API 的 SimpleDateFormat 不同，DateTimeFormatter 是**不可变且线程安全**的，可以定义为 static final 常量在多线程环境中复用，不需要每次创建新实例或加锁。格式化用 `dateTime.format(formatter)`，解析用 `LocalDateTime.parse("2026-06-16 14:30:00", formatter)`。

## 相关术语
- [[wiki/glossary/java-basic/LocalDateTime|LocalDateTime]] — DateTimeFormatter 主要用于格式化/解析 LocalDateTime 等 java.time 对象

## 深入阅读

- [[_posts/Java-basic/14-datetime|java-basics(14) | 日期时间 API：java.time 全梳理]]
