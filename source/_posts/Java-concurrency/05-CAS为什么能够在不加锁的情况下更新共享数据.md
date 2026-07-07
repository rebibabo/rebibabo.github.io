---
title: Java高并发底层原理（五）—— CAS 为什么能够在不加锁的情况下更新共享数据
date: 2026-07-02
abbrlink: 05
tags:
  - Java
  - 高并发
  - CAS
  - AtomicInteger
categories:
  - java-concurrency
---


`synchronized` 通过互斥保护临界区。一个线程持有锁时，其他线程不能进入同一同步区域，竞争激烈时还可能发生阻塞、唤醒和上下文切换。对于必须同时修改多份状态、执行复杂业务判断的场景，互斥是一种直接而可靠的方案；但对于计数器这类只更新一个值的操作，是否一定要让竞争失败的线程进入等待状态？

另一种思路是：线程先读取当前值，根据它计算新值，然后尝试写回；如果写回时发现原值已经被其他线程修改，就放弃本次结果，重新读取并再次尝试。这个过程不要求其他线程停止执行，也不需要把整个方法变成串行临界区。实现这种更新方式的核心操作就是 CAS。

## 1. 从 AtomicInteger 开始

上一章中的计数器可以改成 `AtomicInteger`：

```java
import java.util.concurrent.atomic.AtomicInteger;

public class CasCountDemo {

    private static final int TIMES = 1_000_000;

    static class Counter {

        private final AtomicInteger count = new AtomicInteger(0);

        public void increment() {
            count.incrementAndGet();
        }

        public int getCount() {
            return count.get();
        }
    }

    public static void main(String[] args) throws InterruptedException {
        Counter counter = new Counter();

        Thread threadA = new Thread(() -> {
            for (int i = 0; i < TIMES; i++) {
                counter.increment();
            }
        });

        Thread threadB = new Thread(() -> {
            for (int i = 0; i < TIMES; i++) {
                counter.increment();
            }
        });

        threadA.start();
        threadB.start();

        threadA.join();
        threadB.join();

        System.out.println("expected = " + TIMES * 2);
        System.out.println("actual   = " + counter.getCount());
    }
}
```

`AtomicInteger` 提供了一组原子更新方法，例如：

```java
incrementAndGet();
getAndIncrement();
addAndGet(10);
getAndAdd(10);
compareAndSet(expected, update);
```

`incrementAndGet()` 会执行自增并返回更新后的值，`getAndIncrement()` 会返回旧值再完成自增。它们都能够在多线程环境中保证单次更新不会发生丢失。

这里没有使用 `synchronized`，但不代表多个线程可以随意覆盖结果。`AtomicInteger` 内部仍然需要一种规则，判断当前线程计算出的新值是否还能安全写入。这个判断由 CAS 完成。

## 2. CAS 是什么

CAS 是 Compare And Swap 的缩写，通常翻译为“比较并交换”。一次 CAS 操作包含三个值：

- **Current**：内存中的当前值；
- **Expected**：线程认为内存中应该存在的值；
- **Update**：线程准备写入的新值。

它的逻辑可以写成：

```text
if Current == Expected:
    Current = Update
    return true
else:
    return false
```

关键在于，比较和写入必须作为一个不可分割的整体完成。线程不能在“比较成功”和“写入新值”之间被另一个线程插入修改，否则 CAS 自身也会产生竞态条件。JVM 会借助底层硬件提供的原子操作完成这一步，本章先把它视为 CPU 能够保证原子执行的一项能力。

例如，当前值为 `0`，线程希望把它更新为 `1`：

```java
boolean success = count.compareAndSet(0, 1);
```

如果执行时 `count` 仍然等于 `0`，CAS 更新成功并返回 `true`；如果其他线程已经把它修改成 `1`，当前线程的预期值失效，CAS 不会覆盖新值，而是返回 `false`。

## 3. 为什么失败时不能直接写回

