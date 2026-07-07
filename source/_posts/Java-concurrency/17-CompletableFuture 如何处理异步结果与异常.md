---
title: Java高并发底层原理（十七）—— CompletableFuture 如何处理异步结果与异常
date: 2026-07-03
abbrlink: 17
tags:
    - Java
    - 高并发
    - CompletableFuture
categories:
    - java-concurrency
---


上一章介绍了 `CompletableFuture` 如何编排多个异步任务。任务正常完成时，结果会沿着任务链继续向后传递；但真实程序中，数据库查询可能失败，远程调用可能超时，任务代码也可能抛出运行时异常。

这一章继续沿用上一章的任务链视角，只讨论一个问题：异步阶段失败以后，异常如何保存、传播、恢复，以及调用线程最终如何感知这个失败。

## 一、异步任务中的异常为什么不会直接抛给调用线程

先看一个异步任务：

```java
CompletableFuture<String> future =
        CompletableFuture.supplyAsync(() -> {
            throw new IllegalStateException("查询失败");
        });

System.out.println("调用线程继续执行");
```

调用 `supplyAsync()` 的线程和执行 Lambda 的工作线程通常不是同一个线程。异常只能沿当前线程的调用栈向上传播，工作线程中的异常无法直接跳到主线程的调用栈中。

![](/images/Java-concurrency/IMG-20260707-000074.png)





因此，`CompletableFuture` 必须先把任务的完成状态保存到堆对象中。正常完成时保存正常结果；异常完成时保存异常对象。调用线程之后只能通过异常处理阶段、`get()` 或 `join()`，再去感知这次失败。

这和前文的 `FutureTask` 思路一致：跨线程不能靠方法返回值和异常直接传递，只能靠共享的结果对象保存完成状态。

## 二、Supplier 为什么不能直接抛出受检异常

`CompletableFuture.supplyAsync()` 接收的是 `Supplier<T>`，不是 `Callable<V>`。

| 函数式接口 | 方法声明 | 能否直接声明受检异常 |
|---|---|---:|
| `Supplier<T>` | `T get()` | 否 |
| `Callable<V>` | `V call() throws Exception` | 是 |

`Supplier.get()` 没有声明 `throws`，所以 Lambda 在实现 `Supplier.get()` 时，不能直接把受检异常向外抛出。下面的代码无法通过编译：

```java
CompletableFuture<String> future =
        CompletableFuture.supplyAsync(() -> {
            Thread.sleep(1000);
            return "完成";
        });
```

问题不在于 `CompletableFuture` 不能保存异常，而在于这个 Lambda 正在实现一个不允许抛出受检异常的方法。

常见做法是在 Lambda 内部捕获受检异常，再包装成运行时异常继续抛出：

```java
CompletableFuture<String> future =
        CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(1000);
                return "完成";
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RuntimeException(e);
            }
        });
```

这里的 `try-catch` 不是把失败吞掉，而是把不能直接抛出的受检异常转换成可以继续传播的运行时异常。捕获 `InterruptedException` 后重新调用 `Thread.currentThread().interrupt()`，是为了恢复中断标记，让后续代码仍然知道当前线程曾经收到过中断请求。

如果捕获异常后直接返回默认值：

```java
CompletableFuture<String> future =
        CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(1000);
                return "真正完成";
            } catch (InterruptedException e) {
                return "默认结果";
            }
        });
```

那么从 `CompletableFuture` 的角度看，当前阶段最终正常返回了 `"默认结果"`，所以它会被认为正常完成。也就是说，异常是否继续进入任务链，取决于 Lambda 最终是正常返回，还是继续抛出异常。

## 三、异常如何沿任务链传播

普通后续阶段只会在前一步正常完成时执行。例如：

```java
CompletableFuture<String> future =
        CompletableFuture
                .supplyAsync(() -> {
                    throw new IllegalStateException("查询失败");
                })
                .thenApply(String::toUpperCase);
```

第一阶段异常完成后，`thenApply()` 没有正常结果可用，因此不会执行。异常会继续向后传播，直到遇到能够处理异常的阶段，或者最终被 `get()` / `join()` 感知。

可以把任务链理解成两条路径：

![](/images/Java-concurrency/IMG-20260707-000075.png)





不同方法对前一步完成状态的反应不同：

| 方法 | 前一步正常完成 | 前一步异常完成 |
|---|---:|---:|
| `thenApply()` | 执行 | 跳过 |
| `thenAccept()` | 执行 | 跳过 |
| `thenRun()` | 执行 | 跳过 |
| `exceptionally()` | 跳过 | 执行 |
| `handle()` | 执行 | 执行 |
| `whenComplete()` | 执行 | 执行 |

