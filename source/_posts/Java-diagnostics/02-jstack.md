---
categories:
     - java-diagnostics
date: 2026-07-13
abbrlink: 01
tags:
     - JVM
     - jstack
     - Thread Dump
     - 线程诊断
     - AIOps
title: jstack 多份 Thread Dump 聚类分析：如何从线程快照识别持续性故障
---

Java 程序出现 CPU 飙高、请求卡住、线程池耗尽或大量锁等待时，问题最终往往表现为：某些线程正在长时间执行、等待某个资源，或者阻塞了其他线程。`jstack` 的作用，就是把 JVM 中所有线程在某一时刻的状态和调用栈记录下来，帮助我们还原线程当时正在做什么。

不过，一份 Thread Dump 只是一个瞬间的快照。真正有效的分析不能只看某个线程是 `RUNNABLE`、`WAITING` 还是 `BLOCKED`，而要继续结合调用栈、锁关系、线程角色和多次快照中的变化，判断线程是在正常等待，还是已经形成持续性瓶颈。

## 1、jstack 观察的到底是什么

一个 JVM 进程内部通常存在许多线程，包括：

* 处理 HTTP 请求的业务线程；
* 线程池中的工作线程；
* 数据库连接池维护线程；
* GC、JIT 编译等 JVM 内部线程；
* 用户自己创建的线程。

`jstack` 获取的是这些线程在某一时刻的执行快照，也就是 Thread Dump。

```mermaid
graph LR
    A["JVM 进程"] --> B["全部线程"]
    B --> C["线程状态"]
    C --> D["方法调用栈"]
    D --> E["等待与持锁关系"]
```

因此，`jstack` 主要回答四个问题：

1. JVM 中有哪些线程；
2. 每个线程当前是什么状态；
3. 每个线程执行到了什么位置；
4. 线程正在等待什么资源，或者持有哪些锁。

它适合排查：

* 程序假死；
* Java 层死锁；
* CPU 使用率过高；
* 大量线程阻塞；
* 线程池工作线程被占满；
* 数据库连接池耗尽；
* 远程接口调用长时间不返回；
* 线程数量持续增长。

它不负责直接分析堆内存、对象占用和 GC 原因，这些问题需要结合 `jstat`、GC 日志、堆转储等工具。

## 2、如何获取一份 Thread Dump

首先找到目标 JVM 的进程号：

```bash
jps -l
```

例如：

```text
21836 com.example.Application
```

然后执行：

```bash
jstack 21836
```

线上排查通常保存到文件中：

```bash
jstack 21836 > thread-dump.txt
```

如果希望获得更多关于 `java.util.concurrent` 同步器的信息，可以使用：

```bash
jstack -l 21836 > thread-dump.txt
```

现代 JDK 中也可以使用：

```bash
jcmd 21836 Thread.print
```

带扩展锁信息时：

```bash
jcmd 21836 Thread.print -l
```

实际分析时不应只抓一份。更常见的做法是连续抓取多次：

```bash
for i in {1..5}; do
    ts=$(date +%Y%m%d-%H%M%S)
    jstack -l 21836 > "thread-$ts.txt"
    sleep 5
done
```

连续抓取的原因是：一份 Dump 只能说明线程当时碰巧执行到了哪里，多份 Dump 才能观察线程是否持续停留、调用栈是否发生变化，以及同类线程是否不断增加。

## 3、如何读懂一条线程记录

一条典型线程记录可能是：

```text
"http-nio-8080-exec-8" #28 daemon prio=5 os_prio=0
   tid=0x00007f123400 nid=0x5596 runnable

   java.lang.Thread.State: RUNNABLE

    at java.net.SocketInputStream.socketRead0(Native Method)
    at com.example.order.RemoteOrderClient.query(RemoteOrderClient.java:68)
    at com.example.order.OrderService.create(OrderService.java:42)
```

阅读时可以分成三层。

### 3.1 线程是谁

```text
"http-nio-8080-exec-8"
```

线程名称通常能说明它属于哪个组件。

