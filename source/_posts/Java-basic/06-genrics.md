---
title: 'Java基础(6) | 泛型：类型擦除、通配符与 PECS 原则'
date: 2026-05-06
tags:
  - Java
  - 泛型
categories:
  - Java基础
---

## 前言

泛型是 Java 类型系统中最容易让人困惑的部分——语法不难，但背后的类型擦除机制、通配符的边界规则、PECS 原则，不搞清楚就会在实际开发中反复碰壁。这篇文章从"泛型为什么存在"讲起，把这些概念一次理清。

<!-- more -->

## 1. 没有泛型的年代

Java 5 之前，集合只能存 `Object`，取出来必须强转：

```java
List list = new ArrayList();
list.add("hello");
list.add(123);           // 什么都能塞，编译器不管

String s = (String) list.get(0);  // 必须强转
String s2 = (String) list.get(1); // 运行时 ClassCastException！
```

问题很明显：**类型错误只能在运行时发现**，而且代码里到处是强转。泛型的目标就是把类型检查提前到编译期。

## 2. 泛型基础

### 2.1 泛型类

```java
// T 是类型参数，定义时不确定，使用时指定
public class Box<T> {
    private T value;

    public Box(T value) { this.value = value; }
    public T getValue() { return value; }
    public void setValue(T value) { this.value = value; }
}

Box<String> strBox = new Box<>("hello");
String s = strBox.getValue();        // 不需要强转
// strBox.setValue(123);             // 编译报错！类型安全

Box<Integer> intBox = new Box<>(42);
int n = intBox.getValue();           // 自动拆箱
```

### 2.2 泛型方法

方法也可以独立声明自己的类型参数，不依赖类的泛型：

```java
public class Util {
    // <T> 声明在返回值之前
    public static <T> T firstOrNull(List<T> list) {
        return list.isEmpty() ? null : list.get(0);
    }
}

String s = Util.firstOrNull(List.of("a", "b"));   // 编译器自动推断 T = String
Integer n = Util.firstOrNull(List.of(1, 2, 3));    // T = Integer
```

### 2.3 泛型接口

```java
public interface Comparable<T> {
    int compareTo(T other);
}

public class Student implements Comparable<Student> {
    int score;

    @Override
    public int compareTo(Student other) {
        return this.score - other.score;  // 参数类型确定，不需要强转
    }
}
```

### 2.4 多个类型参数

```java
public class Pair<K, V> {
    private K key;
    private V value;

    public Pair(K key, V value) {
        this.key = key;
        this.value = value;
    }

    public K getKey() { return key; }
    public V getValue() { return value; }
}

Pair<String, Integer> p = new Pair<>("age", 25);
```

常见的类型参数命名约定：`T`（Type）、`E`（Element）、`K`（Key）、`V`（Value）、`R`（Return）。

## 3. 类型擦除（Type Erasure）

这是 Java 泛型最核心也最反直觉的机制。

### 3.1 泛型只存在于编译期

编译器检查完类型安全后，会把所有泛型信息**擦除**，替换成原始类型：

```java
// 你写的代码
List<String> list = new ArrayList<>();
list.add("hello");
String s = list.get(0);

// 编译后（字节码层面）实际变成
List list = new ArrayList();
list.add("hello");
String s = (String) list.get(0);  // 编译器自动插入了强转
```

也就是说，**泛型是纯编译期的语法糖**，运行时 JVM 完全不知道 `List<String>` 和 `List<Integer>` 有什么区别。

### 3.2 类型擦除的后果

```java
// 1. 运行时无法获取泛型类型
List<String> strList = new ArrayList<>();
List<Integer> intList = new ArrayList<>();
System.out.println(strList.getClass() == intList.getClass());  // true，都是 ArrayList

// 2. 不能用基本类型作为类型参数
// List<int> list = ...;  // 编译报错，只能用 List<Integer>

// 3. 不能创建泛型数组
// T[] arr = new T[10];   // 编译报错
// 替代方案：
T[] arr = (T[]) new Object[10];  // 可以，但有警告

// 4. 不能用 instanceof 检查泛型类型
// if (list instanceof List<String>) { }  // 编译报错
if (list instanceof List<?>) { }          // 可以，用通配符

// 5. 不能 new T()
// T obj = new T();  // 编译报错，擦除后变成 new Object()，无意义
```

