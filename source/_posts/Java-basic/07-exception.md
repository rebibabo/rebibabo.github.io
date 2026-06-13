---
title: 'Java全貌(7) | 异常体系：Checked vs Unchecked 与 try-with-resources'
date: 2026-05-07
tags:
  - Java
  - 异常处理
categories:
  - Java全貌
---

## 前言

Java 的异常体系是它最具争议的设计之一——Checked Exception 到底是好是坏，至今没有定论。但不管你怎么看，实际开发中必须和它打交道。这篇文章把异常的分类、处理机制、最佳实践一次讲清。

<!-- more -->

## 1. 异常的类层次

Java 中所有异常都是对象，继承自 `Throwable`：

```
Throwable
├── Error（系统级错误，不应该捕获）
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── ...
└── Exception（程序级异常）
    ├── RuntimeException（Unchecked，运行时异常）
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   ├── ClassCastException
    │   ├── IllegalArgumentException
    │   ├── ArithmeticException
    │   ├── NumberFormatException
    │   ├── UnsupportedOperationException
    │   └── ...
    └── 其他 Exception（Checked，受检异常）
        ├── IOException
        ├── SQLException
        ├── FileNotFoundException
        ├── ClassNotFoundException
        └── ...
```

### 1.1 三大分类

| 分类 | 父类 | 是否必须处理 | 典型场景 |
|------|------|-------------|---------|
| Error | `Error` | 不需要（也处理不了） | JVM 内存耗尽、栈溢出 |
| Checked Exception | `Exception`（非 RuntimeException） | **编译器强制要求** try-catch 或 throws | 文件不存在、网络中断、SQL 错误 |
| Unchecked Exception | `RuntimeException` | 不强制，可以不处理 | 空指针、数组越界、类型转换失败 |

一句话区分：**Checked 是"可以预见并应该处理的外部问题"，Unchecked 是"程序员写了 bug"。**

## 2. 异常处理语法

### 2.1 try-catch-finally

```java
try {
    String s = null;
    s.length();                    // 抛出 NullPointerException
} catch (NullPointerException e) {
    System.out.println("空指针：" + e.getMessage());
} catch (Exception e) {
    System.out.println("其他异常：" + e.getMessage());
} finally {
    System.out.println("无论是否异常都会执行");
    // 常用于关闭资源（但现代 Java 更推荐 try-with-resources）
}
```

### 2.2 多异常捕获（Java 7+）

```java
try {
    // 可能抛出多种异常
} catch (IOException | SQLException e) {
    // 用 | 合并处理，e 的类型是这些异常的共同父类
    System.out.println("IO 或 SQL 异常：" + e.getMessage());
}
```

### 2.3 throws 声明

如果你不想在当前方法处理异常，可以用 `throws` 抛给调用者：

```java
// Checked 异常：必须声明或捕获，否则编译报错
public String readFile(String path) throws IOException {
    return new String(Files.readAllBytes(Paths.get(path)));
}

// 调用者必须处理
try {
    String content = readFile("data.txt");
} catch (IOException e) {
    e.printStackTrace();
}

// Unchecked 异常：不需要声明（但可以声明，作为文档提示）
public int divide(int a, int b) {
    return a / b;  // 可能抛 ArithmeticException，但不用声明
}
```

### 2.4 throw 手动抛出异常

```java
public void setAge(int age) {
    if (age < 0 || age > 150) {
        throw new IllegalArgumentException("Invalid age: " + age);
    }
    this.age = age;
}

// throw vs throws：
// throw  → 在方法体内抛出一个具体的异常对象
// throws → 在方法签名上声明可能抛出的异常类型
```

## 3. try-with-resources（Java 7+）

### 3.1 传统写法的痛苦

在 Java 7 之前，关闭资源需要在 finally 中手写，非常啰嗦且容易遗漏：

```java
// 传统写法：丑陋且容易出错
BufferedReader reader = null;
try {
    reader = new BufferedReader(new FileReader("data.txt"));
    String line = reader.readLine();
} catch (IOException e) {
    e.printStackTrace();
} finally {
    if (reader != null) {
        try {
            reader.close();  // close 本身也可能抛异常
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### 3.2 try-with-resources 自动关闭

只要资源实现了 `AutoCloseable` 接口，就可以放在 `try()` 括号中，作用域结束后自动调用 `close()`：

```java
// 现代写法：简洁、安全
try (BufferedReader reader = new BufferedReader(new FileReader("data.txt"))) {
    String line = reader.readLine();
    System.out.println(line);
} catch (IOException e) {
    e.printStackTrace();
}
// reader 在这里已经自动关闭，不需要 finally

// 多个资源用分号隔开
try (
    FileInputStream fis = new FileInputStream("input.txt");
    FileOutputStream fos = new FileOutputStream("output.txt")
) {
    fos.write(fis.readAllBytes());
}
// fis 和 fos 都会自动关闭，关闭顺序和声明顺序相反（后声明的先关）
```

### 3.3 哪些类可以用 try-with-resources？

所有实现了 `AutoCloseable`（或其子接口 `Closeable`）的类，包括：

```java
// 常见的可自动关闭资源
InputStream / OutputStream       // 文件、网络流
Reader / Writer                  // 字符流
Connection / Statement / ResultSet  // JDBC 数据库
Socket / ServerSocket            // 网络
Scanner                          // 输入扫描

// 自定义可关闭资源
public class MyResource implements AutoCloseable {
    public void doWork() {
        System.out.println("working...");
    }

    @Override
    public void close() {
        System.out.println("resource closed.");
    }
}

