---
title: 'Java基础(14) | 日期时间 API：java.time 全梳理'
date: 2026-05-14
abbrlink: 14
tags:
  - Java
  - 日期时间
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

Java 8 之前的日期 API（`Date`、`Calendar`）设计混乱、线程不安全、API 难用，是公认的 Java 黑历史。Java 8 引入的 `java.time` 包彻底解决了这些问题。这篇文章只讲新 API——旧的不值得花时间学，遇到了知道怎么转换就行。

<!-- more -->

## 1. 核心类一览

| 类 | 含义 | 示例 | 典型场景 |
|---|------|------|---------|
| `LocalDate` | 日期（无时间） | 2026-06-16 | 生日、纪念日、业务日期 |
| `LocalTime` | 时间（无日期） | 14:30:00 | 营业时间、闹钟 |
| `LocalDateTime` | 日期 + 时间（无时区） | 2026-06-16T14:30:00 | 本地事件 |
| `ZonedDateTime` | 日期 + 时间 + 时区 | 2026-06-16T14:30+08:00[Asia/Shanghai] | 跨时区业务 |
| `Instant` | 时间戳（UTC 纪元秒） | 1750000000 | 机器时间、日志、数据库 |
| `Duration` | 时间间隔（时分秒） | PT2H30M | 计时、超时 |
| `Period` | 日期间隔（年月日） | P1Y2M3D | 年龄、合同期限 |
| `DateTimeFormatter` | 格式化/解析 | yyyy-MM-dd | 显示、序列化 |

一个核心设计原则：**所有 java.time 对象都是不可变的、线程安全的。** 任何"修改"操作都会返回新对象。

## 2. LocalDate：日期

```java
// 创建
LocalDate today = LocalDate.now();               // 2026-06-16
LocalDate date = LocalDate.of(2026, 6, 16);      // 指定日期
LocalDate parsed = LocalDate.parse("2026-06-16"); // 从字符串解析

// 获取信息
today.getYear();          // 2026
today.getMonth();         // JUNE（枚举）
today.getMonthValue();    // 6（数字）
today.getDayOfMonth();    // 16
today.getDayOfWeek();     // TUESDAY（枚举）
today.getDayOfYear();     // 167
today.lengthOfMonth();    // 30（6 月有 30 天）
today.isLeapYear();       // false

// 计算（返回新对象，原对象不变）
today.plusDays(7);         // 2026-06-23
today.plusWeeks(2);        // 2026-06-30
today.plusMonths(1);       // 2026-07-16
today.minusYears(1);      // 2025-06-16
today.withMonth(1);       // 2026-01-16（替换月份）
today.withDayOfMonth(1);  // 2026-06-01（替换日）

// 比较
date1.isBefore(date2);
date1.isAfter(date2);
date1.isEqual(date2);
```

## 3. LocalTime：时间

```java
// 创建
LocalTime now = LocalTime.now();              // 14:30:15.123
LocalTime time = LocalTime.of(14, 30);        // 14:30
LocalTime time2 = LocalTime.of(14, 30, 15);   // 14:30:15
LocalTime parsed = LocalTime.parse("14:30:15");

// 获取
now.getHour();     // 14
now.getMinute();   // 30
now.getSecond();   // 15
now.getNano();     // 纳秒

// 计算
now.plusHours(2);
now.plusMinutes(30);
now.minusSeconds(10);

// 特殊值
LocalTime.MIN;    // 00:00
LocalTime.MAX;    // 23:59:59.999999999
LocalTime.NOON;   // 12:00
```

## 4. LocalDateTime：日期 + 时间

```java
// 创建
LocalDateTime now = LocalDateTime.now();
LocalDateTime dt = LocalDateTime.of(2026, 6, 16, 14, 30, 0);
LocalDateTime combined = LocalDateTime.of(
    LocalDate.of(2026, 6, 16),
    LocalTime.of(14, 30)
);

// 拆分
LocalDate date = dt.toLocalDate();
LocalTime time = dt.toLocalTime();

// 计算（所有 plus/minus/with 方法都有）
dt.plusDays(1).plusHours(2);
```

## 5. 时区：ZonedDateTime 与 ZoneId

### 5.1 为什么需要时区？

