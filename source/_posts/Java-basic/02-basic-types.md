---
title: 'Java基础(2) | 基本数据类型：八大原始类型与那些必踩的坑'
date: 2026-05-02
tags:
  - Java
  - 数据类型
  - 基础
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

Java 是一门**强类型语言**——每个变量在编译期就必须确定类型，不像 Python 可以随意赋值。这篇文章系统梳理 Java 的基本数据类型体系，重点放在容易混淆和实际开发中容易踩坑的地方。

<!-- more -->

## 1. 八大基本类型（Primitive Types）

Java 有且只有 8 种基本类型，分为四大类：

| 分类 | 类型 | 大小 | 范围 | 默认值 | 说明 |
|------|------|------|------|--------|------|
| 整型 | `byte` | 1 字节 | -128 ~ 127 | 0 | 网络传输、文件 I/O 常用 |
| | `short` | 2 字节 | -32768 ~ 32767 | 0 | 实际开发中很少用 |
| | `int` | 4 字节 | -2³¹ ~ 2³¹-1（约 ±21 亿） | 0 | **最常用的整数类型** |
| | `long` | 8 字节 | -2⁶³ ~ 2⁶³-1 | 0L | 时间戳、大数场景 |
| 浮点 | `float` | 4 字节 | ±3.4×10³⁸（约 6-7 位有效数字） | 0.0f | 精度有限，慎用 |
| | `double` | 8 字节 | ±1.8×10³⁰⁸（约 15-16 位有效数字） | 0.0d | **默认浮点类型** |
| 字符 | `char` | 2 字节 | 0 ~ 65535（Unicode） | '\u0000' | 注意是**无符号**的 |
| 布尔 | `boolean` | 未规定 | true / false | false | JVM 实现通常用 1 字节 |

### 1.1 几个容易忽略的细节

**整型字面量默认是 `int`**。写 `long x = 2147483648;` 会编译报错，因为右边的数字先按 `int` 解析，已经溢出了。必须加 `L` 后缀：

```java
long x = 2147483648L; // 正确
```

**浮点字面量默认是 `double`**。所以 `float f = 3.14;` 也会报错（double 不能隐式转 float），需要写成：

```java
float f = 3.14f; // 正确
```

**`char` 本质是整数**。它可以参与算术运算：

```java
char c = 'A';
System.out.println(c + 1);     // 输出 66（int）
System.out.println((char)(c + 1)); // 输出 'B'
```

**`boolean` 不能和任何其他类型互转**。不像 C/C++ 中 0 可以当 false 用，Java 中 `if (1)` 直接编译报错。

## 2. 类型转换

### 2.1 自动类型转换（隐式，Widening）

小范围类型可以自动转为大范围类型，不丢失信息：

```
byte → short → int → long → float → double
              char ↗
```

```java
int i = 100;
long l = i;       // int → long，自动转换
double d = l;     // long → double，自动转换
```

> **注意**：`int → float` 和 `long → double` 虽然是"自动"的，但**可能丢失精度**。因为 `float` 只有约 7 位有效数字，而 `int` 最大有 10 位：

```java
int big = 123456789;
float f = big;
System.out.println(f);  // 输出 1.23456792E8，末尾已经不准了
```

### 2.2 强制类型转换（显式，Narrowing）

大范围转小范围必须显式声明，且有丢失数据的风险：

```java
double d = 3.99;
int i = (int) d;        // i = 3，直接截断，不是四舍五入

long big = 130;
byte b = (byte) big;    // b = -126，溢出回绕（130 - 256 = -126）
```

### 2.3 表达式中的类型提升

当不同类型参与同一个表达式运算时，Java 会自动"提升"到更大的类型：

```java
byte a = 10;
byte b = 20;
// byte c = a + b;  // 编译报错！a + b 的结果是 int
int c = a + b;      // 正确

// 规则：byte/short/char 参与运算时，一律先提升为 int
```

这个规则初学时很容易中招，记住一条：**`byte`、`short`、`char` 之间运算，结果都是 `int`。**

## 3. 包装类（Wrapper Classes）
 
每个基本类型都有对应的包装类，用于在需要对象的场合（泛型、集合等）使用：
 
| 基本类型 | 包装类 | 缓存范围 |
|---------|--------|---------|
| `byte` | `Byte` | -128 ~ 127（全部） |
| `short` | `Short` | -128 ~ 127 |
| `int` | `Integer` | -128 ~ 127（可调） |
| `long` | `Long` | -128 ~ 127 |
| `float` | `Float` | 无缓存 |
| `double` | `Double` | 无缓存 |
| `char` | `Character` | 0 ~ 127 |
| `boolean` | `Boolean` | TRUE / FALSE（两个实例） |
 
### 3.1 为什么需要包装类？
 
Java 的泛型和集合框架只能操作**对象**，不能接受基本类型。比如你想用一个 `List` 存一组整数：
 
