---
title: 'Java基础(1) | 从源码到运行：理解Java程序的一生'
date: 2026-05-01
tags:
  - Java
  - JVM
  - 字节码
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

作为一个写了几年 Python / C++ 的人，回头重新审视 Java 的编译运行机制，会发现很多"入门时死记硬背"的东西——`javac`、`.class`、JVM、JRE、JDK——其实背后有一条非常清晰的设计逻辑链。这篇文章的目标是：**用一个 `Hello.java` 的完整生命周期，把 Java 程序"从写下第一行代码到最终执行"的每个环节串起来。**

<!-- more -->

## 1. 先跑起来：一个最小实验

在理解任何概念之前，先动手。创建一个 `Hello.java`：

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, Java!");
    }
}
```

然后在终端执行两步：

```bash
javac Hello.java   # 第一步：编译
java Hello          # 第二步：运行
```

输出 `Hello, Java!`。看起来平平无奇，但这两步背后藏着 Java 区别于 C/C++/Python 的核心设计。

## 2. javac：从源码到字节码

### 2.1 javac 是什么？

`javac` 是 **Java Compiler**，即 Java 编译器。它的职责是：

> 将人类可读的 `.java` 源代码 → 编译为 JVM 可执行的 `.class` 字节码文件

执行 `javac Hello.java` 后，当前目录下会多出一个 `Hello.class` 文件。这个文件**不是**机器码（不像 C++ 的 `gcc -o` 产物可以直接被操作系统执行），而是一种中间表示——**字节码（Bytecode）**。

### 2.2 为什么不直接编译成机器码？

这是 Java 最核心的设计决策之一，也是"Write Once, Run Anywhere"的基础：

| 语言 | 编译目标 | 可移植性 |
|------|---------|---------|
| C/C++ | 平台相关的机器码（x86、ARM...） | 换平台需要重新编译 |
| Python | 不需要显式编译，解释器逐行执行 | 依赖解释器实现 |
| **Java** | **平台无关的字节码** | **只要有对应平台的 JVM 就能运行** |

Java 的思路是：**把"适配不同平台"的脏活交给 JVM，字节码本身保持统一。** 你在 macOS 上编译出的 `.class` 文件，拷贝到 Linux 或 Windows 上，只要装了对应的 JVM，就能直接跑。

### 2.3 字节码长什么样？

用 `javap -c Hello` 可以反编译 `.class` 文件，看到字节码指令：

```bash
javap -c Hello
```

<details>
<summary>点击展开 javap 输出</summary>

```
Compiled from "Hello.java"
public class Hello {
  public Hello();
    Code:
       0: aload_0
       1: invokespecial #1    // Method java/lang/Object."<init>":()V
       4: return

  public static void main(java.lang.String[]);
    Code:
       0: getstatic     #7    // Field java/lang/System.out:Ljava/io/PrintStream;
       3: ldc           #13   // String Hello, Java!
       5: invokevirtual #15   // Method java/io/PrintStream.println:(Ljava/lang/String;)V
       8: return
}
```

</details>

几个值得注意的点：

- **`aload_0`、`invokespecial`、`getstatic`** 这些就是字节码指令，类似汇编，但面向的是 JVM 这台"虚拟机器"而非物理 CPU。
- 即使我们没有写构造函数，编译器也自动生成了一个默认构造函数 `Hello()`，内部调用了 `Object.<init>`——因为 Java 中所有类都隐式继承 `Object`。
- `ldc #13` 是从常量池加载字符串 `"Hello, Java!"`，`invokevirtual` 是虚方法调用（多态的基础）。

## 3. JVM / JRE / JDK：三个容易混淆的概念

这三个缩写经常让人头大，其实它们是一个**层层包含**的关系：

