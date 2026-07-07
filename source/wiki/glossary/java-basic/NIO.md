---
title: NIO
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# NIO

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

NIO（New I/O，Java 1.4 引入）是 Java 的非阻塞 I/O 模型，基于 Channel（双向通道）、Buffer（数据缓冲区）和 Selector（多路复用器）三大核心组件，主要面向高并发网络编程场景。

## 上下文

与 BIO 的"一连接一线程"阻塞模型不同，NIO 采用同步非阻塞 + 多路复用模型：所有 Channel 注册到单个 Selector 上，一个线程通过 `select()` 轮询就绪的 Channel，只处理有数据到达的连接，线程不再空等待。Buffer 是所有数据读写的必经容器，关键操作流程是写完后 `flip()` 切换为读模式，读完后 `clear()` 重置准备下次写入。Channel 之间可以使用 `transferTo`/`transferFrom` 实现零拷贝文件传输，是性能最优的文件复制方式。实际开发中通常使用 Netty 框架（基于 NIO）而非手写 Selector，但理解 Channel + Buffer + Selector 模型是读懂 Netty 源码的前提。

## 相关术语
- [[wiki/glossary/java-basic/字节流|字节流]] — 传统 BIO 字节流，与 NIO 的 Channel/Buffer 模型对比理解
- [[wiki/glossary/java-basic/Path|Path]] — NIO.2 引入的路径抽象，配合 Files 工具类使用
- [[wiki/glossary/java-basic/Files|Files]] — NIO.2 文件操作工具类，现代 Java 文件操作首选

## 深入阅读

- [[_posts/Java-basic/09-io|java-basics(9) | I/O 与文件操作：从 BIO 到 NIO 与 Files 工具类]]
