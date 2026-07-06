---
title: SQL 窗口函数
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# SQL 窗口函数

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

SQL 窗口函数通过 `OVER()` 子句在每一行数据旁边计算一个基于"窗口范围"的统计值，不合并行，保留明细的同时能获取分组排名、前后行对比、分组汇总等信息。

## 上下文

窗口函数的基本语法：`<函数> OVER (PARTITION BY 分组列 ORDER BY 排序列 ROWS/RANGE 框架子句)`。`PARTITION BY` 划分窗口（类似 GROUP BY 但不合并行），`ORDER BY` 决定窗口内行的顺序，`ROWS BETWEEN ... AND ...` 限定窗口框架。排名类函数：`ROW_NUMBER()`（连续序号，不重复）、`RANK()`（相同值同排名，后续跳号）、`DENSE_RANK()`（相同值同排名，后续不跳号）、`NTILE(n)`（分 n 组）。前后行函数：`LAG(column, offset, default)` 取前 N 行，`LEAD()` 取后 N 行——常用于环比计算。聚合窗口函数：`SUM/AVG/COUNT OVER()` 在每行上显示分组汇总，不合并行。当 SELECT 中需要混用逐行字段和分组聚合值时，窗口函数 + `SELECT DISTINCT` 比 GROUP BY 更合适。窗口函数原则上只能写在 SELECT 子句中。

## 相关术语

- [[wiki/glossary/java-basic/CTE|CTE]] — 窗口函数常配合 CTE 使用，先在 CTE 中计算窗口值再在外部筛选
- [[wiki/glossary/java-basic/索引|索引]] — 窗口函数中的 `ORDER BY` 配合合适的索引可显著提升性能

## 深入阅读

- [[_posts/Java-basic/23-sql-advanced-syntax|Java基础(23) SQL 进阶语法：常用函数、CTE 与窗口函数]]
