---
title: Java高并发底层原理（六）—— 多核 CPU 如何保持缓存一致
date: 2026-07-02
abbrlink: 06
tags:
  - Java
  - 高并发
  - CPU Cache
  - MESI
categories:
  - java-concurrency
---


CAS 能够在不使用 Java 锁的情况下完成原子更新，但它仍然需要硬件保证“比较”和“写入”不会被其他 CPU Core 同时破坏。问题在于，现代 CPU 不会让每个 Core 都直接访问主内存。为了缩小 CPU 与内存之间的速度差距，数据通常会先进入 Cache，同一份数据也可能同时出现在多个 Core 的缓存中。

当一个 Core 修改自己的缓存副本时，其他 Core 如何知道旧副本已经失效？两个 Core 同时准备修改同一份数据时，硬件如何决定谁先获得写入权限？这些问题由缓存一致性机制处理。

## 1. 同一份数据为什么会有多个副本

假设 Heap 中存在一个 `Counter` 对象：

```java
class Counter {
    int count = 0;
}
```

Thread A 运行在 Core 1，Thread B 运行在 Core 2。两个线程都读取 `count` 时，处理器可能把包含 `count` 的数据分别加载到两个 Core 的 Cache 中。

![](/images/Java-concurrency/IMG-20260707-000029.png)





从 Java 程序的角度看，`count` 只有一份；从硬件执行过程看，它可能存在多个缓存副本。Cache 的作用就是让 Core 尽量在附近读取数据，而不是每次都等待主内存。

不同处理器的缓存结构并不完全相同。常见设计是每个 Core 拥有私有的 L1、L2 Cache，多个 Core 共享更大的末级缓存，但具体层级和共享方式由硬件决定。无论结构如何变化，只要同一份数据能够同时被多个 Core 缓存，就需要解决副本一致性问题。

## 2. CPU 以 Cache Line 为单位读取数据

CPU Cache 通常不会只加载一个 Java 字段，而是一次加载一整块连续数据，这个基本单位称为 **Cache Line**。常见桌面和服务器处理器的 Cache Line 为 64 字节，但具体大小取决于硬件平台。

假设程序只读取一个 4 字节的 `int`，CPU 仍然会把它所在的整条 Cache Line 加载到缓存中：

![](/images/Java-concurrency/IMG-20260707-000030.png)





这样设计是为了利用局部性。程序访问某个位置后，通常还会继续访问附近的数据，一次读取一整块往往比每次只读取几个字节更高效。

缓存一致性协议跟踪的通常也是 Cache Line，而不是单独的 Java 字段。Core 只修改其中一个字段时，其他 Core 中对应的整条 Cache Line 都可能失效。

## 3. 修改 Cache 不等于立即写回主内存

现代 CPU 通常使用写回缓存策略。Core 修改数据时，可以先修改自己的 Cache Line，并把它标记为已修改，稍后再写回主内存。这样可以把多次连续写入合并，减少访问主内存的次数。

例如，Core 1 连续把某个值从 `0` 修改到 `1`、`2`、`3`，没有必要每次都等待主内存完成写入。只要硬件能够保证其他 Core 不再使用过期副本，修改就可以先保留在 Cache 中。

因此，线程能否看到最新值，不能只理解成“数据是否已经写回主内存”。更准确地说，需要关注两个问题：

- 其他 Core 中的旧副本是否已经失效；
- 其他 Core 下一次读取时能否取得最新数据。

缓存一致性机制负责协调这些缓存副本，而不是要求所有读写都绕过 Cache 直接访问主内存。

## 4. 缓存一致性协议要解决什么问题

假设 Core 1 和 Core 2 都缓存了同一条 Cache Line。只要两个 Core 都只读取，两个副本可以同时存在；一旦某个 Core 准备修改，硬件就必须保证其他 Core 不能继续把旧副本当作有效数据。

缓存一致性机制主要解决两个问题：

1. 同一条 Cache Line 不能同时被多个 Core 以可修改状态持有；
2. 一个 Core 完成修改后，其他 Core 不能继续使用旧副本。

