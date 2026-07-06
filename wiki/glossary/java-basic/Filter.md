---
title: Filter
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Filter

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Servlet Filter 是 Servlet 规范定义的组件，在请求到达 Servlet 之前和响应返回客户端之前执行过滤逻辑，多个 Filter 组成链式调用。

## 上下文

Filter 的核心方法是 `doFilter(request, response, chain)`：调用 `chain.doFilter()` 之前的代码在"请求进入时"执行，之后的代码在"响应返回时"执行，因此 Filter 能"包裹"整个请求处理过程。Filter 属于 Servlet 层，作用范围是所有进入 Tomcat 的请求（不限于 Spring MVC），只能拿到 `HttpServletRequest`/`HttpServletResponse`，无法感知具体是哪个 Controller 方法。典型用途包括字符编码设置、CORS 跨域、请求日志、Gzip 压缩。与 Interceptor 的区别：Filter 是 Servlet 层的"门卫"，范围更广；Interceptor 是 Spring MVC 层的"安检"，能拿到 HandlerMethod 信息（哪个类哪个方法），鉴权场景更常用 Interceptor。

## 相关术语

- [[wiki/glossary/java-basic/Servlet|Servlet]] — Filter 包裹的核心请求处理组件
- [[wiki/glossary/java-basic/Tomcat|Tomcat]] — 管理 Filter 链生命周期的 Servlet 容器
- [[wiki/glossary/java-basic/AOP|AOP]] — Spring AOP 是 Filter 思想的延伸，在方法级别实现横切关注点

## 深入阅读

- [[_posts/Java-basic/29-tomcat-servlet|Java基础(番外) Tomcat 与 Servlet：Spring Boot 背后的请求处理流程]]
