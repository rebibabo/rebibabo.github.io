---
title: final
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - final
type: glossary
source_series: Java-basic
status: seed
---

# final

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

`final` 表示"不可变"，可以修饰三种目标：修饰变量则变量不可重新赋值（对于引用类型只锁引用本身，对象内部状态仍可修改）；修饰方法则子类不能重写；修饰类则不能被继承。Java 标准库中 String、Integer 等包装类都是 final 的。

## 上下文

final 变量有三类：final 类变量（`static final`，类级别常量，全大写下划线命名）、final 实例变量（必须在构造方法结束前赋值，常用于 id、accountId 等不变字段）、final 局部变量（方法内不可变的临时数据）。

final 方法的目的是保护核心行为不被子类篡改。final 类的经典例子是 String——防止子类通过重写方法破坏不可变性和安全性。`static final` 的常量在编译时会被内联到调用处，因此修改常量后需要重新编译所有依赖它的类。

## 相关术语

- [[wiki/glossary/java-basic/static|static]] — static final 定义类级别常量，static 方法不会被重写（隐藏）而非 final
- [[wiki/glossary/java-basic/继承|继承]] — final 类不能被继承，final 方法不能被子类重写，阻断继承链

## 深入阅读

- [[_posts/Java-basic/04-basic-class|java-basics(4) | 类与对象：构造方法、访问控制、static 与 final]]