`AtomicInteger` 提供了下面的方法：

```java
boolean compareAndSet(int expectedValue, int newValue)
```

它接收两个参数：

* `expectedValue`：线程期望当前变量保存的值；
* `newValue`：比较成功后准备写入的新值。

执行下面的代码：

```java
count.compareAndSet(0, 1);
```

表达的意思是：

> 只有当 `count` 当前仍然等于 `0` 时，才把它修改为 `1`。

如果 `count` 当前确实是 `0`，修改成功并返回 `true`；如果 `count` 已经被其他线程修改，不再等于 `0`，那么本次修改失败，原值保持不变，并返回 `false`。

需要注意，`expectedValue` 并不是直接从共享变量中重新读取的值，而是当前线程之前读取并保存的旧值。CAS 会拿这个旧值与共享变量此刻的真实值进行比较，以判断当前线程的计算结果是否已经过期。

假设 Thread A 和 Thread B 都读取到 `count = 0`，并分别计算出新值 `1`。它们都会尝试执行：

```java
count.compareAndSet(0, 1);
```

执行过程如下：

![](/images/Java-concurrency/IMG-20260707-000018.png)





Thread A 执行 `CAS(0, 1)` 时，共享变量仍然等于它期望的 `0`，因此更新成功，`count` 变成 `1`。

Thread B 随后也执行 `CAS(0, 1)`，但此时共享变量已经是 `1`，与它保存的期望值 `0` 不相等，因此更新失败。CAS 不会允许 Thread B 把基于旧值计算出的结果直接写回，否则 Thread A 的更新仍然会被覆盖。

Thread B 必须重新读取当前值 `1`，计算出新值 `2`，再执行：

```java
count.compareAndSet(1, 2);
```

此时共享变量仍然等于期望值 `1`，更新才会成功。

因此，CAS 避免丢失更新的关键在于：

> 写入之前先检查当前值是否仍然等于计算时读取的旧值。旧值已经发生变化，就放弃本次结果并重新计算。


## 4. CAS 循环是如何工作的

使用 `compareAndSet()` 可以手动实现一个自增循环：

```java
import java.util.concurrent.atomic.AtomicInteger;

public class CasCounter {

    private final AtomicInteger count = new AtomicInteger(0);

    public void increment() {
        int expected;
        int update;

        do {
            expected = count.get();
            update = expected + 1;
        } while (!count.compareAndSet(expected, update));
    }

    public int getCount() {
        return count.get();
    }
}
```

循环中的每一次尝试都分为三步：

1. 读取当前值，保存为 `expected`；
2. 根据 `expected` 计算新值 `update`；
3. 执行 `compareAndSet(expected, update)`。

CAS 成功时，循环结束；CAS 失败时，说明读取之后发生过其他线程的修改，当前线程放弃旧结果并重新执行。`AtomicInteger.incrementAndGet()` 的核心思想与这个循环相同，只是具体实现由 JDK 和 JVM 完成，并不需要业务代码手动编写。

这种结构通常称为 **CAS Loop** 或 **Retry Loop**：

![](/images/Java-concurrency/IMG-20260707-000019.png)






这个循环没有锁住整个方法。Thread A 失败时，Thread B 仍然可以继续执行；Thread B 失败时，Thread A 也不需要主动唤醒它。线程通过共享值本身判断本次计算是否仍然有效。

## 5. CAS 和 synchronized 的区别

`synchronized` 与 CAS 都可以保护共享数据，但它们处理竞争的方式不同。

`synchronized` 采用互斥方式。线程获得锁后进入临界区，其他竞争同一把锁的线程不能执行受保护代码。竞争失败的线程可能阻塞，直到锁被释放并重新获得调度机会。

CAS 采用验证和重试方式。线程先执行计算，再通过原子比较确认旧值是否仍然有效。竞争失败时，它通常不会因为一次失败就进入锁等待，而是重新读取并再次尝试。

