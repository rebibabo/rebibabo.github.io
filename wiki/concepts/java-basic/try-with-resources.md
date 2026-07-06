---
title: try-with-resources
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# try-with-resources

[[wiki/concepts/java-basic/异常|返回异常]]

## 这一层回答什么问题

> 资源为什么不用了必须关？finally 关了这么久，为什么 Java 7 还要引入 try-with-resources？

资源管理是 Java 里最容易被写错的代码之一。try-with-resources 不只是语法糖——它解决了 finally 关资源时可能吞异常的问题。

## finally 关资源的问题

```java
BufferedReader br = new BufferedReader(new FileReader(path));
try {
    return br.readLine();
} finally {
    br.close();  // 如果 close() 也抛异常呢？
}
```

如果 `readLine()` 抛异常 → 进 finally → `close()` 也抛异常 → `close()` 的异常**覆盖**了 `readLine()` 的异常。你看到的堆栈是"关闭失败"，真正的业务异常丢了。

## try-with-resources 怎么解决的

```java
try (BufferedReader br = new BufferedReader(new FileReader(path))) {
    return br.readLine();
}
// br.close() 自动调用，不需要 finally
```

如果 `readLine()` 和 `close()` 都抛异常：
- 业务异常（readLine）被抛出
- close 的异常作为**被抑制的异常**附加在业务异常上（`getSuppressed()` 可获取）

两个异常都不丢。

## 只要实现了 AutoCloseable 就行

任何实现了 `AutoCloseable`（或其子接口 `Closeable`）的类都可以用在 try-with-resources 里。Java 标准库中几乎所有 I/O 类、JDBC 连接、Statement、ResultSet 都实现了。

你也可以给自己的类实现：

```java
public class MyResource implements AutoCloseable {
    @Override
    public void close() {
        // 清理逻辑
    }
}
```

## 在系列里的位置

post 07。

## 推荐回看原文

- [[_posts/Java-basic/07-exception|07-异常体系]]

## 相关概念

- [[wiki/concepts/java-basic/Checked与Unchecked|Checked 与 Unchecked]]
- [[wiki/concepts/java-basic/IO|I/O]] — I/O 类是 try-with-resources 的主要使用者
