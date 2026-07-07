---

title: Java高并发底层原理（二十五）—— LockSupport 如何挂起和唤醒线程
date: 2026-07-05
tags:
- Java
- 高并发
- LockSupport
- 线程阻塞
categories:
- java-concurrency
-------------


前面分析 AQS、ReentrantLock、线程等待队列时，经常会看到一个底层工具：`LockSupport`。它不是一把锁，也不维护等待队列，而是提供两个更底层的能力：让当前线程暂停，以及唤醒指定线程。

理解 `LockSupport` 时，先不要把它和完整的锁混在一起。完整的锁至少还需要状态判断、等待队列和唤醒策略；`LockSupport` 只负责其中最底层的一步：线程如何停下，以及如何被指定线程唤醒。

## 1. park 和 unpark 操作的是线程自己的 permit

`LockSupport` 给每个线程关联了一个许可证，可以先把它理解成一个最多为 1 的 permit：

```text
permit = 0：没有许可证，park() 会阻塞
permit = 1：有许可证，park() 会直接返回，并消耗这个许可证
```

所以：

```java
LockSupport.park();
```

含义不是“无条件挂起当前线程”，而是：当前线程尝试获取自己的 permit；如果没有 permit，就阻塞等待。

对应地：

```java
LockSupport.unpark(thread);
```

含义也不是“强行唤醒线程”，而是：给指定线程发放一个 permit；如果这个线程正在 `park()` 中阻塞，就让它返回；如果它还没有执行到 `park()`，这个 permit 会先保留下来。

一个最小例子如下：

```java
import java.util.concurrent.locks.LockSupport;

public class ParkUnparkDemo {

    public static void main(String[] args) throws InterruptedException {
        Thread worker = new Thread(() -> {
            System.out.println("before park");

            LockSupport.park();

            System.out.println("after park");
        });

        worker.start();

        Thread.sleep(1000);

        LockSupport.unpark(worker);
    }
}
```

子线程执行到 `park()` 时，如果还没有 permit，就会阻塞。主线程一秒后调用 `unpark(worker)`，相当于给 `worker` 发放 permit，子线程因此从 `park()` 返回，继续向下执行。

## 2. unpark 可以早于 park，但 permit 不会累加

`LockSupport` 和 `wait/notify` 一个重要区别是：`unpark()` 可以先于 `park()` 发生。

```java
import java.util.concurrent.locks.LockSupport;

public class UnparkBeforeParkDemo {

    public static void main(String[] args) {
        Thread worker = new Thread(() -> {
            System.out.println("before park");

            LockSupport.park();

            System.out.println("after park");
        });

        worker.start();

        LockSupport.unpark(worker);
    }
}
```

即使主线程先执行了 `unpark(worker)`，子线程后执行 `park()` 时也可以直接通过，因为 permit 已经提前发放给了这个线程。`park()` 发现 permit 存在，就消耗它并返回。

但是 permit 不会累加。连续调用多次 `unpark()`，最多也只是把线程的 permit 设为 1：

```java
LockSupport.unpark(worker);
LockSupport.unpark(worker);
LockSupport.unpark(worker);
```

这三次调用不会给 `worker` 三个 permit。后续如果线程连续调用两次 `park()`，第一次可能直接通过，第二次如果没有新的 `unpark()`，仍然会阻塞：

```java
LockSupport.park(); // 消耗已有 permit，直接返回
LockSupport.park(); // 没有新的 permit，可能阻塞
```

所以 `LockSupport` 的 permit 更像一个 0/1 状态，而不是一个可以累加的计数器。

## 3. park 返回不代表条件已经满足

`park()` 只负责让线程暂停和恢复，不负责判断业务条件是否满足。线程从 `park()` 返回，可能有三种原因：

| 返回原因             | 含义                  |
| ---------------- | ------------------- |
| `unpark(thread)` | 其他线程给当前线程发放了 permit |
| `interrupt()`    | 当前线程被中断             |
| 伪唤醒              | 极少数情况下，线程可能无原因返回    |

