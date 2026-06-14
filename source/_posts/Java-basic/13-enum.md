---
title: 'Java基础(13) | 枚举：不只是常量，还能做策略模式和单例'
date: 2026-05-13
tags:
  - Java
  - 枚举
categories:
  - Java基础
---

## 前言

很多人把枚举当成"高级版常量"用完就算了，实际上 Java 的 `enum` 功能远超想象——它可以有字段、方法、实现接口，甚至用来做策略模式和线程安全的单例。这篇文章从基础到进阶，把枚举的所有用法过一遍。

<!-- more -->

## 1. 为什么需要枚举？

Java 5 之前，表示一组固定常量只能用 `static final`：

```java
public class OrderStatus {
    public static final int PENDING = 0;
    public static final int PAID = 1;
    public static final int SHIPPED = 2;
    public static final int CANCELLED = 3;
}

public void process(int status) {
    if (status == OrderStatus.PAID) { ... }
}

// 问题：
// 1. 类型不安全：process(999) 编译通过，运行时出 bug
// 2. 可读性差：日志打出 status=2，看不出是什么意思
// 3. 没有命名空间：PENDING 可能和其他类的常量冲突
```

枚举解决了所有这些问题。

## 2. 枚举基础

### 2.1 定义与使用

```java
public enum OrderStatus {
    PENDING, PAID, SHIPPED, CANCELLED
}

// 使用
OrderStatus status = OrderStatus.PAID;

// 类型安全：只能传入枚举值
public void process(OrderStatus status) {
    // process(999) → 编译报错
}

// 可读性：直接打印名字
System.out.println(status);  // "PAID"
```

### 2.2 常用方法

```java
OrderStatus status = OrderStatus.PAID;

// name()：返回枚举常量名
status.name();             // "PAID"

// ordinal()：返回声明顺序（从 0 开始）
status.ordinal();          // 1

// valueOf()：字符串 → 枚举（大小写敏感）
OrderStatus s = OrderStatus.valueOf("PAID");   // OrderStatus.PAID
// OrderStatus.valueOf("paid");                // 抛 IllegalArgumentException

// values()：返回所有枚举值的数组
OrderStatus[] all = OrderStatus.values();
// [PENDING, PAID, SHIPPED, CANCELLED]

// 比较：直接用 == （枚举值是单例，不需要 equals）
if (status == OrderStatus.PAID) { ... }  // 推荐
if (status.equals(OrderStatus.PAID)) { ... }  // 也行，但没必要
```



### 2.3 枚举的本质

`enum` 不是什么新东西，编译后就是一个**继承 `java.lang.Enum` 的 final 类**。拆开看：

**你写的一行代码**：

```java
public enum OrderStatus { PENDING, PAID, SHIPPED, CANCELLED }
```

**编译器帮你生成的等价代码**：

```java
public final class OrderStatus extends Enum<OrderStatus> {
    // ① 每个枚举值 = 一个 static final 的自身类型对象
    public static final OrderStatus PENDING   = new OrderStatus("PENDING", 0);
    public static final OrderStatus PAID      = new OrderStatus("PAID", 1);
    public static final OrderStatus SHIPPED   = new OrderStatus("SHIPPED", 2);
    public static final OrderStatus CANCELLED = new OrderStatus("CANCELLED", 3);

    // ② 构造方法是 private 的，外部不能 new
    // 两个参数由编译器自动传入：name = 枚举值的名字，ordinal = 声明顺序（从 0 开始）
    private OrderStatus(String name, int ordinal) {
        super(name, ordinal);  // 传给父类 Enum 保存
    }
}
```

**三个关键点**：

| 特征 | 含义 |
|------|------|
| `final class` | 不能被继承 |
| `extends Enum<OrderStatus>` | 继承 Enum 类，获得 `name()`、`ordinal()`、`values()` 等方法 |
| `private` 构造方法 | 外部不能 new，实例数量在编译期就固定了 |

**Enum 父类提供了什么？**

