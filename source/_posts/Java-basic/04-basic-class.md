---
title: 'Java基础(4) | 类与对象：构造方法、访问控制、static 与 final'
date: 2026-05-04
tags:
  - Java
  - 面向对象
  - 基础
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

Java 是一门纯面向对象的语言——除了 8 种基本类型，一切都是对象。这篇文章梳理类与对象的基础机制：怎么定义类、怎么构造对象、访问权限怎么控制，以及 `static` 和 `final` 这两个高频关键字到底在干什么。

<!-- more -->

## 1. 类与对象的关系

一句话：**类是模板，对象是实例。**

```java
// 定义类（模板）
public class Student {
    String name;
    int age;

    void introduce() {
        System.out.println("I'm " + name + ", " + age + " years old.");
    }
}

// 创建对象（实例）
Student s1 = new Student();
s1.name = "Alice";
s1.age = 20;
s1.introduce();  // I'm Alice, 20 years old.

Student s2 = new Student();
s2.name = "Bob";
// s1 和 s2 是两个独立的对象，各自持有自己的 name 和 age
```

`new Student()` 做了三件事：在堆上分配内存 → 调用构造方法初始化 → 返回对象引用。变量 `s1` 存的不是对象本身，而是指向堆上对象的**引用**（类似 C++ 的指针，但不能做指针运算）。

## 2. 构造方法（Constructor）

### 2.1 基本用法

构造方法的名字必须和类名相同，没有返回值类型：

```java
public class Student {
    String name;
    int age;

    // 有参构造
    public Student(String name, int age) {
        this.name = name;  // this 指向当前对象，用于区分参数和成员变量
        this.age = age;
    }

    // 无参构造
    public Student() {
        this("Unknown", 0);  // 用 this() 调用另一个构造方法，必须放在第一行
    }
}

Student s1 = new Student("Alice", 20);
Student s2 = new Student();  // name = "Unknown", age = 0
```

### 2.2 默认构造方法

如果你**一个构造方法都没写**，编译器会自动生成一个无参构造：

```java
public class Dog {
    String name;
    // 编译器自动生成：public Dog() {}
}

Dog d = new Dog();  // 合法
```

但只要你写了**任何一个**构造方法，编译器就不再自动生成了：

```java
public class Dog {
    String name;

    public Dog(String name) {
        this.name = name;
    }
    // 不再有默认无参构造
}

// Dog d = new Dog();  // 编译报错！没有无参构造方法
Dog d = new Dog("Buddy");  // 必须传参
```

这是一个很容易踩的坑，尤其在后面学到继承和框架（Spring 等依赖无参构造）的时候。

## 3. this 关键字

`this` 指向当前对象的引用，有三种用途：

```java
public class Student {
    String name;

    // 用途 1：区分成员变量和同名参数
    public Student(String name) {
        this.name = name;
    }

    // 用途 2：在构造方法中调用另一个构造方法（必须是第一行）
    public Student() {
        this("Unknown");
    }

    // 用途 3：返回当前对象，实现链式调用
    public Student setName(String name) {
        this.name = name;
        return this;
    }
}

// 链式调用
Student s = new Student().setName("Alice");
```

## 4. 访问修饰符

Java 有四种访问级别，控制"谁能看到这个成员"：

| 修饰符 | 同一个类 | 同一个包 | 子类 | 任何地方 |
|--------|---------|---------|------|---------|
| `private` | ✅ | ❌ | ❌ | ❌ |
| 默认（不写） | ✅ | ✅ | ❌ | ❌ |
| `protected` | ✅ | ✅ | ✅ | ❌ |
| `public` | ✅ | ✅ | ✅ | ✅ |

### 4.1 封装：private + getter/setter

面向对象的核心原则之一是**封装**——不直接暴露字段，通过方法控制访问：

```java
public class Student {
    private String name;   // 外部不能直接访问
    private int age;

    public String getName() {
        return name;
    }

    public void setAge(int age) {
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException("Invalid age: " + age);
        }
        this.age = age;  // 在 setter 中加入校验逻辑
    }
}

Student s = new Student();
// s.age = -1;     // 编译报错，age 是 private
s.setAge(-1);      // 运行时抛异常，被校验拦住
```

### 4.2 实际开发中怎么选？

- **字段**：几乎总是 `private`
- **方法**：对外的 API 用 `public`，内部辅助方法用 `private`
- **`protected`**：留给子类访问的，在继承篇细讲
- **默认（包访问）**：同一个包内共享，适合紧密关联的工具类

## 5. static 关键字

`static` 的核心含义：**属于类，而不是属于某个对象。**

### 5.1 静态变量

```java
public class Student {
    String name;               // 实例变量：每个对象各有一份
    static int totalCount = 0; // 静态变量：全班共享一份

    public Student(String name) {
        this.name = name;
        totalCount++;          // 每创建一个学生，计数 +1
    }
}

new Student("Alice");
new Student("Bob");
System.out.println(Student.totalCount);  // 2（通过类名访问，不需要对象）
```

### 5.2 静态方法

```java
public class MathUtil {
    public static int add(int a, int b) {
        return a + b;
    }
}

MathUtil.add(1, 2);  // 通过类名直接调用，不需要创建对象
```

**静态方法的限制**：

```java
public class Student {
    String name;
    static int totalCount;

    public static void printCount() {
        System.out.println(totalCount);  // 可以访问静态变量
        // System.out.println(name);     // 编译报错！静态方法不能访问实例变量
        // this.xxx                      // 编译报错！静态方法中没有 this
    }
}
```

原因很简单：静态方法调用时可能根本没有对象存在，所以它不知道 `name` 是谁的 `name`，也没有 `this` 可指。

### 5.3 静态代码块