### 3.3 为什么 Java 选择类型擦除？

一个词：**向后兼容**。Java 5 引入泛型时，必须保证已有的数百万行非泛型代码（原始类型 `List`、`Map`）能继续运行，不需要重新编译。类型擦除让泛型代码和非泛型代码在字节码层面完全一样，完美兼容。代价就是运行时丢失了类型信息。

作为对比，C++ 的模板会为每种类型参数生成独立的代码（模板实例化），没有擦除问题，但会导致代码膨胀。

## 4. 类型边界（Bounded Types）

默认情况下泛型的类型参数 `T` 可以是任意类型，但有时需要限制 `T` 的范围，比如要求 `T` 必须能比较大小，或者必须有某些方法。类型边界就是用来做这个限制的。

### 4.1 为什么需要上界？

```java
// 没有限制：T 可以是任何类型
public static <T> T max(T a, T b) {
    return a.compareTo(b) >= 0 ? a : b;  // 编译报错！
    // 编译器不知道 T 有没有 compareTo 方法
}

// 加上界：告诉编译器 T 一定实现了 Comparable，所以一定有 compareTo
public static <T extends Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) >= 0 ? a : b;  // 合法！
}

max(1, 2);      // Integer 实现了 Comparable，合法
max("a", "b");  // String 实现了 Comparable，合法
// max(new Object(), new Object());  // 编译报错，Object 没实现 Comparable
```

`T extends Comparable<T>` 的意思是：**T 必须是实现了 Comparable 接口的类型**。这里的 `extends` 不是继承，是"上界"的意思，既可以限制父类也可以限制接口，统一用 `extends`。

### 4.2 多重边界

用 `&` 同时加多个限制，表示 T 必须**同时满足**所有条件：

```java
// T 必须是 Animal 的子类，同时实现 Flyable 接口
// 这样方法体里就可以同时调用两者的方法
public <T extends Animal & Flyable> void doSomething(T t) {
    t.eat();  // 合法：T 是 Animal 子类，有 eat()
    t.fly();  // 合法：T 实现了 Flyable，有 fly()
}

// 只有既继承 Animal 又实现 Flyable 的类才能传进来
// 比如前面定义的 Duck（extends Animal implements Flyable）
doSomething(new Duck("Donald"));  // 合法
// doSomething(new Dog("Buddy")); // 编译报错，Dog 没实现 Flyable
```

语法规则：**类必须写在第一位，接口写在后面**，因为 Java 只能单继承：

```java
<T extends Animal & Flyable & Swimmable>  // ✅ 一个类 + 多个接口
<T extends Flyable & Swimmable>           // ✅ 全是接口，顺序无所谓
<T extends Flyable & Animal>              // ❌ Animal 是类却不在第一位，编译报错
```

## 5. 通配符（Wildcard）

通配符 `?` 表示"某个未知类型"，和类型参数 `T` 的区别是：**`T` 是定义时声明的占位符，`?` 是使用时表示"我不关心具体类型"。**

### 5.1 无界通配符 `<?>`

```java
// 只需要读取、不关心具体类型时使用
public void printList(List<?> list) {
    for (Object item : list) {
        System.out.println(item);
    }
}

printList(List.of("a", "b"));
printList(List.of(1, 2, 3));
```

### 5.2 上界通配符 `<? extends T>` —— 只能读

```java
// 接受 Number 及其子类（Integer、Double、Long...）的 List
public double sum(List<? extends Number> list) {
    double total = 0;
    for (Number n : list) {
        total += n.doubleValue();  // 读取：合法，取出来的一定是 Number
    }
    // list.add(1);               // 编译报错！不能写入
    return total;
}

sum(List.of(1, 2, 3));           // List<Integer> → 合法
sum(List.of(1.5, 2.5));          // List<Double> → 合法
```

