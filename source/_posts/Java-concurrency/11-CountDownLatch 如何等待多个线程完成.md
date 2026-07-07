---
title: Java高并发底层原理（十一）—— CountDownLatch 如何等待多个线程完成
date: 2026-07-03
abbrlink: 11
tags:
    - Java
    - 高并发
    - CountDownLatch
    - AQS
categories:
    - java-concurrency
---


`ReentrantLock` 解决的是多个线程竞争共享数据时，如何保证同一时刻只有一个线程进入临界区；`Condition` 解决的是线程已经获得锁后，如何等待某个业务条件成立。并发程序中还有另一类问题：一个线程不一定要和其他线程互斥执行，但必须等多个任务全部完成后才能继续。

例如主线程启动三个工作线程，三个工作线程可以并发执行，但主线程必须等它们都结束后，才能汇总结果：

```java
CountDownLatch latch = new CountDownLatch(3);

Thread worker1 = new Thread(() -> {
    doWork1();
    latch.countDown();
});

Thread worker2 = new Thread(() -> {
    doWork2();
    latch.countDown();
});

Thread worker3 = new Thread(() -> {
    doWork3();
    latch.countDown();
});

worker1.start();
worker2.start();
worker3.start();

latch.await();
System.out.println("all workers finished");
```

这里的问题不是“谁能进入临界区”，而是“等待线程什么时候可以继续执行”。`CountDownLatch` 就是用来表达这种一次性的等待关系。

## 一、CountDownLatch 等待的是完成事件

创建 `CountDownLatch` 时传入的数字表示还需要发生多少次完成事件：

```java
CountDownLatch latch = new CountDownLatch(3);
```

这个 `3` 通常对应三个任务，但它本质上不是线程数量，而是计数。每调用一次 `countDown()`，计数减少一；调用 `await()` 的线程会等待这个计数变成 `0`。

| 操作 | 作用 |
|---|---|
| `countDown()` | 报告一个完成事件已经发生 |
| `await()` | 等待所有完成事件都发生 |

因此，工作线程调用 `countDown()` 后不会等待其他线程，它只是把“自己这份事件已经完成”报告给 `CountDownLatch`，然后继续执行自己的后续代码。真正可能暂停的是调用 `await()` 的线程。

也因为 CountDownLatch 只维护计数，所以它不能保证“三个不同线程各完成了一次”。即使同一个线程连续调用三次 `countDown()`，计数也会从 `3` 变成 `0`。一次 `countDown()` 是否真的对应一个任务完成，需要业务代码自己保证。

## 二、state 保存剩余计数，countDown 通过 CAS 递减

`CountDownLatch` 基于 AQS 实现，并使用 AQS 的 `state` 保存剩余计数。创建对象时传入的初始值会写入 `state`：

| `state` | 含义 |
|---|---|
| `3` | 还有三个完成事件没有发生 |
| `2` | 还有两个完成事件没有发生 |
| `1` | 还有一个完成事件没有发生 |
| `0` | 等待条件已经满足 |

这里的 `state` 和 `ReentrantLock` 中的含义不同。`ReentrantLock` 把 `state` 解释为锁状态和重入次数；`CountDownLatch` 把 `state` 解释为剩余完成事件数量。AQS 只提供同步状态和等待队列，具体语义由不同同步工具自己定义。

多个工作线程可能同时调用 `countDown()`，所以内部不能直接执行普通的 `state--`。`state--` 至少包含读取、计算、写回三个步骤，两个线程同时执行时可能发生更新丢失。假设当前 `state == 3`，两个线程都读到 `3`，又都写回 `2`，那么两次 `countDown()` 只会产生一次有效递减。

`CountDownLatch` 使用 CAS 循环解决这个问题，可以简化理解为：

```java
for (;;) {
    int oldState = getState();

    if (oldState == 0) {
        return;
    }

    int newState = oldState - 1;

    if (compareAndSetState(oldState, newState)) {
        return;
    }
}
```

如果线程 A 先执行 `CAS(3, 2)` 成功，线程 B 再执行 `CAS(3, 2)` 就会失败。线程 B 必须重新读取最新的 `state == 2`，再尝试 `CAS(2, 1)`。这样可以保证每一次成功的 `countDown()` 都对应一次真实递减。

当 `state` 已经是 `0` 时，继续调用 `countDown()` 会直接返回，不会把计数减成负数。

## 三、await 等待 state 归零，共享模式放行等待线程

调用 `await()` 时，线程会检查当前 `state`。如果 `state == 0`，说明等待条件已经满足，`await()` 直接返回；如果 `state > 0`，说明还有完成事件没有发生，当前线程会进入 AQS 等待队列并暂停，不会持续空转占用 CPU。

只有某次 `countDown()` 成功把 `state` 从 `1` 减到 `0` 时，才表示所有完成事件都已经发生，此时需要唤醒等待线程。前面的递减，例如 `3 → 2`、`2 → 1`，都不会让 `await()` 返回。

![](/images/Java-concurrency/IMG-20260707-000053.png)