```java
// 这些方法不用你写，从 Enum 继承来的

OrderStatus.PENDING.name();      // "PENDING"（构造时传入的第一个参数）
OrderStatus.PENDING.ordinal();   // 0（构造时传入的第二个参数，声明顺序）
OrderStatus.PAID.ordinal();      // 1
OrderStatus.SHIPPED.ordinal();   // 2

OrderStatus.values();            // [PENDING, PAID, SHIPPED, CANCELLED]（所有实例的数组）
OrderStatus.valueOf("PAID");     // OrderStatus.PAID（从字符串查找对应实例）
```

**枚举变量存的是什么？**

枚举变量和普通对象引用一样，指向那几个 static final 实例中的某一个，表示"当前是哪个状态"：

```java
// status 指向 PENDING 这个对象
OrderStatus status = OrderStatus.PENDING;

// 改变状态：让 status 指向另一个对象
status = OrderStatus.PAID;

// == 比较的是引用，因为每个枚举值全局只有一个实例，所以 == 就够了
status == OrderStatus.PAID;    // true
status == OrderStatus.PENDING; // false
```

**自定义构造方法时发生了什么？**

```java
public enum OrderStatus {
    PENDING("待支付"),    // 调用下面的构造方法
    PAID("已支付");

    private final String label;

    // 你写的构造方法只有一个参数 label
    // 但编译器会自动在前面加上 name 和 ordinal 两个参数
    OrderStatus(String label) {
        // 编译器实际生成的是：OrderStatus(String name, int ordinal, String label)
        // super(name, ordinal) 自动调用
        this.label = label;
    }
}

// PENDING("待支付") 实际执行的是：
// new OrderStatus("PENDING", 0, "待支付")
//                  ↑ name    ↑ ordinal  ↑ 你传的 label
// 前两个参数由编译器自动填入，你只需要写自己的参数
```

一句话总结：**枚举 = final 类 + 继承 Enum + private 构造 + 固定数量的 static final 自身实例**。编译器帮你生成了所有样板代码，你只需要列出值。

所以枚举值就是**预定义的、有限个数的类实例**，不能 new，不能继承。


## 3. 带属性和方法的枚举

枚举不只是光秃秃的名字，可以有字段、构造方法和自定义方法：

```java
public enum OrderStatus {
    PENDING(0, "待支付"),
    PAID(1, "已支付"),
    SHIPPED(2, "已发货"),
    CANCELLED(3, "已取消");

    private final int code;
    private final String description;

    // 构造方法必须是 private（可以省略 private 关键字）
    OrderStatus(int code, String description) {
        this.code = code;
        this.description = description;
    }

    public int getCode() { return code; }
    public String getDescription() { return description; }

    // 根据 code 查找枚举值
    public static OrderStatus fromCode(int code) {
        for (OrderStatus s : values()) {
            if (s.code == code) return s;
        }
        throw new IllegalArgumentException("Unknown code: " + code);
    }
}

// 使用
OrderStatus status = OrderStatus.PAID;
status.getCode();         // 1
status.getDescription();  // "已支付"

OrderStatus s = OrderStatus.fromCode(2);  // SHIPPED
```

### fromCode 的优化版：用 Map 缓存

```java
public enum OrderStatus {
    PENDING(0, "待支付"), PAID(1, "已支付"),
    SHIPPED(2, "已发货"), CANCELLED(3, "已取消");

    private final int code;
    private final String description;

    // 用 static Map 缓存，避免每次遍历
    private static final Map<Integer, OrderStatus> CODE_MAP =
        Arrays.stream(values()).collect(Collectors.toMap(OrderStatus::getCode, s -> s));

    OrderStatus(int code, String description) {
        this.code = code;
        this.description = description;
    }

    public int getCode() { return code; }
    public String getDescription() { return description; }

    public static OrderStatus fromCode(int code) {
        OrderStatus status = CODE_MAP.get(code);
        if (status == null) throw new IllegalArgumentException("Unknown code: " + code);
        return status;
    }
}
```

## 4. 枚举实现接口（策略模式）

### 4.1 先看问题

假设你要根据运算符做计算，最直接的写法是 if-else：

```java
public double calculate(String operator, double a, double b) {
    if (operator.equals("+")) return a + b;
    else if (operator.equals("-")) return a - b;
    else if (operator.equals("*")) return a * b;
    else if (operator.equals("/")) return a / b;
    else throw new IllegalArgumentException("不支持的运算符: " + operator);
}
```

