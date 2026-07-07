---
title: 'java-basics(10) | 并发编程：线程、锁、线程池与 CompletableFuture'
date: 2026-05-10
tags:
  - Java
  - 并发
  - 多线程
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

并发编程是 Java 的核心竞争力之一——从最底层的 `Thread`，到 `synchronized`，到 `java.util.concurrent` 包的高级工具，再到 `CompletableFuture` 的异步编排，Java 提供了从低级到高级的全套并发方案。这篇文章按照"从手动到自动"的思路，把并发编程的核心知识串起来。

<!-- more -->

## 1. 线程基础

### 1.1 什么是线程？

**进程**是操作系统分配资源的最小单位，每个进程有自己独立的内存空间。你电脑上的每个程序（浏览器、微信、IDE）都是一个进程。

**线程**是 CPU 调度的最小单位，一个进程可以包含多个线程，它们**共享同一块内存**，但各自有独立的执行流。

```
进程 A（浏览器）          进程 B（IDE）
├── 线程 1（渲染页面）     ├── 线程 1（编辑器 UI）
├── 线程 2（网络请求）     ├── 线程 2（代码编译）
└── 线程 3（执行 JS）      └── 线程 3（文件索引）
    ↑ 共享同一块内存           ↑ 共享同一块内存
    
进程之间内存隔离，互不影响
```

**为什么需要多线程？** 一个线程同一时刻只能做一件事。如果一个 Web 服务器用单线程处理请求，一个用户的请求还没处理完，其他用户就得排队等着。多线程可以让多个任务并发执行，提高吞吐量。

**进程 vs 线程：**

| | 进程 | 线程 |
|---|---|---|
| 内存 | 独立，互不影响 | 共享同一进程的内存 |
| 创建开销 | 大（分配独立内存空间） | 小（只需要栈和寄存器） |
| 通信方式 | 管道、Socket、共享内存等（复杂） | 直接读写共享变量（简单但要注意线程安全） |
| 一个崩溃 | 不影响其他进程 | 可能导致整个进程崩溃 |
| 典型场景 | 隔离性要求高（如 Chrome 每个标签页一个进程） | 同一程序内的并发任务 |

**什么时候用哪个？**

- **用多线程**：同一个程序内需要并发执行多个任务（Web 服务器处理多个请求、后台定时任务、异步 I/O），Java 后端开发 90% 的并发场景都是多线程
- **用多进程**：需要强隔离（一个任务崩溃不能影响其他）、需要利用多台机器（分布式系统）、不同语言的程序之间协作

Java 后端开发的日常基本都是和线程打交道，进程级别的并发更多在运维和架构层面。

### 1.2 创建线程的三种方式

```java
// 方式 1：继承 Thread
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println(Thread.currentThread().getName() + " running");
    }
}
new MyThread().start();

// 方式 2：实现 Runnable（推荐，不占用继承位）
Runnable task = () -> System.out.println(Thread.currentThread().getName() + " running");
new Thread(task).start();

// 方式 3：实现 Callable（可以有返回值和抛异常）
Callable<Integer> callable = () -> {
    Thread.sleep(1000);
    return 42;
};
// 用 FutureTask 包装 Callable，FutureTask 实现了 Runnable，才能提交给 Thread
FutureTask<Integer> futureTask = new FutureTask<>(callable);
new Thread(futureTask).start();
int result = futureTask.get();  // 阻塞等待结果，返回 42
```

实际开发中不会直接 new Thread，而是用线程池。但先理解底层机制。

| | Thread | Runnable | Callable |
|---|---|---|---|
| 类型 | 类（继承） | 接口（实现） | 接口（实现） |
| 有返回值 | ❌ | ❌ | ✅ |
| 能抛受检异常 | ❌ | ❌ | ✅ |
| 占用继承位 | ✅（不推荐） | ❌ | ❌ |
| 实际使用 | 很少 | 简单任务 | 需要结果的任务 |

### 1.3 线程的生命周期

Java 线程有 6 种状态，定义在 `Thread.State` 枚举中：

| 状态 | 含义 | 怎么进入 | 怎么离开 |
|------|------|---------|---------|
| `NEW` | 线程已创建，还没启动 | `new Thread()` | 调用 `start()` |
| `RUNNABLE` | 就绪或正在运行（Java 不区分这两者） | `start()` / 被唤醒 / 获得锁 | 执行完毕 / 等待 / 阻塞 |
| `BLOCKED` | 等待获取 `synchronized` 锁 | 另一个线程持有锁 | 获得锁后回到 RUNNABLE |
| `WAITING` | 无限期等待，直到被唤醒 | `wait()` / `join()` / `LockSupport.park()` | `notify()` / `notifyAll()` / 目标线程结束 |
| `TIMED_WAITING` | 有限期等待，到时间自动醒 | `sleep(ms)` / `wait(ms)` / `join(ms)` | 时间到 / 被提前唤醒 |
| `TERMINATED` | 线程执行完毕或异常退出 | `run()` 方法 return 或抛异常 | 终态，不可逆 |

```
NEW（新建）
  │  start()
  ▼
RUNNABLE（就绪/运行中）
  │          │          │
  │ wait()   │ sleep()  │ 等待锁
  ▼          ▼          ▼
WAITING   TIMED_WAITING  BLOCKED
  │          │          │
  │ notify() │ 时间到    │ 获得锁
  ▼          ▼          ▼
RUNNABLE ←──────────────┘
  │
  │  run() 执行完毕
  ▼
TERMINATED（终止）
```

```java
Thread t = new Thread(() -> {
    try { Thread.sleep(1000); } catch (InterruptedException e) {}
});
t.getState();    // NEW —— 创建了但还没启动
t.start();
t.getState();    // RUNNABLE —— 正在运行或等待 CPU 调度
// Thread.sleep 期间
t.getState();    // TIMED_WAITING —— 在 sleep，到时间自动醒
// sleep 结束后 run() 执行完毕
t.getState();    // TERMINATED —— 已结束，不能再 start()
// t.start();    // 再次调用抛 IllegalThreadStateException，线程不能重复启动
```

