---
title: NIO
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# NIO

[[wiki/concepts/java-basic/IO|返回 I/O]]

## 这一层回答什么问题

> NIO 和 BIO 的根本区别是什么？Channel、Buffer、Selector 怎么配合？多路复用解决了什么？

NIO（Non-blocking I/O）不是"比 BIO 更快"，而是提供了**一个线程管理多个连接**的能力。这对于高并发网络服务来说是决定性的架构差异。

## 三大组件

**Channel**：双向的 I/O 通道，可以读也可以写。对应 BIO 的 Stream，但 Stream 是单向的。

**Buffer**：数据容器。所有数据的读写都要通过 Buffer。核心是三个指针：

```
position  ← 当前读写位置
limit     ← 可读写的上限
capacity  ← 总容量
```

`flip()` 从写模式切换到读模式（`limit = position; position = 0`）。`clear()` 从读模式切换回写模式。

**Selector**：多路复用的核心。一个 Selector 可以注册多个 Channel，哪个 Channel 有数据就处理哪个——一个线程管理成千上万个连接。

```java
Selector selector = Selector.open();
channel.register(selector, SelectionKey.OP_READ);
while (true) {
    selector.select();  // 阻塞，直到有 Channel 就绪
    for (SelectionKey key : selector.selectedKeys()) {
        if (key.isReadable()) { /* 读数据 */ }
    }
}
```

## 零拷贝

`FileChannel.transferTo()` / `transferFrom()` 可以在两个 Channel 之间直接传输数据，不经过用户空间——数据从磁盘到内核缓冲区，直接到网卡。

## BIO vs NIO vs AIO

| | BIO | NIO | AIO |
|------|-----|-----|-----|
| 读操作 | 阻塞，等数据 | 可非阻塞，立即返回 | 回调通知 |
| 线程模型 | 一个连接一个线程 | 一个线程管理多个连接 | 回调 + 线程池 |
| 复杂度 | 低 | 高 | 中 |
| 使用 | 文件读写 | Netty、Tomcat NIO | 极少直接使用 |

## Files 工具类

`java.nio.file.Files` 是日常文件操作的首选。一行代码读/写、惰性 `Files.lines()` 处理大文件、`Files.walk()` 遍历目录树。

## 在系列里的位置

post 09。

## 推荐回看原文

- [[_posts/Java-basic/09-io|09-I/O 与文件操作]]

## 相关概念

- [[wiki/concepts/java-basic/BIO|BIO]]
- [[wiki/concepts/java-basic/JVM|JVM]] — NIO 的 Buffer 是直接内存，不受 JVM 堆 GC 影响
