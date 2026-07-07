---
title: 'Java基础(8) | Lambda 与 Stream API：函数式编程核心工具'
date: 2026-05-08
tags:
  - Java
  - Lambda
  - Stream
  - 函数式编程
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

Java 8 是 Java 历史上变化最大的一个版本，Lambda 表达式和 Stream API 彻底改变了 Java 的代码风格——从冗长的匿名内部类和 for 循环，变成了简洁的声明式写法。这篇文章把 Lambda、函数式接口、方法引用、Stream、Optional 一次讲完。

<!-- more -->

## 1. 从匿名内部类到 Lambda

### 1.1 问题：匿名内部类太啰嗦

Java 8 之前，想把"一段行为"传给方法，只能用匿名内部类。

**什么是匿名内部类？** 就是在创建对象的同时定义一个没有名字的子类。`new 接口/父类() { 实现方法 }` 相当于三步合一：定义一个类 → 实现接口方法 → 创建实例：

```java
// 正常写法：先定义一个实现类，再实例化
class LengthComparator implements Comparator<String> {
    @Override
    public int compare(String a, String b) {
        return a.length() - b.length();
    }
}
list.sort(new LengthComparator());

// 匿名内部类：省掉类名，直接在 new 的时候写实现
list.sort(new Comparator<String>() {   // new 接口() { 实现 }
    @Override
    public int compare(String a, String b) {
        return a.length() - b.length();
    }
});
```

但这样还是很啰嗦——5 行代码，真正有用的只有 `a.length() - b.length()` 一行，其余全是模板代码。

### 1.2 Lambda 表达式

Lambda 本质就是**匿名函数**——一段可以传递的代码：

```java
// 上面的匿名内部类，用 Lambda 一行搞定
list.sort((a, b) -> a.length() - b.length());
```

### 1.3 Lambda 语法

```java
// 完整形式
(String a, String b) -> { return a.length() - b.length(); }

// 参数类型可省略（编译器推断）
(a, b) -> { return a.length() - b.length(); }

// 方法体只有一行时，可以省略大括号和 return
(a, b) -> a.length() - b.length()

// 只有一个参数时，可以省略括号
x -> x * 2

// 无参数
() -> System.out.println("hello")
```

### 1.4 Lambda 的本质

Lambda 不是语法糖那么简单。它的底层不是匿名内部类，而是通过 `invokedynamic` 字节码指令实现，性能更好（不会每次创建新的 class 文件）。

但从使用角度理解，你可以把 Lambda 看作**一个只有一个抽象方法的接口的实例**。这就引出了下一个概念。

## 2. 函数式接口（Functional Interface）

### 2.1 定义

**只有一个抽象方法**的接口就是函数式接口，Lambda 只能赋值给函数式接口：

```java
@FunctionalInterface  // 可选注解，编译器会校验是否只有一个抽象方法
public interface MyFunction {
    int apply(int x);
    // 如果再加一个抽象方法，编译报错
}

MyFunction doubler = x -> x * 2;
System.out.println(doubler.apply(5));  // 10
```

### 2.2 Java 内置的四大函数式接口

Java 在 `java.util.function` 包中预定义了大量函数式接口，最常用的四个：

| 接口 | 方法签名 | 用途 | 示例 |
|------|---------|------|------|
| `Function<T, R>` | `R apply(T t)` | 转换：T → R | `s -> s.length()` |
| `Predicate<T>` | `boolean test(T t)` | 判断：T → boolean | `s -> s.isEmpty()` |
| `Consumer<T>` | `void accept(T t)` | 消费：T → void | `s -> System.out.println(s)` |
| `Supplier<T>` | `T get()` | 生产：() → T | `() -> new ArrayList<>()` |

```java
// Function：转换
Function<String, Integer> strLen = s -> s.length();
strLen.apply("hello");  // 5

// Predicate：判断
Predicate<String> isLong = s -> s.length() > 5;
isLong.test("hello");   // false

// Consumer：消费
Consumer<String> printer = s -> System.out.println(s);
printer.accept("hello");  // 输出 hello

// Supplier：生产
Supplier<List<String>> listFactory = () -> new ArrayList<>();
List<String> list = listFactory.get();
```

