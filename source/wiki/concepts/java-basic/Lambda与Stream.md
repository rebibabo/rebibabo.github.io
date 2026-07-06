---
title: Lambda 与 Stream
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Lambda 与 Stream

[[wiki/concepts/java-basic/Java-Basic-概念总图|返回概念总图]]

## 这一层回答什么问题

> 怎么让 Java 代码从"怎么做"变成"要什么"？Lambda、Stream、Optional 分别解决什么？

Java 8 引入了函数式编程的核心工具。它不只是一套新 API——它是一种不同的思维方式：声明式替代命令式，让代码关注"要什么"而不是"怎么做"。

## 这层的主要分支

- [[wiki/concepts/java-basic/Lambda与函数式接口|Lambda 与函数式接口]] — invokedynamic 底层、四个内置函数式接口、方法引用
- [[wiki/concepts/java-basic/Stream-API|Stream API]] — 三阶段流水线、中间操作 vs 终端操作、Collectors
- [[wiki/concepts/java-basic/Optional|Optional]] — 替代 null 的容器、map/flatMap 链式调用

## Lambda：为什么需要它

匿名内部类的啰嗦问题：

```java
// 匿名内部类（Java 7）
new Thread(new Runnable() {
    @Override
    public void run() { System.out.println("hi"); }
}).start();

// Lambda（Java 8）
new Thread(() -> System.out.println("hi")).start();
```

Lambda 不是匿名内部类的语法糖——它通过 `invokedynamic` 指令在运行时动态生成实现，性能优于匿名内部类。

## 函数式接口

只有一个抽象方法的接口。四个内置类型覆盖 90% 场景：

| 接口 | 方法 | 用途 |
|------|------|------|
| `Function<T, R>` | `R apply(T)` | 转换 |
| `Predicate<T>` | `boolean test(T)` | 判断 |
| `Consumer<T>` | `void accept(T)` | 消费 |
| `Supplier<T>` | `T get()` | 提供 |

## Stream：声明式数据处理

```java
// 命令式：一步步告诉 Java 怎么做
List<String> names = new ArrayList<>();
for (User u : users) {
    if (u.getAge() > 18) names.add(u.getName());
}

// Stream：告诉 Java 你要什么
List<String> names = users.stream()
    .filter(u -> u.getAge() > 18)
    .map(User::getName)
    .collect(Collectors.toList());
```

**关键理解：**
- **中间操作**（filter / map / sorted）是惰性的，不触发执行
- **终端操作**（collect / forEach / reduce）触发管道执行
- Stream 不存数据，它只是一条描述"对数据做什么"的流水线
- 一个 Stream 只能消费一次

## Optional：别用 null 了

null 的问题是它不告诉你"为什么没有值"。Optional 强制调用者面对这种可能性：

```java
// ❌ 层层判 null
if (user != null) {
    Address a = user.getAddress();
    if (a != null) return a.getCity();
}

// ✅ Optional 链式
return Optional.ofNullable(user)
    .map(User::getAddress)
    .map(Address::getCity)
    .orElse("未知");
```

## 在系列里的位置

post 08。在 OOP 和异常之后——Lambda 里写异常处理、Stream 里操作集合，都需要前面的基础。

## 推荐回看原文

- [[_posts/Java-basic/08-lambda-and-stream|08-Lambda 与 Stream API]]

## 相关概念

- [[wiki/concepts/java-basic/面向对象|面向对象]] — 函数式接口说到底还是接口
- [[wiki/concepts/java-basic/泛型|泛型]] — Function<T,R>、Stream<T> 到处都是泛型
- [[wiki/concepts/java-basic/集合框架|集合框架]] — Stream 的数据源通常是集合