```java
List<int> list = new ArrayList<>();  // 编译报错！泛型不接受基本类型
List<Integer> list = new ArrayList<>();  // 正确，Integer 是对象
```
 
这就是包装类存在的根本原因：**它是基本类型的"对象化"版本**，让基本类型能融入 Java 的面向对象体系（泛型、集合、反射、序列化等都要求对象）。
 
### 3.2 装箱与拆箱
 
所谓**装箱（Boxing）**，就是把基本类型"装进"包装类对象里；**拆箱（Unboxing）** 则是反过来，从包装类对象中把基本类型值"取出来"：
 
```java
// 手动装箱 / 拆箱（Java 5 之前的写法）
Integer a = Integer.valueOf(42);  // 装箱：int → Integer 对象
int b = a.intValue();             // 拆箱：Integer 对象 → int
```
 
Java 5 之后，编译器会自动帮你做这件事，称为**自动装箱 / 自动拆箱（Autoboxing / Unboxing）**：
 
```java
// 自动装箱 / 拆箱（Java 5+ 的写法，编译器在背后做了和上面一样的事）
Integer a = 42;    // 编译器自动变成 Integer.valueOf(42)
int b = a;         // 编译器自动变成 a.intValue()
 
List<Integer> list = new ArrayList<>();
list.add(1);             // 自动装箱：int → Integer
int first = list.get(0); // 自动拆箱：Integer → int
```
 
语法上方便了，但本质没变——每次装箱都可能创建对象，每次拆箱都在调方法。理解这一点才能理解后面的缓存池陷阱和 NPE 问题。
 
### 3.3 == 陷阱：这是最经典的坑
 
```java
Integer a = 127;
Integer b = 127;
System.out.println(a == b);  // true —— 命中缓存，是同一个对象
 
Integer c = 128;
Integer d = 128;
System.out.println(c == d);  // false —— 超出缓存范围，是两个不同对象
 
System.out.println(c.equals(d));  // true —— 值相等
```
 
**原理**：`Integer.valueOf()` 对 -128 ~ 127 范围内的值使用了缓存池，返回同一个对象。超出范围就 `new` 一个新对象，所以 `==` 比较的是引用地址，不是值。
 
**结论：比较包装类的值，永远用 `.equals()`，不要用 `==`。**
 
### 3.4 拆箱的 NPE 风险
 
```java
Integer a = null;
int b = a;  // 运行时抛出 NullPointerException！
```
 
自动拆箱实际上是调用 `a.intValue()`，如果 `a` 是 `null`，就会 NPE。这在实际项目中非常常见，尤其是从数据库查询结果或 Map 中取值时。
 
## 4. String：最特殊的"类型"

`String` 不是基本类型，但它的使用频率和重要性堪比基本类型。

### 4.1 不可变性（Immutability）

```java
String s = "hello";
s = s + " world";  // 并没有修改原来的 "hello"，而是创建了新的 "hello world"
```

每次对 `String` 做拼接/替换，都会产生新对象。在循环中大量拼接字符串，应该用 `StringBuilder`：

```java
// 反面教材：每次循环都创建新 String
String result = "";
for (int i = 0; i < 10000; i++) {
    result += i;  // O(n²) 的时间复杂度
}

// 正确做法
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);  // O(n)
}
String result = sb.toString();
```

### 4.2 字符串常量池

```java
String a = "hello";
String b = "hello";
System.out.println(a == b);  // true —— 都指向常量池中的同一个对象

String c = new String("hello");
System.out.println(a == c);  // false —— c 是堆上的新对象
System.out.println(a.equals(c));  // true —— 值相等
```

**和 Integer 缓存一个道理：`==` 比较引用，`.equals()` 比较值。对 String 也一样，比较内容永远用 `.equals()`。**

### 4.3 常用方法速查

```java
String s = "Hello, World!";

s.length();              // 13
s.charAt(0);             // 'H'
s.substring(0, 5);       // "Hello"
s.indexOf("World");      // 7
s.contains("World");     // true
s.toLowerCase();         // "hello, world!"
s.trim();                // 去除首尾空白
s.split(", ");           // ["Hello", "World!"]
s.replace("World", "Java"); // "Hello, Java!"
s.isEmpty();             // false
s.isBlank();             // false（Java 11+，检测空白字符）

// 格式化（类似 C 的 sprintf）
String formatted = String.format("name: %s, age: %d", "Alice", 25);
```

## 5. 数组

Java 数组是固定长度的、类型安全的容器。

### 5.1 声明与初始化

```java
// 声明 + 分配
int[] arr = new int[5];          // 长度 5，所有元素初始化为 0

// 声明 + 直接赋值
int[] arr2 = {1, 2, 3, 4, 5};

// 二维数组
int[][] matrix = new int[3][4];  // 3 行 4 列
int[][] jagged = new int[3][];   // 不规则数组，每行长度可以不同
jagged[0] = new int[2];
jagged[1] = new int[5];
```