所以分析异常传播时，先不要急着看方法名，而要先判断：前一步是正常完成还是异常完成？当前阶段是否会执行？当前阶段执行后，异常是被恢复成正常结果，还是继续向后传播？

## 四、exceptionally：只处理失败分支

如果任务失败后，希望返回一个备用值继续任务链，可以使用 `exceptionally()`：

```java
CompletableFuture<String> future =
        CompletableFuture
                .supplyAsync(() -> {
                    throw new IllegalStateException("查询失败");
                })
                .exceptionally(ex -> "默认结果");
```

当原任务异常完成时，`exceptionally()` 接收异常并返回 `"默认结果"`。从这个阶段开始，任务链重新变成正常完成：

```java
String result = future.join(); // "默认结果"
```

如果前一步正常完成，`exceptionally()` 不会执行，正常结果会直接向后传递：

```java
CompletableFuture<String> future =
        CompletableFuture
                .supplyAsync(() -> "真实结果")
                .exceptionally(ex -> "默认结果");
```

最终结果仍然是 `"真实结果"`。

因此，`exceptionally()` 适合“成功时保留原结果，失败时返回备用值”的场景。例如，优惠券查询失败时按“无优惠券”处理：

```java
CompletableFuture<Coupon> couponFuture =
        queryCouponAsync()
                .exceptionally(ex -> Coupon.empty());
```

需要注意，备用值必须与原结果类型兼容。原任务是 `CompletableFuture<Coupon>`，异常处理阶段也必须返回 `Coupon`。

## 五、handle：成功和失败都进行转换

有时不仅失败时需要处理，成功时也需要转换结果。例如成功时把结果转成大写，失败时返回默认值，可以使用 `handle()`：

```java
CompletableFuture<String> future =
        CompletableFuture
                .supplyAsync(() -> queryData())
                .handle((result, ex) -> {
                    if (ex != null) {
                        return "DEFAULT";
                    }
                    return result.toUpperCase();
                });
```

`handle()` 无论前一步正常还是异常都会执行。

| 前一步状态 | `result` | `ex` |
|---|---|---|
| 正常完成 | 正常结果 | `null` |
| 异常完成 | 通常为 `null` | 异常对象 |

`handle()` 不只是恢复异常，也可以转换正常结果，甚至改变结果类型：

```java
CompletableFuture<Integer> future =
        CompletableFuture
                .supplyAsync(() -> "123")
                .handle((result, ex) -> {
                    if (ex != null) {
                        return 0;
                    }
                    return Integer.parseInt(result);
                });
```

原来的结果类型是 `String`，经过 `handle()` 后变成 `Integer`。

与 `exceptionally()` 相比，`handle()` 更适合“成功和失败都要统一映射成另一个结果”的场景。如果只是失败时返回备用值，`exceptionally()` 通常更直接。

## 六、whenComplete：观察结果和异常，但不负责恢复

`whenComplete()` 也会在成功和失败时都执行，但它主要用于观察结果和异常，例如记录日志、统计耗时、释放资源：

```java
CompletableFuture<String> future =
        CompletableFuture
                .supplyAsync(() -> queryData())
                .whenComplete((result, ex) -> {
                    if (ex != null) {
                        System.out.println("执行失败：" + ex);
                    } else {
                        System.out.println("执行成功：" + result);
                    }
                });
```

`whenComplete()` 接收的回调类似 `BiConsumer`，回调本身没有返回值。但 `whenComplete()` 方法仍然返回 `CompletableFuture<T>`，所以后续任务可以继续编排。

关键点是：`whenComplete()` 默认不会把异常恢复成正常结果。下面的代码虽然记录了异常，但异常仍然会继续传播：

```java
CompletableFuture<String> future =
        CompletableFuture
                .supplyAsync(() -> {
                    throw new IllegalStateException("查询失败");
                })
                .whenComplete((result, ex) -> {
                    System.out.println("记录异常：" + ex);
                });

future.join(); // 仍然抛出异常
```

如果想先记录异常，再返回默认值，可以继续接 `exceptionally()`：

```java
CompletableFuture<String> future =
        queryAsync()
                .whenComplete((result, ex) -> {
                    if (ex != null) {
                        System.out.println("记录异常：" + ex);
                    }
                })
                .exceptionally(ex -> "默认结果");
```

真正把异常恢复成正常结果的是 `exceptionally()`，不是 `whenComplete()`。