| 线程名称                               | 常见含义              |
| ---------------------------------- | ----------------- |
| `http-nio-8080-exec-*`             | Tomcat HTTP 请求线程  |
| `pool-1-thread-*`                  | 普通线程池工作线程         |
| `ForkJoinPool.commonPool-worker-*` | ForkJoinPool 工作线程 |
| `HikariPool-*-housekeeper`         | HikariCP 连接池维护线程  |
| `GC Thread#*`                      | GC 工作线程           |
| `C2 CompilerThread*`               | JIT 编译线程          |

分析时，应先判断它是业务线程、线程池工作线程，还是 JVM 内部线程。

### 3.2 线程是什么状态

```text
java.lang.Thread.State: RUNNABLE
```

状态说明线程当前处于哪一类执行阶段，但状态本身不是结论。

### 3.3 线程为什么处于这个状态

调用栈顶部表示线程当前最接近的执行位置：

```text
SocketInputStream.socketRead0
```

继续向下可以找到触发该操作的业务方法：

```text
RemoteOrderClient.query
OrderService.create
```

因此，这条线程记录表示：

> 一个 Tomcat 请求线程正在处理订单创建请求，当前停在 `RemoteOrderClient.query()` 发起的网络读取中。

分析 Thread Dump 的核心不是只问：

> 线程是什么状态？

而是继续问：

> 它为什么处于这个状态，当前停在哪一段调用链中？

## 4、六种 Java 线程状态应该如何理解

Java 定义了六种线程状态：

| 状态              | 主要含义                       |
| --------------- | -------------------------- |
| `NEW`           | 已创建线程对象，但还未调用 `start()`    |
| `RUNNABLE`      | 可运行、正在运行，或处于某些底层 I/O 操作    |
| `BLOCKED`       | 等待进入 `synchronized` 保护的临界区 |
| `WAITING`       | 无超时时间地等待某个条件               |
| `TIMED_WAITING` | 带最长等待时间地等待                 |
| `TERMINATED`    | `run()` 已执行结束              |

在实际 Thread Dump 中，最常见的是中间四种。

### 4.1 `RUNNABLE` 不一定正在消耗 CPU

例如：

```text
java.lang.Thread.State: RUNNABLE

at java.net.SocketInputStream.socketRead0(Native Method)
```

线程虽然显示为 `RUNNABLE`，但它可能正在等待底层网络数据，并不一定持续占用 CPU。

因此，`RUNNABLE` 可能表示：

* 正在 CPU 上执行计算；
* 已具备运行条件，等待操作系统调度；
* 正在执行 Native Method；
* 正在等待某些底层网络或文件 I/O。

是否高 CPU，不能只根据 `RUNNABLE` 判断。

### 4.2 `BLOCKED` 专门表示等待 Monitor

例如：

```text
java.lang.Thread.State: BLOCKED (on object monitor)

- waiting to lock <0x000000076b21a8f0>
```

它表示线程希望进入某个 `synchronized` 临界区，但对象 Monitor 已被其他线程持有。

`BLOCKED` 不是“线程卡住”的泛称，而是专门表示等待 Monitor。

### 4.3 `WAITING` 表示没有明确超时时间

常见来源包括：

```java
object.wait();
thread.join();
countDownLatch.await();
blockingQueue.take();
```

线程池中的空闲工作线程也经常处于：

```text
WAITING (parking)
```

因为它们正在任务队列上等待新任务。

### 4.4 `TIMED_WAITING` 表示带超时等待

常见来源包括：

```java
Thread.sleep(5000);
object.wait(5000);
thread.join(5000);
LockSupport.parkNanos(...);
```

它与 `WAITING` 的区别是：即使没有其他线程主动唤醒，超时时间到达后也可以返回。

### 4.5 `NEW` 和 `TERMINATED` 通常不常见

`NEW` 线程还未真正启动，`TERMINATED` 线程已经执行结束，因此在常规 Thread Dump 中通常不会大量出现。

## 5、为什么等锁有时是 BLOCKED，有时是 WAITING

“等待锁”并不一定都表现为 `BLOCKED`，这取决于锁的实现方式。

### 5.1 等待 synchronized 通常是 BLOCKED

```java
synchronized (lock) {
    process();
}
```

如果其他线程已经持有 `lock`，当前线程会等待 JVM Monitor：

