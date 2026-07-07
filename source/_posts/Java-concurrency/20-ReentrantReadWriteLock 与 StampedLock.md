---

title: Java高并发底层原理（二十）—— ReentrantReadWriteLock 与 StampedLock
date: 2026-07-04
abbrlink: 20
tags:
- Java
- 高并发
- AQS
- ReentrantReadWriteLock
- StampedLock
categories:
- java-concurrency
-------------

## 一、从互斥锁到读写锁

普通互斥锁解决的是“同一时刻只能有一个线程进入临界区”的问题。无论临界区里是读取数据，还是修改数据，只要一个线程持有锁，其他线程都必须等待。

以一个二维坐标对象为例：

```java
class Point {
    private double x;
    private double y;

    double distanceFromOrigin() {
        return Math.sqrt(x * x + y * y);
    }

    void move(double deltaX, double deltaY) {
        x += deltaX;
        y += deltaY;
    }
}
```

`distanceFromOrigin()` 只是读取 `x` 和 `y`，`move()` 才会修改它们。如果所有方法都用同一把互斥锁保护，那么多个读线程之间也会互相阻塞。但从语义上看，多个线程同时读并不会破坏 `x / y` 的一致性，真正需要互斥的是读和写、写和写。

读写锁就是在这个问题上继续细分锁语义：读操作之间可以共享，写操作仍然独占。

| 操作关系  | 是否可以并发 | 原因                |
| ----- | ------ | ----------------- |
| 读 + 读 | 可以     | 多个线程只读取数据，不修改共享状态 |
| 读 + 写 | 不可以    | 写线程可能改变读线程正在读取的数据 |
| 写 + 写 | 不可以    | 多个写线程同时修改会破坏一致性   |

`ReentrantReadWriteLock` 对外暴露读锁和写锁两个入口：

```java
private final ReentrantReadWriteLock rw = new ReentrantReadWriteLock();
private final Lock readLock = rw.readLock();
private final Lock writeLock = rw.writeLock();
```

改造后的 `Point` 可以写成：

```java
class Point {
    private double x;
    private double y;

    private final ReentrantReadWriteLock rw = new ReentrantReadWriteLock();
    private final Lock readLock = rw.readLock();
    private final Lock writeLock = rw.writeLock();

    double distanceFromOrigin() {
        readLock.lock();
        try {
            return Math.sqrt(x * x + y * y);
        } finally {
            readLock.unlock();
        }
    }

    void move(double deltaX, double deltaY) {
        writeLock.lock();
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            writeLock.unlock();
        }
    }
}
```

这段代码的重点不是 API 本身，而是锁语义发生了变化：读方法不再和其他读方法互斥，但仍然会和写方法互斥。

## 二、两个锁入口为什么要共用同一份状态

`ReentrantReadWriteLock` 表面上有两个锁：`ReadLock` 和 `WriteLock`。但它们不能真的各管各的，因为读锁和写锁之间必须互相感知。

读线程申请读锁时，需要知道当前有没有写线程正在写；写线程申请写锁时，需要知道当前有没有读线程正在读，以及有没有其他写线程正在写。因此，读锁和写锁背后必须共享同一份同步状态。

![](/images/Java-concurrency/IMG-20260707-000095.png)


可以把 `ReadLock` 和 `WriteLock` 理解成两个入口，把 `Sync` 理解成统一的状态管理者。线程从不同入口进入，但最终都要根据同一份状态判断能不能获取锁。

这个设计和普通互斥锁不同。普通 `ReentrantLock` 只需要表达一种独占语义，`state = 0` 表示没有线程持有锁，`state > 0` 表示锁被某个线程持有并可能发生重入。而读写锁要同时表达读锁数量和写锁重入次数，所以它需要在同一个状态值里编码两类信息。

## 三、state 如何同时表示读锁和写锁

AQS 中的核心状态是一个 `int`：

```java
private volatile int state;
```