可以把两种模型概括为：

![](/images/Java-concurrency/IMG-20260707-000020.png)





两者并不是简单的“慢”和“快”的关系。`synchronized` 适合保护包含多个步骤、多个字段或复杂业务规则的临界区；CAS 更适合围绕单个值或简单状态进行短时间更新。实际性能取决于竞争程度、更新成本、线程数量和具体实现。

## 6. 什么是乐观并发

锁的思路是：共享状态可能发生冲突，因此先取得独占权限，再开始修改。这种方式通常被称为偏保守的并发控制。

CAS 的思路是：先假设本次操作不会被其他线程干扰，直接读取并计算；真正写入之前再验证状态是否发生变化。如果没有变化就提交，如果已经变化就重试。这种方式通常称为**乐观并发控制（Optimistic Concurrency Control）**。

“乐观”并不表示忽略并发问题，也不表示更新一定成功。它只是把冲突检查推迟到提交阶段：

![](/images/Java-concurrency/IMG-20260707-000021.png)





当冲突较少时，大部分线程第一次 CAS 就能成功，避免了显式互斥和阻塞。当冲突频繁时，线程可能反复失败，前面完成的读取和计算会被丢弃，CPU 时间也会被消耗在重试上。

## 7. CAS 为什么常被称为非阻塞

CAS 常用于构建非阻塞算法。这里的“非阻塞”不是指线程永远不会暂停，也不是指操作一定马上成功，而是指一个线程的失败不会要求另一个线程释放锁后才能继续。

在锁模型中，Thread B 是否能进入临界区取决于 Thread A 何时释放锁。如果 Thread A 长时间持有锁，Thread B 就可能长时间等待。

在 CAS 模型中，Thread B 的一次尝试失败，通常意味着其他线程已经成功推进了共享状态。Thread B 可以读取新状态继续尝试，不需要等待某个特定线程执行解锁动作。

![](/images/Java-concurrency/IMG-20260707-000022.png)





这种整体进展能力是非阻塞算法的重要特征。但非阻塞不等于没有成本。线程可能在循环中连续失败，虽然没有进入传统的锁等待，却仍然无法完成自己的操作。

## 8. CAS 在低竞争下为什么有效

假设多个线程偶尔更新一个计数器，而且每次更新只做一次加法。在大部分时刻，线程读取值以后，没有其他线程恰好在 CAS 前修改它，那么第一次尝试就能成功。

一次成功过程大致包含：

![](/images/Java-concurrency/IMG-20260707-000023.png)





没有竞争线程需要进入等待队列，也不需要因为锁释放而执行唤醒。对于非常短的单值更新，这种路径通常比较直接。

CAS 还允许多个线程同时完成读取和计算，只有最终提交阶段需要对同一位置进行原子竞争。虽然最终仍然只有一个线程能成功更新某个旧值，但其他线程不会在整个计算期间都被排除在外。

## 9. 高竞争下 CAS 会发生什么

当大量线程持续修改同一个值时，一个线程从读取到执行 CAS 之间，很可能已经有其他线程完成更新。CAS 失败次数随竞争增加而上升，线程会不断执行读取、计算和比较。

![](/images/Java-concurrency/IMG-20260707-000024.png)





这些失败不会产生正确性问题，但会消耗 CPU。线程没有阻塞，并不意味着资源没有被使用；相反，重试循环会持续执行指令。竞争极端激烈时，大量线程可能围绕同一个值反复重试，真正成功的操作只占少数。

因此，CAS 更适合：

- 更新过程很短；
- 共享状态较简单；
- 冲突概率较低；
- 失败后重新计算的成本较小。

如果一次更新需要复杂计算、远程调用或同时维护多个字段，CAS 失败后重新执行的代价可能很高，也很难用一个简单的比较值表达完整约束。

## 10. CAS 能比较对象引用吗