### 2.3 其他常用变体

**双参数版本**：在四大接口前加 `Bi` 前缀，表示接受两个参数：

```java
// BiFunction：两个入参，一个返回值
BiFunction<String, String, Integer> sumLen = (a, b) -> a.length() + b.length();
sumLen.apply("hello", "world");  // 10

// BiPredicate：两个入参，返回 boolean
BiPredicate<String, Integer> longerThan = (s, n) -> s.length() > n;
longerThan.test("hello", 3);  // true

// BiConsumer：两个入参，无返回值
BiConsumer<String, Integer> printPair = (k, v) -> System.out.println(k + "=" + v);
printPair.accept("age", 18);  // age=18
```

**基本类型特化**：泛型只能用包装类（`Integer`、`Double`），每次调用都要装箱/拆箱有性能开销。Java 提供了直接操作基本类型的版本：

```java
// ToIntFunction：入参任意类型，返回 int（省去 Integer 装箱）
ToIntFunction<String> strToInt = s -> s.length();
strToInt.applyAsInt("hello");  // 5

// IntFunction：入参 int，返回任意类型
IntFunction<String> intToStr = i -> "num:" + i;
intToStr.apply(42);  // "num:42"

// IntPredicate：入参 int，返回 boolean
IntPredicate isPositive = n -> n > 0;
isPositive.test(5);   // true

// IntConsumer：入参 int，无返回值
IntConsumer printInt = n -> System.out.println(n);
printInt.accept(42);  // 42

// IntSupplier：无入参，返回 int
IntSupplier randomInt = () -> (int)(Math.random() * 100);
randomInt.getAsInt();  // 0~99 的随机整数
```

类似的还有 `LongFunction`、`DoubleFunction` 等，命名规律一样，实际开发中用到再查即可。

**同类型输入输出的简化版**：

```java
// UnaryOperator<T>：入参和返回值同类型，是 Function<T,T> 的简化
UnaryOperator<String> toUpper = s -> s.toUpperCase();
toUpper.apply("hello");  // "HELLO"

// BinaryOperator<T>：两个同类型入参，返回同类型，是 BiFunction<T,T,T> 的简化
BinaryOperator<Integer> add = (a, b) -> a + b;
add.apply(3, 4);  // 7
```

实际开发中最常用的就是四大核心接口（`Function`、`Predicate`、`Consumer`、`Supplier`），其余变体在 Stream 和框架源码中会遇到，用到时对照命名规律就能猜出用途。

### 2.4 函数式接口的组合

函数式接口可以通过内置方法组合成更复杂的逻辑，避免写嵌套 Lambda。

**Predicate 组合**：

| 方法 | 含义 | 示例 |
|------|------|------|
| `and(other)` | 两个条件都满足 | `isLong.and(startsWithA)` |
| `or(other)` | 任一条件满足 | `isLong.or(startsWithA)` |
| `negate()` | 取反 | `isLong.negate()` |

```java
Predicate<String> isLong = s -> s.length() > 5;
Predicate<String> startsWithA = s -> s.startsWith("A");

isLong.and(startsWithA).test("Alexander");   // true（长度>5 且 以A开头）
isLong.or(startsWithA).test("Alice");        // true（长度不>5，但以A开头）
isLong.negate().test("hi");                  // true（长度不>5）
```

**Function 组合**：

| 方法 | 含义 | 执行顺序 |
|------|------|---------|
| `andThen(after)` | 先执行自己，再执行 after | this → after |
| `compose(before)` | 先执行 before，再执行自己 | before → this |

```java
Function<String, String> trim  = s -> s.trim();
Function<String, String> upper = s -> s.toUpperCase();

// andThen：先 trim 再 upper
trim.andThen(upper).apply("  hello  ");  // "HELLO"

// compose：先 upper 再 trim（和 andThen 顺序相反）
trim.compose(upper).apply("  hello  ");  // "  HELLO  "（先大写再trim，trim没效果）
```

记忆技巧：`andThen` 就是"然后再做"，顺序和代码书写顺序一致；`compose` 是数学里的函数复合 f∘g，先执行括号里的。实际开发中 `andThen` 更常用。

## 3. 方法引用（Method Reference）