写入过程可以简化为：

![](/images/Java-concurrency/IMG-20260707-000031.png)





这里的 `ownership` 是 Cache Line 的硬件修改权限，不是 Java 对象锁。`synchronized` 保护的是一段业务代码，缓存一致性协议协调的是多个 Core 对同一条 Cache Line 的读写，两者处于不同层次。

## 5. MESI 的四种状态

MESI 是一种经典的缓存一致性协议模型，名称来自四种状态的首字母：

| 状态 | 含义 |
|---|---|
| Modified | 当前 Core 独占并修改过这条 Cache Line，内容可能与主内存不同 |
| Exclusive | 当前 Core 独占这条 Cache Line，内容与主内存一致 |
| Shared | 多个 Core 可以持有相同的只读副本 |
| Invalid | 当前副本已经失效，不能继续读取 |


真实处理器可能使用 MESIF、MOESI 或其他扩展协议，并加入更多优化状态。本章使用 MESI 只是为了建立一个清晰模型，重点不是记住每一种状态转换，而是理解共享读取、独占修改和副本失效。

## 6. 多个 Core 读取同一份数据

假设 Core 1 首先读取 `count`，并且其他 Core 中没有对应副本，Core 1 可能以 Exclusive 状态持有这条 Cache Line：

```text
Core 1: Exclusive
Core 2: Invalid
```

随后 Core 2 也读取 `count`。两个 Core 都只读取，不会破坏数据，因此它们可以同时持有 Shared 状态的副本：

```text
Core 1: Shared
Core 2: Shared
```

![](/images/Java-concurrency/IMG-20260707-000032.png)





Shared 状态允许多个 Core 并发读取。只要没有 Core 发起写入，这些副本都可以继续使用。

## 7. 一个 Core 修改数据时会发生什么

如果 Core 1 准备把 `count` 从 `0` 修改为 `1`，它不能直接在 Shared 状态下写入，因为 Core 2 仍然持有有效副本。Core 1 必须先取得独占修改权限，并让 Core 2 的副本失效。

![](/images/Java-concurrency/IMG-20260707-000033.png)





Core 2 再次读取 `count` 时，会发现自己的 Cache Line 已经处于 Invalid 状态，不能继续返回旧值 `0`。它必须重新取得有效数据，最终看到 Core 1 修改后的结果。在许多处理器中，最新的 Cache Line 可以通过 CPU 内部的缓存一致性互连，直接从 Core 1 的 Cache 传递给 Core 2，不需要先写回主内存再重新读取。


这些失效通知和状态转换由处理器自动完成。Java 程序不需要手动清除 CPU Cache，也不能通过普通代码直接控制某条 Cache Line 的 MESI 状态。

## 8. 两个 Core 同时修改会发生什么

如果 Core 1 和 Core 2 同时准备修改处于 Shared 状态的同一条 Cache Line，它们都会请求独占权限。硬件不能同时批准两个请求，否则两个 Core 会各自修改自己的副本，再次产生不一致。

处理器会通过内部互连结构对请求进行协调，只有一个 Core 能先取得这条 Cache Line 的修改权限。另一个 Core 的副本会失效，它必须等待或重新取得最新状态后再尝试。

![](/images/Java-concurrency/IMG-20260707-000034.png)





多个 Core 频繁修改同一条 Cache Line 时，修改权限会不断在 Core 之间转移。Cache Line 反复失效、重新获取，常被形容为在不同 Core 之间“来回弹跳”。即使程序只修改一个整数，硬件仍然需要协调一整条 Cache Line。

## 9. CAS 为什么需要硬件支持

CAS 必须原子地完成“比较当前值”和“写入新值”。假设 Core 1 执行：

```text
CAS(expected = 0, newValue = 1)
```

处理器需要保证，在比较当前值是否为 `0` 并决定是否写入 `1` 的过程中，其他 Core 不能同时完成冲突写入。否则，比较成功后再写入的结果仍然可能覆盖其他线程的修改。