两个容易混淆的点：
- **BLOCKED vs WAITING**：BLOCKED 是想拿锁但拿不到，被动等；WAITING 是主动调用 `wait()` 放弃锁并等待通知
- **RUNNABLE 包含两种情况**：线程可能正在 CPU 上执行，也可能在就绪队列里等 CPU 调度，Java 不区分这两者

### 1.4 常用方法

```java
// 休眠：当前线程暂停指定时间
Thread.sleep(1000);  // 毫秒

// 让出 CPU：提示调度器可以切换线程（不保证）
Thread.yield();

// 等待另一个线程结束
Thread t = new Thread(() -> doWork());
t.start();
t.join();        // 阻塞当前线程，直到 t 执行完毕
t.join(5000);    // 最多等 5 秒

// 中断机制
t.interrupt();              // 设置中断标志
Thread.currentThread().isInterrupted();  // 检查中断标志

// 在线程内响应中断
while (!Thread.currentThread().isInterrupted()) {
    try {
        doWork();
        Thread.sleep(100);
    } catch (InterruptedException e) {
        // sleep/wait/join 被中断时抛此异常，中断标志会被清除
        Thread.currentThread().interrupt();  // 重新设置中断标志
        break;
    }
}
```

### 1.5 守护线程

```java
Thread daemon = new Thread(() -> {
    while (true) {
        // 后台任务
    }
});
daemon.setDaemon(true);  // 必须在 start() 之前设置
daemon.start();
// 所有非守护线程结束时，JVM 退出，守护线程被强制终止
// 典型用途：GC 线程、心跳检测
```

## 2. 线程安全问题

### 2.1 什么是线程安全问题？

多个线程同时读写共享数据时，结果可能不符合预期：

```java
public class Counter {
    private int count = 0;

    public void increment() {
        count++;  // 不是原子操作！实际是 read → add → write 三步
    }

    public int getCount() { return count; }
}

Counter counter = new Counter();

// 启动 1000 个线程，每个线程 +1
List<Thread> threads = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
    Thread t = new Thread(counter::increment);
    threads.add(t);
    t.start();
}
for (Thread t : threads) t.join();

System.out.println(counter.getCount());  // 大概率不是 1000
```

### 2.2 三大问题

| 问题 | 含义 | 例子 |
|------|------|------|
| 原子性 | 操作不可中断 | `count++` 被其他线程穿插 |
| 可见性 | 一个线程的修改对其他线程可见 | 线程 A 改了值，线程 B 看到的还是旧值 |
| 有序性 | 指令执行顺序符合预期 | JVM/CPU 可能重排序指令 |

## 3. synchronized

### 3.1 基本用法

`synchronized` 是 Java 最基础的锁机制，保证同一时刻只有一个线程执行被保护的代码：

```java
public class Counter {
    private int count = 0;

    // 方式 1：修饰实例方法，锁对象是 this
    public synchronized void increment() {
        count++;
    }

    // 方式 2：修饰静态方法，锁对象是 Class 对象
    public static synchronized void staticMethod() { ... }

    // 方式 3：同步代码块，手动指定锁对象（更灵活）
    private final Object lock = new Object();
    public void increment2() {
        synchronized (lock) {
            count++;
        }
    }
}
```

### 3.2 锁的本质

每个 Java 对象都有一个内置的**监视器锁（Monitor）**。`synchronized` 的工作方式：

```
线程 A 进入 synchronized 块
  → 尝试获取对象的 Monitor 锁
  → 成功 → 执行代码 → 释放锁
  → 失败 → 进入 BLOCKED 状态，等待锁释放
```

### 3.3 wait / notify：线程间通信

`synchronized` 解决了"互斥"问题，但有时线程之间还需要**协作**——一个线程等待某个条件满足，另一个线程满足条件后通知它。这就是 `wait()` 和 `notify()` 的作用。

**三个方法**（都定义在 Object 类上，必须在 `synchronized` 块内调用）：

| 方法 | 作用 |
|------|------|
| `wait()` | 释放锁，当前线程进入 WAITING 状态，直到被唤醒 |
| `notify()` | 随机唤醒一个在此对象上 `wait()` 的线程 |
| `notifyAll()` | 唤醒所有在此对象上 `wait()` 的线程 |

**为什么不能省略 notify？** 因为 `wait()` 不会自己醒来，没有通知就永远卡死：

```java
// 线程 A
synchronized (lock) {
    while (!条件满足) {
        lock.wait();    // 释放锁，进入 WAITING，永远不会自己醒
    }
    // 条件满足，继续执行
}

// 线程 B
synchronized (lock) {
    // 做一些事，让条件满足
    lock.notifyAll();   // 不写这行，线程 A 永远不会醒来
}
```

**notify vs notifyAll：**

```java
// 假设 3 个线程都在 wait()：生产者 P1、P2，消费者 C1

notify();      // 随机唤醒 1 个，可能唤醒错的角色
notifyAll();   // 唤醒所有，每个线程自己重新判断条件
```

`notify()` 的风险：

```
场景：队列满了，P1 和 P2 在 wait()，C1 也在 wait()
C1 被唤醒 → 取走一条消息 → 调用 notify()
  → 如果唤醒了 P1 → ✅ 生产者可以继续放消息
  → 如果唤醒了 C1（另一个消费者）→ ❌ 队列空了，又 wait() → 没人通知生产者 → 死锁
```

所以**有多种角色等待时必须用 `notifyAll()`**，只有一种角色时 `notify()` 可以用。拿不准就用 `notifyAll()`。

**为什么 wait 要配 while 而不是 if？**

```java
// ❌ 错误：用 if
synchronized (lock) {
    if (queue.isEmpty()) {
        lock.wait();   // 被 notifyAll 唤醒后直接往下走
    }
    queue.poll();      // 可能队列还是空的！因为其他线程可能先抢到锁把数据取走了
}

// ✅ 正确：用 while
synchronized (lock) {
    while (queue.isEmpty()) {
        lock.wait();   // 被唤醒后重新检查条件
    }
    queue.poll();      // 能走到这里，说明队列一定不为空
}
```