当 Lambda 只是调用一个已有方法时，可以用方法引用进一步简化：

```java
// Lambda                           →  方法引用
s -> System.out.println(s)          →  System.out::println
s -> s.toUpperCase()                →  String::toUpperCase
s -> Integer.parseInt(s)            →  Integer::parseInt
() -> new ArrayList<>()             →  ArrayList::new
```

### 3.1 四种形式

| 类型 | 语法 | 等价 Lambda | 示例 |
|------|------|------------|------|
| 静态方法引用 | `类名::静态方法` | `x -> 类名.方法(x)` | `Integer::parseInt` |
| 实例方法引用（对象） | `对象::实例方法` | `x -> 对象.方法(x)` | `System.out::println` |
| 实例方法引用（类） | `类名::实例方法` | `(obj, x) -> obj.方法(x)` | `String::compareTo` |
| 构造方法引用 | `类名::new` | `x -> new 类名(x)` | `ArrayList::new` |

```java
List<String> list = List.of("banana", "apple", "cherry");

// 静态方法引用
list.stream().map(Integer::parseInt);  // 如果 list 是数字字符串

// 实例方法引用（通过类名）
list.sort(String::compareToIgnoreCase);
// 等价于 list.sort((a, b) -> a.compareToIgnoreCase(b))

// 构造方法引用
list.stream().map(StringBuilder::new);
// 等价于 list.stream().map(s -> new StringBuilder(s))
```

## 4. Stream API

### 4.1 Stream 是什么？

Stream 是对集合数据的**声明式处理管道**——你描述"要做什么"，而不是"怎么做"：

```java
// 命令式：手动循环
List<String> result = new ArrayList<>();
for (String s : list) {
    if (s.length() > 4) {
        result.add(s.toUpperCase());
    }
}

// 声明式：Stream
List<String> result = list.stream()
    .filter(s -> s.length() > 4)
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```

### 4.2 Stream 的三个阶段

```
数据源 → 中间操作（lazy） → 终端操作（触发执行）
```

**中间操作**返回新的 Stream，可以链式调用，不会立即执行（惰性求值）：

| 操作 | 说明 | 示例 |
|------|------|------|
| `filter` | 过滤 | `.filter(s -> s.length() > 3)` |
| `map` | 转换 | `.map(String::toUpperCase)` |
| `flatMap` | 一对多展开 | `.flatMap(line -> Arrays.stream(line.split(" ")))` |
| `distinct` | 去重 | `.distinct()` |
| `sorted` | 排序 | `.sorted()` 或 `.sorted(Comparator)` |
| `peek` | 查看（调试用） | `.peek(System.out::println)` |
| `limit` | 截取前 n 个 | `.limit(5)` |
| `skip` | 跳过前 n 个 | `.skip(2)` |

**终端操作**触发整个管道执行，返回结果：

| 操作 | 说明 | 示例 |
|------|------|------|
| `collect` | 收集为集合 | `.collect(Collectors.toList())` |
| `forEach` | 遍历 | `.forEach(System.out::println)` |
| `count` | 计数 | `.count()` |
| `reduce` | 归约 | `.reduce(0, Integer::sum)` |
| `findFirst` | 第一个元素 | `.findFirst()` |
| `findAny` | 任意一个 | `.findAny()` |
| `anyMatch` | 任一匹配 | `.anyMatch(s -> s.isEmpty())` |
| `allMatch` | 全部匹配 | `.allMatch(s -> s.length() > 0)` |
| `noneMatch` | 全不匹配 | `.noneMatch(s -> s.isEmpty())` |
| `min / max` | 最值 | `.min(Comparator.naturalOrder())` |
| `toArray` | 转数组 | `.toArray(String[]::new)` |

### 4.3 stream 的 Collectors 收集器详解

`collect()` 是 Stream 最重要的终端操作，需要传入一个 `Collector` 告诉它怎么收集结果。`Collectors` 工具类提供了所有常用的收集器：

**基本收集**：

```java
List<String> names = List.of("Alice", "Bob", "Charlie", "Alice");

// toList：最常用
List<String> list = names.stream().collect(Collectors.toList());

// toSet：自动去重，顺序不保证
Set<String> set = names.stream().collect(Collectors.toSet());
// {Alice, Bob, Charlie}

// toCollection：指定具体实现类
LinkedList<String> linked = names.stream()
    .collect(Collectors.toCollection(LinkedList::new));
```