问题：每加一种运算符，就要改这个方法，加一个 else if。方法越来越长，而且容易漏改。

### 4.2 用枚举解决

让每个枚举值自己知道怎么计算，不需要 if-else：

**第一步：定义接口**

```java
public interface Calculable {
    double calculate(double a, double b);
}
```

**第二步：枚举实现接口，每个值给出自己的实现**

```java
public enum Operation implements Calculable {

    // 每个枚举值后面的 { } 就是它自己对 calculate 的实现
    // 语法上类似匿名内部类，每个值相当于 Operation 的一个"子类"

    ADD("+") {
        @Override
        public double calculate(double a, double b) {
            return a + b;
        }
    },

    SUBTRACT("-") {
        @Override
        public double calculate(double a, double b) {
            return a - b;
        }
    },

    MULTIPLY("*") {
        @Override
        public double calculate(double a, double b) {
            return a * b;
        }
    },

    DIVIDE("/") {
        @Override
        public double calculate(double a, double b) {
            if (b == 0) throw new ArithmeticException("除数不能为 0");
            return a / b;
        }
    };

    // 枚举的字段和构造方法
    private final String symbol;

    Operation(String symbol) {      // ADD("+") 就是调用这个构造方法
        this.symbol = symbol;
    }

    public String getSymbol() {
        return symbol;
    }
}
```

每个枚举值拆开看就是三部分：

```java
ADD          // 枚举值的名字
("+")        // 构造方法的参数，symbol = "+"
{            // 这个枚举值自己的方法实现
    @Override
    public double calculate(double a, double b) {
        return a + b;
    }
}
```

**第三步：使用**

```java
// 直接调用，每个枚举值有自己的行为
Operation.ADD.calculate(10, 3);         // 13.0
Operation.SUBTRACT.calculate(10, 3);    // 7.0
Operation.MULTIPLY.calculate(10, 3);    // 30.0
Operation.DIVIDE.calculate(10, 3);      // 3.333...

// 遍历所有运算符
for (Operation op : Operation.values()) {
    System.out.printf("10 %s 3 = %.1f%n", op.getSymbol(), op.calculate(10, 3));
}
// 10 + 3 = 13.0
// 10 - 3 = 7.0
// 10 * 3 = 30.0
// 10 / 3 = 3.3

// 从字符串获取枚举值
Operation op = Operation.valueOf("ADD");
op.calculate(10, 3);  // 13.0
```

### 4.3 对比 if-else

```java
// 新增一个取模运算：

// if-else 方式：找到那个方法，加一个 else if，容易漏改
else if (operator.equals("%")) return a % b;

// 枚举方式：加一个枚举值就行，其他代码一行不动
MODULO("%") {
    @Override
    public double calculate(double a, double b) { return a % b; }
},
```

| | if-else | 枚举策略 |
|---|---|---|
| 新增运算符 | 改已有代码，加 else if | 加一个枚举值，不动已有代码 |
| 漏改风险 | 有（可能忘了某处 if-else） | 无（编译器强制你实现接口方法） |
| 运算符和逻辑的关系 | 分离的（运算符是字符串，逻辑在别处） | 绑定的（每个枚举值自带逻辑） |

## 5. 枚举实现单例

### 5.1 什么是单例？

单例就是**整个程序中只有一个实例**。比如数据库连接池、配置管理器，全局只需要一个，创建多个会浪费资源甚至出 bug。

### 5.2 为什么用枚举实现？

枚举的每个值本质上就是一个 `static final` 的对象。写一个值就只有一个实例——天然单例：

```java
public enum DatabaseConnection {
    INSTANCE;  // 只写一个值 = 只有一个实例
}
```

编译器看到这行，实际生成的是：

```java
// 编译器帮你生成的（伪代码）
public final class DatabaseConnection {
    public static final DatabaseConnection INSTANCE = new DatabaseConnection();

    private DatabaseConnection() { }  // 构造方法是 private 的，外部不能 new
}
```

验证确实是同一个对象：

```java
DatabaseConnection a = DatabaseConnection.INSTANCE;
DatabaseConnection b = DatabaseConnection.INSTANCE;
System.out.println(a == b);  // true，始终是同一个对象

// new DatabaseConnection();  // 编译报错！枚举不能 new
```