`LocalDateTime` 没有时区信息——"2026-06-16 14:30" 在北京和伦敦表示的不是同一个时刻。跨时区业务必须用 `ZonedDateTime`。

```java
// 查看所有可用时区
ZoneId.getAvailableZoneIds();  // 约 600 个

// 常用时区
ZoneId shanghai = ZoneId.of("Asia/Shanghai");       // 东八区
ZoneId tokyo = ZoneId.of("Asia/Tokyo");             // 东九区
ZoneId utc = ZoneId.of("UTC");                      // 协调世界时
ZoneId london = ZoneId.of("Europe/London");

// 创建 ZonedDateTime
ZonedDateTime shanghaiTime = ZonedDateTime.now(shanghai);
ZonedDateTime tokyoTime = ZonedDateTime.now(tokyo);

// 同一时刻，不同时区
ZonedDateTime meeting = ZonedDateTime.of(
    LocalDateTime.of(2026, 6, 16, 14, 0),
    ZoneId.of("Asia/Shanghai")
);
System.out.println(meeting);
// 2026-06-16T14:00+08:00[Asia/Shanghai]

// 转换时区（同一时刻在东京是几点？）
ZonedDateTime inTokyo = meeting.withZoneSameInstant(ZoneId.of("Asia/Tokyo"));
System.out.println(inTokyo);
// 2026-06-16T15:00+09:00[Asia/Tokyo]
```

### 5.2 时区选择建议

```
存储/传输/日志 → 统一用 UTC（或时间戳）
展示给用户 → 转换为用户所在时区
数据库 → TIMESTAMP WITH TIME ZONE（如 PostgreSQL）或存 UTC 时间戳

// 在广告系统中尤其重要：
// 广告投放按用户当地时间控制（早 8 点到晚 10 点），
// 但竞价记录和计费用 UTC 时间戳
```

## 6. Instant：机器时间

`Instant` 表示时间线上的一个精确点，底层是 UTC 纪元以来的秒数 + 纳秒：

```java
Instant now = Instant.now();
System.out.println(now);   // 2026-06-16T06:30:00.123Z（UTC 时间，Z 代表 UTC）

// 获取时间戳
now.getEpochSecond();      // 秒级时间戳
now.toEpochMilli();        // 毫秒级时间戳（等价于 System.currentTimeMillis()）
now.getNano();             // 纳秒部分

// 从时间戳创建
Instant fromSecond = Instant.ofEpochSecond(1750000000L);
Instant fromMilli = Instant.ofEpochMilli(1750000000000L);

// Instant → ZonedDateTime
ZonedDateTime zdt = now.atZone(ZoneId.of("Asia/Shanghai"));

// ZonedDateTime → Instant
Instant instant = zdt.toInstant();

// 计算
now.plusSeconds(3600);
now.minus(Duration.ofHours(1));
```

## 7. Duration 和 Period：时间间隔

```java
// Duration：精确的时间量（时、分、秒、纳秒）
Duration d1 = Duration.ofHours(2);               // PT2H
Duration d2 = Duration.ofMinutes(30);            // PT30M
Duration d3 = Duration.between(time1, time2);    // 两个时间之间的间隔
Duration d4 = Duration.parse("PT2H30M");         // 从字符串解析

d1.toMinutes();    // 120
d1.toSeconds();    // 7200
d1.plus(d2);       // PT2H30M

// Period：日期量（年、月、日）
Period p1 = Period.ofMonths(3);                  // P3M
Period p2 = Period.between(date1, date2);        // 两个日期之间的间隔
Period p3 = Period.parse("P1Y2M3D");             // 1 年 2 个月 3 天

p2.getYears();
p2.getMonths();
p2.getDays();

// 应用
LocalDate deadline = LocalDate.now().plus(Period.ofMonths(3));
LocalTime end = LocalTime.now().plus(Duration.ofHours(2));
```

### Duration vs Period

| | Duration | Period |
|--|---------|--------|
| 单位 | 秒、纳秒 | 年、月、日 |
| 适用于 | `LocalTime`、`Instant`、`LocalDateTime` | `LocalDate`、`LocalDateTime` |
| 精确性 | 精确（1天 = 86400秒） | 日历概念（1个月可能是28-31天） |

## 8. DateTimeFormatter：格式化与解析