还要注意，如果前一步正常完成，但 `whenComplete()` 自己抛出了异常，那么它返回的新阶段会异常完成。因此，“`whenComplete()` 不改变原结果”有一个前提：`whenComplete()` 自己正常执行结束。

## 七、三种异常处理方法如何选择

`exceptionally()`、`handle()` 和 `whenComplete()` 的区别可以放在同一张表里：

| 方法 | 正常时执行 | 异常时执行 | 能否返回新结果 | 典型用途 |
|---|---:|---:|---:|---|
| `exceptionally()` | 否 | 是 | 是 | 失败时返回备用值 |
| `handle()` | 是 | 是 | 是 | 成功和失败统一转换 |
| `whenComplete()` | 是 | 是 | 否 | 日志、统计、资源释放 |

选择时可以按这个顺序判断：只在失败时恢复，用 `exceptionally()`；成功和失败都要转换，用 `handle()`；只想观察结果或异常，不想改变结果，用 `whenComplete()`。

还要区分三处不同的异常处理。

第一处是任务定义处：

```java
CompletableFuture<String> future =
        CompletableFuture.supplyAsync(() -> {
            try {
                return queryData();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });
```

这里处理的是 `Supplier.get()` 不能直接抛出受检异常。

第二处是任务链运行过程中：

```java
future
        .whenComplete((result, ex) -> log(result, ex))
        .exceptionally(ex -> "默认结果");
```

这里处理的是已经被 `CompletableFuture` 保存下来的异常，后续应该如何观察、转换或恢复。

第三处是获取最终结果时：

```java
future.get();
future.join();
```

这里处理的是整条任务链最终是正常完成还是异常完成。

不要把这三处混为一谈。Lambda 内部的 `try-catch` 解决的是函数式接口签名限制；`exceptionally()` / `handle()` / `whenComplete()` 处理的是异步阶段保存的异常；`get()` / `join()` 处理的是最终消费结果时看到的完成状态。

## 八、get() 与 join() 有什么区别

`get()` 和 `join()` 都会等待任务完成并取得结果。正常完成时，两者得到的结果相同，主要区别在于异常处理方式。

`get()` 来自 `Future` 接口，方法声明中包含受检异常：

```java
V get() throws InterruptedException, ExecutionException;
```

调用时必须处理等待线程被中断和任务执行失败两类情况：

```java
try {
    String result = future.get();
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
} catch (ExecutionException e) {
    Throwable cause = e.getCause();
}
```

`InterruptedException` 表示等待结果的线程被中断，`ExecutionException` 表示异步任务执行失败。原始异常保存在 `ExecutionException.getCause()` 中。

`join()` 是 `CompletableFuture` 自己提供的方法：

```java
String result = future.join();
```

它不声明 `InterruptedException` 和 `ExecutionException`，因此编译器不会强制调用者编写 `try-catch`。如果任务异常完成，`join()` 通常抛出 `CompletionException`，原始异常同样可以通过 `getCause()` 取得。

| 方法 | 是否声明受检异常 | 任务失败时的包装异常 | 等待线程中断 |
|---|---:|---|---|
| `get()` | 是 | `ExecutionException` | 抛出 `InterruptedException` |
| `join()` | 否 | `CompletionException` | 不以 `InterruptedException` 形式返回 |

`join()` 不强制处理受检异常，不代表异常消失了，只是异常通过运行时异常继续传播。

任务链内部应尽量继续编排，不要每一步都调用 `join()` 或 `get()`。更合理的方式是先描述完整任务链，在真正需要最终结果的边界处，再调用 `get()` 或 `join()`。

## 九、超时不等于任务停止

普通 `get()` 可能无限等待。带超时的 `get()` 可以让调用线程最多等待一段时间：

```java
String result =
        future.get(1, TimeUnit.SECONDS);
```

超过一秒后，等待线程会抛出 `TimeoutException`，但工作线程中的任务可能仍然继续执行。也就是说，等待超时和任务停止是两件不同的事情。

`CompletableFuture` 还提供了和阶段完成状态相关的超时方法。

`orTimeout()` 表示规定时间内没有完成时，让这个 `CompletableFuture` 异常完成：

```java
CompletableFuture<String> future =
        queryAsync()
                .orTimeout(1, TimeUnit.SECONDS);
```

之后可以继续用异常处理阶段恢复：

```java
CompletableFuture<String> future =
        queryAsync()
                .orTimeout(1, TimeUnit.SECONDS)
                .exceptionally(ex -> "默认结果");
```

`completeOnTimeout()` 表示超时后使用默认值正常完成：

```java
CompletableFuture<String> future =
        queryAsync()
                .completeOnTimeout(
                        "默认结果",
                        1,
                        TimeUnit.SECONDS
                );
```

