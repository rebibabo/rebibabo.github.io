---
title: IoC 与 DI
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# IoC 与 DI

[[wiki/concepts/java-basic/Spring|返回 Spring]]

## 这一层回答什么问题

> 什么叫"控制反转"？依赖注入的三种方式各有什么优劣？Spring 容器本质上是什么？

IoC 和 DI 是 Spring 的根基。不理解它们，`@Autowired`、`ApplicationContext`、`@Bean` 这些概念永远是"照着写"而不是"理解了再写"。

## 没有 IoC 的世界

```java
public class UserService {
    private EmailService emailService = new EmailService();  // 自己 new
    // UserService 创建、管理 EmailService 的生命周期
}
```

问题：写死了实现类、测试时无法 mock、配置散落在代码各处。

## IoC：控制反转

控制反转不是"把依赖倒过来"——是**对象创建的控制权从代码转移给容器**。

```java
@Service
public class UserService {
    private final EmailService emailService;
    public UserService(EmailService emailService) {  // 容器注入
        this.emailService = emailService;
    }
}
```

你不 new 对象了——你声明需要什么，容器给你。

## DI：三种注入方式

| 方式 | 代码 | 优劣 |
|------|------|------|
| **构造器注入** | `public UserService(EmailService es)` | ✅ 不可变、必依赖清晰、测试不用 Spring |
| Setter 注入 | `setEmailService(EmailService es)` | 🔸 可选依赖、但可能漏注入 |
| 字段注入 | `@Autowired private EmailService es` | ❌ 测试必须启动 Spring、依赖隐藏 |

**构造器注入是推荐做法**。Spring 4.3+ 甚至不需要 `@Autowired`——只有一个构造方法时自动注入。用 Lombok 的 `@RequiredArgsConstructor` 可以省去构造方法的样板代码。

## Spring 容器本质

`ApplicationContext` 本质上是一个**巨大的 Map + 反射工厂**：

```
启动时：
1. 扫描 @Component → Class.forName → 反射创建实例 → 放进 Map
2. 扫描 @Autowired → 从 Map 取出依赖 → field.set(target, bean)
3. 调用 @PostConstruct 初始化方法
```

## Bean 的 scope

- **singleton**（默认）：全容器一个实例
- **prototype**：每次获取新实例
- request / session：Web 环境专用

## 在系列里的位置

post 16 的核心。

## 推荐回看原文

- [[_posts/Java-basic/16-spring-ioc-aop|16-Spring 核心思想]]

## 相关概念

- [[wiki/concepts/java-basic/AOP|AOP]]
- [[wiki/concepts/java-basic/Spring-Boot|Spring Boot]]
- [[wiki/concepts/java-basic/反射|反射]] — IoC 的底层是反射