`notifyAll()` 会唤醒所有线程，但锁同一时刻只有一个线程能拿到。先拿到锁的线程可能改变了条件，后拿到的线程必须重新检查，所以要用 `while` 循环。

**完整示例：生产者-消费者模型**

```java
public class MessageQueue {
    private final Queue<String> queue = new LinkedList<>();
    private final int capacity;

    public MessageQueue(int capacity) {
        this.capacity = capacity;
    }

    // 生产者调用：放入消息
    public synchronized void put(String msg) throws InterruptedException {
        while (queue.size() == capacity) {
            wait();  // 队列满了 → 释放锁 → 等消费者取走消息后通知我
        }
        queue.add(msg);
        notifyAll();   // 放入成功 → 通知所有等待的线程（消费者可以来取了）
    }

    // 消费者调用：取出消息
    public synchronized String take() throws InterruptedException {
        while (queue.isEmpty()) {
            wait();  // 队列空了 → 释放锁 → 等生产者放入消息后通知我
        }
        String msg = queue.poll();
        notifyAll();   // 取出成功 → 通知所有等待的线程（生产者可以继续放了）
        return msg;
    }
}
```

```java
// 使用
MessageQueue mq = new MessageQueue(5);

// 生产者线程
new Thread(() -> {
    for (int i = 0; i < 10; i++) {
        mq.put("消息" + i);
        System.out.println("生产: 消息" + i);
    }
}).start();

// 消费者线程
new Thread(() -> {
    for (int i = 0; i < 10; i++) {
        String msg = mq.take();
        System.out.println("消费: " + msg);
    }
}).start();
```

> **为什么用 `while` 而不是 `if`？** 因为线程被唤醒后需要重新检查条件（可能被其他线程抢先消费了），这叫"虚假唤醒"防护。

### 4.4 线程安全的集合

普通集合（`ArrayList`、`HashMap`）不是线程安全的，多线程同时读写会出问题。Java 提供了三代线程安全集合：

**第一代：synchronized 包装（不推荐）**

```java
// Collections 工具类包装，给所有方法加 synchronized，性能差
List<String> list = Collections.synchronizedList(new ArrayList<>());
Map<String, Integer> map = Collections.synchronizedMap(new HashMap<>());
```

整个集合共用一把锁，任何操作都要排队，并发性能很差。

**第二代：遗留类（不推荐）**

| 类 | 对应的普通集合 | 问题 |
|---|---|---|
| `Vector` | `ArrayList` | 所有方法加 synchronized，性能差 |
| `Hashtable` | `HashMap` | 所有方法加 synchronized，性能差 |
| `Stack` | `ArrayDeque` | 继承 Vector，设计有问题 |

这些是 Java 1.0 的产物，现在不要用。

**第三代：java.util.concurrent 包（推荐）**

| 类 | 对应的普通集合 | 特点 |
|---|---|---|
| `ConcurrentHashMap` | `HashMap` | 分段锁 / CAS，读不加锁，写锁粒度小，**最常用** |
| `CopyOnWriteArrayList` | `ArrayList` | 写时复制整个数组，适合读多写极少的场景 |
| `CopyOnWriteArraySet` | `HashSet` | 基于 CopyOnWriteArrayList，同上 |
| `ConcurrentLinkedQueue` | `LinkedList`（队列） | 无锁（CAS），高并发队列 |
| `ConcurrentSkipListMap` | `TreeMap` | 并发有序 Map，基于跳表 |
| `ConcurrentSkipListSet` | `TreeSet` | 并发有序 Set |

```java
// ConcurrentHashMap：最常用的线程安全 Map
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// 基本操作和 HashMap 一样
map.put("Alice", 90);
map.get("Alice");

// 原子操作（HashMap 没有的）
map.putIfAbsent("Bob", 85);              // key 不存在才放入，线程安全
map.compute("Alice", (k, v) -> v + 10);  // 原子地更新 value
map.merge("Alice", 5, Integer::sum);     // 原子地合并 value

// ❌ 虽然单个操作是线程安全的，但组合操作不是
if (!map.containsKey("Charlie")) {  // 检查和放入之间其他线程可能插入
    map.put("Charlie", 70);
}
// ✅ 用 putIfAbsent 代替
map.putIfAbsent("Charlie", 70);   // 原子操作，检查+放入一步完成
```

```java
// CopyOnWriteArrayList：读多写少场景（如事件监听器列表、配置列表）
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();

list.add("a");       // 写：复制整个底层数组 → 修改副本 → 替换引用
list.get(0);         // 读：直接读，不加锁，性能高

// 遍历时不会抛 ConcurrentModificationException
// 因为遍历的是快照，写入不影响正在进行的遍历
for (String s : list) {
    list.add("new");  // 安全，但遍历看不到这个新元素
}
```

**BlockingQueue：生产者-消费者首选**

`BlockingQueue` 是线程安全的队列，内置了 wait/notify 逻辑，替代手写的生产者-消费者模型：

| 实现 | 底层 | 特点 |
|------|------|------|
| `ArrayBlockingQueue` | 数组 | 有界，创建时必须指定容量 |
| `LinkedBlockingQueue` | 链表 | 可选有界，默认无界（Integer.MAX_VALUE） |
| `PriorityBlockingQueue` | 堆 | 按优先级出队 |
| `SynchronousQueue` | 无容量 | 放入操作必须等取出操作配对，用于线程间直接传递 |

```java
// ArrayBlockingQueue：有界阻塞队列
BlockingQueue<String> queue = new ArrayBlockingQueue<>(10);  // 容量 10

// 生产者
queue.put("消息A");    // 队列满时阻塞等待（= 之前手写的 wait）

// 消费者
String msg = queue.take();  // 队列空时阻塞等待（= 之前手写的 wait）
```

对比手写的 MessageQueue：

```java
// 手写版：需要自己处理 synchronized + wait + notifyAll
public synchronized void put(String msg) throws InterruptedException {
    while (queue.size() == capacity) { wait(); }
    queue.add(msg);
    notifyAll();
}

// BlockingQueue 版：一行搞定，内部已封装好所有同步逻辑
queue.put(msg);
```