在类**第一次被加载**时执行一次，常用于初始化静态资源：

```java
public class Config {
    static Map<String, String> settings;

    static {
        settings = new HashMap<>();
        settings.put("env", "production");
        settings.put("version", "1.0");
        System.out.println("Config loaded.");  // 只会输出一次
    }
}
```

### 5.4 静态方法 vs 实例方法：什么时候用 static？

```
这个方法需要访问对象的状态（实例变量）吗？
├── 需要 → 实例方法
└── 不需要 → 考虑 static
    ├── 纯工具/计算（如 Math.max、Integer.parseInt）→ static
    └── 工厂方法（如 List.of、LocalDate.now）→ static
```

## 6. final 关键字

`final` 表示"不可变"，可以修饰变量、方法、类：

### 6.1 final 变量（常量）

```java
final int MAX_SIZE = 100;
// MAX_SIZE = 200;  // 编译报错，不能重新赋值

// 对于引用类型，final 限制的是引用本身，不是对象内容
final List<String> list = new ArrayList<>();
list.add("a");           // 合法，修改的是对象内容
// list = new ArrayList<>();  // 编译报错，不能让 list 指向新对象
```

这个区别非常重要：**`final` 只保证引用不变，不保证对象内部状态不变。**

### 6.2 final 方法

```java
public class Parent {
    public final void doSomething() {
        System.out.println("This cannot be overridden.");
    }
}

public class Child extends Parent {
    // public void doSomething() {}  // 编译报错，不能重写 final 方法
}
```

### 6.3 final 类

```java
public final class MathUtil {
    // 这个类不能被继承
}

// public class SuperMath extends MathUtil {}  // 编译报错
```

Java 标准库中 `String`、`Integer` 等包装类都是 `final` 的，防止被子类篡改行为。

### 6.4 常量命名规范

```java
// static + final = 类级别常量，用全大写 + 下划线命名
public static final int MAX_RETRY_COUNT = 3;
public static final String DEFAULT_CHARSET = "UTF-8";
```

## 7. 一个完整的类示例

把上面所有知识点串起来：

```java
public class BankAccount {
    // 静态常量
    private static final double MIN_BALANCE = 10.0;

    // 静态变量
    private static int accountCount = 0;

    // 实例变量
    private String owner;
    private double balance;
    private final String accountId;  // 创建后不可修改

    // 静态代码块
    static {
        System.out.println("BankAccount class loaded.");
    }

    // 有参构造
    public BankAccount(String owner, double initialBalance) {
        this.owner = owner;
        this.balance = initialBalance;
        this.accountId = "ACC-" + (++accountCount);
    }

    // 无参构造
    public BankAccount(String owner) {
        this(owner, 0.0);
    }

    // 实例方法
    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("Amount must be positive");
        this.balance += amount;
    }

    public void withdraw(double amount) {
        if (balance - amount < MIN_BALANCE) {
            throw new IllegalStateException("Insufficient balance");
        }
        this.balance -= amount;
    }

    // getter（不提供 setter，balance 只能通过 deposit/withdraw 修改）
    public String getOwner() { return owner; }
    public double getBalance() { return balance; }
    public String getAccountId() { return accountId; }

    // 静态方法
    public static int getAccountCount() {
        return accountCount;
    }

    @Override
    public String toString() {
        return accountId + " [" + owner + "] balance=" + balance;
    }
}
```

```java
// 使用
BankAccount a1 = new BankAccount("Alice", 100);
BankAccount a2 = new BankAccount("Bob");

a1.deposit(50);
a1.withdraw(30);
System.out.println(a1);                      // ACC-1 [Alice] balance=120.0
System.out.println(BankAccount.getAccountCount()); // 2
```

## 8. 小结

| 主题 | 关键要点 |
|------|---------|
| 类与对象 | 类是模板，对象是实例；变量存的是引用，不是对象本身 |
| 构造方法 | 和类同名，无返回值；写了任何构造方法后默认无参构造消失 |
| this | 区分同名变量、调用其他构造方法、实现链式调用 |
| 访问修饰符 | 字段用 private 封装，方法按需暴露；四级：private < 默认 < protected < public |
| static | 属于类不属于对象；静态方法不能访问实例成员、没有 this |
| final | 变量不可重新赋值（引用类型只锁引用）、方法不可重写、类不可继承 |
| static final | 类级别常量，全大写下划线命名 |

下图展示了 Java 中类级别成员与对象级别成员的归属关系及生命周期：

![类与对象结构全景](/images/Java-basic/class-object-structure.png)

**类级别（紫色）**：随 JVM 类加载而存在，整个程序生命周期内只有一份。
- `static {}` 静态代码块：类第一次被加载时执行一次，常用于初始化静态资源
- `static` 变量：所有对象共享同一份，通过类名访问
- `static` 方法：无 `this`，不能访问实例变量，适合工具方法和工厂方法
- `static final` 常量：类级别不可变量，全大写下划线命名

**对象级别（青色）**：随 `new` 创建、随 GC 回收，每个对象各自独立。
- 构造方法：`new` 时调用，负责初始化实例变量
- 实例变量：每个对象各有一份，互不影响
- 实例方法：持有 `this` 引用，可访问当前对象的所有实例变量
- `final` 实例变量：构造方法赋值后不可重新赋值，常用于 id、accountId 等不变字段
- `finalize()`：GC 回收前调用，Java 9 起已废弃，实际开发中不要依赖它做资源释放，应使用 `try-with-resources` 代替

**`static` 变量与对象的关系**（图中虚线）：所有对象读写的是同一份 `static` 变量，因此常用于计数器、全局配置等场景。

---

> **下一篇预告**：继承与多态——extends、方法重写、抽象类 vs 接口

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