CAS 不只能比较整数，也可以比较对象引用。Java 提供了 `AtomicReference`，用于原子地读取和替换一个对象引用。

如果一份业务状态包含多个字段，可以把这些字段封装到一个不可变对象中，再通过 CAS 整体替换这个对象：

```java
import java.util.concurrent.atomic.AtomicReference;

record AccountState(int balance, long version) {
}

class Account {

    private final AtomicReference<AccountState> state =
            new AtomicReference<>(new AccountState(1000, 0));

    public void deposit(int amount) {
        while (true) {
            AccountState expected = state.get();

            AccountState update = new AccountState(
                    expected.balance() + amount,
                    expected.version() + 1
            );

            if (state.compareAndSet(expected, update)) {
                return;
            }
        }
    }
}
```

线程首先通过 `state.get()` 取得当前状态对象，并根据它创建一个新的 `AccountState`。随后执行：

```java
state.compareAndSet(expected, update);
```

它表达的含义是：

> 只有当 `state` 当前仍然指向 `expected` 对象时，才把它替换成 `update`。

这里比较的不是对象中的 `balance` 和 `version` 字段，也不会调用对象的 `equals()` 方法，而是比较当前引用是否仍然指向同一个对象。

假设 Thread A 和 Thread B 同时读取到同一个状态对象：

```text
expected → AccountState(balance = 1000, version = 0)
```

Thread A 创建的新状态是：

```text
AccountState(balance = 1100, version = 1)
```

Thread B 创建的新状态是：

```text
AccountState(balance = 1200, version = 1)
```

如果 Thread A 先完成替换，`state` 就不再指向原来的 `expected`。Thread B 随后的 CAS 会失败，因为它计算新状态时使用的旧对象已经过期。Thread B 必须重新读取最新状态，再重新计算。

因此，CAS 仍然只比较一个共享位置，只不过这个位置保存的是对象引用。对象本身可以包含多个字段，从而把一组相关状态作为一个整体进行替换。

这种写法通常要求状态对象不可变。线程读取到旧对象后，只根据它创建新对象，而不直接修改旧对象内部字段。这样才能保证 `expected` 在 CAS 执行前保持稳定，也能避免多个线程同时修改同一个对象内部状态。

不过，只比较当前引用是否等于旧引用，也存在一个特殊问题：如果引用中途发生变化，最后又恢复成原来的对象，CAS 是否还能发现这次变化？

## 11. CAS 的 ABA 问题

假设一个无锁栈使用 `AtomicReference<Node>` 保存栈顶节点：

```java
private final AtomicReference<Node> top = new AtomicReference<>();
```

执行出栈操作时，线程先读取当前栈顶节点，再准备把栈顶替换为它的下一个节点：

```java
Node expected = top.get();
Node update = expected.next;

top.compareAndSet(expected, update);
```

假设初始栈结构如下：

![](/images/Java-concurrency/IMG-20260707-000025.png)





Thread A 准备弹出 `Node A`，因此保存了两个引用：

```text
expected = Node A
update   = Node B
```

在 Thread A 执行 CAS 之前，它暂时停止运行。此时 Thread B 连续完成三个操作：

1. 弹出 `Node A`；
2. 弹出 `Node B`；
3. 把原来的 `Node A` 再次放回栈顶。

栈结构发生了下面的变化：

![](/images/Java-concurrency/IMG-20260707-000026.png)





Thread A 恢复执行后，发现栈顶仍然指向原来的 `Node A`，于是执行：

```java
top.compareAndSet(nodeA, nodeB);
```

CAS 比较成功，因为当前引用确实仍然等于 `nodeA`。随后，栈顶被修改成 Thread A 之前保存的 `nodeB`。

问题在于，当前栈的结构已经发生变化。`Node B` 已经被 Thread B 弹出，不再是 `Node A` 当前的下一个节点。Thread A 使用的是变化之前保存的旧关系，因此把一个已经失效的节点重新设置成了栈顶。