**选型速查**：

| 场景 | 推荐 |
|------|------|
| 并发读写 Map | `ConcurrentHashMap` |
| 读多写极少的 List | `CopyOnWriteArrayList` |
| 生产者-消费者 | `ArrayBlockingQueue` / `LinkedBlockingQueue` |
| 高并发无锁队列 | `ConcurrentLinkedQueue` |
| 并发有序 Map / Set | `ConcurrentSkipListMap` / `ConcurrentSkipListSet` |
| 线程池内部 | `SynchronousQueue`（Executors.newCachedThreadPool 用的就是它） |

## 4. volatile

`volatile` 解决可见性和有序性问题，但**不保证原子性**：

```java
// 典型用法：停止标志
private volatile boolean running = true;

public void run() {
    while (running) {  // 没有 volatile，其他线程修改 running 可能不可见
        doWork();
    }
}

public void stop() {
    running = false;  // 其他线程立即可见
}
```

```java
// volatile 不能替代 synchronized
private volatile int count = 0;
count++;  // 仍然不是原子操作！volatile 只保证读写的可见性
```

**什么时候用 volatile？** 一写多读的简单标志位场景。需要原子操作时用 `synchronized` 或 `Atomic` 类。

## 5. Lock 接口（java.util.concurrent.locks）

### 5.1 ReentrantLock

比 `synchronized` 更灵活的显式锁：

```java
private final ReentrantLock lock = new ReentrantLock();

public void increment() {
    lock.lock();
    try {
        count++;
    } finally {
        lock.unlock();  // 必须在 finally 中释放，防止异常导致死锁
    }
}
```

### 5.2 ReentrantLock 的进阶功能

**tryLock：尝试获取锁**

`synchronized` 获取不到锁就一直等，没有超时机制。`tryLock` 可以设置等待时间，超时就放弃，避免死锁：

```java
ReentrantLock lock = new ReentrantLock();

if (lock.tryLock(1, TimeUnit.SECONDS)) {  // 最多等 1 秒
    try {
        // 1 秒内拿到锁了，执行业务
    } finally {
        lock.unlock();
    }
} else {
    // 1 秒没拿到，走降级逻辑（比如返回默认值、重试、报错）
}
```

对比：

| | `lock()` | `tryLock()` | `tryLock(time, unit)` |
|---|---|---|---|
| 拿不到锁 | 一直等 | 立即返回 false | 等指定时间，超时返回 false |
| 会死锁吗 | 可能 | 不会 | 不会 |

**Condition：精准的线程通信**

`wait/notify` 只有一个等待队列，`notifyAll()` 会唤醒所有线程，包括不需要醒的。`Condition` 可以创建多个等待队列，精准唤醒指定角色：

```java
// wait/notify：一个等待队列，生产者消费者混在一起
synchronized (this) {
    notifyAll();  // 全部唤醒，生产者消费者都醒了，但只有一种角色需要醒
}

// Condition：多个等待队列，各管各的
ReentrantLock lock = new ReentrantLock();
Condition notFull  = lock.newCondition();  // 队列 1：生产者在这里等"不满"
Condition notEmpty = lock.newCondition();  // 队列 2：消费者在这里等"不空"
```

`Condition` 的方法和 `wait/notify` 一一对应，不是信号量：

| Condition | wait/notify | 作用 |
|-----------|-------------|------|
| `await()` | `wait()` | 释放锁，进入等待 |
| `signal()` | `notify()` | 唤醒该队列中的一个线程 |
| `signalAll()` | `notifyAll()` | 唤醒该队列中的所有线程 |

**完整示例：用 Condition 改写生产者-消费者**

```java
public class MessageQueue {
    private final Queue<String> queue = new LinkedList<>();
    private final int capacity;

    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull  = lock.newCondition();  // 生产者等待队列
    private final Condition notEmpty = lock.newCondition();  // 消费者等待队列

    public MessageQueue(int capacity) {
        this.capacity = capacity;
    }

    // 生产者调用
    public void put(String msg) throws InterruptedException {
        lock.lock();
        try {
            while (queue.size() == capacity) {
                notFull.await();      // 队列满了 → 生产者在"不满"队列上等
            }
            queue.add(msg);
            notEmpty.signal();        // 放入成功 → 只唤醒消费者（精准通知）
        } finally {
            lock.unlock();
        }
    }

    // 消费者调用
    public String take() throws InterruptedException {
        lock.lock();
        try {
            while (queue.isEmpty()) {
                notEmpty.await();     // 队列空了 → 消费者在"不空"队列上等
            }
            String msg = queue.poll();
            notFull.signal();         // 取出成功 → 只唤醒生产者（精准通知）
            return msg;
        } finally {
            lock.unlock();
        }
    }
}
```

对比三种实现方式：

| | synchronized + wait/notify | ReentrantLock + Condition | BlockingQueue |
|---|---|---|---|
| 等待队列 | 1 个，全部混在一起 | 多个，按角色分开 | 内部已封装 |
| 唤醒精度 | `notifyAll` 全部唤醒 | `signal` 精准唤醒 | 不需要关心 |
| 代码量 | 多 | 中 | 最少（一行） |
| 实际开发 | 了解原理 | 需要精细控制时 | **首选** |

> 实际开发直接用 `BlockingQueue`，但理解从 synchronized → ReentrantLock + Condition → BlockingQueue 的演进过程，有助于读懂框架源码（`ArrayBlockingQueue` 内部就是用 ReentrantLock + 两个 Condition 实现的）。

### 5.3 ReadWriteLock

读多写少场景下的优化——读读不互斥，读写/写写互斥：

```java
private final ReadWriteLock rwLock = new ReentrantReadWriteLock();
private final Lock readLock = rwLock.readLock();
private final Lock writeLock = rwLock.writeLock();

public String read() {
    readLock.lock();
    try {
        return data;  // 多个线程可以同时读
    } finally {
        readLock.unlock();
    }
}

public void write(String newData) {
    writeLock.lock();
    try {
        data = newData;  // 写时独占
    } finally {
        writeLock.unlock();
    }
}
```

## 6. 原子类（java.util.concurrent.atomic）