`state` 不是对象，也不保存线程对象。它只是一个整数。`ReentrantReadWriteLock` 把这个 32 bit 的整数拆成高低两部分：

```text
state = 00000000 00000000 00000000 00000000
        └────── high 16 bit ─────┘ └────── low 16 bit ──────┘
              read count                 write count
```

高 16 bit 表示读锁总数，低 16 bit 表示写锁重入次数。

源码中的核心常量也体现了这个拆分思路：

```java
static final int SHARED_SHIFT   = 16;
static final int SHARED_UNIT    = (1 << SHARED_SHIFT);
static final int MAX_COUNT      = (1 << SHARED_SHIFT) - 1;
static final int EXCLUSIVE_MASK = (1 << SHARED_SHIFT) - 1;
```

写锁增加一次，本质上是低 16 bit 加 1：

```java
state + 1
```

读锁增加一次，本质上是高 16 bit 加 1，也就是：

```java
state + (1 << 16)
```

因此，读写计数可以这样取出：

```java
int writeCount = state & 0xFFFF;
int readCount  = state >>> 16;
```

写锁放在低 16 bit，是因为它和普通独占锁类似，重入时直接加 1，释放时直接减 1。读锁放在高 16 bit，则是为了和写锁计数隔离，避免两类计数互相影响。

## 四、写锁和读锁的申请规则

在前面的 `state` 拆分基础上，写锁的判断逻辑就比较直接了：写锁是独占锁，它要求当前没有读锁；如果已经有写锁，则只能是当前线程自己重入。

| 当前状态       | 写锁是否可以获取 | 说明          |
| ---------- | -------- | ----------- |
| 没有读锁，没有写锁  | 可以       | 当前没有任何线程持有锁 |
| 当前线程已经持有写锁 | 可以       | 写锁可重入       |
| 有读锁        | 不可以      | 读写互斥        |
| 别的线程持有写锁   | 不可以      | 写写互斥        |

读锁的判断规则不同。读锁只排斥“别人持有的写锁”。如果当前没有写锁，读线程可以获取读锁；如果写锁正由当前线程自己持有，当前线程也可以继续获取读锁。

| 当前状态     | 读锁是否可以获取 | 说明              |
| -------- | -------- | --------------- |
| 没有写锁     | 可以       | 读读共享            |
| 别的线程持有写锁 | 不可以      | 写锁独占            |
| 当前线程持有写锁 | 可以       | 当前线程已经独占数据，可以再读 |

因此，`ReentrantReadWriteLock` 的基本规则可以压缩为两句话：写锁怕任何读锁，也怕别人持有的写锁；读锁只怕别人持有的写锁。

## 五、为什么写锁可以降级为读锁

由于当前线程持有写锁时可以继续获取读锁，所以 `ReentrantReadWriteLock` 支持锁降级。锁降级指的是线程先以写锁身份修改数据，然后在释放写锁之前先获取读锁，最后只保留读锁继续读取。

以前面的 `Point` 为例，假设写线程修改坐标后，还需要继续读取修改后的坐标快照，那么正确顺序是：

```java
writeLock.lock();
try {
    x += deltaX;
    y += deltaY;

    readLock.lock();
} finally {
    writeLock.unlock();
}

try {
    // 这里只剩读锁，可以继续读取 x / y
} finally {
    readLock.unlock();
}
```

关键是先获取读锁，再释放写锁。如果先释放写锁，再去获取读锁，中间会出现无锁空档，其他写线程可能插入并修改 `x / y`，当前线程随后读到的就不一定是自己刚刚修改后的状态。

锁降级的本质是从“独占写”平滑过渡到“共享读”。它不是为了让锁释放顺序符合嵌套结构，而是为了避免写锁释放到读锁获取之间出现状态失控的窗口。

反过来的锁升级通常不允许。一个线程持有读锁时再去申请写锁，写锁会要求所有读锁都释放；如果多个读线程都尝试升级，就容易互相等待，形成死等。