CAS 的硬件过程可以概括为：

![](/images/Java-concurrency/IMG-20260707-000035.png)





不同 CPU 架构使用的实现方式并不完全相同。有些架构提供原子读改写指令，有些架构通过一组配套指令完成条件更新。具体指令可以不同，但都必须保证比较和写入作为一个原子动作完成。

因此，CAS 并不是完全不需要互斥。它没有使用 Java Monitor，也不会先把整个方法锁住，但硬件仍然需要协调目标内存位置的修改权限。更准确的说法是：

> CAS 不使用线程级互斥锁，而是依赖 CPU 提供的原子读改写能力。

## 10. 为什么 CAS 竞争也有成本

CAS 不会像 `synchronized` 那样先让一个线程独占整段临界区，但多个 Core 同时更新同一个值时，仍然会争夺对应 Cache Line 的修改权限。

假设十个线程不断对同一个 `AtomicInteger` 自增。每一轮只有一个线程能够基于某个旧值更新成功，其他线程的 CAS 会失败，然后重新读取并重试。与此同时，Cache Line 的所有权也可能在多个 Core 之间反复转移。

CAS 的主要成本包括：

- 失败后的重复读取和计算；
- 持续占用 CPU 执行重试；
- Cache Line 在多个 Core 之间频繁转移；
- 其他 Core 中对应副本反复失效。

这也是 CAS 在低竞争场景中通常表现较好，而在高竞争场景中可能出现明显性能下降的原因。它避免的是线程阻塞，不是竞争本身。

## 11. 缓存一致性不等于线程可见性

缓存一致性协议能够保证同一条 Cache Line 的多个副本不会长期保持相互冲突的有效状态，但这并不等于 Java 程序中的所有读写都会按照源码顺序立刻被其他线程观察到。

处理器可能使用 Store Buffer 暂存写入，编译器和 JVM 也可能在不破坏单线程语义的前提下调整指令顺序。例如：

```java
data = 42;
ready = true;
```

另一个线程执行：

```java
if (ready) {
    System.out.println(data);
}
```

程序希望另一个线程看到 `ready == true` 时，`data` 已经等于 `42`。缓存一致性协议能够处理 `data` 和 `ready` 各自的缓存副本，但它并不单独规定这两个写操作必须以什么顺序对其他线程可见。

因此，需要区分三个概念：

- **Cache Coherence**：同一内存位置的多个缓存副本如何保持一致；
- **Memory Ordering**：多个内存操作以什么顺序完成并对外可见；
- **Thread Safety**：所有合法执行顺序是否都能得到正确业务结果。

缓存一致性是 Java 并发的硬件基础之一，但不是完整答案。Java 还需要在 JVM 和语言层定义统一的内存规则。

## 12. 什么是伪共享

Cache Line 是缓存一致性协议维护的基本单位，因此两个完全不同的变量只要位于同一条 Cache Line 中，也可能互相影响。这种现象称为**伪共享（False Sharing）**。

假设 Thread A 只修改 `left`，Thread B 只修改 `right`：

```java
class PairCounter {
    long left;
    long right;
}
```

从业务逻辑看，两个线程没有修改同一个字段；但如果 `left` 和 `right` 位于同一条 Cache Line，Core 1 修改 `left` 时会取得整条 Cache Line 的修改权限，使 Core 2 中包含 `right` 的副本失效。Core 2 随后修改 `right`，又会让 Core 1 的副本失效。

![](/images/Java-concurrency/IMG-20260707-000036.png)





两个线程没有业务上的数据竞争，却因为共享同一条 Cache Line 而产生硬件争用，所以称为伪共享。它通常会造成 Cache Line 频繁失效、重新加载和迁移，最终降低吞吐量。

伪共享主要出现在高频计数器、队列游标和性能敏感的数据结构中。普通业务代码不应该仅凭字段相邻就随意增加填充，因为对象布局还受到 JVM、字段重排、对象头和硬件平台影响。只有通过性能分析确认瓶颈后，才需要专门处理。