无锁线程安全，底层用 CAS（Compare-And-Swap）实现：当前值和预期值一致才更新，否则重试。没有加锁/释放锁的开销，性能优于 synchronized。

**常用原子类**：

| 类型 | 原子类 | 对应的普通类型 | 典型场景 |
|------|--------|--------------|---------|
| 整数 | `AtomicInteger` | `int` | 计数器、序号生成 |
| 长整数 | `AtomicLong` | `long` | 大范围计数 |
| 布尔 | `AtomicBoolean` | `boolean` | 开关标志 |
| 引用 | `AtomicReference<T>` | 对象引用 | 原子地替换对象 |
| 高并发计数 | `LongAdder` | `long` | 统计、监控（比 AtomicLong 更快） |
| 高并发累加 | `LongAccumulator` | `long` | 自定义累加规则 |
| 数组元素 | `AtomicIntegerArray` | `int[]` | 原子地操作数组中的某个元素 |
| 对象字段 | `AtomicIntegerFieldUpdater` | 对象的 int 字段 | 不想改类定义时给字段加原子操作 |

**AtomicInteger 常用方法**：

| 方法 | 含义 | 等价操作 |
|------|------|---------|
| `get()` | 读取 | `i` |
| `set(n)` | 赋值 | `i = n` |
| `incrementAndGet()` | 先加再取 | `++i` |
| `getAndIncrement()` | 先取再加 | `i++` |
| `decrementAndGet()` | 先减再取 | `--i` |
| `addAndGet(n)` | 加 n 再取 | `i += n` |
| `compareAndSet(expect, update)` | 当前值等于 expect 才改为 update | CAS 操作 |
| `updateAndGet(fn)` | 用函数更新并返回新值 | `i = fn(i)` |

```java
AtomicInteger count = new AtomicInteger(0);

count.incrementAndGet();         // 1（原子的 ++count）
count.getAndIncrement();         // 1（原子的 count++，返回旧值 1，新值变为 2）
count.addAndGet(5);              // 7（原子的 count += 5）
count.compareAndSet(7, 10);      // true，当前值是 7，改为 10
count.updateAndGet(n -> n * 2);  // 20（原子地乘以 2）
```

**AtomicLong vs LongAdder**：

```java
// AtomicLong：所有线程 CAS 竞争同一个值，高并发下冲突多，重试多
AtomicLong atomicLong = new AtomicLong(0);
atomicLong.incrementAndGet();

// LongAdder：内部分成多个 Cell，每个线程加到不同的 Cell 上，最后 sum 汇总
// 高并发写场景下性能远优于 AtomicLong
LongAdder adder = new LongAdder();
adder.increment();     // 各线程分散计数
adder.add(5);
adder.sum();           // 汇总所有 Cell 的值（注意：并发下 sum 可能不精确）
adder.reset();         // 归零
```

| | AtomicLong | LongAdder |
|---|---|---|
| 并发写性能 | 低（所有线程抢一个值） | 高（分散到多个 Cell） |
| 读取精确性 | 精确 | `sum()` 在并发下可能不精确 |
| 适用场景 | 需要精确值（如序号生成） | 只需要最终统计（如监控计数、QPS 统计） |

**AtomicReference：原子地替换对象**：

```java
AtomicReference<String> ref = new AtomicReference<>("hello");

ref.compareAndSet("hello", "world");  // 当前是 "hello"，替换为 "world"
ref.get();                             // "world"

// 常用于无锁地替换不可变对象
AtomicReference<List<String>> listRef = new AtomicReference<>(List.of("a"));
listRef.compareAndSet(listRef.get(), List.of("a", "b"));
```

## 7. 线程池（ExecutorService）

### 7.1 为什么不直接 new Thread？

每次 `new Thread()` 都要创建线程、分配内存，任务完成后销毁，开销很大。就像每来一个客人就招一个服务员，客人走了就开除——效率极低。线程池是提前雇好一批服务员，循环接待客人。

### 7.2 ThreadPoolExecutor：7 个参数

用餐厅来类比理解 7 个参数：

```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
    4,                                          // ① corePoolSize
    8,                                          // ② maximumPoolSize
    60,                                         // ③ keepAliveTime
    TimeUnit.SECONDS,                           // ④ unit
    new LinkedBlockingQueue<>(100),             // ⑤ workQueue
    Executors.defaultThreadFactory(),           // ⑥ threadFactory
    new ThreadPoolExecutor.CallerRunsPolicy()   // ⑦ handler
);
```

| 参数 | 餐厅类比 | 含义 |
|------|---------|------|
| ① `corePoolSize = 4` | 正式员工 4 人 | 核心线程数，永远不裁员，即使空闲也保留 |
| ② `maximumPoolSize = 8` | 最多雇 8 人 | 最大线程数 = 核心线程 + 临时工上限 |
| ③ `keepAliveTime = 60` | 临时工闲 60 秒就走 | 非核心线程（临时工）的空闲存活时间 |
| ④ `unit = SECONDS` | 时间单位 | 配合 ③ 使用 |
| ⑤ `workQueue = 容量100` | 等候区 100 个座位 | 任务排队的队列，核心线程忙不过来时任务先排队 |
| ⑥ `threadFactory` | 员工工牌模板 | 创建线程的工厂，可以自定义线程名 |
| ⑦ `handler` | 等候区也满了怎么办 | 拒绝策略，队列满 + 线程数达到上限时的处理方式 |

**核心线程 vs 非核心线程**：

```
核心线程（正式员工）：一直在岗，即使没有任务也不销毁
非核心线程（临时工）：忙不过来时临时招的，空闲超过 keepAliveTime 就被销毁

本例中：核心 4 个，最多 8 个，所以最多有 4 个临时工
```

### 7.3 任务提交流程

用餐厅接待客人的流程来理解：

