---
title: 'Java基础(5) | 继承与多态：extends、重写、抽象类与接口'
date: 2026-05-05
tags:
  - Java
  - 面向对象
  - 继承
  - 多态
categories:
  - Java基础
---

## 前言

上一篇搞定了类与对象的基本机制，这篇进入面向对象的核心战场：继承和多态。这两个概念决定了 Java 代码如何组织复用和扩展，也是后面理解 Spring 等框架设计的基础。

<!-- more -->

## 1. 继承（extends）

### 1.1 基本语法

子类通过 `extends` 继承父类，获得父类的所有非 private 成员：

```java
public class Animal {
    protected String name;

    public Animal(String name) {
        this.name = name;
    }

    public void eat() {
        System.out.println(name + " is eating.");
    }
}

public class Dog extends Animal {
    private String breed;

    public Dog(String name, String breed) {
        super(name);         // 调用父类构造方法，必须放在第一行
        this.breed = breed;
    }

    public void bark() {
        System.out.println(name + " is barking!");  // 可以访问父类的 protected 字段
    }
}

Dog d = new Dog("Buddy", "Golden Retriever");
d.eat();   // 继承自 Animal
d.bark();  // Dog 自己的方法
```

### 1.2 super 关键字

`super` 用来引用父类，和 `this` 对称：

```java
public class Dog extends Animal {

    // 用途 1：调用父类构造方法（必须在子类构造方法的第一行）
    public Dog(String name) {
        super(name);
    }

    // 用途 2：调用父类被重写的方法
    @Override
    public void eat() {
        super.eat();  // 先执行父类的 eat
        System.out.println(name + " wags tail after eating.");
    }
}
```

### 1.3 构造方法的调用链

子类构造时，**必须先完成父类的构造**。如果你不显式写 `super()`，编译器会自动插入无参的 `super()`：

```java
public class Animal {
    public Animal() {
        System.out.println("Animal 构造");
    }
}

public class Dog extends Animal {
    public Dog() {
        // 编译器自动插入 super();
        System.out.println("Dog 构造");
    }
}

new Dog();
// 输出：
// Animal 构造
// Dog 构造
```

如果父类没有无参构造，子类必须显式调用父类的有参构造，否则编译报错：

```java
public class Animal {
    public Animal(String name) { ... }  // 只有有参构造
}

public class Dog extends Animal {
    public Dog() {
        // 编译报错！Animal 没有无参构造，编译器无法自动插入 super()
    }

    public Dog(String name) {
        super(name);  // 正确，显式调用父类有参构造
    }
}
```

### 1.4 Java 继承的限制

**Java 只支持单继承**——一个类只能 `extends` 一个父类：

```java
// class Dog extends Animal, Pet { }  // 编译报错！不支持多继承
```

这是 Java 对 C++ 多继承菱形问题的回避方案。需要"多继承"效果时，用接口。

**所有类都隐式继承 `Object`**。你没写 `extends` 的类，编译器自动加上 `extends Object`：

```java
// 你写的
public class Student { }

// 编译器理解的
public class Student extends Object { }
```

所以每个对象都有 `toString()`、`equals()`、`hashCode()` 等方法——它们定义在 `Object` 中。

## 2. 方法重写（Override）

### 2.1 基本规则

子类可以重写父类的方法，提供自己的实现：

```java
public class Animal {
    public void speak() {
        System.out.println("...");
    }
}

public class Dog extends Animal {
    @Override  // 这个注解不是必须的，但强烈建议加——防止拼错方法名变成新方法
    public void speak() {
        System.out.println("Woof!");
    }
}

public class Cat extends Animal {
    @Override
    public void speak() {
        System.out.println("Meow!");
    }
}
```

### 2.2 重写的约束

```java
// 父类方法
public class Animal {
    protected Animal create() throws IOException { ... }
}

// 子类重写
public class Dog extends Animal {
    @Override
    public Dog create() throws FileNotFoundException {  // 全部合法
        ...
    }
}
```

```Java
// static 方法不是重写，是隐藏（hiding）
public class Animal {
    public static void staticMethod() { System.out.println("Animal"); }
}
public class Dog extends Animal {
    public static void staticMethod() { System.out.println("Dog"); }
}

Animal a = new Dog();
a.staticMethod();  // 输出 "Animal"！看的是引用类型，不是对象类型
```