`CountDownLatch` 使用的是 AQS 共享模式。共享的意思不是多个线程可以随意并发修改 `state`，而是当同步条件满足后，多个等待线程都可以通过。

假设线程 A、B、C 都在同一个 `CountDownLatch` 上调用了 `await()`，当最后一次 `countDown()` 把 `state` 减到 `0` 后，A、B、C 都可以从 `await()` 返回。它们返回时不会消耗计数，`state` 仍然保持为 `0`。这和 `ReentrantLock` 的独占模式不同：锁一次只能由一个线程持有，而 CountDownLatch 的闸门打开后，所有等待线程都可以通过。

## 四、CountDownLatch 是一次性闸门

`CountDownLatch` 的计数只能从初始值逐步减少到 `0`，不能重新增加，也没有 `reset()` 方法。一旦 `state` 变成 `0`，后续调用 `await()` 的线程都会直接返回，继续调用 `countDown()` 也不会改变状态。

可以把它理解为一道一次性闸门：

| 状态 | 含义 |
|---|---|
| `state > 0` | 闸门关闭，`await()` 线程等待 |
| `state == 0` | 闸门打开，所有等待线程通过 |

闸门打开后不会再次关闭。如果还要等待下一批任务完成，需要创建新的 `CountDownLatch`。如果需要同一批线程反复在多个阶段会合，应使用更适合循环使用的同步工具，而不是让一个 CountDownLatch 承担多轮协调。

## 五、countDown 通常放在 finally 中

如果某个工作线程在执行任务时抛出异常，并且没有执行到 `countDown()`，计数可能永远无法归零。比如初始计数是 `3`，两个任务正常调用了 `countDown()`，另一个任务异常退出却没有调用，那么 `state` 会停在 `1`，等待线程也会一直阻塞。

这不是严格意义上的“两个线程互相等待对方释放资源”，更准确地说，是等待条件永远无法满足。因此，工作线程通常把 `countDown()` 放在 `finally` 中：

```java
Thread worker = new Thread(() -> {
    try {
        doWork();
    } finally {
        latch.countDown();
    }
});
```

这样无论任务正常结束还是异常退出，当前任务对应的完成事件都会被报告。不过要注意，`countDown()` 只表示任务已经结束，不表示任务执行成功。完成状态和成功状态需要分开表达。

## 六、CountDownLatch 不保存任务结果

`CountDownLatch` 只维护“还有多少任务没有结束”，不会记录任务返回值、成功失败或异常信息。如果等待线程还需要汇总结果，必须使用其他对象单独保存。

例如多个工作线程可能抛出异常，可以使用线程安全队列保存错误：

```java
CountDownLatch latch = new CountDownLatch(3);

ConcurrentLinkedQueue<Throwable> errors =
        new ConcurrentLinkedQueue<>();

Thread worker = new Thread(() -> {
    try {
        doWork();
    } catch (Throwable e) {
        errors.add(e);
    } finally {
        latch.countDown();
    }
});
```

主线程在 `await()` 返回后再检查：

```java
latch.await();

if (errors.isEmpty()) {
    System.out.println("all workers succeeded");
} else {
    System.out.println("some workers failed");
}
```

这里有两个独立职责：`CountDownLatch` 负责判断所有任务是否结束，结果容器负责保存任务结果。不能因为用了 CountDownLatch，就忽略结果容器本身的线程安全问题。

如果多个线程都会向同一个集合添加异常，不能直接使用普通 `ArrayList`。一次 `add()` 可能涉及写入数组、修改 `size`、扩容等多个步骤，多个线程同时修改会破坏集合内部状态。此时应使用线程安全容器，或者额外加锁。

不过，如果每个工作线程只写数组中固定的位置，就不一定需要线程安全队列：

```java
CountDownLatch latch = new CountDownLatch(3);
Throwable[] errors = new Throwable[3];

Thread worker1 = new Thread(() -> {
    try {
        doWork1();
    } catch (Throwable e) {
        errors[0] = e;
    } finally {
        latch.countDown();
    }
});

Thread worker2 = new Thread(() -> {
    try {
        doWork2();
    } catch (Throwable e) {
        errors[1] = e;
    } finally {
        latch.countDown();
    }
});

Thread worker3 = new Thread(() -> {
    try {
        doWork3();
    } catch (Throwable e) {
        errors[2] = e;
    } finally {
        latch.countDown();
    }
});
```

数组元素可以看作独立变量。只要每个线程写入自己的固定位置，就没有多个线程同时写同一个变量。主线程在 `await()` 返回后再读取这些位置即可。

这种写法需要同时满足三个条件：每个工作线程只写自己的固定位置；写入结果发生在 `countDown()` 之前；主线程在 `await()` 返回之后读取。如果多个线程需要动态申请下标，例如使用 `nextIndex++`，竞争点就变成了 `nextIndex`，此时需要 `AtomicInteger` 等方式原子分配下标。

## 七、Lambda 捕获局部变量时，修改的是对象不是引用

保存单个工作线程的异常时，有时会看到长度为 `1` 的数组：

