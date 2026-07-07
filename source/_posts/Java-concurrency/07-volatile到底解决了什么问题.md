---
title: Java高并发底层原理（七）—— volatile 到底解决了什么问题
date: 2026-07-02
abbrlink: 07
tags:
  - Java
  - 高并发
  - volatile
  - JMM
categories:
  - java-concurrency
---


缓存一致性协议能够协调多个 CPU Core 对同一条 Cache Line 的读写，但 Java 程序仍然需要明确一件事：一个线程修改变量以后，另一个线程什么时候必须看到这个修改？

`volatile` 就是 Java 提供的一种内存语义。它不负责把一段代码变成临界区，也不会阻止多个线程同时执行，而是围绕一个变量建立可见性和有序性规则。

## 1. 一个线程为什么可能看不到另一个线程的修改

先看一个常见的停止线程示例：

```java
public class StopDemo {

    private static boolean running = true;

    public static void main(String[] args) throws InterruptedException {
        Thread worker = new Thread(() -> {
            while (running) {
                // do something
            }

            System.out.println("worker stopped");
        });

        worker.start();

        Thread.sleep(1000);
        running = false;
    }
}
```

主线程在一秒后把 `running` 修改为 `false`，从源码顺序看，工作线程似乎应该很快退出循环。但在没有任何同步规则的情况下，Java 并不保证工作线程一定能及时观察到这个修改。

工作线程可能反复使用寄存器、CPU Cache 或编译器优化后的结果，而不是在每次循环时都重新按照源码形式读取共享变量。JIT 编译器只需要保证单线程语义不被破坏，在它看来，如果当前线程内部没有代码修改 `running`，就可能减少重复读取。

这并不表示 Java 规定线程必须拥有一份独立的变量副本，也不能简单理解为“线程只读自己的缓存”。真实执行可能涉及寄存器、Cache、Store Buffer、JIT 优化和处理器指令。Java 内存模型不要求开发者依赖某一种具体硬件结构，而是通过规则规定哪些结果必须被其他线程看到。

## 2. volatile 保证可见性

把 `running` 声明为 `volatile`：

```java
private static volatile boolean running = true;
```

主线程写入：

```java
running = false;
```

工作线程读取：

```java
while (running) {
    // do something
}
```

此时，Java 内存模型要求工作线程能够观察到对 `running` 的最新写入。主线程把它修改为 `false` 后，工作线程后续读取不能一直使用已经失效的旧值 `true`。

这里的核心保证是：

> 一个线程对 volatile 变量的写入，对随后读取同一个 volatile 变量的线程可见。

`volatile` 不会让两个线程停止并发执行，也不会要求读线程先获得某把锁。它只是让这个变量的读写具备特殊内存语义。

## 3. volatile 不是每次都直接访问主内存

很多资料把 `volatile` 描述成“每次读取都从主内存读取，每次写入都立即刷新到主内存”。这种说法方便记忆，但不够准确。

现代 CPU 仍然会使用寄存器和 Cache，`volatile` 不会关闭缓存，也不会强制所有访问都绕过 Cache。JVM 会根据目标处理器的内存模型生成合适的指令，并在需要的位置加入内存屏障或使用带有顺序语义的读写指令。

缓存一致性机制负责让不同 Core 的缓存副本保持协调，内存屏障负责限制某些读写的执行顺序。两者共同实现 Java 对 `volatile` 的语义要求。

因此，更准确的理解是：

> volatile 规定线程必须按照特定规则观察读写结果，具体如何实现由 JVM 和 CPU 决定。

## 4. 什么是指令重排

编译器和处理器可以在不改变单线程结果的前提下调整指令执行顺序，这种优化称为**指令重排（Instruction Reordering）**。

例如：

```java
int a = 1;
int b = 2;
```

如果后面的代码不依赖这两个赋值的先后顺序，编译器或处理器可能先执行 `b = 2`，再执行 `a = 1`。在单线程中，两种顺序得到的结果相同，因此这种调整通常没有问题。

多线程程序却可能观察到中间状态。假设一个线程发布数据：

```java
data = 42;
ready = true;
```

另一个线程读取：

```java
if (ready) {
    System.out.println(data);
}
```

程序希望 `ready` 表示“数据已经准备完成”。如果两个写操作对其他线程的可见顺序没有约束，读线程就可能先看到 `ready == true`，却仍然没有看到 `data = 42`。

问题不一定来自源码被简单交换，也可能来自写入暂存在 Store Buffer、不同缓存行传播速度不同，或者读操作以不同顺序完成。Java 不要求开发者区分每一种硬件原因，而是通过内存模型统一规定哪些重排必须被禁止。

## 5. volatile 如何保证有序性

把 `ready` 声明为 `volatile`：

```java
private static int data;
private static volatile boolean ready;
```

写线程执行：

```java
data = 42;
ready = true;
```

读线程执行：