try (MyResource r = new MyResource()) {
    r.doWork();
}
// 输出：
// working...
// resource closed.
```

## 4. 自定义异常

### 4.1 什么时候需要自定义？

当标准异常无法准确表达你的业务语义时。比如"用户余额不足"用 `IllegalStateException` 也行，但自定义的 `InsufficientBalanceException` 调用者一看就懂，还能携带业务信息。

### 4.2 怎么写？

```java
// Unchecked 自定义异常：继承 RuntimeException
public class InsufficientBalanceException extends RuntimeException {
    private final double balance;
    private final double amount;

    public InsufficientBalanceException(double balance, double amount) {
        super(String.format("余额不足：当前 %.2f，需要 %.2f", balance, amount));
        this.balance = balance;
        this.amount = amount;
    }

    public double getBalance() { return balance; }
    public double getAmount() { return amount; }
}

// 使用
public void withdraw(double amount) {
    if (balance < amount) {
        throw new InsufficientBalanceException(balance, amount);
    }
    balance -= amount;
}
```

```java
// Checked 自定义异常：继承 Exception
public class FileParseException extends Exception {
    private final int lineNumber;

    public FileParseException(String message, int lineNumber) {
        super(message);
        this.lineNumber = lineNumber;
    }

    public FileParseException(String message, int lineNumber, Throwable cause) {
        super(message, cause);  // 保留原始异常链
        this.lineNumber = lineNumber;
    }

    public int getLineNumber() { return lineNumber; }
}
```

### 4.3 选 Checked 还是 Unchecked？

| 场景 | 选择 | 原因 |
|------|------|------|
| 调用者可以合理地恢复处理 | Checked | 强制调用者面对这个问题 |
| 程序错误（参数非法、状态异常） | Unchecked | 不应该让调用者 try-catch 来掩盖 bug |
| 不确定 | **Unchecked** | 现代 Java 开发和 Spring 生态的主流倾向 |

## 5. 异常链（Chained Exceptions）

捕获底层异常后抛出高层异常时，务必保留原始原因：

```java
// 错误：丢失了原始异常信息
try {
    readFile("data.txt");
} catch (IOException e) {
    throw new RuntimeException("处理失败");  // 原始的 IOException 丢了
}

// 正确：通过 cause 保留异常链
try {
    readFile("data.txt");
} catch (IOException e) {
    throw new RuntimeException("处理失败", e);  // e 作为 cause 传入
}

// 排查问题时可以追溯完整链路：
// RuntimeException: 处理失败
//   Caused by: java.io.IOException: No such file
//     Caused by: java.io.FileNotFoundException: data.txt
```

## 6. 异常处理的最佳实践

### 6.1 不要吞掉异常

```java
// 最差的写法：异常被吞掉了，出了问题完全无法排查
try {
    riskyOperation();
} catch (Exception e) {
    // 什么都不做
}

// 至少要记录日志
try {
    riskyOperation();
} catch (Exception e) {
    log.error("操作失败", e);  // 或 e.printStackTrace() 用于调试
}
```

### 6.2 不要用异常控制流程

```java
// 错误：用异常代替条件判断，性能差且意图不清
try {
    int value = Integer.parseInt(input);
} catch (NumberFormatException e) {
    value = 0;  // 把异常当 if-else 用
}

// 正确：先检查
if (input != null && input.matches("-?\\d+")) {
    value = Integer.parseInt(input);
} else {
    value = 0;
}
```

### 6.3 精确捕获，不要一把梭

```java
// 错误：捕获范围太大，可能掩盖其他 bug
try {
    String s = map.get(key).trim().toLowerCase();
} catch (Exception e) {
    return "";  // NullPointerException? ClassCastException? 全吞了
}

// 正确：只捕获你预期的异常
try {
    String s = map.get(key).trim().toLowerCase();
} catch (NullPointerException e) {
    return "";  // 明确处理 key 不存在的情况
}

// 更好：根本不用异常
String raw = map.get(key);
return raw != null ? raw.trim().toLowerCase() : "";
```

### 6.4 finally 中不要 return

```java
// 危险：finally 中的 return 会覆盖 try/catch 中的返回值和异常
public int dangerous() {
    try {
        throw new RuntimeException("出错了！");
    } finally {
        return 0;  // 异常被吞掉了，方法正常返回 0，调用者完全不知道出了问题
    }
}
```

### 6.5 常见的异常使用场景速查

| 异常 | 使用场景 |
|------|---------|
| `IllegalArgumentException` | 方法参数不合法 |
| `IllegalStateException` | 对象状态不对（如未初始化就调用） |
| `NullPointerException` | 通常是 bug，避免手动 throw |
| `UnsupportedOperationException` | 不支持的操作（如不可变集合的 add） |
| `IndexOutOfBoundsException` | 索引越界 |
| `ConcurrentModificationException` | 遍历时修改集合 |
| `IOException` | I/O 操作失败 |
| `NumberFormatException` | 字符串转数字格式错误 |

## 7. 小结

| 主题 | 关键要点 |
|------|---------|
| 三大分类 | Error（别管）、Checked（编译器强制处理）、Unchecked（运行时异常） |
| try-catch | 多异常可用 `\|` 合并；catch 顺序从子类到父类 |
| try-with-resources | 实现 AutoCloseable 的资源自动关闭，替代 finally 关资源 |
| throw / throws | throw 抛具体异常，throws 在签名上声明 |
| 自定义异常 | 不确定时选 Unchecked；携带业务信息；保留异常链 |
| 最佳实践 | 不吞异常、不用异常控制流程、精确捕获、finally 中不 return |

---

> **下一篇预告**：Lambda 与 Stream API——Java 8 函数式编程的核心工具