```text
java.lang.Thread.State: BLOCKED

- waiting to lock <0x1000>
```

### 5.2 等待 ReentrantLock 通常是 WAITING

```java
lock.lock();
try {
    process();
} finally {
    lock.unlock();
}
```

`ReentrantLock` 基于 AQS 管理竞争线程。线程获取失败后，通常通过 `LockSupport.park()` 挂起：

```text
java.lang.Thread.State: WAITING (parking)

at jdk.internal.misc.Unsafe.park(Native Method)
at java.util.concurrent.locks.LockSupport.park(...)
at java.util.concurrent.locks.AbstractQueuedSynchronizer.acquire(...)
at java.util.concurrent.locks.ReentrantLock.lock(...)
```

因此：

| 等待对象             | 常见等待机制               | 常见状态      |
| ---------------- | -------------------- | --------- |
| `synchronized`   | JVM Monitor          | `BLOCKED` |
| `ReentrantLock`  | AQS + `park()`       | `WAITING` |
| 线程池任务队列          | Condition + `park()` | `WAITING` |
| `CountDownLatch` | AQS + `park()`       | `WAITING` |

看到 `WAITING (parking)` 时，不能直接判断线程在等待什么，必须继续看调用栈。

## 6、如何理解 Thread Dump 中的锁标记

Thread Dump 中常见的锁信息包括：

### 6.1 `waiting to lock`

```text
- waiting to lock <0x1000>
```

表示线程正在等待获取对应的 Monitor。

### 6.2 `locked`

```text
- locked <0x1000>
```

表示线程当前已经持有对应的 Monitor。

如果出现：

```text
线程 A：- locked <0x1000>
线程 B：- waiting to lock <0x1000>
```

就可以确定线程 B 正在等待线程 A 释放锁。

### 6.3 `parking to wait for`

```text
- parking to wait for <0x2000>
```

表示线程通过 `LockSupport.park()` 等待某个同步器对象。

它可能对应：

* `ReentrantLock`；
* `Condition`；
* `CountDownLatch`；
* 线程池任务队列；
* `CompletableFuture`；
* 其他 AQS 同步器。

对象地址并不能直接说明线程究竟在等待哪种业务资源，仍然要结合调用栈判断。

### 6.4 `waiting on`

```text
- waiting on <0x3000>
```

常见于线程执行：

```java
object.wait();
```

线程已经释放对应 Monitor，并等待 `notify()`、`notifyAll()` 或中断。

### 6.5 `waiting to re-lock in wait()`

```text
- waiting to re-lock in wait() <0x3000>
```

表示线程已经从 `wait()` 中被唤醒，但必须重新获取 Monitor，才能继续执行同步代码块。

这些标记帮助我们建立线程与资源之间的关系，但不能替代调用栈分析。

## 7、如何识别死锁和普通锁等待

普通锁等待中，持锁线程最终会释放锁：

```mermaid
graph LR
    A["线程 A 持锁"] --> B["线程 B 等待"]
    B --> C["线程 A 释放"]
    C --> D["线程 B 继续"]
```

死锁则形成循环等待：

```text
线程 A：持有 lock1，等待 lock2
线程 B：持有 lock2，等待 lock1
```

此时两个线程都无法继续。

`jstack` 通常会在输出末尾给出：

```text
Found one Java-level deadlock:
```

分析时仍应验证完整关系：

1. 找到线程正在等待的锁；
2. 找到持有该锁的线程；
3. 继续查看持有者又在等待什么；
4. 判断等待链是否回到起点。

死锁的关键不是存在锁等待，而是存在循环等待。

需要注意的是，现实中的系统假死并不一定存在 Java 层死锁。例如：

```text
所有 Tomcat 线程等待数据库连接
所有数据库连接又被慢事务长期占用
```

系统已经无法处理请求，但 Thread Dump 末尾未必会出现死锁提示。

## 8、CPU 飙高时如何结合 top 和 jstack

`jstack` 不能直接告诉我们哪个线程当前最耗 CPU，因此需要先用操作系统工具找到高 CPU 线程。

假设 JVM PID 是 `21836`：

```bash
top -Hp 21836
```

可能看到：

```text
PID      %CPU
21910    85.3
21911     2.1
```

