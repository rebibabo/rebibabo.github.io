---
title: Lambda 与函数式接口
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Lambda 与函数式接口

[[wiki/concepts/java-basic/Lambda与Stream|返回 Lambda 与 Stream]]

## 这一层回答什么问题

> Lambda 是什么？函数式接口怎么定义的？四个内置函数式接口能覆盖多少场景？

Lambda 让 Java 从"怎么做"变成"要什么"——它不只是一套更短的语法，它是 Java 函数式编程的入口。

## Lambda 语法

```java
(int a, int b) -> a + b           // 完整
(a, b) -> a + b                   // 省略类型
s -> s.length()                   // 单参数省略括号
() -> System.out.println()        // 无参数
(String s) -> { return s.length(); }  // 有花括号要写 return
```

**本质**：Lambda 不是匿名内部类的语法糖。它通过 `invokedynamic` 指令在运行时动态生成实现——不是编译期生成一个匿名类文件。性能优于匿名内部类。

## 函数式接口

只有一个抽象方法的接口，标注 `@FunctionalInterface`。这个注解不强制，但加了之后编译器会帮你检查是否真的只有一个抽象方法。

## 四个内置函数式接口（覆盖 90% 场景）

| 接口 | 方法签名 | 你用它做 |
|------|----------|----------|
| `Function<T, R>` | `R apply(T t)` | 转换：`s -> s.length()` |
| `Predicate<T>` | `boolean test(T t)` | 判断：`s -> s.isEmpty()` |
| `Consumer<T>` | `void accept(T t)` | 消费：`s -> System.out.println(s)` |
| `Supplier<T>` | `T get()` | 提供：`() -> new User()` |

还有变体：`BiFunction<T, U, R>` 两个参数、`UnaryOperator<T>` 同类型转换、`IntFunction<R>` / `ToIntFunction<T>` 等基本类型特化（避免装箱开销）。

## 方法引用：Lambda 的简化写法

| 形式 | 写法 | 等价的 Lambda |
|------|------|---------------|
| 静态方法 | `Integer::parseInt` | `s -> Integer.parseInt(s)` |
| 实例方法（对象） | `System.out::println` | `s -> System.out.println(s)` |
| 实例方法（类） | `String::length` | `s -> s.length()` |
| 构造方法 | `User::new` | `() -> new User()` |

## 在系列里的位置

post 08。

## 推荐回看原文

- [[_posts/Java-basic/08-lambda-and-stream|08-Lambda 与 Stream API]]

## 相关概念

- [[wiki/concepts/java-basic/Stream-API|Stream API]]
- [[wiki/concepts/java-basic/Optional|Optional]]
- [[wiki/concepts/java-basic/接口与抽象|接口与抽象]] — 函数式接口的基础是接口
