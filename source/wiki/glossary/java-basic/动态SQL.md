---
title: 动态SQL
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - mybatis
type: glossary
source_series: Java-basic
status: seed
---

# 动态 SQL

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

动态 SQL 是 MyBatis 的核心特性，通过 `<if>`、`<choose>`、`<foreach>`、`<where>`、`<set>`、`<trim>` 等 XML 标签，根据传入参数条件动态拼接 SQL 语句，避免在 Java 代码中手动拼接 SQL 字符串。

## 上下文

各标签作用：`<if test="">` 条件判断是否包含某 SQL 片段；`<choose>/<when>/<otherwise>` 实现多分支选择（类似 switch）；`<foreach collection="" item="" separator="">` 遍历集合生成 IN 子句或批量插入；`<where>` 自动处理 WHERE 关键字并移除开头多余的 AND/OR；`<set>` 用于 UPDATE 语句，自动处理 SET 关键字和末尾多余的逗号；`<trim>` 是最通用的标签，可自定义前缀/后缀及要移除的前后缀字符。`<sql>` 配合 `<include refid="">` 可提取和复用重复 SQL 片段。常见坑点：`<if test="">` 中字符串比较需写双引号单引号嵌套（`test='name != null and name != ""'`）、`<foreach>` 遍历空集合导致 SQL 语法错误、`<where>` 内条件全为 false 时不生成 WHERE 子句（可能导致全表查询）。

## 相关术语

- [[wiki/glossary/java-basic/MyBatis|MyBatis]] — 动态 SQL 是 MyBatis 区别于其他 ORM 框架的核心特性

## 深入阅读

- [[_posts/Java-basic/18-mybatis|java-basics(18) | MyBatis 数据访问：SQL 映射、动态 SQL 与 MyBatis-Plus]]
