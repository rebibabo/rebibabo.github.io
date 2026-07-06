---
title: PECS
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# PECS

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

PECS（Producer Extends, Consumer Super）是 Effective Java 中总结的通配符使用原则：从集合读取数据（生产者）用 `<? extends T>`，向集合写入数据（消费者）用 `<? super T>`。

## 上下文

PECS 的本质是类型安全：`<? extends T>` 上界通配符表示容器里的是"某种 T 的子类"——编译器只知道取出来的一定是 T，但不知道具体是哪种子类，所以只能读不能写；`<? super T>` 下界通配符表示容器能接受"T 及其父类"——编译器知道写入 T 一定是安全的，但取出来的类型不确定只能用 Object 接收，所以只能写不能安全读。典型应用如 `Collections.copy(List<? super T> dest, List<? extends T> src)`，src 是生产者（读取）用 extends，dest 是消费者（写入）用 super。记住 PECS 口诀可以少踩泛型通配符的坑。

## 相关术语

- [[wiki/glossary/java-basic/通配符|通配符]] — `? extends T` 和 `? super T` 是 PECS 原则的语法基础
- [[wiki/glossary/java-basic/泛型|泛型]] — PECS 是泛型编程中通配符使用的核心指导原则
- [[wiki/glossary/java-basic/类型擦除|类型擦除]] — 类型擦除导致运行时无法区分泛型类型，PECS 在编译期保证安全

## 深入阅读

- [[_posts/Java-basic/06-genrics|Java基础(6) 泛型：类型擦除、通配符与 PECS 原则]]
