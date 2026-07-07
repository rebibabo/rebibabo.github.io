---
title: Java 进阶系列
tags:
  - wiki
  - series
  - java
  - java-advanced
type: series
source_series: Java-advanced
status: seed
---

# Java 进阶系列

[[wiki/index|返回 Wiki 首页]]

## 系列定位

这组文章建立在 `Java-basic` 之上，开始从“写一个应用”走向“跑一个系统”。

核心主题是架构升级、部署环境、安全与可观测性。

## 这个系列回答什么问题

- 为什么单体系统会走向微服务
- 容器和 Kubernetes 在交付链路里各自解决什么问题
- JWT 认证授权的基本模型是什么
- 监控指标、Grafana 大盘、链路追踪三者如何组成一套可观测性体系

## 推荐阅读顺序

1. [[_posts/Java-advanced/01-microservices-intro|java-advanced(1) | 微服务入门：从单体到 Spring Cloud 全家桶]]
2. [[_posts/Java-advanced/02-docker|java-advanced(2) | Docker 容器入门：从原理到打包部署]]
3. [[_posts/Java-advanced/03-k8s|java-advanced(3) | Kubernetes 入门：为什么需要它，核心概念与实战]]
4. [[_posts/Java-advanced/04-jwt|java-advanced(4) | Spring Security + JWT：认证授权入门]]
5. [[_posts/Java-advanced/05-metric|Java全貌(5) | 监控指标入门：Micrometer + Prometheus]]
6. [[_posts/Java-advanced/06-grafana|java-advanced(6) | Grafana 搭建监控大盘：让指标"看得见"]]
7. [[_posts/Java-advanced/07-tracing|java-advanced(7) | 链路追踪入门：一个请求是怎么被"全程跟拍"的]]

## 结构脉络

### 1. 架构与交付

- [[_posts/Java-advanced/01-microservices-intro|01-microservices-intro]]
- [[_posts/Java-advanced/02-docker|02-docker]]
- [[_posts/Java-advanced/03-k8s|03-k8s]]

这一段把系统拆分、打包、部署和编排串成一条链。

### 2. 安全与访问控制

- [[_posts/Java-advanced/04-jwt|04-jwt]]

这一段解释用户身份、认证流程和接口授权的基本闭环。

### 3. 可观测性

- [[_posts/Java-advanced/05-metric|05-metric]]
- [[_posts/Java-advanced/06-grafana|06-grafana]]
- [[_posts/Java-advanced/07-tracing|07-tracing]]

这一段把指标、可视化和链路追踪组成同一套观察系统运行状态的方法论。

## 当前这页的作用

这页适合当成“从单机应用迈向分布式系统”的入口。

后续更适合继续拆出的概念页包括：

- 微服务
- Docker
- Kubernetes
- JWT
- Metrics / Tracing / Dashboard