```java
if (ready) {
    System.out.println(data);
}
```

`volatile` 在这里不仅保证 `ready` 的可见性，还建立了一条顺序关系：

- `ready = true` 之前的普通写，不能被移动到这个 volatile 写之后；
- 读取到 `ready == true` 之后的普通读，不能被移动到这个 volatile 读之前。

可以用下面的模型表示：

![](/images/Java-concurrency/IMG-20260707-000041.png)




中间的横线表示一条内存可见边界。只要读线程读取到写线程发布的 `ready == true`，它也必须能够看到这个 volatile 写之前已经完成的普通写，因此 `data` 应当等于 `42`。

## 6. volatile 与 happens-before

Java 内存模型使用 **happens-before** 描述线程之间的可见性和顺序保证。它并不表示两个操作在现实时间上一定紧挨着发生，而是表示前一个操作的结果必须对后一个操作可见，并且前一个操作在内存语义上排在后一个操作之前。

与 `volatile` 直接相关的规则是：

> 对一个 volatile 变量的写入，happens-before 随后对同一个变量的读取。

结合程序内部的执行顺序，可以得到：

![](/images/Java-concurrency/IMG-20260707-000042.png)




因此，`data = 42` 的结果能够传递到读线程。这里真正起作用的不是读线程直接读取了写线程的局部数据，而是 Java 内存模型通过 volatile 读写建立了跨线程的可见关系。

happens-before 是判断并发代码是否具备可靠内存语义的重要工具。没有这类关系时，即使某次运行“看起来正常”，也不能证明所有线程都一定能够看到预期结果。

## 7. volatile 为什么不能解决 count++

`volatile` 保证单次读取能够看到较新的值，也保证单次写入能够按照规则发布，但它不能把多个步骤合并成一个原子操作。

例如：

```java
private volatile int count = 0;

public void increment() {
    count++;
}
```

`count++` 仍然包含读取、计算和写回：

![](/images/Java-concurrency/IMG-20260707-000043.png)




假设 Thread A 和 Thread B 都读取到 `count = 0`，随后分别计算出 `1` 并写回。即使每次读取和写入都遵守 volatile 的可见性规则，最终仍然可能只有一个 `1`。

![](/images/Java-concurrency/IMG-20260707-000044.png)




`volatile` 解决的是“是否看得到”和“以什么顺序看到”，不是“多个步骤能否被其他线程插入”。需要保护复合操作时，仍然要使用锁、CAS 或其他能够保证原子性的方案。

## 8. volatile 适合什么场景

`volatile` 最适合一个线程写、多个线程读，并且每次写入不依赖旧值的场景。

### 8.1 状态标记

```java
class Task {

    private volatile boolean stopped;

    public void stop() {
        stopped = true;
    }

    public void run() {
        while (!stopped) {
            doWork();
        }
    }

    private void doWork() {
        // business logic
    }
}
```

`stop()` 只是把状态直接设置为 `true`，不需要根据旧值计算新值，因此不涉及读取后再写回的复合操作。

### 8.2 配置发布

```java
class ConfigCenter {

    private volatile Config config = loadConfig();

    public Config getConfig() {
        return config;
    }

    public void reload() {
        config = loadConfig();
    }
}
```

写线程先构造完整的新配置对象，再一次性替换 `config` 引用。读线程读取到新引用后，也能看到 volatile 写之前已经完成的对象初始化结果。为了避免对象发布后又被并发修改，配置对象通常设计为不可变对象。

### 8.3 完成标记

```java
class ResultHolder {

    private Result result;
    private volatile boolean completed;

    public void complete(Result value) {
        result = value;
        completed = true;
    }

    public Result getResult() {
        if (!completed) {
            return null;
        }

        return result;
    }
}
```

写线程先保存结果，再写入 volatile 标记。读线程读取到 `completed == true` 后，能够看到之前写入的 `result`。

这些场景都有一个共同特点：volatile 变量本身只承担状态发布或引用替换，不需要保护多个线程围绕旧值进行竞争更新。

## 9. volatile 不能保证复杂业务状态一致

假设账户中有两个字段：

```java
class Account {

    private volatile int balance;
    private volatile int transactionCount;

    public void withdraw(int amount) {
        if (balance >= amount) {
            balance -= amount;
            transactionCount++;
        }
    }
}
```

即使两个字段都声明为 `volatile`，这段代码仍然不安全。余额检查、余额扣减和交易次数增加属于一个完整业务操作，多个线程可以在中间交错执行。

`volatile` 只能约束每个字段各自的读写，不能自动把多个字段组合成一个事务，也不能保证两个字段总是同时变化。只要业务正确性依赖多个操作共同完成，就需要更完整的同步边界。

## 10. volatile 与 synchronized 的区别

`volatile` 和 `synchronized` 都能建立可见性关系，但用途不同。

