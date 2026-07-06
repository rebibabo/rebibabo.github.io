---
title: Files
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Files

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

`java.nio.file.Files` 是 Java 7 引入的纯静态方法工具类，提供一站式文件操作，覆盖了文件的判断、创建、复制、移动、删除、读写和目录遍历等全部常用场景，是现代 Java 文件操作的首选 API。

## 上下文

便捷读写：`Files.readString(path)`（Java 11+）一行读取整个文本文件、`Files.writeString(path, content)` 一行写入、`Files.readAllLines(path)` 读取所有行、`Files.readAllBytes(path)` 读取二进制文件。大文件处理：`Files.lines(path)` 返回惰性 Stream，逐行处理大文件时内存友好。目录遍历：`Files.list(path)` 列出直接子项、`Files.walk(path)` 递归遍历（深度优先）、`Files.find(path, maxDepth, matcher)` 带条件递归查找，三者都返回 Stream 且必须用 try-with-resources 关闭以释放文件句柄。判断类方法：`exists`、`isDirectory`、`isRegularFile`、`isReadable`、`size`。创建类方法：`createFile`、`createDirectory`（单层）、`createDirectories`（多层，等价 Python 的 `os.makedirs`）。Files 配合 Path 使用，是现代 Java 替代传统 `java.io.File` + 流的推荐方式。

## 相关术语
- [[wiki/glossary/java-basic/Path|Path]] — Files 所有操作都接受 Path 参数，两者配合使用
- [[wiki/glossary/java-basic/NIO|NIO]] — Files 属于 NIO.2 的一部分，是传统 I/O 的现代替代

## 深入阅读

- [[_posts/Java-basic/09-io|Java基础(9) | I/O 与文件操作：从 BIO 到 NIO 与 Files 工具类]]
