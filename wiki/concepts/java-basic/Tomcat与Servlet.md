---
title: Tomcat 与 Servlet
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Tomcat 与 Servlet

[[wiki/concepts/java-basic/工程实践|返回工程实践]]

## 这一层回答什么问题

> 一个 HTTP 请求从浏览器到达 Controller 方法，中间经历了什么？Filter 和 Interceptor 有什么区别？Spring Boot 怎么做到不用部署 war 就能跑？

理解了这条请求链路，就理解了 Spring MVC 的运转机制——不是"照着写注解"而是"知道每一层在什么时机做了什么"。

## 一次请求的完整旅程

```
浏览器 → Connector（Tomcat 接收连接）
       → Filter 链（请求过滤：编码、CORS、XSS）
       → DispatcherServlet（Spring MVC 统一入口）
       → HandlerMapping（URL → Controller 方法）
       → Interceptor 链 preHandle（鉴权、日志）
       → Controller 方法
       → Interceptor 链 postHandle
       → 视图渲染
       → Interceptor 链 afterCompletion
       → Filter 链（反向返回）
       → Connector → 浏览器
```

## Filter vs Interceptor

| | Filter | Interceptor |
|------|--------|-------------|
| 属于 | Servlet 规范（Tomcat 层） | Spring MVC |
| 能访问 | Request / Response | 还能拿到 Controller 方法、参数 |
| 使用场景 | 编码、CORS、XSS 过滤 | 鉴权、日志、性能统计 |
| 实现 | `implements Filter` | `implements HandlerInterceptor` |

**经验法则**：Web 容器层的事用 Filter（字符编码、跨域）；业务层的事用 Interceptor（鉴权、权限）。

## 内嵌 Tomcat

Spring Boot 把 Tomcat 打包进 jar 里——`java -jar` 启动时，Spring Boot 自动启动内嵌 Tomcat、注册 DispatcherServlet、绑定端口。不需要安装 Tomcat、不需要部署 war。

## Servlet 本质

Servlet 是一个单实例、多线程的 Java 类。Tomcat 为每个请求分配一个线程，调用 Servlet 的 `service()` 方法。所以 Servlet 必须是无状态的——不要在 Servlet 里存请求相关的成员变量。

## 在系列里的位置

post 29。

## 推荐回看原文

- [[_posts/Java-basic/29-tomcat-servlet|29-Tomcat 与 Servlet]]

## 相关概念

- [[wiki/concepts/java-basic/Spring-Boot|Spring Boot]]
- [[wiki/concepts/java-basic/AOP|AOP]] — Interceptor 和 AOP 都是横切逻辑的机制
