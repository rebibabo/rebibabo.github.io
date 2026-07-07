---
title: Tomcat
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Tomcat

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Tomcat 是开源的 Servlet 容器，实现了 Java EE（Jakarta EE）Servlet 规范，负责接收 HTTP 请求并将其分发给对应的 Servlet 处理，Spring Boot 内嵌的默认 Web 服务器就是 Tomcat。

## 上下文

Tomcat 内部是一层套一层的容器结构：Server -> Service -> Connector + Engine -> Host -> Context -> Wrapper。作为后端开发者主要关心两层：Connector 负责监听端口（如 8080），接收 TCP 连接并解析 HTTP 协议；Context 对应一个 Web 应用，里面注册了 DispatcherServlet 和各种 Filter。Spring Boot 将 Tomcat 核心代码作为依赖打入 jar 包，`java -jar` 一条命令即可启动，无需传统 WAR 包部署方式。了解内嵌 Tomcat 与独立部署的区别，以及 `server.port`、`server.tomcat.threads.max` 等配置项的含义，对新人来说已经足够。

## 相关术语

- [[wiki/glossary/java-basic/Servlet|Servlet]] — Tomcat 管理的 Web 组件，处理 HTTP 请求的核心接口
- [[wiki/glossary/java-basic/Filter|Filter]] — Servlet 规范定义的过滤链组件，在请求到达前/响应返回前执行
- [[wiki/glossary/java-basic/SpringBoot|SpringBoot]] — 内嵌 Tomcat 的开箱即用框架

## 深入阅读

- [[_posts/Java-basic/29-tomcat-servlet|java-basics(番外) Tomcat 与 Servlet：Spring Boot 背后的请求处理流程]]