```java
Throwable[] error = new Throwable[1];
```

使用数组不是因为异常必须存进数组，而是因为 Lambda 捕获的局部变量必须是 `final` 或事实上 `final`。下面的代码无法编译：

```java
Throwable error = null;

Thread worker = new Thread(() -> {
    try {
        doWork();
    } catch (Throwable e) {
        error = e;
    }
});
```

Lambda 试图重新给局部变量 `error` 赋值，所以它不再是事实上 `final`。使用数组后，局部变量 `error` 保存的数组引用没有变化，线程修改的是数组对象内部的元素。

![](/images/Java-concurrency/IMG-20260707-000054.png)



也可以使用普通 Holder 对象：

```java
class ResultHolder {
    Throwable error;
}
```

然后在线程中修改对象字段：

```java
ResultHolder holder = new ResultHolder();

Thread worker = new Thread(() -> {
    try {
        doWork();
    } catch (Throwable e) {
        holder.error = e;
    } finally {
        latch.countDown();
    }
});
```

Lambda 限制的是不能重新给捕获的局部变量赋值，不是不能修改该局部变量所指向的对象。

这一节和 CountDownLatch 本身没有直接绑定关系，只是解释结果保存代码中常见的数组或 Holder 写法。真正的并发保证仍然来自前文的线程安全容器、固定位置写入，以及后文要讲的 `await()` 可见性规则。

## 八、await 返回后为什么能看到任务结果

`CountDownLatch` 不只负责等待，还提供内存可见性保证：一个线程在调用 `countDown()` 之前完成的操作，happens-before 另一个线程从对应 `await()` 成功返回后的操作。

例如工作线程先保存异常，再调用 `countDown()`：

```java
try {
    doWork();
} catch (Throwable e) {
    errors.add(e);
} finally {
    latch.countDown();
}
```

主线程随后从 `await()` 返回并检查结果：

```java
latch.await();
boolean success = errors.isEmpty();
```

当 `await()` 成功返回后，主线程不仅知道计数已经变成 `0`，还能够看到工作线程在各自 `countDown()` 之前产生的内存更新。

顺序不能写反：

```java
latch.countDown();
errors.add(e);
```

`errors.add(e)` 发生在 `countDown()` 之后，CountDownLatch 建立的 happens-before 关系不能保证主线程在 `await()` 返回时已经看到这次写入。所以任务结果必须先保存，再调用 `countDown()`。

还要区分两件事：happens-before 保证的是写入结果对等待线程可见，但它不会修复多个线程同时修改同一个非线程安全对象时已经造成的内部破坏。比如多个线程并发修改普通 `ArrayList`，即使主线程在 `await()` 返回后能够看到内存更新，集合内部状态也可能已经不一致。

## 九、await 的中断、超时和边界

`await()` 在等待期间支持中断：

```java
try {
    latch.await();
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}
```

如果等待线程被其他线程中断，`await()` 会抛出 `InterruptedException`。捕获后重新调用 `Thread.currentThread().interrupt()`，是为了恢复中断标记，让上层代码仍然知道这个线程曾经被请求中断。

线程因为中断离开 `await()`，不代表计数已经变成 `0`。这只是当前线程不再继续等待，其他等待线程和剩余计数不会因此自动改变。

普通 `await()` 会一直等待，直到计数归零。如果某个任务因为代码错误永远没有调用 `countDown()`，等待线程就可能永久阻塞。可以使用带超时的方法避免无限等待：

```java
boolean completed = latch.await(5, TimeUnit.SECONDS);

if (!completed) {
    System.out.println("some tasks did not finish in time");
}
```

返回值为 `true` 表示计数已经在超时前变成 `0`；返回值为 `false` 表示等待超时，计数仍然大于 `0`。超时不会自动停止工作线程，也不会把剩余计数改成 `0`，它只是让当前等待线程不再无限期阻塞。

从适用范围看，CountDownLatch 适合表达“一批事件完成后再继续”的一次性协调，例如主线程等待多个工作线程结束、多个服务初始化完成后再开始接收请求、多个并行查询结束后汇总结果、测试线程等待一组并发操作执行完毕。它不适合代替互斥锁，也不适合需要反复打开和关闭的同步条件。

## 本章总结

CountDownLatch 的主线可以从“完成事件”开始理解：业务代码先把一批任务抽象成固定数量的完成事件，AQS 的 `state` 保存还剩多少事件没有发生；每个工作线程在任务收尾处通过 CAS 把 `state` 减一，只有最后一次递减把计数推到 `0` 时，等待线程才从 AQS 共享模式中被放行。

这条链条也决定了它的使用边界。因为它只观察完成事件，所以它不保存任务结果，也不判断任务是否成功；因为它只在 `countDown()` 之前建立可见性，所以结果必须先写入再递减计数；因为它只从非零走向零，所以闸门一旦打开就不能复位。也就是说，CountDownLatch 解决的是“一批事情是否都结束”的时序问题，而不是“共享数据如何互斥修改”或“结果容器如何保证线程安全”的问题。
