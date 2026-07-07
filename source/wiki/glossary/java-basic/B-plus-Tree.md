---
title: B+Tree
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# B+Tree

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

B+Tree 是 InnoDB 存储引擎的默认索引结构，非叶子节点只存索引键值和指针（不存数据），所有数据存储在叶子节点，叶子节点之间通过双向链表连接，支持高效的范围查询和顺序遍历。

## 上下文

B+Tree 相比 B-Tree 的优势：B-Tree 的非叶子节点也存数据，导致一页能存的键值变少、指针变少，树更高；B+Tree 非叶子节点只存索引和指针，能容纳更多指针，树更"矮胖"——同样数据量下树的高度更低，磁盘 I/O 次数更少。叶子节点之间的双向链表使得范围查询（BETWEEN、>、<、ORDER BY）非常高效——定位到起始位置后沿着链表顺序扫描即可，不需要回溯。相比二叉树（每个节点只有两个子节点），B+Tree 每个节点可以有多个子节点，层级更少。相比 Hash 索引，B+Tree 数据有序存储，天然支持范围查询和排序，而 Hash 只能做等值查询。InnoDB 的聚集索引（主键索引）的叶子节点存完整行数据，二级索引的叶子节点存主键值。

## 相关术语

- [[wiki/glossary/java-basic/索引|索引]] — B+Tree 是 InnoDB 索引的底层实现，理解 B+Tree 是理解索引工作原理的基础
- [[wiki/glossary/java-basic/红黑树|红黑树]] — 与 B+Tree 同为平衡树，但红黑树常用于内存结构，B+Tree 针对磁盘 I/O 优化

## 深入阅读

- [[_posts/Java-basic/24-mysql-internals|java-basics(24) MySQL 原理与优化：事务、存储引擎、索引与锁]]