**为什么不能写入？** 因为编译器只知道 list 里存的是"某种 Number 的子类"，但不知道具体是哪种。如果 list 实际是 `List<Double>`，你往里塞一个 `Integer` 就类型不安全了。所以编译器一律禁止写入。

### 5.3 下界通配符 `<? super T>` —— 只能写

```java
// 接受 Integer 及其父类（Number、Object）的 List
public void addNumbers(List<? super Integer> list) {
    list.add(1);       // 写入：合法，Integer 一定是 list 元素类型的子类
    list.add(2);
    // Integer n = list.get(0);  // 编译报错！取出来的类型不确定，只能当 Object 用
    Object o = list.get(0);      // 只能用 Object 接收
}

addNumbers(new ArrayList<Integer>());  // 合法
addNumbers(new ArrayList<Number>());   // 合法
addNumbers(new ArrayList<Object>());   // 合法
```

## 6. PECS 原则

**Producer Extends, Consumer Super。** 这是 Effective Java 中总结的通配符使用口诀：

- **生产者（从集合中读取数据）** → `<? extends T>`
- **消费者（向集合中写入数据）** → `<? super T>`

```java
// 一个实际例子：把 src 的内容复制到 dest
public static <T> void copy(List<? super T> dest, List<? extends T> src) {
    for (T item : src) {     // src 是生产者，用 extends，只读
        dest.add(item);       // dest 是消费者，用 super，只写
    }
}

List<Number> numbers = new ArrayList<>();
List<Integer> ints = List.of(1, 2, 3);
copy(numbers, ints);  // 合法：dest 接受 Number（Integer 的父类），src 提供 Integer
```

如果**既要读又要写**，那就不用通配符，直接用确定的类型参数 `<T>`。

### 6.1 一张图记住

```
<? extends T>  →  能读不能写  →  从集合取数据（Producer）
<? super T>    →  能写不能读  →  往集合塞数据（Consumer）
<T>            →  能读能写    →  既取又塞
<?>            →  只能读Object →  完全不关心类型
```

## 7. 泛型的常见使用模式

### 7.1 泛型工具方法

```java
public class CollectionUtil {
    // 交换列表中两个位置的元素
    public static <T> void swap(List<T> list, int i, int j) {
        T temp = list.get(i);
        list.set(i, list.get(j));
        list.set(j, temp);
    }

    // 过滤列表
    public static <T> List<T> filter(List<T> list, Predicate<T> predicate) {
        List<T> result = new ArrayList<>();
        for (T item : list) {
            if (predicate.test(item)) result.add(item);
        }
        return result;
    }
}

List<String> longNames = CollectionUtil.filter(
    List.of("Alice", "Bob", "Christopher"),
    name -> name.length() > 4
);
// ["Alice", "Christopher"]
```

### 7.2 泛型类的继承

泛型类继承时，子类有三种处理父类（`Box<T>`）类型参数的方式：

| 方式 | 写法 | 含义 |
|------|------|------|
| 固定类型 | `StringBox extends Box<String>` | 子类直接指定 T 是什么，不再泛型 |
| 透传类型 | `NamedBox<T> extends Box<T>` | 子类保留泛型，T 由使用时决定 |
| 扩展类型 | `MappedBox<K, V> extends Box<V>` | 子类新增自己的类型参数 |

```java
// 方式 1：固定类型——子类确定父类的类型参数，StringBox 不再是泛型类
public class StringBox extends Box<String> {
    public StringBox(String value) { super(value); }
}
StringBox sb = new StringBox("hello");  // 只能装 String

// 方式 2：透传类型——子类保留泛型，T 由创建对象时决定
public class NamedBox<T> extends Box<T> {
    private String label;
    public NamedBox(String label, T value) {
        super(value);
        this.label = label;
    }
}
NamedBox<Integer> nb = new NamedBox<>("age", 18);  // T 在这里才确定

// 方式 3：扩展类型——子类新增自己的类型参数 K，父类的 V 由子类传入
public class MappedBox<K, V> extends Box<V> {
    private K key;
    public MappedBox(K key, V value) {
        super(value);
        this.key = key;
    }
}
MappedBox<String, Integer> mb = new MappedBox<>("age", 18);  // K=String，V=Integer
```