**字符串拼接 joining**：

```java
// joining() 只能用于 Stream<String>
List<String> words = List.of("hello", "world", "java");

words.stream().collect(Collectors.joining());
// "helloworldjava"

words.stream().collect(Collectors.joining(", "));
// "hello, world, java"

words.stream().collect(Collectors.joining(", ", "[", "]"));
// "[hello, world, java]"
//    ↑分隔符  ↑前缀  ↑后缀
```

**toMap：收集为 Map**：

```java
List<String> names = List.of("Alice", "Bob", "Charlie");

// toMap(key提取函数, value提取函数)
Map<String, Integer> nameToLength = names.stream()
    .collect(Collectors.toMap(
        name -> name,       // key：名字本身
        String::length      // value：名字长度
    ));
// {Alice=5, Bob=3, Charlie=7}

// key 冲突时需要提供合并函数，否则抛异常
List<String> withDup = List.of("Alice", "Bob", "Alice");
Map<String, Integer> map = withDup.stream()
    .collect(Collectors.toMap(
        name -> name,
        String::length,
        (old, newVal) -> old  // key 重复时保留旧值
    ));
```

**groupingBy：分组**：

按某个条件把元素分成多组，返回 `Map<分组key, List<元素>>`：

```java
List<String> names = List.of("Alice", "Bob", "Charlie", "David", "Amy");

// 按字符串长度分组
Map<Integer, List<String>> byLength = names.stream()
    .collect(Collectors.groupingBy(String::length));
// {3=[Bob, Amy], 5=[Alice, David], 7=[Charlie]}

// 按首字母分组
Map<Character, List<String>> byFirstChar = names.stream()
    .collect(Collectors.groupingBy(s -> s.charAt(0)));
// {A=[Alice, Amy], B=[Bob], C=[Charlie], D=[David]}

// 分组后再统计数量（downstream collector）
Map<Integer, Long> countByLength = names.stream()
    .collect(Collectors.groupingBy(
        String::length,
        Collectors.counting()   // 每组的数量
    ));
// {3=2, 5=2, 7=1}

// 分组后再收集为 Set（去重）
Map<Integer, Set<String>> setByLength = names.stream()
    .collect(Collectors.groupingBy(
        String::length,
        Collectors.toSet()
    ));
```

**partitioningBy：分区**：

按条件把元素分成**恰好两组**，返回 `Map<Boolean, List<元素>>`，key 只有 `true` 和 `false`：

```java
List<String> names = List.of("Alice", "Bob", "Charlie", "Amy");

// 按长度是否大于 4 分区
Map<Boolean, List<String>> partition = names.stream()
    .collect(Collectors.partitioningBy(s -> s.length() > 4));
// {false=[Bob, Amy], true=[Alice, Charlie]}

List<String> longNames  = partition.get(true);   // [Alice, Charlie]
List<String> shortNames = partition.get(false);  // [Bob, Amy]
```

`groupingBy` vs `partitioningBy` 的选择：

| | `groupingBy` | `partitioningBy` |
|---|---|---|
| 分组数量 | 任意多组 | 恰好两组 |
| key 类型 | 任意类型 | Boolean |
| 适用场景 | 按类别分组 | 按条件过滤出两组 |

**统计类收集器**：

```java
List<Integer> nums = List.of(1, 2, 3, 4, 5);

// counting：计数
long count = nums.stream().collect(Collectors.counting());  // 5

// summingInt / averagingInt：求和 / 求平均
int sum = nums.stream().collect(Collectors.summingInt(n -> n));  // 15
double avg = nums.stream().collect(Collectors.averagingInt(n -> n));  // 3.0

// summarizingInt：一次性获取所有统计信息
IntSummaryStatistics stats = nums.stream()
    .collect(Collectors.summarizingInt(n -> n));
stats.getCount();    // 5
stats.getSum();      // 15
stats.getMin();      // 1
stats.getMax();      // 5
stats.getAverage();  // 3.0
```

**常用收集器速查表**：