```
来了一个新任务（客人进门）
  │
  ├─ 正式员工（核心线程）有空的吗？
  │    └─ 有 → 正式员工直接接待（创建核心线程执行）
  │
  ├─ 正式员工都在忙 → 等候区（队列）有空位吗？
  │    └─ 有 → 客人去等候区排队（任务放入队列）
  │
  ├─ 等候区也满了 → 还能招临时工吗（线程数 < maximumPoolSize）？
  │    └─ 能 → 招一个临时工来接待（创建非核心线程执行）
  │
  └─ 临时工也招满了 → 执行拒绝策略（见下面）
```

注意顺序：**先排队，排满了才招临时工**。不是先招临时工再排队。

用具体数字走一遍：

```
pool = (core=4, max=8, queue=100)

第 1~4 个任务：  创建核心线程 1~4 执行
第 5~104 个任务：核心线程都在忙 → 放入队列排队（队列容量 100）
第 105~108 个任务：队列满了 → 创建非核心线程 5~8 执行
第 109 个任务：  队列满 + 线程数已达 8 → 触发拒绝策略
```

### 7.4 四种拒绝策略

队列满了 + 线程数达到上限，新任务怎么处理：

| 策略 | 餐厅类比 | 行为 |
|------|---------|------|
| `AbortPolicy`（默认） | 直接拒客，告诉客人"满了不接" | 抛 `RejectedExecutionException` 异常 |
| `CallerRunsPolicy` | 老板亲自接待（提交任务的线程自己执行） | 起到限流作用，提交方变慢了就不会继续提交 |
| `DiscardPolicy` | 假装没看见客人 | 默默丢弃任务，不抛异常 |
| `DiscardOldestPolicy` | 让等最久的客人走，新客人插队 | 丢弃队列中最老的任务，重试提交新任务 |

实际开发中最常用的是 `CallerRunsPolicy`，它不会丢任务也不会抛异常，还能自动限流。

### 7.5 使用线程池

```java
// 创建线程池
ExecutorService pool = new ThreadPoolExecutor(
    4, 8, 60, TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(100),
    new ThreadPoolExecutor.CallerRunsPolicy()
);

// 提交 Runnable：无返回值，相当于"帮我做这件事，我不需要结果"
pool.execute(() -> System.out.println("任务 1"));

// 提交 Callable：有返回值，相当于"帮我做这件事，做完告诉我结果"
Future<String> future = pool.submit(() -> {
    Thread.sleep(1000);
    return "done";
});
String result = future.get();                     // 阻塞等待结果
String result2 = future.get(2, TimeUnit.SECONDS); // 最多等 2 秒，超时抛异常

// 关闭线程池（程序结束前必须关闭，否则线程一直活着，程序不会退出）
pool.shutdown();          // 温和关闭：不接新任务，等正在执行的任务做完
pool.shutdownNow();       // 强制关闭：尝试中断所有正在执行的任务
pool.awaitTermination(10, TimeUnit.SECONDS);  // 等待关闭完成，最多等 10 秒
```

```Java
// execute：不关心结果，"帮我做就行"
pool.execute(() -> System.out.println("fire and forget"));

// submit：需要结果，"做完把结果给我"
Future<String> future = pool.submit(() -> "结果");
String result = future.get();  // "结果"

// submit 也能提交 Runnable，但返回的 Future 拿到的是 null
Future<?> f = pool.submit(() -> System.out.println("task"));
f.get();  // null，但可以用来判断任务是否执行完毕
```

> 简单说：不需要返回值用 execute，需要返回值或需要知道任务是否完成用 submit。

### 7.6 不要用 Executors 工厂方法

```java
// 这些写法看起来简洁，但有隐患
Executors.newFixedThreadPool(10);
// 底层队列是无界的 LinkedBlockingQueue（默认 Integer.MAX_VALUE）
// 任务堆积过多 → OOM（内存溢出）

Executors.newCachedThreadPool();
// 最大线程数是 Integer.MAX_VALUE
// 短时间内大量任务 → 创建上万个线程 → 系统崩溃

Executors.newSingleThreadExecutor();
// 同样无界队列，同样 OOM 风险
```

所以要用 `ThreadPoolExecutor` 手动指定参数，明确队列容量和拒绝策略。这是阿里巴巴 Java 开发手册的强制规范。

## 8. Future：获取异步任务的结果

### 8.1 为什么需要 Future？

前面讲过，`execute` 提交任务后就不管了，拿不到结果。但很多场景需要知道结果：

```java
// execute：火烧了就忘了，不知道任务执行得怎么样
pool.execute(() -> fetchData());  // 返回 void，数据去哪了？

// 需要一个"凭证"，将来用它取结果
```

`Future` 就是这个**凭证**——提交任务时拿到一个 Future 对象，将来通过它获取结果，使用sumbit能够拿到 Future，但是一次只能提交一个任务，无法批量提交：

```java
// submit 返回 Future，相当于拿到一张取餐小票
Future<String> future = pool.submit(() -> {
    Thread.sleep(2000);  // 模拟耗时操作
    return "数据来了";
});

// 先去做别的事...
doOtherWork();

// 需要结果时，拿着小票去取
String result = future.get();  // 如果任务还没完成，阻塞等待
```

### 8.2 Future 的方法

| 方法 | 作用 |
|------|------|
| `get()` | 阻塞等待结果，直到任务完成 |
| `get(timeout, unit)` | 最多等指定时间，超时抛 `TimeoutException` |
| `isDone()` | 任务是否已完成（不阻塞） |
| `isCancelled()` | 任务是否被取消 |
| `cancel(mayInterrupt)` | 取消任务 |

```java
Future<String> future = pool.submit(() -> {
    Thread.sleep(5000);
    return "result";
});

future.isDone();    // false，还没完成

// 方式 1：一直等到完成
String r1 = future.get();

// 方式 2：最多等 2 秒
try {
    String r2 = future.get(2, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    // 2 秒还没完成，超时了
    future.cancel(true);  // 可以选择取消任务
}
```

### 8.3 Future 的局限

Future 能拿到结果，但用起来很不方便：