## 六、读锁为什么还要记录每个线程自己的持有次数

`state` 的高 16 bit 只记录读锁总数，但它不知道这些读锁分别属于哪个线程。例如：

![](/images/Java-concurrency/IMG-20260707-000096.png)


从 `state` 看，只能知道当前总共有 3 次读锁持有，无法知道线程 A 持有了几次，线程 B 持有了几次。问题会出现在释放读锁时：如果线程 A 调用 `readLock.unlock()`，它必须确认自己确实持有读锁，并且只能减少自己的那一部分计数。

因此，读锁需要两类记录配合：

| 记录位置             | 记录内容        | 作用            |
| ---------------- | ----------- | ------------- |
| `state` 高 16 bit | 所有线程的读锁总数   | 判断写锁能不能获取     |
| 每个线程自己的计数        | 当前线程持有读锁的次数 | 判断当前线程能不能释放读锁 |

线程 A 获取两次读锁后，释放一次，只能表示它自己的读锁计数从 2 变成 1，同时总读锁数从 3 变成 2。此时线程 A 仍然持有读锁。只有当前线程自己的读锁计数减到 0，它才算完全释放读锁。

源码中为了减少 `ThreadLocal` 访问，还会使用 `firstReader`、`firstReaderHoldCount`、`cachedHoldCounter` 等优化字段。它们不改变读锁计数的基本含义，只是为了让常见路径更快。

## 七、读写线程获取失败后如何等待

读锁和写锁虽然是两个入口，但获取失败后都会进入同一条 AQS 等待队列。区别在于，读锁失败后进入共享模式，写锁失败后进入独占模式。

| 申请的锁 | AQS 节点模式  | 含义              |
| ---- | --------- | --------------- |
| 读锁失败 | shared    | 后续可能和其他读节点一起被放行 |
| 写锁失败 | exclusive | 成功后独占临界区        |

队列结构可以这样理解：

![](/images/Java-concurrency/IMG-20260707-000097.png)


当锁释放后，如果队列前面是连续的读节点，`reader A` 和 `reader B` 可以一起被放行，因为读读共享。传播到 `writer C` 时停止，因为写节点必须等所有`reader A` 和 `reader B` 可以一起被放读锁释放后才能获取写锁。`reader D` 虽然也是读节点，但它排在 `writer C` 后面，不能越过写节点。

所以队列内部的推进规则是：连续读节点可以共享传播，遇到第一个写节点就形成边界。这个边界可以避免写节点后面的读线程不断越过写节点，从而导致写线程长期饥饿。

公平性会影响新来的线程是否可以插队。默认构造方法创建的是非公平锁：

```java
new ReentrantReadWriteLock();
```

也可以显式创建公平锁：

```java
new ReentrantReadWriteLock(true);
```

公平锁会更严格地尊重队列顺序；非公平锁更倾向于先尝试当前状态是否允许获取。但即使是非公平读锁，也会对“队列前方已有写节点等待”的情况做一定限制，以降低写线程饥饿风险。

## 八、StampedLock 为什么还要引入乐观读

`ReentrantReadWriteLock` 已经允许多个读线程并发，但读线程仍然需要真正加锁。每次读操作都要修改读锁计数，释放时还要再修改回来。对于读多写少，并且读操作很短的场景，这部分同步成本可能变得明显。

继续沿用 `Point` 例子。`distanceFromOrigin()` 只是读取 `x / y` 并计算距离。如果写操作很少，大多数读操作期间根本没有写线程修改坐标，那么每次读都加读锁就显得偏保守。

`StampedLock` 在读写锁语义之外增加了乐观读。乐观读的思想不是先阻止写线程，而是先假设没有写线程干扰，直接把共享字段读到局部变量，然后再校验读取期间有没有写发生。

`StampedLock` 提供三种主要模式：

