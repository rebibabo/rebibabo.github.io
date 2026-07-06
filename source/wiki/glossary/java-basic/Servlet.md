---
title: Servlet
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Servlet

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Servlet 是 Java EE（Jakarta EE）规范定义的 Web 组件，用于处理 HTTP 请求并返回 HTTP 响应，其生命周期由 Servlet 容器（如 Tomcat）管理。

## 上下文

Servlet 生命周期分三个阶段：`init()` 在第一次请求或容器启动时调用，只执行一次；`service()`（最终路由到 `doGet()`/`doPost()` 等）每次 HTTP 请求都调用；`destroy()` 在容器关闭时调用，只执行一次。Servlet 容器对同一个 Servlet 只创建一个实例，所有请求共享——因此不要在 Servlet 里存"请求相关"的实例变量，会有线程安全问题。实际开发中几乎不会自己写 Servlet，Spring MVC 的 `DispatcherServlet` 是所有请求的统一入口，会将请求路由到对应的 `@Controller` 方法。但理解这层概念有助于理解 Filter、Interceptor 以及整个请求处理链路。

## 相关术语

- [[wiki/glossary/java-basic/Tomcat|Tomcat]] — 管理 Servlet 生命周期的 Servlet 容器
- [[wiki/glossary/java-basic/Filter|Filter]] — Servlet 层请求过滤链，包裹 Servlet 处理过程

## 深入阅读

- [[_posts/Java-basic/29-tomcat-servlet|Java基础(番外) Tomcat 与 Servlet：Spring Boot 背后的请求处理流程]]