### 5.2 常见操作

```java
int[] arr = {5, 3, 1, 4, 2};

arr.length;                  // 5（注意：是字段，不是方法，没有括号）

Arrays.sort(arr);            // 排序：[1, 2, 3, 4, 5]，原地，无返回值（void）
Arrays.toString(arr);        // 转字符串："[1, 2, 3, 4, 5]"，返回新 String
Arrays.copyOf(arr, 10);      // 拷贝并扩容，多余位置填 0，返回新数组，原数组不变
Arrays.fill(arr, 0);         // 全部填充为 0，原地，无返回值（void）
Arrays.binarySearch(arr, 3); // 二分查找（需先排序），返回 int（索引）
```

### 5.3 数组 vs ArrayList

| 特性 | 数组 | ArrayList |
|------|------|-----------|
| 长度 | 固定 | 动态扩容 |
| 存储类型 | 基本类型 + 对象 | 仅对象（基本类型需要包装类） |
| 性能 | 更快（连续内存，无装箱） | 略慢（有装箱开销） |
| 使用场景 | 长度确定、性能敏感 | 大多数业务场景 |

## 6. 类型推断：var（Java 10+）

Java 10 引入了局部变量类型推断，让代码更简洁：

```java
// 传统写法
HashMap<String, List<Integer>> map = new HashMap<String, List<Integer>>();

// 使用 var
var map = new HashMap<String, List<Integer>>();  // 编译器自动推断类型
```

**限制**：

```java
var x = 10;          // 合法，推断为 int
var s = "hello";     // 合法，推断为 String

// var y;            // 不合法，必须有初始化表达式
// var z = null;     // 不合法，无法推断类型
// var 不能用于方法参数、成员变量、返回值类型
```

`var` 只是编译期语法糖，编译后和显式声明完全一样，不影响运行时性能。使用原则是：**当类型从右侧表达式一眼可知时用 `var` 减少噪音，否则显式写出类型增加可读性。**

## 7. 实际开发中的常见陷阱

### 7.1 浮点精度问题

```java
System.out.println(0.1 + 0.2);         // 0.30000000000000004
System.out.println(0.1 + 0.2 == 0.3);  // false
```

这不是 Java 的 bug，是 IEEE 754 浮点标准的固有限制。涉及金额计算时，必须用 `BigDecimal`：

```java
BigDecimal a = new BigDecimal("0.1");
BigDecimal b = new BigDecimal("0.2");
System.out.println(a.add(b));  // 0.3（精确）

// 注意：一定用字符串构造，不要用 double 构造
// new BigDecimal(0.1) 仍然不精确
```

### 7.2 整数溢出

```java
int max = Integer.MAX_VALUE;  // 2147483647
System.out.println(max + 1);  // -2147483648（静默溢出，没有异常！）
```

Java 整数运算溢出不会抛异常，而是悄悄回绕。如果需要检测溢出，可以使用 Java 8 引入的安全方法：

```java
Math.addExact(Integer.MAX_VALUE, 1);  // 抛出 ArithmeticException
```

### 7.3 整数除法

```java
int a = 7;
int b = 2;
System.out.println(a / b);    // 3，不是 3.5
System.out.println(a / (double) b);  // 3.5
```

两个 `int` 相除结果还是 `int`，直接截断小数部分。需要浮点结果时，至少将一个操作数转为 `double`。

### 7.4 char 的编码问题

```java
char c = '中';               // 合法，Java 的 char 是 UTF-16
System.out.println((int) c); // 20013

// 但 emoji 等 BMP 之外的字符用一个 char 装不下
String emoji = "😀";
System.out.println(emoji.length());      // 2（两个 char 单元）
System.out.println(emoji.codePointCount(0, emoji.length())); // 1（一个码点）
```

## 8. 小结

一张表回顾全文的核心知识：

| 主题 | 关键要点 |
|------|---------|
| 8 种基本类型 | 整型 4 种 + 浮点 2 种 + char + boolean，没有无符号整型（char 除外） |
| 字面量默认类型 | 整数默认 `int`（大数加 `L`），浮点默认 `double`（单精度加 `f`） |
| 类型转换 | 小→大自动，大→小强制；byte/short/char 运算一律提升为 int |
| 包装类 | 注意缓存范围内 `==` 的假象，比较值永远用 `.equals()` |
| String | 不可变，循环拼接用 StringBuilder，比较用 `.equals()` |
| 浮点精度 | 金额计算用 `BigDecimal`，且用字符串构造 |
| 整数溢出 | 静默回绕不报错，安全计算用 `Math.addExact()` |

---

> **下一篇预告**：面向对象——类、对象、封装、继承、多态、接口，从 C++ 视角理解 Java 的设计取舍

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