这里的 `21910` 是操作系统线程 ID，通常以十进制显示。

Thread Dump 中对应的是：

```text
nid=0x5596
```

因此需要先转换：

```bash
printf "%x\n" 21910
```

得到：

```text
5596
```

然后在 Dump 中搜索：

```text
nid=0x5596
```

完整过程是：

```mermaid
graph LR
    A["top 找高 CPU 线程"] --> B["线程 ID 转十六进制"]
    B --> C["匹配 jstack nid"]
    C --> D["查看线程调用栈"]
    D --> E["连续抓取验证"]
```

需要区分：

| 字段    | 含义          |
| ----- | ----------- |
| `tid` | JVM 内部线程标识  |
| `nid` | 操作系统原生线程 ID |

与 `top -Hp` 对应的是 `nid`。

### 8.1 为什么不能只抓一次 Dump

第一次看到：

```text
at com.example.CalculateService.calculate(CalculateService.java:42)
```

只能说明抓取快照时线程恰好执行到了第 42 行。

如果连续三份 Dump 中，同一个高 CPU `nid` 都停在相同或相近位置：

```text
Dump 1：calculate:42
Dump 2：calculate:42
Dump 3：calculate:43
```

并且 CPU 一直很高，才更可能存在：

* 死循环；
* 自旋；
* 大量重复计算；
* 执行时间异常长的算法。

部分 JDK 的线程头还会显示累计 CPU 时间：

```text
cpu=125.30ms elapsed=3600.12s
```

其中：

* `cpu` 是线程累计使用的 CPU 时间；
* `elapsed` 是线程存活时间。

单次 `cpu` 数值很大不代表当前仍然高 CPU。更有意义的是比较两份 Dump 中 `cpu` 的增量。

如果两次 Dump 间隔 5 秒，而某线程的 `cpu` 增加接近 5 秒，说明它在这段时间内几乎一直占用一个 CPU 核心。

### 8.2 先判断是业务线程还是 JVM 内部线程

如果高 CPU 线程是：

```text
"http-nio-8080-exec-8"
```

应继续分析业务调用栈。

如果是：

```text
"GC Thread#2"
"G1 Conc#0"
```

则更可能与垃圾回收压力有关，需要切换到 `jstat`、GC 日志和堆内存分析。

如果是：

```text
"C2 CompilerThread0"
```

则可能是 JIT 编译活动，而不一定是业务死循环。

## 9、如何分析大量 BLOCKED、WAITING 和线程池耗尽

一份 Thread Dump 中最值得关注的通常不是某条线程偶然出现了什么，而是大量线程是否集中表现出相同模式。

### 9.1 大量 BLOCKED：先找热点锁，再看持锁线程

如果许多线程都显示：

```text
- waiting to lock <0x1000>
```

说明 `<0x1000>` 可能是热点 Monitor。

然后搜索：

```text
- locked <0x1000>
```

找到当前持锁线程。

真正需要重点分析的通常不是几十个等待线程，而是持锁线程为什么迟迟没有释放锁。

例如：

```text
"worker-A"
java.lang.Thread.State: RUNNABLE

at java.net.SocketInputStream.socketRead0(Native Method)
at com.example.RemoteService.call(RemoteService.java:58)
at com.example.OrderService.process(OrderService.java:42)
- locked <0x1000>
```

这说明线程在持锁期间调用了远程接口。网络响应越慢，锁持有时间越长，其他线程被阻塞的时间也越长。

问题不一定是锁本身，而可能是把不可控的 I/O 放进了临界区。

### 9.2 大量 WAITING 不一定异常

线程池空闲时，工作线程可能全部停在：

```text
LinkedBlockingQueue.take
ThreadPoolExecutor.getTask
ThreadPoolExecutor.runWorker
```

这通常说明线程池正在等待任务，是正常状态。

但如果系统外部请求很多，而对应工作线程仍全部停在 `getTask()`，则可能意味着：

* 请求没有被提交到这个线程池；
* 提交逻辑被上游阻塞；
* 实际处理请求的是另一个线程池；
* 任务被拒绝或提前失败。

因此，线程状态必须结合当前业务负载解释。

### 9.3 线程池工作线程全部忙碌