### 5.3 完整示例

```java
public enum DatabaseConnection {
    INSTANCE;  // 唯一实例

    private Connection connection;

    // 枚举的构造方法（JVM 加载类时执行一次，之后不再执行）
    DatabaseConnection() {
        this.connection = createConnection();
    }

    public Connection getConnection() {
        return connection;
    }

    private Connection createConnection() {
        // 实际的连接创建逻辑
        return DriverManager.getConnection("jdbc:mysql://localhost:3306/db");
    }
}
```

**调用时发生了什么？**

```java
// 第一次调用
Connection conn = DatabaseConnection.INSTANCE.getConnection();
//
// 1. DatabaseConnection.INSTANCE
//    → JVM 第一次访问这个枚举类，触发类加载
//    → 执行构造方法：this.connection = createConnection()
//    → INSTANCE 对象创建完毕
//
// 2. .getConnection()
//    → 返回刚才创建好的 connection

// 第二次调用
Connection conn2 = DatabaseConnection.INSTANCE.getConnection();
//
// 1. DatabaseConnection.INSTANCE
//    → 类已经加载过了，不再初始化，直接返回同一个 INSTANCE
//
// 2. .getConnection()
//    → 返回同一个 connection（和上面是同一个对象）
```

### 5.4 为什么枚举单例最安全？

其他单例实现方式都有漏洞：

```java
// 漏洞 1：反射攻击——强行调用 private 构造方法，创建第二个实例
Constructor<?> c = Singleton.class.getDeclaredConstructor();
c.setAccessible(true);
Singleton s2 = (Singleton) c.newInstance();  // 单例被破坏！

// 漏洞 2：反序列化——读取字节流时会创建新对象
Singleton s3 = (Singleton) objectInputStream.readObject();  // 又一个新的！

// 枚举对这两种攻击都免疫：
// 反射：JVM 层面禁止对枚举调用 newInstance()，直接抛 IllegalArgumentException
// 反序列化：JVM 对枚举做了特殊处理，保证返回已存在的实例
```

各种单例方案对比：

| 方案 | 线程安全 | 防反射 | 防反序列化 | 代码复杂度 |
|------|---------|--------|-----------|----------|
| 懒汉式 + synchronized | ✅ | ❌ | ❌ | 中 |
| 双重检查锁 | ✅ | ❌ | ❌ | 高 |
| 静态内部类 | ✅ | ❌ | ❌ | 中 |
| **枚举** | **✅** | **✅** | **✅** | **最简单** |

这也是 Effective Java 推荐枚举单例的原因——最安全、最简洁、没有任何漏洞。

## 6. EnumSet 和 EnumMap

### 6.1 为什么需要专用集合？

前面学过 `HashSet` 和 `HashMap`，枚举也能放进去：

```java
Set<OrderStatus> set = new HashSet<>();
set.add(OrderStatus.PENDING);

Map<OrderStatus, String> map = new HashMap<>();
map.put(OrderStatus.PENDING, "待支付");
```

能用，但不够好。枚举值的数量是固定的、有限的（比如订单状态就那么几个），`HashMap` 要算哈希值、处理冲突，是杀鸡用牛刀。Java 专门为枚举设计了两个集合，底层更简单，性能更好。

### 6.2 EnumSet：枚举专用 Set

底层用**位向量**实现——每个枚举值对应一个 bit（0 或 1），存在就是 1，不存在就是 0。比 `HashSet` 快得多，内存也更省：

```java
// 假设有这个枚举
public enum OrderStatus {
    PENDING, PAID, SHIPPED, DELIVERED, CANCELLED
}
```

```java
// 创建方式
EnumSet<OrderStatus> active = EnumSet.of(OrderStatus.PENDING, OrderStatus.PAID);
// 只包含 PENDING 和 PAID

EnumSet<OrderStatus> all = EnumSet.allOf(OrderStatus.class);
// 包含所有值：PENDING, PAID, SHIPPED, DELIVERED, CANCELLED

EnumSet<OrderStatus> none = EnumSet.noneOf(OrderStatus.class);
// 空的，之后可以 add

EnumSet<OrderStatus> range = EnumSet.range(OrderStatus.PENDING, OrderStatus.SHIPPED);
// 从 PENDING 到 SHIPPED（按声明顺序）：PENDING, PAID, SHIPPED
```