从引用值上看，栈顶经历了下面的变化：

![](/images/Java-concurrency/IMG-20260707-000027.png)





最终值仍然是 `Node A`，但中间已经发生过修改。这种现象称为 **ABA Problem**：

> 一个值最初是 A，中间变成 B，之后又恢复成 A。CAS 只能看到当前值仍然是 A，无法判断中间是否发生过变化。

ABA 并不表示 CAS 的原子性失效。CAS 正确完成了“当前引用是否等于预期引用”的比较，只是这个比较条件不足以描述完整状态。

对于普通计数器来说，数值从 `10` 变成 `11`，再变回 `10`，中间过程可能并不影响业务结果；但对于链表节点、栈顶引用、对象生命周期或资源状态，中间是否发生过变化往往非常重要。

常见的解决方式是为引用增加版本号。每次修改引用时，同时递增版本：

![](/images/Java-concurrency/IMG-20260707-000028.png)





虽然引用重新变成了 `Node A`，版本号已经从 `1` 变成 `3`。Thread A 原来读取的状态是：

```text
Node A, version 1
```

当前状态则是：

```text
Node A, version 3
```

引用相同，但版本号不同，因此 CAS 失败。

Java 提供了 `AtomicStampedReference`，可以同时保存对象引用和版本号：

```java
AtomicStampedReference<Node> top =
        new AtomicStampedReference<>(nodeA, 1);
```

更新时需要同时提供预期引用、目标引用、预期版本和新版本：

```java
top.compareAndSet(
        expectedReference,
        newReference,
        expectedStamp,
        newStamp
);
```

`AtomicStampedReference` 不只检查当前对象是否仍然相同，还会检查版本号是否保持不变。即使引用经历变化后重新指向原对象，版本号也能反映期间发生过修改。

ABA 问题的本质不是值不能恢复成原值，而是：

> 仅比较当前值是否相等，可能不足以判断这份状态是否仍然是线程最初读取到的状态。


## 12. AtomicInteger 保证了什么

`AtomicInteger` 中以原子方式更新值的方法，可以保证单次操作在并发环境中不发生丢失更新，例如：

```java
count.incrementAndGet();
count.compareAndSet(10, 11);
count.getAndAdd(5);
```

但把多个原子方法组合在一起，不会自动变成一个更大的原子操作：

```java
if (count.get() < 100) {
    count.incrementAndGet();
}
```

`get()` 和 `incrementAndGet()` 分别是原子的，但“先检查小于 100，再执行加一”由两个独立操作组成。多个线程可能同时看到 `count = 99`，然后分别执行自增，最终超过限制。

如果整个业务要求是“只有小于 100 时才能加一”，就需要把判断条件合并进 CAS 循环：

```java
public boolean incrementIfLessThan(
        AtomicInteger count,
        int limit
) {
    while (true) {
        int expected = count.get();

        if (expected >= limit) {
            return false;
        }

        int update = expected + 1;

        if (count.compareAndSet(expected, update)) {
            return true;
        }
    }
}
```

这段代码每次 CAS 都同时验证“我计算时看到的值是否仍然有效”。如果其他线程已经修改，当前线程重新检查限制并重新计算。由此可以看出，原子类保证的是具体原子方法的语义，不会自动理解业务代码中多个方法之间的关系。

## 13. CAS 与业务不变量

并发控制的目标不是让某一行代码看起来安全，而是保护业务不变量。计数器的不变量可能只是“每次调用必须增加一次”；库存的不变量可能是“库存不能小于零”；账户的不变量可能是“转账前后总金额保持一致”。

CAS 能否直接使用，取决于业务不变量能否表达为“当状态仍然等于 expected 时，把它替换为 update”。对于单个计数、单个状态机或不可变对象整体替换，这种表达通常比较自然；对于需要同时修改多个相互独立对象的操作，单个 CAS 往往不足以覆盖完整边界。