```java
// 预定义格式
LocalDate date = LocalDate.now();
date.format(DateTimeFormatter.ISO_LOCAL_DATE);    // "2026-06-16"
LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
// "2026-06-16T14:30:00"

// 自定义格式
DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyy年MM月dd日 HH:mm:ss");
String text = LocalDateTime.now().format(fmt);   // "2026年06月16日 14:30:00"

// 解析
LocalDateTime parsed = LocalDateTime.parse("2026年06月16日 14:30:00", fmt);

// 带时区的格式化
DateTimeFormatter zonedFmt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss Z");
ZonedDateTime.now().format(zonedFmt);  // "2026-06-16 14:30:00 +0800"

// 常用的 pattern 符号速查
// yyyy → 年（2026）
// MM   → 月（06）
// dd   → 日（16）
// HH   → 时（24小时制）
// hh   → 时（12小时制）
// mm   → 分
// ss   → 秒
// SSS  → 毫秒
// E    → 星期（Mon）
// a    → AM/PM
// Z    → 时区偏移（+0800）
// VV   → 时区ID（Asia/Shanghai）
```

## 9. 与旧 API 互转

项目中难免遇到旧的 `Date` 和 `Calendar`，知道怎么转就行：

```java
// Date ↔ Instant
Date oldDate = new Date();
Instant instant = oldDate.toInstant();            // Date → Instant
Date backToDate = Date.from(instant);             // Instant → Date

// Date → LocalDateTime
LocalDateTime ldt = oldDate.toInstant()
    .atZone(ZoneId.systemDefault())
    .toLocalDateTime();

// LocalDateTime → Date
Date date = Date.from(
    ldt.atZone(ZoneId.systemDefault()).toInstant()
);

// Calendar → ZonedDateTime
Calendar cal = Calendar.getInstance();
ZonedDateTime zdt = cal.toInstant().atZone(cal.getTimeZone().toZoneId());

// 时间戳 → LocalDateTime
long timestamp = System.currentTimeMillis();
LocalDateTime fromTs = LocalDateTime.ofInstant(
    Instant.ofEpochMilli(timestamp),
    ZoneId.of("Asia/Shanghai")
);

// LocalDateTime → 时间戳
long ts = ldt.atZone(ZoneId.of("Asia/Shanghai")).toInstant().toEpochMilli();
```

## 10. 实用工具方法

```java
// 计算年龄
LocalDate birthday = LocalDate.of(2002, 8, 15);
int age = Period.between(birthday, LocalDate.now()).getYears();  // 23

// 判断是否是工作日
boolean isWeekday = !EnumSet.of(DayOfWeek.SATURDAY, DayOfWeek.SUNDAY)
    .contains(LocalDate.now().getDayOfWeek());

// 获取当月第一天 / 最后一天
LocalDate firstDay = LocalDate.now().withDayOfMonth(1);
LocalDate lastDay = LocalDate.now().with(TemporalAdjusters.lastDayOfMonth());

// 获取下一个周一
LocalDate nextMonday = LocalDate.now().with(TemporalAdjusters.next(DayOfWeek.MONDAY));

// 计算两个日期之间的天数
long days = ChronoUnit.DAYS.between(date1, date2);
long hours = ChronoUnit.HOURS.between(dateTime1, dateTime2);

// 判断时间是否在某个范围内
boolean inRange = !now.isBefore(start) && !now.isAfter(end);
```

## 11. 小结

| 主题 | 关键要点 |
|------|---------|
| 核心原则 | 所有 java.time 对象不可变、线程安全 |
| LocalDate/Time/DateTime | 无时区，表示本地日期/时间 |
| ZonedDateTime | 有时区，跨时区业务必用 |
| Instant | UTC 时间戳，存储和传输用 |
| Duration / Period | 时间间隔 vs 日期间隔，不要混用 |
| DateTimeFormatter | ofPattern 自定义格式，线程安全（旧的 SimpleDateFormat 不是） |
| 时区策略 | 存储/日志用 UTC，展示转用户时区 |
| 旧 API 互转 | Date ↔ Instant 为桥梁，再转其他类型 |

---

> **下一篇预告**：构建工具——Maven vs Gradle，依赖管理与多模块项目

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