## 13. LongAdder 为什么适合高竞争计数

`AtomicInteger` 只有一个共享值。所有线程执行自增时，都要对这个值进行 CAS：

![](/images/Java-concurrency/IMG-20260707-000037.png)





线程较少时，这种方式没有问题；线程很多时，大量 CAS 会集中在同一个变量上。一个线程更新成功后，其他线程基于旧值执行的 CAS 会失败，只能重新读取并重试。这个值所在的 Cache Line 也会在多个 Core 之间频繁转移。

`LongAdder` 不让所有线程一直竞争同一个值，而是把总数拆成一个 `base` 和多个 `Cell`：

![](/images/Java-concurrency/IMG-20260707-000038.png)





刚开始没有竞争时，线程会优先使用 `base`，效果与普通原子计数器类似：

![](/images/Java-concurrency/IMG-20260707-000039.png)





如果多个线程同时更新 `base`，其中一些线程 CAS 失败，`LongAdder` 就会创建 `Cell` 数组，把后续更新分散到不同的 Cell 中：

![](/images/Java-concurrency/IMG-20260707-000040.png)





线程并不是永久绑定某个 Cell，也不是一个 Core 固定对应一个 Cell。`LongAdder` 会根据线程自身的探测值选择 Cell；如果选中的 Cell 仍然竞争激烈，还可以尝试其他位置，并在需要时扩容 Cell 数组。

每个 Cell 都有自己的数值，线程通常只需要对选中的 Cell 执行 CAS：

```java
cell.value = cell.value + 1;
```

实际更新仍然依赖 CAS，只是竞争从一个共享变量分散到了多个 Cell。原来所有线程都争抢同一个位置，现在不同线程更可能修改不同位置，因此 CAS 失败次数和 Cache Line 争用都会减少。

读取总数时，`LongAdder` 会把 `base` 和所有 Cell 相加：

```java
long total = base;

for (Cell cell : cells) {
    total += cell.value;
}
```

使用方式如下：

```java
LongAdder adder = new LongAdder();

adder.increment();
adder.add(10);

long total = adder.sum();
```

这种拆分并没有减少自增次数，而是把更新压力分散到多个内存位置，因此 `LongAdder` 在大量线程频繁计数时，通常比 `AtomicInteger` 更适合。

不过，调用 `sum()` 时，其他线程仍然可能继续更新不同的 Cell，所以汇总结果不一定对应某个严格瞬间的值。`LongAdder` 适合请求次数、事件数量等统计场景，不适合“余额是否足够”“库存是否大于零”这类需要读取后立即判断并更新的业务逻辑。


## 本章总结

现代 CPU 使用多级 Cache 缩小 Core 与主内存之间的速度差距，同一份数据也可能同时存在多个缓存副本。缓存一致性协议通过跟踪 Cache Line 状态、协调修改权限和发送失效通知，保证多个 Core 不会长期使用相互冲突的有效副本。

本章的核心结论包括：

- CPU 通常以 Cache Line 为单位读取和维护缓存数据；
- 修改可以先发生在 Cache 中，不必每次立即写回主内存；
- 多个 Core 可以同时读取同一条 Cache Line，但修改前必须取得独占权限；
- MESI 使用 Modified、Exclusive、Shared 和 Invalid 描述缓存状态；
- 多个 Core 同时修改时，硬件必须协调 Cache Line 的所有权；
- CAS 依赖 CPU 提供的原子读改写能力；
- CAS 避免了线程级锁，但高竞争下仍然会发生重试和 Cache Line 争用；
- 缓存一致性只解决同一内存位置的副本一致，不等于完整的线程可见性；
- 不同字段位于同一条 Cache Line 时，可能发生伪共享；
- `LongAdder` 通过分散热点降低高并发计数时的 Cache Line 竞争。

缓存一致性解决了多个 Core 如何围绕同一份数据协作的问题，但还没有解释多个读写操作之间的可见顺序。下一章将继续分析 Java 中的可见性、指令重排和 `volatile`。