```java
// 使用方式和普通 Set 完全一样
active.contains(OrderStatus.PAID);      // true
active.contains(OrderStatus.SHIPPED);   // false
active.add(OrderStatus.SHIPPED);        // 加入
active.remove(OrderStatus.PENDING);     // 移除
```

### 6.3 EnumMap：枚举专用 Map

底层用**数组**实现——枚举有几个值，数组就多长，用枚举的序号当下标直接访问，不需要算哈希：

```java
// 创建时必须传入枚举的 Class
EnumMap<OrderStatus, String> labels = new EnumMap<>(OrderStatus.class);

labels.put(OrderStatus.PENDING, "待支付");
labels.put(OrderStatus.PAID, "已支付");
labels.put(OrderStatus.SHIPPED, "已发货");

// 使用方式和普通 Map 完全一样
labels.get(OrderStatus.PAID);           // "已支付"
labels.containsKey(OrderStatus.SHIPPED); // true
```

### 6.4 什么时候用？

| 场景 | 用什么 |
|------|--------|
| key 是枚举类型的 Map | `EnumMap` 替代 `HashMap` |
| 存一组枚举值的集合 | `EnumSet` 替代 `HashSet` |
| key 不是枚举 | 还是用 `HashMap` / `HashSet` |

不需要刻意记，就是一句话：**key 或元素是枚举时，用 EnumMap / EnumSet 性能更好**。

## 7. 实际开发中的枚举模式

### 7.1 HTTP 状态码

```java
public enum HttpStatus {
    OK(200, "OK"),
    BAD_REQUEST(400, "Bad Request"),
    UNAUTHORIZED(401, "Unauthorized"),
    FORBIDDEN(403, "Forbidden"),
    NOT_FOUND(404, "Not Found"),
    INTERNAL_SERVER_ERROR(500, "Internal Server Error");

    private final int code;
    private final String reason;

    HttpStatus(int code, String reason) { this.code = code; this.reason = reason; }
    public int getCode() { return code; }
    public String getReason() { return reason; }
    public boolean isError() { return code >= 400; }
}
```

### 7.2 配置项

```java
public enum Environment {
    DEV("http://localhost:8080", false),
    STAGING("https://staging.example.com", false),
    PROD("https://api.example.com", true);

    private final String baseUrl;
    private final boolean httpsOnly;

    Environment(String baseUrl, boolean httpsOnly) {
        this.baseUrl = baseUrl;
        this.httpsOnly = httpsOnly;
    }

    public String getBaseUrl() { return baseUrl; }
    public boolean isHttpsOnly() { return httpsOnly; }
}
```

### 7.3 与 JSON 互转（Jackson）

```java
public enum OrderStatus {
    @JsonProperty("pending")
    PENDING(0, "待支付"),

    @JsonProperty("paid")
    PAID(1, "已支付");

    // ... 省略字段和构造方法

    // 或者用 @JsonValue 控制序列化输出
    @JsonValue
    public int getCode() { return code; }

    // 用 @JsonCreator 控制反序列化输入
    @JsonCreator
    public static OrderStatus fromCode(int code) { return CODE_MAP.get(code); }
}

// 序列化：{"status": 1}
// 反序列化：OrderStatus.PAID
```

## 8. 小结

| 主题 | 关键要点 |
|------|---------|
| 本质 | 继承 Enum 的 final 类，每个枚举值是一个 static final 实例 |
| 比较 | 用 `==` 直接比较，不需要 equals |
| 带属性 | 可以有字段、构造方法、自定义方法；用 Map 缓存 fromCode 查找 |
| 实现接口 | 每个枚举值可以有不同实现——策略模式 |
| 单例 | Effective Java 推荐方式，天然线程安全、防反射、防反序列化 |
| EnumSet/EnumMap | 枚举专用集合，基于位向量/数组，比 HashSet/HashMap 更快 |
| JSON 互转 | Jackson 的 @JsonValue / @JsonCreator |

---

> **下一篇预告**：日期时间 API——java.time 全梳理