```java
// 问题 1：get() 是阻塞的，调用后当前线程就卡住了
String result = future.get();  // 在这里干等，和同步调用没区别

// 问题 2：无法链式处理——"拿到结果后自动做下一步"
// 想实现：查数据库 → 处理数据 → 发邮件
Future<String> f1 = pool.submit(() -> fetchFromDB());
String data = f1.get();          // 阻塞等
Future<String> f2 = pool.submit(() -> process(data));
String processed = f2.get();      // 又阻塞等
pool.execute(() -> sendEmail(processed));
// 每一步都要 get() 阻塞，串行化了，失去了异步的意义

// 问题 3：无法组合多个 Future
// 想实现：同时查价格和库存，两个都完成后合并
Future<Double> priceFuture = pool.submit(() -> getPrice());
Future<Integer> stockFuture = pool.submit(() -> getStock());
// 只能分别 get()，没有"两个都完成后执行回调"的机制
```

这些局限就是 `CompletableFuture` 要解决的问题。

### 8.4 Future vs CompletableFuture 预览

| | Future | CompletableFuture |
|---|---|---|
| 获取结果 | `get()` 阻塞等 | `thenApply()` 异步回调，不阻塞 |
| 链式处理 | ❌ 不支持 | ✅ `thenApply → thenAccept → ...` |
| 组合多个任务 | ❌ 不支持 | ✅ `allOf` / `thenCombine` |
| 异常处理 | `get()` 时抛 ExecutionException | `exceptionally()` / `handle()` |
| 手动完成 | ❌ | ✅ `complete()` / `completeExceptionally()` |

一句话总结：**Future 是"给你一张取餐票，你自己来取"；CompletableFuture 是"做好了自动送到你桌上，还能加配菜"。**

## 9. CompletableFuture：异步编排

### 9.1 为什么需要 CompletableFuture？

上一节讲了 Future 的三个局限：get 阻塞、不能链式处理、不能组合多个任务。CompletableFuture（Java 8）就是为了解决这些问题——任务完成后自动触发下一步，不用干等。

```java
// Future：每一步都要 get() 阻塞等
Future<String> f = pool.submit(() -> fetchData());
String data = f.get();        // 阻塞
String result = process(data); // 串行

// CompletableFuture：链式回调，不阻塞
CompletableFuture.supplyAsync(() -> fetchData())
    .thenApply(data -> process(data))
    .thenAccept(result -> System.out.println(result))
    .exceptionally(e -> { e.printStackTrace(); return null; });
```

### 9.2 创建异步任务

| 方法 | 有无返回值 | 参数类型 | 类比 |
|------|---------|---------|------|
| `supplyAsync(supplier)` | 有返回值 | `Supplier<T>` | "帮我算个结果" |
| `runAsync(runnable)` | 无返回值 | `Runnable` | "帮我做件事" |

```java
// 有返回值：supplyAsync
CompletableFuture<String> cf1 = CompletableFuture.supplyAsync(() -> {
    return fetchFromDB();
});

// 无返回值：runAsync
CompletableFuture<Void> cf2 = CompletableFuture.runAsync(() -> {
    sendEmail();
});

// 推荐：指定自己的线程池，避免使用默认的 ForkJoinPool.commonPool
ExecutorService pool = new ThreadPoolExecutor(...);
CompletableFuture<String> cf3 = CompletableFuture.supplyAsync(() -> fetchFromDB(), pool);
```

### 9.3 链式转换

拿到上一步的结果后，自动执行下一步。四个方法对应四种场景：

| 方法 | 入参 | 返回值 | 用途 | 类比函数式接口 |
|------|------|--------|------|--------------|
| `thenApply(fn)` | 上一步结果 | 有 | 转换结果 | `Function` |
| `thenAccept(fn)` | 上一步结果 | 无（Void） | 消费结果 | `Consumer` |
| `thenRun(fn)` | 无 | 无（Void） | 执行动作，不关心上一步结果 | `Runnable` |
| `thenCompose(fn)` | 上一步结果 | CompletableFuture | 异步转换（展平嵌套） | flatMap |

```java
CompletableFuture.supplyAsync(() -> "hello")        // 第一步：返回 "hello"
    .thenApply(s -> s + " world")                    // 第二步：拼接 → "hello world"
    .thenApply(String::toUpperCase)                  // 第三步：大写 → "HELLO WORLD"
    .thenAccept(s -> System.out.println(s))          // 第四步：打印，没有返回值
    .thenRun(() -> System.out.println("全部完成"));   // 第五步：不关心之前的结果
```

**thenApply vs thenCompose**：

当下一步本身也是异步的，用 `thenCompose` 避免嵌套：

```java
// thenApply：结果会嵌套成 CompletableFuture<CompletableFuture<User>>
cf.thenApply(id -> CompletableFuture.supplyAsync(() -> fetchUser(id)));

// thenCompose：自动展平为 CompletableFuture<User>
cf.thenCompose(id -> CompletableFuture.supplyAsync(() -> fetchUser(id)));
```

和 Stream 的 `map` vs `flatMap` 是同一个道理。

### 9.4 组合多个异步任务

| 方法 | 作用 | 等待策略 |
|------|------|---------|
| `thenCombine(other, fn)` | 两个任务都完成后，合并两个结果 | 等两个都完成 |
| `allOf(cf1, cf2, ...)` | 多个任务全部完成后触发回调 | 等全部完成 |
| `anyOf(cf1, cf2, ...)` | 多个任务任意一个完成后触发回调 | 等最快的一个 |

**thenCombine：合并两个结果**

```java
CompletableFuture<Double> priceCf = CompletableFuture.supplyAsync(() -> getPrice());
CompletableFuture<Integer> stockCf = CompletableFuture.supplyAsync(() -> getStock());

// 两个都完成后，把结果合并成一个字符串
CompletableFuture<String> combined = priceCf.thenCombine(stockCf,
    (price, stock) -> "价格: " + price + ", 库存: " + stock);

System.out.println(combined.join());  // "价格: 99.9, 库存: 50"
```

**allOf：等待全部完成**

```java
CompletableFuture<String> cf1 = CompletableFuture.supplyAsync(() -> fetchA());
CompletableFuture<String> cf2 = CompletableFuture.supplyAsync(() -> fetchB());
CompletableFuture<String> cf3 = CompletableFuture.supplyAsync(() -> fetchC());

CompletableFuture.allOf(cf1, cf2, cf3).thenRun(() -> {
    // 走到这里说明三个都完成了
    String a = cf1.join();   // join() 和 get() 类似，但抛 unchecked 异常
    String b = cf2.join();
    String c = cf3.join();
    System.out.println(a + b + c);
});
```

