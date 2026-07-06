---
title: hashCode
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - hashcode
type: glossary
source_series: Java-basic
status: seed
---

# hashCode

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

`hashCode()` 是 `Object` 中定义的方法，返回对象的哈希码（int 值）。它与 `equals()` 存在契约关系：两个 `equals()` 返回 true 的对象，`hashCode()` 必须返回相同的值；但 `hashCode()` 相同的两个对象，`equals()` 不一定返回 true（哈希冲突）。

## 上下文

`HashMap`、`HashSet` 等基于哈希的集合先用 `hashCode()` 快速定位桶，再用 `equals()` 精确判断是否相同。如果只重写 `equals()` 而不重写 `hashCode()`，两个"按内容相等"的对象可能被分配到不同的桶，导致集合行为错乱——比如 `set.contains(obj)` 返回 false，或者同一个 key 被重复存储。

实际开发中通常用 `Objects.hash(field1, field2, ...)` 生成哈希码，或在 IDE 中自动生成。重写 `equals()` 必须同步重写 `hashCode()`，这是一条铁律。

## 相关术语

- [[wiki/glossary/java-basic/equals-和-==|equals 和 ==]] — hashCode 相等的两个对象 equals() 不一定相等（哈希冲突），但 equals() 相等的对象 hashCode() 必等
- [[wiki/glossary/java-basic/HashMap|HashMap]] — 先用 hashCode() 定位桶，再用 equals() 精确匹配，两者协同工作支撑哈希表结构

## 深入阅读

- [[_posts/Java-basic/05-advanced-class|Java基础(5) | 继承与多态：extends、重写、抽象类与接口]]