因此，`park()` 外面通常不能只写一次 `if` 判断：

```java
if (!ready) {
    LockSupport.park();
}
```

更稳妥的写法是使用 `while` 反复检查条件：

```java
while (!ready) {
    LockSupport.park();
}
```

这里的核心不是循环本身，而是职责分离：`park()` 只负责阻塞当前线程，`ready` 这类共享状态才负责表达线程是否真的可以继续执行。

例如：

```java
import java.util.concurrent.locks.LockSupport;

public class ConditionParkDemo {

    private static volatile boolean ready = false;
    private static Thread worker;

    public static void main(String[] args) throws InterruptedException {
        worker = new Thread(() -> {
            while (!ready) {
                LockSupport.park();
            }

            System.out.println("condition satisfied");
        });

        worker.start();

        Thread.sleep(1000);

        ready = true;
        LockSupport.unpark(worker);
    }
}
```

这段代码里，`unpark(worker)` 只是让 `worker` 有机会从 `park()` 返回；真正决定它能不能继续执行的是 `ready == true`。如果线程因为中断或伪唤醒提前返回，`while` 会再次检查条件，条件不满足就继续等待。

## 4. interrupt 也会让 park 返回

`LockSupport.park()` 遇到中断时会返回，但它不会抛出 `InterruptedException`，也不会清除线程的中断标记。

```java
import java.util.concurrent.locks.LockSupport;

public class ParkInterruptDemo {

    public static void main(String[] args) throws InterruptedException {
        Thread worker = new Thread(() -> {
            System.out.println("before park");

            LockSupport.park();

            System.out.println("after park");
            System.out.println("isInterrupted = "
                    + Thread.currentThread().isInterrupted());
        });

        worker.start();

        Thread.sleep(1000);

        worker.interrupt();
    }
}
```

这段代码正常情况下会输出：

```text
before park
after park
isInterrupted = true
```

执行过程是：`worker` 线程先打印 `before park`，然后执行 `LockSupport.park()` 进入等待。主线程休眠 1 秒后调用 `worker.interrupt()`，中断会让正在 `park()` 的线程返回。由于 `park()` 不会抛出 `InterruptedException`，也不会清除中断标记，所以线程继续向下执行，打印 `after park`，最后通过 `Thread.currentThread().isInterrupted()` 读取到当前线程的中断标记，结果为 `true`。

这里如果把最后一行改成：

```java
System.out.println("interrupted = " + Thread.interrupted());
System.out.println("isInterrupted = "
        + Thread.currentThread().isInterrupted());
```

输出会变成：

```text
before park
after park
interrupted = true
isInterrupted = false
```

原因是 `Thread.interrupted()` 会读取并清除当前线程的中断标记，而 `isInterrupted()` 只读取，不清除。这个差异也是后面理解“先记录中断，再恢复中断标记”的基础。


这里要区分两个方法：

| 方法                                       | 作用对象 | 是否清除中断标记 |
| ---------------------------------------- | ---- | -------: |
| `Thread.currentThread().isInterrupted()` | 当前线程 |        否 |
| `thread.isInterrupted()`                 | 指定线程 |        否 |
| `Thread.interrupted()`                   | 当前线程 |        是 |

`Thread.interrupted()` 是静态方法，它检查的是当前线程，并且会清除当前线程的中断标记。这个细节在基于 `park()` 写等待逻辑时非常重要。

## 5. 等待过程中被中断，通常要记录并恢复中断标记

如果一个等待逻辑的语义是“即使被中断，也继续等待条件满足”，那么它不能因为 `park()` 被中断返回就直接退出。但它也不能把中断信号彻底吞掉，所以常见做法是：先清除并记录，最后再恢复。

```java
boolean interrupted = false;

while (!ready) {
    LockSupport.park(this);

    if (Thread.interrupted()) {
        interrupted = true;
    }
}

if (interrupted) {
    Thread.currentThread().interrupt();
}
```

这段代码可以拆开理解。