总结成规则：

| 维度 | 约束 |
|------|------|
| 方法名 | 必须相同 |
| 参数列表 | 必须相同（否则是重载，不是重写） |
| 返回值类型 | 相同或是子类（协变返回） |
| 访问修饰符 | 不能比父类更严格（protected → public 可以，反过来不行） |
| 异常 | 不能抛比父类更宽的受检异常 |
| final 方法 | 不能重写 |
| static 方法 | 不能重写（可以定义同签名方法，但那是隐藏，不是重写） |



### 2.3 重写 vs 重载

这两个概念名字像，本质完全不同：

| | 重写 Override | 重载 Overload |
|--|--------------|--------------|
| 发生位置 | 子类与父类之间 | 同一个类中 |
| 方法名 | 相同 | 相同 |
| 参数列表 | 必须相同 | **必须不同** |
| 绑定时机 | **运行时**（动态绑定） | **编译时**（静态绑定） |
| 关键字 | @Override | 无 |

```java
public class Calculator {
    // 重载：同一个类中，方法名相同，参数不同
    public int add(int a, int b) { return a + b; }
    public double add(double a, double b) { return a + b; }
    public int add(int a, int b, int c) { return a + b + c; }
}
```

### 2.4 哪些成员参与多态？

Java 中只有**普通实例方法**才有多态，`static` 方法和字段都不参与：

| 成员类型 | 绑定时机 | 看谁 | 是否多态 |
|----------|---------|------|---------|
| 普通实例方法 | 运行时 | 对象实际类型 | ✅ |
| `static` 方法 | 编译时 | 引用声明类型 | ❌（隐藏） |
| 字段 | 编译时 | 引用声明类型 | ❌ |

```java
Animal a = new Dog("Buddy");

a.speak();         // 普通方法 → 看对象（Dog）→ "Woof!"
a.staticMethod();  // static 方法 → 看引用（Animal）→ "Animal"
System.out.println(a.name);  // 字段 → 看引用（Animal）→ "Animal"
```

`static` 方法的同名定义叫**隐藏（Hiding）**，不叫重写；字段也不参与多态，但实际开发中字段几乎都是 `private`，这个坑基本踩不到。

## 3. 多态（Polymorphism）

### 3.1 向上转型

父类引用可以指向子类对象：

```java
Animal a = new Dog("Buddy");  // Dog 对象赋给 Animal 引用，自动向上转型，引用是 Animal，对象是 Dog
a.eat();    // 合法，Animal 有 eat 方法
// a.bark();  // 编译报错！编译器只看引用类型（Animal），Animal 没有 bark
```

### 3.2 动态绑定

**调用哪个方法，取决于对象的实际类型，而不是引用的声明类型**：

```java
Animal a1 = new Dog("Buddy");
Animal a2 = new Cat("Kitty");
Animal a3 = new Animal("Something");

a1.speak();  // "Woof!"   —— 实际是 Dog 对象，调用 Dog.speak()
a2.speak();  // "Meow!"   —— 实际是 Cat 对象，调用 Cat.speak()
a3.speak();  // "..."     —— 实际是 Animal 对象，调用 Animal.speak()
```

这就是多态的威力——同一段代码 `a.speak()` 根据实际对象类型表现出不同行为。

### 3.3 多态的典型应用

```java
// 不用多态：每加一种动物就要改代码
public void makeThemSpeak(Dog dog) { dog.speak(); }
public void makeThemSpeak(Cat cat) { cat.speak(); }
// 加一种 Bird？又要写一个方法...

// 用多态：一个方法搞定所有
public void makeThemSpeak(Animal animal) {
    animal.speak();  // 运行时自动调用正确的实现
}

// 更进一步：处理一组不同类型的动物
List<Animal> animals = List.of(new Dog("D"), new Cat("C"), new Dog("D2"));
for (Animal a : animals) {
    a.speak();  // 每个对象调用自己的实现
}
```

### 3.4 向下转型与 instanceof

有时需要把父类引用转回子类类型：