| 模式   | 方法                    | 是否真正加锁 | 典型用途              |
| ---- | --------------------- | ------ | ----------------- |
| 写锁   | `writeLock()`         | 是      | 修改共享数据            |
| 悲观读锁 | `readLock()`          | 是      | 稳定读取，阻止写线程        |
| 乐观读  | `tryOptimisticRead()` | 否      | 先读取局部快照，再校验中途有没有写 |

写锁和悲观读锁仍然是真正的锁。乐观读则不阻塞写线程，它依赖后置校验判断本次读取是否可信。

## 九、stamp 是状态版本凭证

`StampedLock` 的方法通常会返回一个 `long` 类型的 `stamp`：

```java
long stamp = lock.writeLock();
long stamp = lock.readLock();
long stamp = lock.tryOptimisticRead();
```

`stamp` 可以粗略理解成“版本时间戳”，但它不是物理时间，不表示毫秒或纳秒。更准确地说，它是锁状态的版本凭证。

不同方法返回的 `stamp` 有不同用途：

| 来源                    | stamp 的作用                 |
| --------------------- | ------------------------- |
| `tryOptimisticRead()` | 用于后续 `validate(stamp)` 校验 |
| `readLock()`          | 作为读锁凭证，用于释放读锁             |
| `writeLock()`         | 作为写锁凭证，用于释放写锁             |

对乐观读来说，`stamp` 主要用于判断从获取它到校验它之间，有没有写锁成功修改过状态。只要写锁成功介入，内部版本就会变化，旧的乐观读 `stamp` 就会失效。

## 十、乐观读读取的是一次局部快照

乐观读最容易误解的地方是：它不保证 `validate()` 之后共享变量不再变化，它只保证本次已经复制到局部变量里的快照没有被写操作打断。

正确写法如下：

```java
class Point {
    private double x;
    private double y;
    private final StampedLock lock = new StampedLock();

    double distanceFromOrigin() {
        long stamp = lock.tryOptimisticRead();

        double currentX = x;
        double currentY = y;

        if (!lock.validate(stamp)) {
            stamp = lock.readLock();
            try {
                currentX = x;
                currentY = y;
            } finally {
                lock.unlockRead(stamp);
            }
        }

        return Math.sqrt(currentX * currentX + currentY * currentY);
    }

    void move(double deltaX, double deltaY) {
        long stamp = lock.writeLock();
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            lock.unlockWrite(stamp);
        }
    }
}
```

这个模板必须遵守一个顺序：先拿 `stamp`，再把共享字段复制到局部变量，然后调用 `validate(stamp)`。如果校验成功，后续只能使用已经复制出来的 `currentX / currentY`；如果校验失败，则退回悲观读锁重新读取。

错误写法是先校验，再读取共享字段：

```java
long stamp = lock.tryOptimisticRead();

if (lock.validate(stamp)) {
    return Math.sqrt(x * x + y * y);
}
```

这段代码的问题是，`validate()` 通过之后，写线程仍然可能立刻修改 `x / y`。当前线程随后再读取共享字段，依然可能读到不一致状态。

另一个错误写法是已经复制了局部变量，也完成了校验，但最后又重新访问共享字段：

```java
long stamp = lock.tryOptimisticRead();

double currentX = x;
double currentY = y;

if (!lock.validate(stamp)) {
    stamp = lock.readLock();
    try {
        currentX = x;
        currentY = y;
    } finally {
        lock.unlockRead(stamp);
    }
}

return Math.sqrt(x * x + y * y);
```

最后一行应该使用 `currentX / currentY`，而不是重新读取 `x / y`。乐观读要保护的是“这一次读取形成的局部快照”，而不是之后所有对共享字段的访问。

## 十一、StampedLock 的限制和转换

`StampedLock` 不是 `ReentrantReadWriteLock` 的简单替代品。它为了支持乐观读，牺牲了一些传统锁能力，其中最重要的是不可重入。