| 收集器 | 返回类型 | 用途 |
|--------|---------|------|
| `toList()` | `List<T>` | 收集为列表 |
| `toSet()` | `Set<T>` | 收集为集合（去重） |
| `toMap(k, v)` | `Map<K,V>` | 收集为映射 |
| `joining(sep)` | `String` | 字符串拼接 |
| `groupingBy(fn)` | `Map<K, List<T>>` | 按条件分组 |
| `partitioningBy(pred)` | `Map<Boolean, List<T>>` | 按条件分成两组 |
| `counting()` | `Long` | 计数 |
| `summingInt(fn)` | `Integer` | 求和 |
| `averagingInt(fn)` | `Double` | 求平均 |
| `summarizingInt(fn)` | `IntSummaryStatistics` | 全部统计信息 |

### 4.4 Stream 的 map 操作详解

`map` 是最常用的中间操作，作用是**把每个元素转换成另一种类型**：

```java
// 基本用法：String → Integer
List<String> names = List.of("Alice", "Bob", "Charlie");
List<Integer> lengths = names.stream()
    .map(String::length)        // 每个字符串转成长度
    .collect(Collectors.toList());
// [5, 3, 7]

// 对象字段提取
List<User> users = List.of(new User("Alice", 20), new User("Bob", 25));
List<String> nameList = users.stream()
    .map(User::getName)         // 提取每个 User 的 name 字段
    .collect(Collectors.toList());
// ["Alice", "Bob"]

// 链式转换
List<String> result = names.stream()
    .map(String::toLowerCase)   // 先转小写
    .map(s -> s + "!")          // 再加感叹号
    .collect(Collectors.toList());
// ["alice!", "bob!", "charlie!"]
```

**基本类型特化版本**（避免装箱开销）：

| 方法 | 返回类型 | 用途 |
|------|---------|------|
| `mapToInt(fn)` | `IntStream` | 转换为 int 流 |
| `mapToLong(fn)` | `LongStream` | 转换为 long 流 |
| `mapToDouble(fn)` | `DoubleStream` | 转换为 double 流 |
| `mapToObj(fn)` | `Stream<T>` | 基本类型流转回对象流 |

```java
List<String> names = List.of("Alice", "Bob", "Charlie");

// mapToInt：转成 IntStream，可以直接调用 sum/avg/min/max
int totalLength = names.stream()
    .mapToInt(String::length)
    .sum();   // 15

double avgLength = names.stream()
    .mapToInt(String::length)
    .average()
    .orElse(0);  // 5.0

// IntStream 转回 Stream<T>
IntStream.of(1, 2, 3)
    .mapToObj(i -> "num" + i)   // IntStream → Stream<String>
    .collect(Collectors.toList());
// ["num1", "num2", "num3"]
```

**flatMap：一对多展开**：

`map` 是一对一转换，`flatMap` 是一对多转换，会把嵌套结构展平一层：

```java
// map 的结果是嵌套的 Stream<Stream<String>>
// flatMap 把它展平成 Stream<String>

// 场景：每行文本拆成单词
List<String> lines = List.of("hello world", "foo bar baz");

// map：结果是 [[hello, world], [foo, bar, baz]]（嵌套）
List<List<String>> nested = lines.stream()
    .map(line -> Arrays.asList(line.split(" ")))
    .collect(Collectors.toList());

// flatMap：结果是 [hello, world, foo, bar, baz]（展平）
List<String> words = lines.stream()
    .flatMap(line -> Arrays.stream(line.split(" ")))
    .collect(Collectors.toList());

// 场景：展平嵌套列表
List<List<Integer>> nums = List.of(
    List.of(1, 2, 3),
    List.of(4, 5),
    List.of(6)
);
List<Integer> flat = nums.stream()
    .flatMap(Collection::stream)
    .collect(Collectors.toList());
// [1, 2, 3, 4, 5, 6]
```

`map` vs `flatMap` 一句话总结：

| | 输入 | 输出 | 结果形状 |
|---|---|---|---|
| `map(fn)` | 一个元素 | 一个元素 | 不变 |
| `flatMap(fn)` | 一个元素 | 多个元素（Stream） | 展平一层 |

### 4.5 其他常用中间操作

