---
title: Path
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Path

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

Path 是 Java 7 引入的 `java.nio.file.Path` 接口，用于替代老旧的 `java.io.File` 类，提供更清晰的路径抽象和更丰富的路径操作方法。

## 上下文

创建方式：Java 11+ 推荐 `Path.of("a", "b", "c")`（等价于 `Paths.get`，更简洁）。路径操作：`resolve(path)` 拼接子路径（等价 Python `os.path.join`）、`resolveSibling(name)` 替换最后一段、`normalize()` 解析 `.` 和 `..`、`relativize(other)` 计算相对路径。信息提取：`getFileName()`（等价 `os.path.basename`）、`getParent()`（等价 `os.path.dirname`）、`toAbsolutePath()`（等价 `os.path.abspath`）。Path 本身只表示路径字符串，不操作文件，所有文件操作交由 `Files` 工具类处理。与传统 `File` 的互转通过 `path.toFile()` 和 `file.toPath()` 实现。相比 `File`，Path 的优势在于方法命名更合理、异常信息更明确（如删除失败会抛出具体原因而非只返回 false）、天然支持符号链接处理。

## 相关术语
- [[wiki/glossary/java-basic/Files|Files]] — Path 只表示路径，所有文件操作交由 Files 工具类处理
- [[wiki/glossary/java-basic/NIO|NIO]] — Path 是 NIO.2 的核心接口，替代传统 java.io.File

## 深入阅读

- [[_posts/Java-basic/09-io|Java基础(9) | I/O 与文件操作：从 BIO 到 NIO 与 Files 工具类]]