<div style="font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.6;">
  <div style="border: 2px solid #4A90D9; border-radius: 8px; padding: 16px; background: #EBF2FA;">
    <div style="font-weight: bold; color: #4A90D9; margin-bottom: 8px;">JDK (Java Development Kit)</div>
    <div style="border: 2px solid #7B61FF; border-radius: 8px; padding: 14px; background: #F0ECFF;">
      <div style="font-weight: bold; color: #7B61FF; margin-bottom: 8px;">JRE (Java Runtime Environment)</div>
      <div style="border: 2px solid #E85D75; border-radius: 8px; padding: 12px; background: #FFF0F2;">
        <div style="font-weight: bold; color: #E85D75; margin-bottom: 6px;">JVM (Java Virtual Machine)</div>
        <div style="color: #555; padding-left: 8px;">
          · 类加载器<br>
          · 字节码解释器<br>
          · JIT 编译器<br>
          · 垃圾回收器<br>
          · 内存管理
        </div>
      </div>
      <div style="color: #555; margin-top: 10px; padding-left: 8px;">
        + 核心类库 (java.lang, java.util, ...)<br>
        + java 命令 (启动 JVM)
      </div>
    </div>
    <div style="color: #555; margin-top: 10px; padding-left: 8px;">
      + javac (编译器)<br>
      + javap (反编译工具)<br>
      + jdb (调试器)<br>
      + jar (打包工具)<br>
      + 其他开发工具
    </div>
  </div>
</div>

用一句话总结各自的角色：

- **JVM**：执行字节码的虚拟机，是 Java 跨平台的关键。它本身是平台相关的（macOS 的 JVM 和 Linux 的 JVM 是不同的二进制程序），但它对上层暴露统一的字节码接口。
- **JRE**：JVM + 核心类库。有了 JRE 就能**运行** Java 程序，但不能编译。
- **JDK**：JRE + 开发工具（javac、javap、jdb 等）。**开发者**需要装 JDK，纯用户只需要 JRE。

> **注意**：从 Java 11 开始，Oracle 不再单独提供 JRE 下载，JDK 成了唯一的发行单元。但概念上的分层关系依然成立。

## 4. 一个更直观的对比

为了加深理解，把 Java 和你熟悉的 C++ / Python 放在一起对比：

| 维度 | C++ | Python | Java |
|------|-----|--------|------|
| 编译/解释 | 编译为机器码 | 解释执行（.pyc 是优化缓存） | 编译为字节码 + JVM 解释/JIT |
| 编译产物 | 可执行文件（ELF/PE） | 无显式产物 | `.class` 文件 |
| 跨平台方式 | 重新编译 | 依赖 Python 解释器 | 依赖 JVM |
| 运行时性能 | 最高 | 最低 | 中高（JIT 优化后接近 C++） |
| 内存管理 | 手动（new/delete） | GC | GC |
| 启动速度 | 快 | 快 | 较慢（JVM 启动开销） |

## 5. 动手验证

可以自己跑一遍以下实验加深印象：

### 实验 1：观察编译产物

```bash
# 编译
javac Hello.java

# 查看生成的 .class 文件
ls -la Hello.class
```

### 实验 2：反编译观察字节码

```bash
# 基础反编译
javap -c Hello

# 更详细的信息（常量池、版本号等）
javap -v Hello
```

### 实验 3：跨版本观察

```bash
# 查看 class 文件的版本号
javap -v Hello | grep "major version"
# Java 8 → 52, Java 11 → 55, Java 17 → 61, Java 21 → 65
```

版本号决定了这个 `.class` 文件需要多高版本的 JVM 才能运行。高版本 JVM 可以运行低版本 class，反过来不行。

## 6. 小结

一张图概括 Java 程序的一生：

```
源码 (.java)
   │
   │  javac 编译
   ▼
字节码 (.class)      ← 平台无关的中间表示
   │
   │  java 命令启动 JVM
   ▼
JVM 加载 → 执行
            ↑
    平台相关（不同 OS 有不同 JVM 实现）
```

核心要点回顾：

- `javac` 把 `.java` 编译成 `.class`（字节码），而非机器码。
- `.class` 是一种平台无关的中间表示，由 JVM 负责加载和执行。
- JVM 是执行字节码的虚拟机，它本身是平台相关的，但对上提供统一接口。
- JDK ⊃ JRE ⊃ JVM，开发需要 JDK，运行只需 JRE（Java 11+ 合并了）。

---

> **下一篇预告**：Java 基础(2) | 基本数据类型——八大原始类型与那些必踩的坑

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
![[IMG-20260706212413574.png]]