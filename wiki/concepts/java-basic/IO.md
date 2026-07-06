---
title: I/O
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# I/O

[[wiki/concepts/java-basic/Java-Basic-概念总图|返回概念总图]]

## 这一层回答什么问题

> Java 怎么读写文件？BIO、NIO、AIO 有什么区别？什么时候该用哪个？

I/O 是 Java 程序与外部世界交换数据的通道——读文件、发网络请求、处理输入输出流。不理解 I/O 模型，就理解不了为什么 Netty 要重新设计一套 API。

## 这层的主要分支

- [[wiki/concepts/java-basic/BIO|BIO]] — 传统流式 I/O、装饰器模式、字节流与字符流
- [[wiki/concepts/java-basic/NIO|NIO]] — Channel + Buffer + Selector、多路复用、Files 工具类
- [[wiki/concepts/java-basic/序列化|序列化]] — Serializable、Jackson JSON、对象与字节流的互转

## 三套 I/O 模型

| 模型 | 全称 | 核心 | 阻塞 | 使用场景 |
|------|------|------|------|----------|
| **BIO** | Blocking I/O | Stream（流） | 是 | 简单文件读写、低并发 |
| **NIO** | Non-blocking I/O | Channel + Buffer | 可非阻塞 | 高并发网络服务 |
| **AIO** | Asynchronous I/O | 回调 | 否 | 极少直接使用 |

**BIO 的问题不是"慢"，而是"一个线程只能处理一个连接"。** 当并发连接数上去后，线程资源就成了瓶颈。

## BIO：传统的流式 I/O

核心是四大抽象类：
- `InputStream` / `OutputStream` — 字节流
- `Reader` / `Writer` — 字符流（内置编解码）

装饰器模式是这个体系的核心设计：`BufferedReader` 包装 `FileReader` 加缓冲，`InputStreamReader` 桥接字节流和字符流。每一层包装加一种能力。

## NIO：面向 Channel 和 Buffer

三大组件：
- **Channel**：双向通道，可以读也可以写
- **Buffer**：数据容器，position / limit / capacity 三指针控制读写
- **Selector**：一个线程管理多个 Channel，谁有数据就处理谁——这是多路复用的核心

NIO 最大的贡献不是性能，而是**编程模型**——它证明了"一个线程管理多个连接"是可行的。Netty 就是基于 NIO 构建的。

## Files 工具类（Java 7+）

`java.nio.file.Files` 是日常文件操作的首选：

```java
// 一行代码读/写
String content = Files.readString(Path.of("file.txt"));
Files.writeString(Path.of("out.txt"), "hello");

// 惰性流式处理大文件
try (Stream<String> lines = Files.lines(Path.of("large.csv"))) {
    lines.filter(l -> !l.startsWith("#")).forEach(...);
}
```

## 序列化

把对象转成字节流（序列化）和从字节流恢复对象（反序列化）。Java 原生 `Serializable` 简单但笨重，Jackson JSON 是工程上的主流选择。

## 在系列里的位置

post 09。在异常之后——I/O 操作是 Checked Exception 的重灾区，`try-with-resources` 是标准写法。

## 推荐回看原文

- [[_posts/Java-basic/09-io|09-I/O 与文件操作]]

## 相关概念

- [[wiki/concepts/java-basic/异常|异常]] — I/O 操作大量使用 Checked Exception
- [[wiki/concepts/java-basic/Lambda与Stream|Lambda 与 Stream]] — `Files.lines()` 返回的就是 Stream