线程在 `park(this)` 中等待时，如果其他线程调用了当前线程的 `interrupt()`，`park()` 会返回。随后执行：

```java
Thread.interrupted()
```

如果当前线程确实被中断过，这个方法会返回 `true`，同时把当前线程的中断标记清除为 `false`。代码再用局部变量记录这件事：

```java
interrupted = true;
```

为什么要先清除中断标记？因为如果中断标记一直保持为 `true`，后面再次执行 `park()` 时可能会立即返回，线程无法真正阻塞，等待循环就可能变成忙等。

等条件最终满足后，再执行：

```java
Thread.currentThread().interrupt();
```

这一步是恢复中断标记。它表达的意思是：虽然当前等待逻辑没有因为中断而退出，但等待期间确实发生过中断，不能把这个信号吞掉。恢复之后，上层代码可以通过 `isInterrupted()` 感知到这件事，再决定是退出、清理、返回，还是继续执行。

## 6. park(Object blocker) 用来记录阻塞原因

除了无参 `park()`，源码中还经常能看到：

```java
LockSupport.park(this);
```

这里的 `this` 是 blocker，表示当前线程是因为哪个对象而阻塞的。它不改变 `park/unpark` 的语义，只是把阻塞原因记录下来，方便排查线程问题。

例如：

```java
import java.util.concurrent.locks.LockSupport;

public class BlockerDemo {

    public void waitHere() {
        LockSupport.park(this);
    }
}
```

当线程阻塞在这里时，使用线程 Dump 工具可能会看到类似信息：

```text
"worker-1" WAITING
    at java.util.concurrent.locks.LockSupport.park(...)
    - parking to wait for <0x0000000712345678> (a BlockerDemo)
```

如果只写 `LockSupport.park()`，线程 Dump 只能看到线程停在 `park()`；如果写 `LockSupport.park(this)`，还能看到它是因为哪个对象进入等待。这个参数不是唤醒条件，也不是锁本身的特殊逻辑，只是排查信息。

## 7. LockSupport 不维护等待队列

`LockSupport.unpark(thread)` 必须明确传入一个 `Thread`：

```java
LockSupport.unpark(worker);
```

这说明 `LockSupport` 不知道“有哪些线程在等待”，也不会自动选择应该唤醒谁。它只会对指定线程发放 permit。

因此，如果有多个线程需要排队等待，就必须由上层结构维护等待关系。例如 AQS 会维护同步队列，记录哪些线程在等、谁排在前面、释放锁时该唤醒谁。`LockSupport` 只在最终一步发挥作用：对某个确定的线程执行 `unpark(thread)`。

可以把职责分成三层：

| 职责        | 由谁负责                      |
| --------- | ------------------------- |
| 条件是否满足    | 上层状态，例如锁状态、任务状态、业务标志      |
| 哪些线程在等待   | 上层队列，例如 AQS 同步队列          |
| 线程如何暂停和唤醒 | `LockSupport.park/unpark` |

所以不要把 `LockSupport` 理解成完整的锁。它只是构建锁、同步器、阻塞队列等工具时使用的底层线程阻塞原语。

## 总结

本章的因果链条可以从线程等待开始理解：当一个线程暂时不能继续执行时，需要一种方式让它停止占用 CPU，于是有了 `park()`；当条件可能发生变化时，又需要其他线程能够指定唤醒它，于是有了 `unpark(thread)`。为了避免唤醒先于等待而丢失信号，`LockSupport` 使用每个线程自己的 permit 保存一次唤醒机会；为了避免线程被错误唤醒后直接继续执行，等待逻辑又必须在 `park()` 外层反复检查条件。

中断进一步说明了 `park()` 的边界：它只负责让线程返回，不负责决定线程是否退出等待，也不负责清理中断语义。是否继续等待、是否恢复中断标记、是否把中断交给上层处理，都属于调用方的设计。最终，`LockSupport` 解决的是“线程怎么停、怎么被指定线程叫醒”，但它不解决“条件是否满足”，也不解决“线程如何排队”。