```java
Animal a = new Dog("Buddy");

// 向下转型：需要强制类型转换
Dog d = (Dog) a;      // 合法，a 实际上就是 Dog
d.bark();

// Cat c = (Cat) a;   // 编译通过，但运行时抛 ClassCastException！

// 安全做法：先用 instanceof 检查
if (a instanceof Dog) {
    Dog d2 = (Dog) a;
    d2.bark();
}

// Java 16+ 模式匹配：检查 + 转型一步到位
if (a instanceof Dog dog) {
    dog.bark();  // 直接用，不需要再强转
}

Animal a = new Dog();
a instanceof Animal  // true，包括子类
a.getClass() == Animal.class  // false，只匹配精确类型
```

## 4. 抽象类（abstract）

### 4.1 基本概念

有些类天生就不该被实例化——比如 `Animal` 只是一个概念，真实世界里只有 Dog、Cat。用 `abstract` 标记：

```java
public abstract class Animal {
    protected String name;

    public Animal(String name) {
        this.name = name;
    }

    // 抽象方法：只有声明，没有实现，强制子类必须重写
    public abstract void speak();

    // 普通方法：可以有实现，子类直接继承
    public void eat() {
        System.out.println(name + " is eating.");
    }
}

// new Animal("x");  // 编译报错！抽象类不能实例化

public class Dog extends Animal {
    public Dog(String name) { super(name); }

    @Override
    public void speak() {  // 必须实现，否则 Dog 也得是 abstract
        System.out.println("Woof!");
    }
}
```

### 4.2 抽象类的特点

- 可以有构造方法（供子类调用）
- 可以有普通方法和字段（提供默认实现和共享状态）
- 可以有抽象方法（强制子类实现）
- 不能被实例化
- 一个类如果有任何抽象方法，它就必须声明为 `abstract`

## 5. 接口（interface）

### 5.1 基本语法

接口定义一组行为的契约，不关心怎么实现：

```java
public interface Flyable {
    void fly();  // 默认是 public abstract，不需要写出来
}

public interface Swimmable {
    void swim();
}

// 一个类可以实现多个接口（弥补单继承的不足）
public class Duck extends Animal implements Flyable, Swimmable {
    public Duck(String name) { super(name); }

    @Override
    public void speak() { System.out.println("Quack!"); }

    @Override
    public void fly() { System.out.println(name + " is flying."); }

    @Override
    public void swim() { System.out.println(name + " is swimming."); }
}
```

接口类型也能作为引用（接口多态）：

```java
Flyable f = new Duck("Donald");
f.fly();     // 合法
// f.swim(); // 编译报错，Flyable 接口没有 swim 方法
```

### 5.2 接口中的成员

```java
public interface MyInterface {
    // 常量：默认 public static final
    int MAX = 100;

    // 抽象方法：默认 public abstract
    void doSomething();

    // 默认方法（Java 8+）：有实现体，实现类可以直接用或重写
    default void greet() {
        System.out.println("Hello from interface!");
    }

    // 静态方法（Java 8+）：通过接口名调用
    static void staticMethod() {
        System.out.println("Interface static method.");
    }

    // 私有方法（Java 9+）：接口内部复用代码
    private void helper() {
        System.out.println("internal helper");
    }
}
```

### 5.3 default 方法解决了什么问题？

在 Java 8 之前，给接口加一个方法意味着所有实现类都必须改代码。`default` 方法允许接口在不破坏已有实现的前提下演进：

```java
// Java 8 给 List 接口新增了 sort 方法，用 default 实现
// 已有的几百万个 List 实现类完全不受影响
public interface List<E> extends Collection<E> {
    default void sort(Comparator<? super E> c) {
        // 默认实现
    }
}
```

### 5.4 函数式接口

**只有一个抽象方法**的接口叫函数式接口，可以用 Lambda 表达式代替匿名内部类：

```java
// 用 @FunctionalInterface 标记（可选，但建议加——编译器会帮你检查）
@FunctionalInterface
public interface Comparator<T> {
    int compare(T o1, T o2);  // 只有一个抽象方法
}

// 没有 Lambda 之前：匿名内部类
list.sort(new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return a.length() - b.length();
    }
});

// 有了 Lambda：直接传行为
list.sort((a, b) -> a.length() - b.length());
```

