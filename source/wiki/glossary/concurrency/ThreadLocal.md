---
title: ThreadLocal
tags:
  - wiki
  - glossary
  - concurrency
  - threadlocal
type: glossary
source_series: concurrency
status: seed
---

# ThreadLocal

[[wiki/glossary/concurrency/index|返回词汇表]]

## 定义

`ThreadLocal` 为每个线程提供独立的变量副本。一个线程往 ThreadLocal 里 set 的值，只有自己 get 得到——不需要显式传参就能在线程的任意调用链中访问。

## 上下文

典型场景：Web 请求上下文（requestId、用户信息）、数据库连接（每个线程一个连接）、日期格式化（SimpleDateFormat 线程不安全，ThreadLocal 给每线程一个实例）。实现原理：Thread 对象内部维护 ThreadLocalMap，ThreadLocal 作为 key。

线程池中的核心问题：线程复用后 ThreadLocal 的值不会自动清除。前一个任务 set 的值，后一个任务如果不清除就会读到脏数据。因此必须 `finally { threadLocal.remove(); }`——尤其是 Tomcat 这类线程池管理请求线程的场景。

## 相关术语

- [[wiki/glossary/concurrency/ThreadPoolExecutor|ThreadPoolExecutor]] — 线程池复用导致 ThreadLocal 泄漏风险

## 深入阅读

- [[wiki/concepts/concurrency/ThreadLocal|ThreadLocal 概念页（完整版）]]
- [[_posts/concurrency/18-ThreadLocal 的线程隔离与线程池问题|18-ThreadLocal]]
