---
title: Spring Boot
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Spring Boot

[[wiki/concepts/java-basic/Spring|返回 Spring]]

## 这一层回答什么问题

> Spring Boot 和 Spring 有什么区别？自动配置是怎么"自动"的？一个 Starter 到底是什么？

Spring Boot 不是 Spring 的替代——它是 Spring 的"快速启动器"。用 Spring 需要手动配数据源、事务管理器、视图解析器。Spring Boot 把这些都自动化了。

## 自动配置：怎么做到的

`@SpringBootApplication` = `@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan`。

核心在 `@EnableAutoConfiguration`——它触发 `spring-boot-autoconfigure` jar 里的大量配置类。每个配置类上都挂着条件注解：

```java
@Configuration
@ConditionalOnClass(DataSource.class)  // classpath 有 DataSource → 自动配数据源
@ConditionalOnMissingBean(DataSource.class)  // 你没手动配 → Spring Boot 帮你配
public class DataSourceAutoConfiguration { ... }
```

启动流程：Spring Boot 检查 classpath → 满足条件的配置自动生效 → 你应该手动配的（手动配了 Bean）就不覆盖。

## Starter：一站式依赖

`spring-boot-starter-web` 引入后，你得到的不只是一个依赖——是一整套：
- Tomcat（内嵌）
- Spring MVC
- Jackson（JSON 序列化）
- 自动配置（DispatcherServlet、视图解析器、静态资源映射...）

不需要写 XML、不需要部署 war 到 Tomcat。`java -jar` 直接跑。

## 约定优于配置

- 没写 `server.port` → 默认 8080
- 没写数据源 → 尝试连接本地 MySQL（如果 classpath 有 driver）
- 没写模板引擎 → 默认 Thymeleaf 去 `templates/` 找
- `application.yml` 不存在 → 用默认值

约定让你少写配置。当约定不符合你的需求时，一个配置覆盖即可。

## application.yml 多环境

```yaml
# application.yml（公共）
spring:
  application.name: myapp

# application-dev.yml
server.port: 8080

# application-prod.yml
server.port: 80
```

`spring.profiles.active=prod` 激活对应配置。profile 文件会**覆盖**主文件的同名字段。

## 在系列里的位置

post 17。

## 推荐回看原文

- [[_posts/Java-basic/17-springboot|17-Spring Boot 快速上手]]

## 相关概念

- [[wiki/concepts/java-basic/IoC与DI|IoC 与 DI]]
- [[wiki/concepts/java-basic/AOP|AOP]]
- [[wiki/concepts/java-basic/构建工具|构建工具]] — Starter 本质是 Maven/Gradle 依赖描述符