假设线程池只有四个线程：

```text
thread-1：数据库查询
thread-2：数据库查询
thread-3：远程接口
thread-4：远程接口
```

此时新任务只能进入队列等待。

分析重点是：

> 所有工作线程被什么操作占住了？

如果全部卡在：

```text
socketRead0
```

更可能是下游接口慢。

如果全部卡在：

```text
executeQuery
```

更可能是数据库响应慢。

如果全部卡在：

```text
ReentrantLock.lock
```

更可能是本地锁竞争。

不能看到线程池满就直接增加线程数。增加线程可能让更多请求同时打向已经变慢的下游，使问题进一步恶化。

线程池任务堆积的本质是：

```text
任务进入速度 > 任务完成速度
```

这可能由两侧造成：

| 情况       | 可能原因             |
| -------- | ---------------- |
| 上游突然加速   | 流量暴增、批量任务集中提交    |
| 下游突然变慢   | 数据库、远程服务或锁等待时间增加 |
| 本地处理变慢   | CPU 计算、长事务、同步竞争  |
| 任务未进入线程池 | 提交链路异常或使用了错误线程池  |

`jstack` 主要帮助判断工作线程正在做什么；任务提交速率和队列长度还需要结合监控数据。

## 10、如何分析数据库连接池耗尽

如果大量线程停在：

```text
HikariPool.getConnection
```

能够确认的是：

> 这些线程正在等待数据库连接。

但这不等于已经确认“连接池配置太小”。

连接池耗尽常见的因果链是：

```mermaid
graph LR
    A["SQL 或事务变慢"] --> B["连接长期占用"]
    B --> C["可用连接耗尽"]
    C --> D["线程等待连接"]
    D --> E["请求持续堆积"]
```

可能原因包括：

* SQL 执行时间过长；
* 数据库网络响应慢；
* 事务范围过大；
* 连接拿到后又执行远程调用；
* 连接没有正确关闭；
* 突发请求超过连接池容量。

因此，看到大量线程等待 `getConnection()` 后，应继续分析那些已经拿到连接的线程正在做什么。

例如另一批线程集中停在：

```text
PreparedStatement.executeQuery
SocketInputStream.socketRead0
```

可能说明数据库查询或数据库网络响应较慢。

如果线程拿到连接并开启事务后，又执行远程调用，则 SQL 本身可能不慢，但连接仍然会被业务代码长时间持有。

直接增大连接池可能只是让更多请求同时打向数据库，并不能解决慢 SQL或长事务问题。

## 11、多份 Thread Dump 为什么需要聚类分析

当一份 Dump 中存在几百条线程时，逐条阅读效率很低。更有效的方法是按照相同或相似调用栈分组。

例如：

```text
40 个线程停在 HikariPool.getConnection
30 个线程停在 SocketInputStream.socketRead0
20 个线程停在 ThreadPoolExecutor.getTask
10 个线程等待同一个 Monitor
```

这类分组能够快速说明系统的主要线程分布。

但多份 Dump 分析还要进一步区分两个概念。

### 11.1 聚类持续存在

假设三份 Dump 中都有线程停在 `socketRead0()`：

```text
Dump 1：线程 A、B、C
Dump 2：线程 D、E、F
Dump 3：线程 G、H、I
```

说明远程读取这种执行模式持续存在，但旧线程可能仍能完成，只是新线程不断进入。

### 11.2 同一批线程持续停滞

另一种情况是：

```text
Dump 1：线程 A、B、C
Dump 2：线程 A、B、C
Dump 3：线程 A、B、C
```

如果这些线程的调用栈位置也没有变化，则说明同一批线程持续停留，没有观察到明显推进。

因此，多份 Dump 分析至少要比较：

| 维度     | 作用            |
| ------ | ------------- |
| 线程角色   | 判断是否为同类工作线程   |
| 线程状态   | 判断执行阶段是否相同    |
| 调用栈方法  | 判断是否位于同一执行路径  |
| 栈顶位置   | 判断线程是否发生可见推进  |
| `nid`  | 判断是否为同一个原生线程  |
| 聚类数量   | 判断有多少线程集中在该位置 |
| 同类线程占比 | 判断线程池是否大面积被占用 |
| 数量趋势   | 判断线程是否不断积压    |
| 成员稳定性  | 判断是否为同一批线程    |

