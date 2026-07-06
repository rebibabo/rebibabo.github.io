---
title: Starter
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - spring-boot
type: glossary
source_series: Java-basic
status: seed
---

# Starter

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Starter 是 Spring Boot 的一站式依赖描述符，将某个功能模块所需的所有依赖（核心库 + 自动配置 + 第三方集成）打包为一个 Maven/Gradle 坐标，开发者引入即可使用，无需逐一罗列依赖。

## 上下文

每个 Starter 遵循命名规范：官方 Starter 为 `spring-boot-starter-xxx`（如 `spring-boot-starter-web`、`spring-boot-starter-data-redis`），第三方 Starter 为 `xxx-spring-boot-starter`。Starter 本身是一个空项目，只包含 pom.xml 声明传递依赖和自动配置类的引用，不包含代码。例如引入 `spring-boot-starter-web` 后自动获得：Spring MVC、内嵌 Tomcat、Jackson JSON 序列化、参数校验（Hibernate Validator）等一整套 Web 开发能力。常见坑点：引入了功能重复的 Starter 导致冲突、自定义 Starter 时自动配置类的注册路径错误导致不生效。

## 相关术语

- [[wiki/glossary/java-basic/SpringBoot|SpringBoot]] — Starter 是 Spring Boot "开箱即用"哲学的载体
- [[wiki/glossary/java-basic/自动配置|自动配置]] — 每个 Starter 内包含对应的自动配置类，引入即生效

## 深入阅读

- [[_posts/Java-basic/17-springboot|Java基础(17) | Spring Boot 快速上手：自动配置与 REST 服务实战]]