**为什么每个结果都要单独 `join()`？** 因为 `allOf` 返回的是 `CompletableFuture<Void>`——它只告诉你"全部完成了"，但不帮你收集结果。每个任务的结果还存在各自的 CompletableFuture 里，要分别取：

```java
all.join();      // 返回 null，拿不到任何数据
cf1.join();      // 返回 cf1 的结果
```

在 `thenRun` 回调里调用 `join()` 是安全的，因为走到回调说明任务已经完成了，`join()` 不会阻塞，只是取一下结果。

**`join()` vs `get()`**：功能一样，都是获取结果。区别是 `get()` 抛受检异常必须 try-catch，`join()` 抛非受检异常不用 try-catch，代码更干净。CompletableFuture 里统一用 `join()`。

**anyOf：只要最快的那个**

```java
// 从三个镜像源下载，谁最快用谁
CompletableFuture<String> mirror1 = CompletableFuture.supplyAsync(() -> downloadFrom("us"));
CompletableFuture<String> mirror2 = CompletableFuture.supplyAsync(() -> downloadFrom("eu"));
CompletableFuture<String> mirror3 = CompletableFuture.supplyAsync(() -> downloadFrom("cn"));

CompletableFuture<Object> fastest = CompletableFuture.anyOf(mirror1, mirror2, mirror3);
System.out.println(fastest.join());  // 最先完成的那个结果
```

### 9.5 异常处理

| 方法 | 触发时机 | 入参 | 返回值 |
|------|---------|------|--------|
| `exceptionally(fn)` | 只在异常时触发 | 异常 e | 兜底值（替代异常结果） |
| `handle(fn)` | 无论成功失败都触发 | (result, e) | 新的结果 |
| `whenComplete(fn)` | 无论成功失败都触发 | (result, e) | 不改变结果（只做副作用） |

```java
CompletableFuture<String> cf = CompletableFuture.supplyAsync(() -> {
    if (true) throw new RuntimeException("网络超时");
    return "ok";
});

// exceptionally：异常时返回兜底值（类似 try-catch）
cf.exceptionally(e -> {
    System.out.println("出错了: " + e.getMessage());
    return "默认值";
});

// handle：成功和失败都处理（类似 try-catch-finally）
cf.handle((result, e) -> {
    if (e != null) return "出错了: " + e.getMessage();
    return "成功: " + result;
});

// whenComplete：只记录，不改变结果（类似日志）
cf.whenComplete((result, e) -> {
    if (e != null) log.error("任务失败", e);
    else log.info("任务成功: " + result);
});
```

### 9.6 实战：并发调用多个接口

一个常见的后端场景——用户详情页需要同时查用户信息、订单列表、推荐列表：

```java
// 串行调用：总耗时 = 200ms + 300ms + 150ms = 650ms
User user = userService.getUser(userId);           // 200ms
List<Order> orders = orderService.getOrders(userId); // 300ms
List<Item> recs = recService.getRecommendations(userId); // 150ms

// 并发调用：总耗时 ≈ max(200, 300, 150) = 300ms
CompletableFuture<User> userCf = CompletableFuture.supplyAsync(
    () -> userService.getUser(userId), pool);
CompletableFuture<List<Order>> ordersCf = CompletableFuture.supplyAsync(
    () -> orderService.getOrders(userId), pool);
CompletableFuture<List<Item>> recsCf = CompletableFuture.supplyAsync(
    () -> recService.getRecommendations(userId), pool);

// 三个都完成后组装页面
CompletableFuture.allOf(userCf, ordersCf, recsCf).thenRun(() -> {
    UserPage page = new UserPage(
        userCf.join(),
        ordersCf.join(),
        recsCf.join()
    );
});
```

### 9.7 CompletableFuture 方法速查

| 方法 | 作用 |
|------|------|
| `supplyAsync(fn)` | 创建有返回值的异步任务 |
| `runAsync(fn)` | 创建无返回值的异步任务 |
| `thenApply(fn)` | 转换结果（同步） |
| `thenCompose(fn)` | 转换结果（异步，展平嵌套） |
| `thenAccept(fn)` | 消费结果 |
| `thenRun(fn)` | 执行动作，不关心结果 |
| `thenCombine(other, fn)` | 合并两个任务的结果 |
| `allOf(cf1, cf2, ...)` | 等待全部完成 |
| `anyOf(cf1, cf2, ...)` | 等待任意一个完成 |
| `exceptionally(fn)` | 异常兜底 |
| `handle(fn)` | 成功和异常都处理 |
| `whenComplete(fn)` | 成功和异常都处理，但不改变结果 |
| `join()` | 获取结果（和 get 类似，抛 unchecked 异常） |

## 10. 小结

| 主题 | 关键要点 |
|------|---------|
| 创建线程 | Runnable / Callable + FutureTask；实际用线程池 |
| 线程安全三问题 | 原子性、可见性、有序性 |
| synchronized | 最基础的锁，自动释放；wait/notify 实现通信 |
| volatile | 保证可见性和有序性，不保证原子性；适合一写多读标志位 |
| ReentrantLock | 比 synchronized 更灵活：可中断、可超时、公平锁、多 Condition |
| 原子类 | CAS 无锁操作，高并发计数用 LongAdder |
| 线程池 | 手动创建 ThreadPoolExecutor，不用 Executors 工厂方法 |
| 核心参数 | corePoolSize → 队列 → maximumPoolSize → 拒绝策略 |
| 并发工具 | CountDownLatch（一等多）、CyclicBarrier（互相等）、Semaphore（限并发） |
| ConcurrentHashMap | 线程安全 Map 首选，atomic 方法避免先 get 再 put |
| CompletableFuture | 链式异步编排；thenApply/thenCompose/thenCombine/allOf |

---

> **下一篇预告**：JVM 基础——内存结构、类加载机制与垃圾回收

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