### 11.3 调用栈不能只按栈顶聚类

大量不同操作都可能停在：

```text
SocketInputStream.socketRead0
```

其中可能包括：

* HTTP 远程调用；
* 数据库通信；
* Redis 请求；
* 消息队列消费。

如果只按栈顶聚类，会把完全不同的业务操作合并在一起。

更合理的是同时参考：

```text
底层阻塞位置
+
第一条业务调用位置
```

例如：

```text
SocketInputStream.socketRead0
+
RemoteOrderClient.query
```

才可以描述为：

> 一组请求线程正在 `RemoteOrderClient.query()` 发起的网络读取中。

### 11.4 多份 Dump 能确认什么

假设 40 个 Tomcat 请求线程中：

| 快照     | 停在远程调用的线程数 |
| ------ | ---------: |
| Dump 1 |         25 |
| Dump 2 |         29 |
| Dump 3 |         33 |
| Dump 4 |         36 |

并且其中 21 个 `nid` 在四份 Dump 中保持相同调用栈位置。

能够确认的是：

> 大量 Tomcat 请求线程持续被同一个远程读取调用占用，其中部分线程在多个采样周期内没有观察到调用栈推进。

但不能仅凭 Thread Dump 确认：

> 下游服务自身一定发生了性能故障。

因为网络读取不返回还可能由网络链路、代理、客户端连接或超时配置造成。

Thread Dump 能观察线程行为，但不能直接观察整个远程调用链上的根因。

## 12、jstack 的使用边界

`jstack` 擅长回答：

* 线程是谁；
* 线程是什么状态；
* 线程停在哪里；
* 线程正在等待什么；
* 哪个线程持有锁；
* 是否存在 Java 层死锁；
* 哪些线程表现出相同模式；
* 同一线程在多份 Dump 中是否持续停留。

它不能单独回答：

* 线程池队列到底有多长；
* 每秒提交了多少任务；
* 接口具体耗时是多少；
* 哪条 SQL 最慢；
* 数据库连接池当前活动数是多少；
* 哪些对象占用了堆内存；
* GC 为什么频繁；
* 网络链路的哪一段发生延迟。

因此，实际故障诊断通常需要组合：

| 工具或数据    | 主要作用           |
| -------- | -------------- |
| `jstack` | 线程状态、调用栈和锁关系   |
| `top`    | 进程和线程 CPU 使用率  |
| `jstat`  | GC 次数、时间和内存区变化 |
| GC 日志    | GC 事件与停顿原因     |
| 应用日志     | 请求、异常和业务上下文    |
| 监控指标     | 吞吐、延迟、队列和连接池状态 |
| 数据库监控    | SQL、事务和连接使用情况  |

`jstack` 不是一个直接输出根因的工具。它提供的是线程层面的证据，需要结合系统状态还原完整因果链。

## 总结

`jstack` 从线程视角观察 JVM：线程名称帮助判断它属于哪个组件，线程状态说明它处于哪种执行阶段，调用栈解释它为什么进入这个状态，锁标记则建立线程和资源之间的等待关系。

单条线程记录只能说明某个瞬间发生了什么，因此不能看到 `RUNNABLE` 就判断高 CPU，也不能看到 `WAITING` 就判断线程异常。真正有效的分析需要从调用栈出发，判断线程是在正常等待任务、等待网络、竞争锁，还是长期停留在某段业务代码。

当大量线程出现相同模式时，应从群体关系继续分析：大量 `BLOCKED` 要找热点锁和持锁线程，大量工作线程停在 I/O 要判断下游是否变慢，大量线程等待连接要继续查找长期占用连接的线程。CPU 问题则需要先通过操作系统线程 ID 找到对应 `nid`，再结合多份 Dump 验证调用栈是否持续不变。

多份 Thread Dump 最终解决的是时间维度问题：它不仅观察某种调用栈是否反复出现，还要区分是否为同一批线程持续停滞。只有把线程身份、调用栈、资源关系和时间变化串联起来，Thread Dump 才能从一份静态文本变成可靠的线程诊断证据。