`ReentrantReadWriteLock` 的写锁可以被同一个线程重复获取，`state` 的低 16 bit 会记录写锁重入次数。但 `StampedLock` 不围绕“当前线程重入几次”设计，而是围绕 `stamp` 凭证设计。

下面这种写法在 `StampedLock` 中是危险的：

```java
long s1 = lock.writeLock();
try {
    long s2 = lock.writeLock();
    try {
        // ...
    } finally {
        lock.unlockWrite(s2);
    }
} finally {
    lock.unlockWrite(s1);
}
```

第一次 `writeLock()` 后，当前线程已经持有写锁。第二次再调用 `writeLock()` 时，`StampedLock` 不会识别“这是同一个线程，所以允许重入”，而是看到写锁已经被持有，于是当前线程可能等待自己释放锁。

同理，在已经持有读锁时，也不要直接阻塞等待写锁。因为写锁要求没有任何读锁，而当前线程自己的读锁也会阻止写锁成功。

`StampedLock` 为这类场景提供了转换方法：

```java
long newStamp = lock.tryConvertToWriteLock(stamp);
```

转换成功会返回新的写锁 `stamp`，转换失败会返回 `0L`。典型写法是先尝试转换，失败后释放原来的读锁，再正式申请写锁：

```java
long stamp = lock.readLock();
try {
    while (needUpdate()) {
        long ws = lock.tryConvertToWriteLock(stamp);
        if (ws != 0L) {
            stamp = ws;
            update();
            break;
        } else {
            lock.unlockRead(stamp);
            stamp = lock.writeLock();
        }
    }
} finally {
    lock.unlock(stamp);
}
```

这里的关键不是 API 名称，而是避免“持有读锁时阻塞等待写锁”。转换是一次非阻塞尝试，成功就直接切换为写锁，失败就说明当前条件不满足，必须先放开原有读锁。

## 十二、两者如何选择

`ReentrantReadWriteLock` 更像传统读写锁。它支持可重入，写锁支持 `Condition`，代码结构也更符合常见锁模型。`StampedLock` 更像凭证式读写控制器，它通过 `stamp` 表示锁状态版本或锁凭证，适合在特定场景下减少读锁成本。

| 场景             | 更适合                                                 |
| -------------- | --------------------------------------------------- |
| 需要可重入          | `ReentrantReadWriteLock`                            |
| 需要 `Condition` | `ReentrantReadWriteLock` 的写锁                        |
| 希望代码简单、稳定、容易维护 | `ReentrantReadWriteLock`                            |
| 读很多、写很少，且读操作短小 | `StampedLock` 乐观读                                   |
| 读取的是一组相关字段的快照  | `StampedLock` 乐观读                                   |
| 读取过程较长或逻辑复杂    | 悲观读锁                                                |
| 必须阻止写线程进入读取过程  | `ReentrantReadWriteLock` 或 `StampedLock.readLock()` |

实际选择时，可以先考虑 `ReentrantReadWriteLock`。只有当读操作非常频繁、写操作很少，并且读逻辑能够清晰写成“复制局部快照 + validate 校验”时，再考虑 `StampedLock`。

## 总结

从互斥锁走到读写锁，是因为读操作和写操作对共享状态的破坏性不同：读读之间不需要互斥，读写和写写才需要互斥。`ReentrantReadWriteLock` 把这种语义落实到 AQS 状态上，用同一个 `state` 同时记录读锁总数和写锁重入次数，再通过共享模式和独占模式把读线程、写线程放入同一条等待队列中协调。

但读写锁仍然要求读线程真正加锁。对于读多写少、读取过程很短的场景，`StampedLock` 进一步把“读取”拆成悲观读和乐观读：悲观读仍然阻止写线程，乐观读则先形成局部快照，再用 `stamp` 校验这次快照是否被写操作打断。它用更复杂的使用约束换取更低的成功读成本，因此适合性能敏感但读取边界清晰的场景，而不适合作为所有读写锁场景的默认替代品。