例如转账涉及两个账户：

```text
Source Account: balance - amount
Target Account: balance + amount
```

只对源账户余额执行一次 CAS，并不能保证目标账户一定完成对应增加。此时需要更完整的事务或同步设计，而不是因为 CAS 非阻塞就强行使用。

因此，CAS 是一种底层并发原语，不是替代所有锁的通用方案。选择 CAS 还是互斥，首先取决于需要保护的状态结构和业务约束，其次才是性能。


## 14. synchronized 和 CAS 应该如何选择

`synchronized` 和 CAS 都可以解决共享数据的并发修改问题，但处理竞争的方式不同。

`synchronized` 会让线程先获得锁。一个线程进入临界区后，其他线程只能等待；CAS 不会先加锁，而是在写入前比较当前值是否仍然等于旧值，失败后重新读取并重试。

| 对比项  | synchronized | CAS             |
| ---- | ------------ | --------------- |
| 竞争方式 | 获得锁后独占执行     | 比较失败后重试         |
| 失败线程 | 可能阻塞         | 通常继续占用 CPU 重试   |
| 适用范围 | 多行代码、多个关联状态  | 单个值或对象引用        |
| 主要成本 | 阻塞、唤醒、上下文切换  | CAS 失败和空转重试     |
| 常见问题 | 锁竞争、死锁       | ABA、高竞争下 CPU 消耗 |

CAS 更适合计数器、状态标记、引用替换等简单更新。操作时间短、竞争不激烈时，大部分线程一次尝试就能成功，不需要进入阻塞状态。

```java
AtomicInteger count = new AtomicInteger();

count.incrementAndGet();
```

`synchronized` 更适合需要同时判断和修改多个关联状态的业务操作。例如余额检查和扣款必须作为一个整体执行：

```java
public synchronized boolean withdraw(int amount) {
    if (balance < amount) {
        return false;
    }

    balance -= amount;
    transactionCount++;
    return true;
}
```

CAS 并不一定比 `synchronized` 快。竞争激烈时，大量线程可能不断 CAS 失败并重新计算，持续占用 CPU；`synchronized` 虽然存在阻塞和调度成本，但阻塞线程不会一直消耗 CPU。

因此，选择时可以遵循一个基本原则：

> 简单、短小、低竞争的单值更新适合 CAS；复杂、多状态或高竞争的临界区更适合 synchronized。

无论选择哪一种方式，首先都要保证完整的业务操作不会被并发执行破坏，再考虑性能。


## 本章总结

CAS 通过“比较当前值是否仍然等于预期值”来判断线程基于旧状态计算出的结果是否有效。比较和写入作为一个原子步骤执行：预期值没有变化就提交新值，预期值已经失效就拒绝写入。失败线程重新读取、重新计算并再次尝试，因此不会把过期结果覆盖到新状态上。

本章的核心结论包括：

- CAS 包含当前值、预期值和更新值三个要素；
- 比较与写入必须以原子方式完成；
- CAS 失败表示线程读取的旧状态已经失效；
- CAS 循环通过失败重试避免丢失更新；
- CAS 不要求线程先获得独占锁，常用于构建非阻塞更新；
- 低竞争时失败次数较少，高竞争时反复重试会消耗 CPU；
- `AtomicInteger` 适合单值原子更新，但多个原子方法组合后不一定仍然原子；
- ABA 表明“当前值相同”不一定代表“期间没有发生变化”；
- CAS 是否适合某个场景，取决于业务不变量能否被一个可比较状态完整表达。

CAS 最终仍然需要底层硬件保证比较和写入的原子性。下一步需要继续向下分析：多个 CPU Core 拥有各自的 Cache 时，硬件如何保证一个 Core 执行 CAS 的过程中，其他 Core 不能同时破坏同一位置的状态。
