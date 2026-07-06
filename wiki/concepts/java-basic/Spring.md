---
title: Spring
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Spring

[[wiki/concepts/java-basic/Java-Basic-概念总图|返回概念总图]]

## 这一层回答什么问题

> Spring 到底解决了什么？IoC 容器是什么？AOP 切面怎么工作的？Spring Boot 又简化了什么？

Spring 是 Java 后端的事实标准骨架。它不是"又一套新 API"——它重新定义了 Java 项目怎么组织、对象怎么管理、横切逻辑怎么分离。

## 这层的主要分支

- [[wiki/concepts/java-basic/IoC与DI|IoC 与 DI]] — 控制反转、三种注入方式、Spring 容器本质
- [[wiki/concepts/java-basic/AOP|AOP]] — 五种通知、切点表达式、JDK vs CGLIB 代理
- [[wiki/concepts/java-basic/Spring-Boot|Spring Boot]] — 自动配置原理、Starter、内嵌 Tomcat

## IoC：控制反转

**没有 Spring 的世界**：每个类自己 `new` 依赖对象。`UserService` 里写死了 `new EmailService()`——换实现要改代码，测试时无法 mock。

**有了 IoC 之后**：对象创建的控制权从"类自己 new"转移给 Spring 容器。你只需要声明需要什么，容器负责注入：

```java
@Service
public class UserService {
    private final EmailService emailService;
    
    public UserService(EmailService emailService) {  // 构造器注入
        this.emailService = emailService;
    }
}
```

**Spring 容器的本质**：一个巨大的 Map + 反射工厂。启动时扫描 `@Component`、反射创建实例、放 Map 里；看到 `@Autowired`、从 Map 取出依赖、反射注入。

**三种注入方式**：构造器注入（推荐，不可变，测试友好）> Setter 注入 > 字段注入（`@Autowired` 直接加字段上，不推荐——测试时必须启动 Spring 容器）。

## AOP：面向切面编程

业务代码里散落着日志、事务、权限——这些不是业务逻辑，但又无处不在。AOP 把它们抽成"切面"，织入到指定"切点"。

```
@Around("@annotation(LogExecution)")
public Object log(ProceedingJoinPoint pjp) {
    // 前置
    Object result = pjp.proceed();  // 执行业务方法
    // 后置
    return result;
}
```

| 概念 | 你写的 |
|------|--------|
| 切面（Aspect） | 日志类 |
| 切点（Pointcut） | `@annotation(LogExecution)` —— 在哪生效 |
| 通知（Advice） | `@Around` —— 什么时候、做什么 |

**底层实现**：目标类有接口 → JDK 动态代理；没有接口 → CGLIB 生成子类代理。这也是 `@Transactional` 内部调用 this 失效的根本原因——this 是原始对象，不是代理。

## Spring Boot：让 Spring 变快

Spring Boot 的核心是**自动配置**——根据 classpath 里有什么 jar，自动创建对应的 Bean。

`@SpringBootApplication` = `@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan`。

**Starter** 是一站式依赖描述符——`spring-boot-starter-web` 引入后，Tomcat、Spring MVC、Jackson 一次性到位。

**约定优于配置**：没写 `application.yml` 也能启动，Spring Boot 有合理的默认值。内嵌 Tomcat 让你 `java -jar` 直接跑，不需要部署 war 到 Servlet 容器。

## 在系列里的位置

post 16（Spring IoC/AOP）和 post 17（Spring Boot）。在注解与反射之后——IoC 和 AOP 的底层就是注解扫描 + 反射注入 + 动态代理。

## 推荐回看原文

- [[_posts/Java-basic/16-spring-ioc-aop|16-Spring 核心思想]]
- [[_posts/Java-basic/17-springboot|17-Spring Boot 快速上手]]

## 相关概念

- [[wiki/concepts/java-basic/注解与反射|注解与反射]] — Spring 的底层积木
- [[wiki/concepts/java-basic/数据访问|数据访问]] — Spring 管理 MyBatis、Redis 的集成
- [[wiki/concepts/java-basic/工程实践|工程实践]] — Spring 项目最终要测试、部署、上线
