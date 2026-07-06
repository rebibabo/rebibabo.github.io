---
title: Lambda
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Lambda

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Lambda 表达式是 Java 8 引入的匿名函数语法，本质是一段可以传递的代码块，用于替代冗长的匿名内部类。其底层并非通过生成匿名类实现，而是使用 `invokedynamic` 字节码指令动态绑定，性能优于匿名内部类。

## 上下文

Lambda 只能赋值给函数式接口（只有一个抽象方法的接口），编译器通过目标类型推断参数类型。语法支持参数类型省略、单行表达式省略大括号和 return、单参数省略括号等简化写法。Lambda 的核心价值在于将"行为"作为参数传递，配合 Stream API 实现声明式数据处理。常见误区是将 Lambda 等同于匿名内部类的语法糖，实际上两者在字节码层面完全不同。

## 相关术语
- [[wiki/glossary/java-basic/函数式接口|函数式接口]] — Lambda 只能赋值给函数式接口类型的变量
- [[wiki/glossary/java-basic/方法引用|方法引用]] — Lambda 表达式的简写形式，直接引用已有方法
- [[wiki/glossary/java-basic/Stream-API|Stream API]] — Lambda 的主要应用场景，实现声明式数据处理

## 深入阅读

- [[_posts/Java-basic/08-lambda-and-stream|Java基础(8) | Lambda 与 Stream API：函数式编程核心工具]]