## 8. 实际开发中的注意事项

### 8.1 泛型与可变参数

可变参数（`T... items`）允许传入任意数量的参数，等价于传入一个数组，和 Python 的 `*args` 类似：

```java
// Java
public static <T> List<T> listOf(T... items) { ... }
listOf("a", "b", "c");   // 传几个都行

# Python
def list_of(*args):
    return list(args)
list_of("a", "b", "c")
```

Python 还有 `**kwargs` 接收键值对，Java 没有直接对应的语法，键值对一般用 `Map` 传入。

**为什么编译器会报警告？**

泛型 + 可变参数组合在一起有一个潜在风险。可变参数底层是数组，而 Java 的泛型数组会有类型安全问题：

```java
public static <T> T[] toArray(T... items) {
    return items;  // 运行时 T 已被擦除，实际是 Object[]
}

String[] arr = toArray("a", "b");  // 运行时抛 ClassCastException！
// 编译器擦除后实际是：String[] arr = (String[]) new Object[]{"a","b"}
// Object[] 无法强转成 String[]
```

所以编译器看到泛型可变参数就报警告，提醒你"这里可能有堆污染（Heap Pollution）"。

**`@SafeVarargs` 的含义**

如果你确认方法内部只是**读取**数组元素，没有做危险的转型或写入，就可以加 `@SafeVarargs` 告诉编译器"我知道这是安全的，不用警告"：

```java
// 安全：只是把元素读出来放进 List，没有危险操作
@SafeVarargs
public static <T> List<T> listOf(T... items) {
    return Arrays.asList(items);  // 合法，不会有运行时问题
}

listOf("a", "b", "c");     // ["a", "b", "c"]
listOf(1, 2, 3);           // [1, 2, 3]
```

注意 `@SafeVarargs` 只能加在 `static` 方法、`final` 方法或构造方法上，因为这些方法不能被重写，能保证安全承诺不会被子类破坏。

### 8.2 获取泛型类型信息（绕过擦除）

虽然运行时泛型被擦除了，但通过反射可以获取类/字段/方法签名上的泛型信息：

> 需要反射基础，建议学完第 12 篇后再回来看。

```java
// 这就是为什么 Jackson、Spring 等框架能正确反序列化泛型类型
// 它们通过匿名子类保留泛型信息（TypeReference 模式）

// Jackson 示例
List<User> users = objectMapper.readValue(
    json,
    new TypeReference<List<User>>() {}  // 匿名子类保留了 List<User> 的类型信息
);
```

### 8.3 菱形推断（Diamond Inference）

```java
// Java 7+：右侧的类型参数可以省略，编译器从左侧推断
List<String> list = new ArrayList<>();          // 不需要写 new ArrayList<String>()
Map<String, List<Integer>> map = new HashMap<>();

// Java 10+：var 让推断更彻底
var list = new ArrayList<String>();  // 推断为 ArrayList<String>
// 注意：var list = new ArrayList<>(); 推断为 ArrayList<Object>，不是你想要的
```

## 9. 小结

| 主题 | 关键要点 |
|------|---------|
| 泛型目的 | 编译期类型检查，消除强转，类型安全 |
| 类型擦除 | 泛型只存在于编译期，运行时全部变成 Object / 上界类型 |
| 擦除代价 | 不能 new T()、不能用基本类型、不能 instanceof 泛型、运行时获取不到类型参数 |
| extends 边界 | `<T extends X>` 限制 T 必须是 X 的子类型 |
| 通配符 | `?` 表示未知类型；`? extends` 只读，`? super` 只写 |
| PECS | Producer Extends, Consumer Super |
| 实际应用 | TypeReference 绕过擦除、@SafeVarargs、菱形推断 |

---

> **下一篇预告**：异常体系——Checked vs Unchecked，try-with-resources 与最佳实践