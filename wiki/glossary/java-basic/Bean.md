---
title: Bean
tags:
  - wiki
  - glossary
  - java
  - java-basic
  - spring
type: glossary
source_series: Java-basic
status: seed
---

# Bean

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Bean 是 Spring IoC 容器管理的对象实例，由容器负责其创建、装配、初始化和销毁的全生命周期。

## 上下文

Bean 的定义方式经历三个阶段：XML 配置（`<bean>` 标签）、注解驱动（`@Component`、`@Service`、`@Repository`、`@Controller`）、Java Config（`@Bean` 方法配合 `@Configuration`）。Spring Boot 后以注解和 Java Config 为主流。默认作用域是 singleton（容器内全局唯一），也支持 prototype（每次获取新建）、request/session（Web 环境）。Bean 生命周期：构造实例 -> 属性填充 -> Aware 回调 -> BeanPostProcessor 前置处理 -> @PostConstruct -> InitializingBean -> BeanPostProcessor 后置处理 -> 就绪 -> @PreDestroy -> DisposableBean -> 销毁。常见坑点：singleton Bean 持有 prototype Bean 导致作用域失效（需 `@Scope` + proxyMode）、@PostConstruct 方法私有不执行。

## 相关术语

- [[wiki/glossary/java-basic/IoC|IoC]] — 控制反转设计原则，Bean 是 IoC 容器管理的核心单元
- [[wiki/glossary/java-basic/DI|DI]] — 依赖注入，Bean 之间依赖关系的装配方式
- [[wiki/glossary/java-basic/SpringBoot|SpringBoot]] — Spring Boot 框架，通过自动配置简化 Bean 的定义和装配

## 深入阅读

- [[_posts/Java-basic/16-spring-ioc-aop|Java基础(16) | Spring 核心思想：IoC 与 AOP 到底解决了什么问题]]