**filter：过滤**

```java
List<String> names = List.of("Alice", "Bob", "Charlie", "Amy");

// 保留满足条件的元素
List<String> longNames = names.stream()
    .filter(s -> s.length() > 3)
    .collect(Collectors.toList());
// ["Alice", "Charlie"]

// 多个 filter 可以链式叠加（等价于 and）
List<String> result = names.stream()
    .filter(s -> s.length() > 3)
    .filter(s -> s.startsWith("A"))
    .collect(Collectors.toList());
// ["Alice"]
```

**sorted：排序**

```java
List<String> names = List.of("Charlie", "Alice", "Bob");

// 自然排序（字典序）
names.stream().sorted().collect(Collectors.toList());
// ["Alice", "Bob", "Charlie"]

// 自定义排序
names.stream()
    .sorted(Comparator.comparingInt(String::length))  // 按长度升序
    .collect(Collectors.toList());
// ["Bob", "Alice", "Charlie"]

// 多字段排序
names.stream()
    .sorted(Comparator.comparingInt(String::length)
                      .thenComparing(Comparator.naturalOrder()))  // 长度相同再按字典序
    .collect(Collectors.toList());

// 降序
names.stream()
    .sorted(Comparator.comparingInt(String::length).reversed())
    .collect(Collectors.toList());
// ["Charlie", "Alice", "Bob"]
```

**distinct / limit / skip：去重和截取**

```java
List<Integer> nums = List.of(1, 2, 2, 3, 3, 3, 4, 5);

nums.stream().distinct().collect(Collectors.toList());
// [1, 2, 3, 4, 5]（去重，保持顺序）

nums.stream().limit(3).collect(Collectors.toList());
// [1, 2, 2]（只取前3个）

nums.stream().skip(5).collect(Collectors.toList());
// [3, 4, 5]（跳过前5个）

// 组合使用：分页效果
int page = 2, pageSize = 3;
nums.stream()
    .skip((page - 1) * pageSize)   // 跳过前一页
    .limit(pageSize)                // 取一页
    .collect(Collectors.toList());
// [3, 3, 4]（第2页）
```

**peek：调试用**

`peek` 不改变元素，只是"偷看"一下，常用于调试时打印中间结果：

```java
List<String> result = names.stream()
    .peek(s -> System.out.println("过滤前: " + s))
    .filter(s -> s.length() > 3)
    .peek(s -> System.out.println("过滤后: " + s))
    .map(String::toUpperCase)
    .collect(Collectors.toList());
// 过滤前: Charlie
// 过滤前: Alice
// 过滤前: Bob
// 过滤后: Charlie
// 过滤后: Alice
```

注意 `peek` 只用于调试，不要在里面做修改元素内容等有副作用的操作。

### 4.6 终端操作详解

**match 系列：匹配判断**

```java
List<String> names = List.of("Alice", "Bob", "Charlie");

names.stream().anyMatch(s -> s.startsWith("A"));   // true（任意一个满足）
names.stream().allMatch(s -> s.length() > 2);      // true（全部满足）
names.stream().noneMatch(s -> s.startsWith("Z"));  // true（全不满足）
```

**find 系列：查找元素**

```java
// findFirst：返回第一个元素（有序流用这个）
Optional<String> first = names.stream()
    .filter(s -> s.length() > 3)
    .findFirst();
first.orElse("none");  // "Alice"

// findAny：返回任意一个（并行流下更快）
Optional<String> any = names.stream()
    .filter(s -> s.length() > 3)
    .findAny();
```

**reduce：归约**

把所有元素合并成一个结果：

```java
List<Integer> nums = List.of(1, 2, 3, 4, 5);

// 有初始值：不会返回 Optional
int sum = nums.stream().reduce(0, (a, b) -> a + b);   // 15
int sum2 = nums.stream().reduce(0, Integer::sum);      // 15（方法引用简化）

// 无初始值：可能流为空，返回 Optional（将会在下一节介绍）
Optional<Integer> max = nums.stream().reduce(Integer::max);
max.orElse(0);  // 5

// 字符串拼接（实际更推荐用 Collectors.joining）
String joined = Stream.of("a", "b", "c")
    .reduce("", (a, b) -> a + b);  // "abc"
```