Java 8 在 `java.util.function` 包中内置了四个最常用的函数式接口：

| 接口 | 方法签名 | 用途 |
|------|---------|------|
| `Supplier<T>` | `T get()` | 无入参，有返回值（生产者） |
| `Consumer<T>` | `void accept(T t)` | 有入参，无返回值（消费者） |
| `Function<T,R>` | `R apply(T t)` | 有入参，有返回值（转换） |
| `Predicate<T>` | `boolean test(T t)` | 有入参，返回 boolean（判断） |

Lambda 和这四个接口会在后面的 Lambda 与 Stream 篇详细展开。

## 6. 抽象类 vs 接口：怎么选？

| 维度 | 抽象类 | 接口 |
|------|--------|------|
| 关键字 | `abstract class` | `interface` |
| 继承/实现 | 单继承（extends） | 多实现（implements） |
| 构造方法 | 有 | 无 |
| 字段 | 任意字段 | 只有 `public static final` 常量 |
| 方法 | 抽象 + 普通 | 抽象 + default + static + private |
| 设计含义 | "是什么"（is-a） | "能做什么"（can-do） |

选择的思路：

```
需要共享状态（字段）或提供构造方法？
├── 是 → 抽象类
└── 否 → 接口
    需要多继承？
    ├── 是 → 只能用接口
    └── 否 → 优先接口（更灵活）
```

**现代 Java（8+）的趋势是优先用接口。** 因为 default 方法的引入让接口也能提供默认实现，而接口的多实现特性给了更大的灵活性。抽象类主要在需要维护共享状态时使用。

## 7. Object 类：所有类的祖先

每个类都继承了 `Object`，它有几个特别重要的方法需要了解（后面会频繁遇到）：

### 7.1 toString()

```java
public class Student {
    String name;
    int age;

    // 不重写：输出类似 Student@1a2b3c（类名 + 哈希值的十六进制）
    // 重写后：输出有意义的信息
    @Override
    public String toString() {
        return "Student{name='" + name + "', age=" + age + "}";
    }
}

System.out.println(new Student());  // 自动调用 toString()
```

### 7.2 equals() 和 hashCode()

```java
public class Student {
    String name;
    int age;

    // 默认的 equals() 比较引用地址（== 的效果）
    // 重写后按内容比较
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Student s)) return false;  // Java 16+ 模式匹配：判断 + 转型一步完成
        return age == s.age && Objects.equals(name, s.name);
    }

    // 重写 equals 就必须重写 hashCode
    // 规则：equals 返回 true 的两个对象，hashCode 必须相同
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}
```

为什么必须同时重写？因为 `HashMap`、`HashSet` 等集合先用 `hashCode()` 定位桶，再用 `equals()` 判断是否相同。如果只重写 `equals` 不重写 `hashCode`，两个"相等"的对象可能被放进不同的桶，集合行为就错乱了。

### 7.3 其他方法

`getClass()` 返回对象的运行时类型，反射中常用：

```java
Student s = new Student();
s.getClass().getName();          // "Student"
s.getClass() == Student.class;   // true
```

`wait() / notify() / notifyAll()` 用于多线程协调，必须在 `synchronized` 块中调用，会在并发篇展开。

`clone()` 可对对象做浅拷贝，需实现 `Cloneable` 接口，实际开发中较少直接使用，一般用拷贝构造函数替代。

## 8. 小结

| 主题 | 关键要点 |
|------|---------|
| 继承 | `extends` 单继承，`super` 调用父类构造/方法，所有类继承 Object |
| 构造链 | 子类构造必须先调父类构造，不写则自动插入 `super()` |
| 方法重写 | @Override，运行时动态绑定；不能比父类更严格 |
| 多态 | 父类引用指向子类对象，调用方法看实际类型 |
| instanceof | 安全向下转型；Java 16+ 支持模式匹配 |
| 抽象类 | 不能实例化，可以有字段和构造方法，强制子类实现抽象方法 |
| 接口 | 多实现，default 方法，优先于抽象类 |
| Object | toString / equals / hashCode 三件套，重写 equals 必须重写 hashCode |

---

> **下一篇预告**：泛型——类型擦除、通配符与 PECS 原则