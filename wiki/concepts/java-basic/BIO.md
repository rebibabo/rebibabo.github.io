---
title: BIO
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# BIO

[[wiki/concepts/java-basic/IO|返回 I/O]]

## 这一层回答什么问题

> Java 传统 I/O 怎么组织的？字节流和字符流有什么区别？装饰器模式在 I/O 里怎么体现？

BIO（Blocking I/O）是 Java 最早的 I/O 模型。它的 API 设计是装饰器模式的教科书级应用——每一层包装加一种能力。

## 流的四大抽象

```
InputStream    ← 字节输入
OutputStream   ← 字节输出
Reader         ← 字符输入（内置编解码）
Writer         ← 字符输出（内置编解码）
```

**字节流 vs 字符流**：字节流处理二进制数据（图片、视频），字符流处理文本并自动编码解码。

## 装饰器模式：BIO 的核心设计

```java
// 文件字节流 → 加缓冲 → 加数据读取能力
DataInputStream dis = new DataInputStream(
    new BufferedInputStream(
        new FileInputStream("data.bin")
    )
);
dis.readInt();  // 读一个 int
dis.readUTF();  // 读一个 UTF 字符串
```

每一层包装是独立的装饰器，可以自由组合。`FileInputStream` 负责从文件读字节，`BufferedInputStream` 加缓冲减少系统调用，`DataInputStream` 加类型化读取能力。

## 桥接流：字节和字符之间的桥梁

`InputStreamReader` / `OutputStreamWriter` 是字节流和字符流之间的转换器。关键——构造时可以指定字符编码：

```java
try (BufferedReader br = new BufferedReader(
        new InputStreamReader(new FileInputStream(path), StandardCharsets.UTF_8))) {
    String line = br.readLine();
}
```

## BIO 的问题

BIO 的核心问题是**一个线程一个连接**。`InputStream.read()` 是阻塞的——在数据到达前，当前线程什么也做不了。当并发连接数上万时，需要上万个线程——线程切换开销和内存占用都不可接受。这就是 NIO 要解决的问题。

## 在系列里的位置

post 09。

## 推荐回看原文

- [[_posts/Java-basic/09-io|09-I/O 与文件操作]]

## 相关概念

- [[wiki/concepts/java-basic/NIO|NIO]]
- [[wiki/concepts/java-basic/序列化|序列化]]