三者的区别是：

| 方法 | 超时后的表现 |
|---|---|
| `get(timeout)` | 等待线程抛出 `TimeoutException` |
| `orTimeout()` | `CompletableFuture` 异常完成 |
| `completeOnTimeout()` | 使用默认值正常完成 |

这些方法都不保证底层任务已经真正停止。它们改变的是等待线程的状态，或者 `CompletableFuture` 本身的完成状态。

## 十、cancel(true) 也只是协作式取消

取消任务可以调用：

```java
future.cancel(true);
```

但 `cancel(true)` 只能尝试取消任务，不能强制杀死线程。任务能否停止取决于任务是否已经开始执行、任务是否检查中断状态、阻塞操作是否支持中断、任务代码是否正确响应中断，以及底层操作是否支持取消。

如果任务主动检查中断状态：

```java
CompletableFuture<Void> future =
        CompletableFuture.runAsync(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                doWork();
            }
        });
```

它更有机会配合取消请求及时结束。

如果任务完全不检查中断：

```java
CompletableFuture<Void> future =
        CompletableFuture.runAsync(() -> {
            while (true) {
                doWork();
            }
        });
```

取消请求可能无法让它及时停止。

因此，取消是一种协作机制，不是强制终止机制。这一点和前文 `FutureTask.cancel(true)` 的语义一致。

## 十一、allOf 和 anyOf 遇到异常时会怎样

`allOf()` 等待所有任务完成。如果其中至少一个任务异常完成，组合后的 `CompletableFuture<Void>` 也会异常完成。

![](/images/Java-concurrency/IMG-20260707-000076.png)





各个任务的结果和异常仍然保存在原来的 `CompletableFuture` 中。`allOf()` 本身只表达“这一批任务都完成了”，不负责收集每个业务结果。

`anyOf()` 在任意一个任务最先完成时结束，这里的“完成”包括正常完成和异常完成。

![](/images/Java-concurrency/IMG-20260707-000077.png)





所以，`anyOf()` 等待的是最快完成，不是最快成功。它不会自动忽略失败任务，也不会在一个任务完成后自动取消其他仍在执行的任务。

## 十二、常见错误

第一，捕获异常后直接返回 `null`：

```java
catch (IOException e) {
    return null;
}
```

这会让任务被认为正常完成，同时丢失失败原因。除非 `null` 是明确设计的业务结果，否则不应这样处理。

第二，捕获 `InterruptedException` 后不恢复中断标记。通常应先调用 `Thread.currentThread().interrupt()`，再决定继续抛出还是返回备用结果。

第三，认为 `whenComplete()` 已经处理异常。它通常只观察异常，不会自动恢复异常状态。

第四，所有异常场景都使用 `handle()`。如果只是失败时返回备用值，`exceptionally()` 更直接。

第五，在任务链每一步调用 `join()`。这会破坏异步编排，让调用线程重新承担等待和推动任务的职责。

第六，认为超时等于取消。超时通常只改变等待状态或 `CompletableFuture` 的完成状态，不保证底层任务停止。

第七，认为 `cancel(true)` 一定能停止任务。取消能否成功，取决于任务是否配合响应中断。

## 本章总结

`CompletableFuture` 的异常处理可以从“跨线程异常不能直接传播”开始理解：工作线程中的异常不会跳到调用线程栈中，而是被保存到 `CompletableFuture` 的完成状态里。后续普通阶段需要正常结果，所以遇到异常会被跳过；异常会继续向后传播，直到被异常处理阶段观察、转换或恢复，或者最终在 `get()` / `join()` 处暴露出来。

`exceptionally()`、`handle()` 和 `whenComplete()` 解决的是任务链中的异常分支：`exceptionally()` 只在失败时执行，并可返回备用值；`handle()` 成功和失败都会执行，并可统一转换结果；`whenComplete()` 适合日志、统计和资源释放，默认不恢复异常。它们和 Lambda 内部捕获受检异常不是同一层问题，也和最终调用 `get()` / `join()` 取结果不是同一层问题。

超时和取消也要分开看。`get(timeout)` 只是让等待线程不再无限等待，`orTimeout()` 和 `completeOnTimeout()` 改变的是 `CompletableFuture` 的完成方式，但它们都不保证底层任务停止。`cancel(true)` 也只是发出中断请求，任务是否结束取决于代码是否配合响应。只有把“异常保存、异常恢复、最终取结果、超时取消”这几条线分清，才能正确判断一条 `CompletableFuture` 任务链最终会正常完成、异常完成，还是被取消。
