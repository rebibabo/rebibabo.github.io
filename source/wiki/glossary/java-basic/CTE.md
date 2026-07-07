---
title: CTE
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# CTE

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

CTE（Common Table Expression，公共表表达式）用 `WITH ... AS (...)` 将复杂查询拆分为多个命名的临时结果集，后续查询可以像引用普通表一样引用它们，提高可读性和可调试性。

## 上下文

CTE 的核心价值是将一层套一层的嵌套子查询拆成可单独调试的步骤——每个 CTE 都可以单独拿出来跑，看中间结果对不对，逐步排查。多个 CTE 用逗号分隔，后面的 CTE 可以引用前面的。单行 CTE 通过逗号 join 到其他表上可以实现"把一个计算值广播到每一行"的效果（如先算出最大日期，再让所有行使用这个日期作为筛选基准）。CTE 与子查询的区别：CTE 可读性更好、可复用（同一 CTE 在后续被多次引用），但 MySQL 中 CTE 是临时的，不会物化存储。CTE 适合替代复杂的嵌套子查询，尤其是数据分析、报表统计等"逐步筛选、逐步汇总"的场景。

## 相关术语

- [[wiki/glossary/java-basic/SQL窗口函数|SQL窗口函数]] — CTE 常与窗口函数配合使用，先 CTE 拆解、再窗口函数计算、最后筛选汇总

## 深入阅读

- [[_posts/Java-basic/23-sql-advanced-syntax|java-basics(23) SQL 进阶语法：常用函数、CTE 与窗口函数]]
