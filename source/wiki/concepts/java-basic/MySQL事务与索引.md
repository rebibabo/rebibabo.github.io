---
title: MySQL 事务与索引
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# MySQL 事务与索引

[[wiki/concepts/java-basic/数据访问|返回数据访问]]

## 这一层回答什么问题

> 事务隔离级别到底在防什么？B+ 树为什么是 MySQL 的默认索引结构？最左前缀匹配是什么？

事务和索引是 MySQL 的两条腿。事务保证数据正确，索引保证查询速度。不理解它们，CRUD 写得出但一有性能问题就无从下手。

## 事务（ACID）

| 特性 | 说明 |
|------|------|
| 原子性 | 一荣俱荣，一损俱损 |
| 一致性 | 事务前后数据满足所有约束 |
| 隔离性 | 并发事务互不干扰 |
| 持久性 | 提交了就永久保存 |

## 隔离级别与它防什么

三个并发问题：**脏读**（读到别人未提交的）、**不可重复读**（同一行两次读不一样）、**幻读**（两次查多出/少了行）。

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|----------|------|-----------|------|
| READ UNCOMMITTED | ✓ | ✓ | ✓ |
| READ COMMITTED | ✗ | ✓ | ✓ |
| **REPEATABLE READ**（MySQL 默认） | ✗ | ✗ | ✓（MVCC 部分解决） |
| SERIALIZABLE | ✗ | ✗ | ✗ |

MySQL 用 **MVCC**（多版本并发控制）实现高并发事务隔离：读操作基于快照，不阻塞写；写操作加行锁。`SELECT` 不加锁，`SELECT ... FOR UPDATE` 加排他锁。

## B+ 树索引

**为什么是 B+ 树不是二叉树？** 二叉树深度太大（100 万行数据深度约 20 层），每层一次磁盘 I/O。B+ 树每个节点存多个 key，100 万行只需 3 层——3 次磁盘 I/O 完成查找。

**聚簇索引 vs 二级索引**：聚簇索引的叶子节点存完整行数据（InnoDB 的主键索引）；二级索引的叶子节点只存主键值，查到后要**回表**（用主键去聚簇索引找完整行）。

**覆盖索引**：查询列全在索引中 → 不需要回表。`EXPLAIN` 里 `Extra: Using index` 就是覆盖索引。

## 最左前缀匹配

联合索引 `(a, b, c)` 像字典先按 a 排序、a 相同再按 b、b 相同再按 c。所以：
- `WHERE a=1 AND b=2` ✅ 走索引
- `WHERE b=2` ❌ 不走（没从最左开始）
- `WHERE a=1 AND c=3` → a 走索引，c 不走（跳过了 b）

## 索引失效常见场景

- 对索引列用函数：`WHERE DATE(create_time) = ...`
- LIKE 前导通配符：`WHERE name LIKE '%abc'`
- 隐式类型转换：phone 是 varchar，`WHERE phone = 13800000000`（数字会转字符串）
- OR 连接非索引列：每个 OR 分支都要有独立索引

## 在系列里的位置

post 24。

## 推荐回看原文

- [[_posts/Java-basic/24-mysql-internals|24-MySQL 原理与优化]]

## 相关概念

- [[wiki/concepts/java-basic/MyBatis|MyBatis]]
- [[wiki/concepts/java-basic/Redis缓存|Redis 缓存]]
