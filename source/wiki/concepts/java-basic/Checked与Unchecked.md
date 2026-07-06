---
title: Checked 与 Unchecked
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# Checked 与 Unchecked

[[wiki/concepts/java-basic/异常|返回异常]]

## 这一层回答什么问题

> 为什么有些异常编译器逼着你处理，有些不会？两者的设计意图是什么？什么时候该自定义 Checked 异常？

Checked 和 Unchecked 的区别不只是一句"一个必须 try-catch，一个不用"——它背后是两种不同的错误处理哲学。

## 异常层次

```
Throwable
├── Error（不应捕获：OOM、StackOverflow、NoClassDefFound）
└── Exception
    ├── RuntimeException（Unchecked）
    │   ├── NullPointerException
    │   ├── IllegalArgumentException
    │   └── IndexOutOfBoundsException
    └── 其他（Checked）
        ├── IOException
        ├── SQLException
        └── InterruptedException
```

## 两者的设计意图

| | Checked | Unchecked |
|------|---------|-----------|
| 典型场景 | 外部条件不可控（网络断了、文件不存在） | 程序 bug（判 null、数组越界） |
| 编译器 | 强制 try-catch 或 throws | 不强制 |
| 设计哲学 | 调用者有**义务**处理这种失败 | 应该通过**修代码**来避免 |

**经验法则**：能用 if 避免的 → 修代码，别用异常兜底；外部条件不可控的 → Checked Exception，让调用者知道"这个操作可能失败，你必须处理"。

## 自定义异常

```java
// Checked：调用者必须处理
public class InsufficientBalanceException extends Exception {
    private final BigDecimal shortfall;
    // constructor...
}

// Unchecked：调用者可以选择处理
public class DuplicateEmailException extends RuntimeException {
    public DuplicateEmailException(String email) {
        super("邮箱已存在: " + email);
    }
}
```

什么时候选 Checked？当"这个操作失败了"属于正常业务流程的一部分，调用者**必须有意识地决定怎么办**。比如转账余额不足——这不是 bug，是业务规则。

什么时候选 Unchecked？当这是调用者的编码错误——比如传了 null、传了非法参数。这种情况要求调用者改代码，不是 try-catch 兜底。

## 异常链

```java
catch (SQLException e) {
    throw new ServiceException("查询用户失败", e);  // cause
}
```

上层看到 `ServiceException` 就知道是服务层的问题。排查时顺着 `getCause()` 一路追到 SQLException——根因不丢。

## 在系列里的位置

post 07。

## 推荐回看原文

- [[_posts/Java-basic/07-exception|07-异常体系]]

## 相关概念

- [[wiki/concepts/java-basic/try-with-resources|try-with-resources]]
