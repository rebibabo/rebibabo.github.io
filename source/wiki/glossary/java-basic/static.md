---
title: static
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - static
type: glossary
source_series: Java-basic
status: seed
---

# static

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

`static` 修饰的成员属于类本身，而非某个具体实例。所有对象共享同一份 static 变量，static 方法通过类名直接调用，不需要创建对象。static 代码块在类第一次被加载时执行一次。

## 上下文

static 方法的核心限制是没有 `this`，不能访问实例变量，因为调用时可能根本没有对象存在。static 变量常用于全局计数器、配置信息、单例实例等场景。`static final` 组合定义类级别常量，约定全大写下划线命名（如 `MAX_RETRY_COUNT`）。

static 方法不会被重写——子类定义同签名 static 方法叫"隐藏（Hiding）"，调用时看引用声明类型而非实际对象类型。判断一个方法是否该用 static 的原则：是否需要访问实例状态？需要则实例方法，不需要（纯工具计算、工厂方法）则 static。

## 相关术语

- [[wiki/glossary/java-basic/final|final]] — static final 组合定义类级别常量，编译时内联到调用处，修改后需重新编译所有依赖类
- [[wiki/glossary/java-basic/构造方法|构造方法]] — 构造方法是实例级别初始化，static 代码块是类级别初始化，类加载时先于任何实例化

## 深入阅读

- [[_posts/Java-basic/04-basic-class|Java基础(4) | 类与对象：构造方法、访问控制、static 与 final]]