| 对比项 | volatile | synchronized |
|---|---|---|
| 是否互斥 | 否 | 是 |
| 是否会阻止其他线程进入代码区域 | 否 | 会 |
| 可见性 | 保证 | 保证 |
| 有序性 | 限制 volatile 前后的特定重排 | 同步区域具有进入和退出语义 |
| 原子性 | 只保证单次读写，不保护复合操作 | 可以保护整个临界区 |
| 适用场景 | 状态标记、引用发布、简单开关 | 多步骤操作、多个关联状态 |

`volatile` 更轻量，是因为它不建立线程级互斥；这也意味着它不能替代锁。选择时不能只看哪个关键字开销更小，而要先判断业务是否需要互斥。

## 11. 双重检查锁为什么需要 volatile

单例模式中的双重检查锁是 `volatile` 同时发挥可见性和有序性作用的经典场景：

```java
public class Singleton {

    private static volatile Singleton instance;

    private Singleton() {
    }

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }

        return instance;
    }
}
```

第一次检查避免每次调用都进入同步区域，第二次检查防止多个线程先后创建对象。`instance` 必须声明为 `volatile`，因为创建对象并赋值给引用并不是一个抽象上的单一步骤，可以粗略理解为：

![](/images/Java-concurrency/IMG-20260707-000045.png)




如果缺少内存顺序约束，其他线程可能先观察到非空引用，却还不能可靠地看到完整初始化结果。`volatile` 会限制这种不安全发布，并保证读取到 `instance` 的线程能够看到对象构造期间已经完成的写入。

这里不应理解为 JVM 必然机械地把三步交换成某个固定顺序，而应理解为：没有安全发布规则时，其他线程观察对象状态的结果缺乏保证；`volatile` 为引用发布建立了必要的 happens-before 关系。

## 12. 常见误解

### 12.1 volatile 会把变量锁住

不会。多个线程仍然可以同时读取和写入 volatile 变量，`volatile` 不建立临界区，也不会让某个线程独占变量。

### 12.2 volatile 能让所有操作变成原子操作

不会。它不能保护 `count++`、先判断再修改、同时更新多个字段等复合操作。

### 12.3 volatile 等于禁用 CPU Cache

不会。CPU 仍然使用 Cache，JVM 通过内存屏障、特殊指令和硬件一致性机制实现 volatile 语义。

### 12.4 volatile 保证读到绝对最新的现实时间值

更准确地说，volatile 读必须遵守 Java 内存模型的可见性规则。并发程序中不存在一个脱离同步规则、所有线程随时共享的“绝对瞬间”。程序应依据 happens-before 判断结果是否可靠，而不是依赖现实时间上的先后猜测。

### 12.5 声明了 volatile 就是线程安全

线程安全取决于完整业务操作。一个字段声明为 volatile，只能保证围绕这个字段的特定内存语义，不能自动保证整个类或整个方法安全。

## 13. 如何判断是否适合使用 volatile

可以依次判断三个问题：

1. 写入是否只是直接设置新值，而不是根据旧值计算新值；
2. 是否不需要多个线程互斥执行一段代码；
3. 是否只需要发布状态、对象引用或完成标记。

如果答案都是肯定的，`volatile` 通常比较合适。如果操作包含“读取—判断—修改”，或者需要同时维护多个字段之间的一致性，就不能只依靠 `volatile`。

例如：

```java
running = false;
config = newConfig;
completed = true;
```

这些操作通常可以使用 `volatile`。

而下面这些操作通常不行：

```java
count++;
balance -= amount;

if (stock > 0) {
    stock--;
}
```

判断标准不是代码有几行，而是业务操作是否依赖旧状态，以及多个线程是否可以在步骤之间交错执行。

## 本章总结

`volatile` 为一个变量建立了可见性和有序性规则。一个线程写入 volatile 变量后，随后读取同一变量的线程能够观察到这次写入；volatile 写之前的普通写，也能够通过 happens-before 关系对读线程可见。

本章的核心结论包括：

- 线程之间的数据可见性不能只用“是否写回主内存”解释；
- `volatile` 不会关闭 Cache，也不会让所有访问都直接经过主内存；
- JVM 通过内存屏障、特殊指令和硬件一致性机制实现 volatile 语义；
- volatile 写与随后对同一变量的 volatile 读之间存在 happens-before 关系；
- `volatile` 能限制特定的指令重排；
- `volatile` 不提供互斥，不能保护 `count++` 等复合操作；
- 状态标记、配置发布和完成通知是常见使用场景；
- 多字段一致性和读取后修改仍然需要锁、CAS 或其他同步方案；
- 双重检查锁中的实例引用必须安全发布；
- 判断是否适合使用 `volatile`，关键在于操作是否依赖旧状态。

原子性、可见性和有序性是并发程序中三个不同的问题。`synchronized`、CAS 和 `volatile` 分别从不同角度处理这些问题，后续可以继续把它们统一到 Java 内存模型中理解。
