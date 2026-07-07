---
title: SpringBoot
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

# SpringBoot

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Spring Boot 是简化 Spring 应用开发的框架，通过自动配置、Starter 依赖和嵌入式服务器三大核心能力，让开发者快速创建独立运行的生产级 Spring 应用。

## 上下文

Spring Boot 的核心哲学是"约定优于配置"——只要引入了对应的 Starter，框架会根据类路径上的 jar 自动配置 Bean，无需手动写 XML 或 Java Config。内嵌 Tomcat / Jetty / Undertow 使得应用可以以 `java -jar` 方式独立运行，不再需要部署到外部 Servlet 容器。`@SpringBootApplication` 是组合注解（`@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan`），一键启用三大能力。配置文件 `application.yml` / `application.properties` 集中管理参数，配合 Profile（`application-{profile}.yml`）区分环境。Actuator 模块提供生产级监控端点（health、metrics、env 等）。常见坑点：包扫描规则（默认扫描启动类同级及子包）、第三方 jar 无法自动配置时需要手动 `@Import`、配置文件优先级容易混淆。

## 相关术语

- [[wiki/glossary/java-basic/自动配置|自动配置]] — Spring Boot 核心机制，根据类路径 jar 自动推断并配置 Bean
- [[wiki/glossary/java-basic/Starter|Starter]] — 一站式依赖描述符，引入即获得某功能模块的完整依赖
- [[wiki/glossary/java-basic/Bean|Bean]] — Spring IoC 容器管理的对象，Spring Boot 通过自动配置简化 Bean 定义
- [[wiki/glossary/java-basic/IoC|IoC]] — 控制反转，Spring Boot 底层依赖 Spring IoC 容器

## 深入阅读

- [[_posts/Java-basic/17-springboot|java-basics(17) | Spring Boot 快速上手：自动配置与 REST 服务实战]]