**min / max：最值**

```java
Optional<String> shortest = names.stream()
    .min(Comparator.comparingInt(String::length));
shortest.orElse("");  // "Bob"

Optional<String> longest = names.stream()
    .max(Comparator.comparingInt(String::length));
longest.orElse("");  // "Charlie"
```

**count / toArray**

```java
long count = names.stream().filter(s -> s.length() > 3).count();  // 2

// toArray：转成数组
String[] arr = names.stream().toArray(String[]::new);
```

## 5. Optional

### 5.1 为什么需要 Optional？

`Optional` 是一个容器，表示"值可能存在，也可能不存在"，用来替代 null 减少 NPE（NullPointerException）：

```java
// 传统写法：满屏的 null 检查
String city = null;
if (user != null) {
    Address addr = user.getAddress();
    if (addr != null) {
        city = addr.getCity();
    }
}
if (city == null) city = "Unknown";
```

### 5.2 基本用法

```java
// 创建
Optional<String> opt1 = Optional.of("hello");       // 值不能为 null
Optional<String> opt2 = Optional.ofNullable(null);   // 值可以为 null
Optional<String> opt3 = Optional.empty();             // 空的 Optional

// 判断和获取
opt1.isPresent();   // true
opt2.isPresent();   // false
opt1.isEmpty();     // false（Java 11+）

opt1.get();         // "hello"（有值时获取）
// opt2.get();      // 抛 NoSuchElementException！空的不能 get

// 安全获取
opt2.orElse("default");                    // "default"
opt2.orElseGet(() -> computeDefault());    // 惰性计算默认值
opt2.orElseThrow(() -> new RuntimeException("no value"));  // 抛自定义异常
```

### 5.3 链式操作

```java
// 用 Optional 改写上面的嵌套 null 检查
String city = Optional.ofNullable(user)
    .map(User::getAddress)
    .map(Address::getCity)
    .orElse("Unknown");

// filter：条件不满足时变成空 Optional
Optional<String> longName = Optional.of("Alice")
    .filter(s -> s.length() > 10);  // Optional.empty()

// flatMap：当映射函数本身返回 Optional 时
Optional<String> city = Optional.ofNullable(user)
    .flatMap(User::getOptionalAddress)   // 返回 Optional<Address>
    .flatMap(Address::getOptionalCity);  // 返回 Optional<String>
```

### 5.4 Optional 的使用原则

```java
// ✅ 用作方法返回值，表示结果可能不存在
public Optional<User> findById(String id) {
    User user = db.query(id);
    return Optional.ofNullable(user);
}

// ❌ 不要用作方法参数（调用者还是要判断传 Optional 还是传 null）
// ❌ 不要用作类的字段（Optional 没有实现 Serializable）
// ❌ 不要用 Optional 包装集合（空集合比 Optional<List> 更好）
// ❌ 不要用 isPresent() + get() 替代 null 检查（这和直接判 null 一样丑）

// 反面教材
if (opt.isPresent()) {
    doSomething(opt.get());
}

// 正确姿势
opt.ifPresent(value -> doSomething(value));
// 或
opt.ifPresentOrElse(
    value -> doSomething(value),
    () -> handleEmpty()
);  // Java 9+
```

## 6. 小结

| 主题 | 关键要点 |
|------|---------|
| Lambda | 匿名函数，替代匿名内部类；底层用 invokedynamic 而非生成类 |
| 函数式接口 | 只有一个抽象方法；四大核心：Function、Predicate、Consumer、Supplier |
| 方法引用 | Lambda 的简写；四种形式：静态、实例(对象)、实例(类)、构造 |
| Stream 三阶段 | 数据源 → 中间操作(lazy) → 终端操作(触发执行) |
| 常用终端操作 | collect、forEach、count、reduce、findFirst、anyMatch |
| Collectors | toList、toSet、toMap、groupingBy、joining、partitioningBy |
| flatMap | 展平嵌套结构，一对多映射 |
| Optional | 替代 null；用作返回值，不用作参数和字段；链式 map/flatMap/orElse |

---

> **下一篇预告**：I/O 与文件操作——BIO、NIO 与 Files 工具类

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
