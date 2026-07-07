---
title: 'Java基础(12) | 注解与反射：框架背后的魔法'
date: 2026-05-12
abbrlink: 12
tags:
  - Java
  - 注解
  - 反射
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

如果你用过 Spring，一定写过 `@Autowired`、`@RequestMapping`、`@Transactional`——这些注解看起来像"魔法标签"，贴上去就生效了。但它们到底是怎么工作的？答案是：**注解定义"标记"，反射读取"标记"，然后执行对应逻辑。** 这篇文章把注解和反射这对搭档一次讲透。

<!-- more -->

## 1. 注解（Annotation）

### 1.1 注解是什么？

注解本质上就是一种**特殊的接口**，用来给代码（类、方法、字段、参数等）附加元数据。它本身不包含业务逻辑，只是一个标记，真正的逻辑由"读取注解的代码"（通常是框架，通过反射）来执行。

```java
// 你写的
@Override
public String toString() { ... }

// @Override 本身什么都不做
// 是编译器读取到它后，帮你检查父类是否有这个方法
```

### 1.2 Java 内置注解

```java
// 编译期注解（给编译器看的）
@Override          // 检查是否正确重写了父类方法
@Deprecated        // 标记已过时，IDE 会划删除线提醒
@SuppressWarnings("unchecked")  // 抑制编译器警告

// 函数式接口标记
@FunctionalInterface  // 检查接口是否只有一个抽象方法

// Java 8+
@Deprecated(since = "9", forRemoval = true)  // 标记将在未来版本移除
```

### 1.3 元注解（给注解加的注解）

Java 提供了 4 个核心元注解，用来定义"注解的行为"：

```java
// @Target：注解可以贴在哪里
@Target(ElementType.METHOD)           // 只能贴在方法上
@Target({ElementType.TYPE, ElementType.METHOD})  // 类或方法
// 常用值：TYPE(类/接口), METHOD, FIELD, PARAMETER, CONSTRUCTOR, LOCAL_VARIABLE

// @Retention：注解保留到什么阶段
@Retention(RetentionPolicy.SOURCE)    // 只在源码中，编译后丢弃（如 @Override）
@Retention(RetentionPolicy.CLASS)     // 保留到 class 文件，但运行时不可读（默认）
@Retention(RetentionPolicy.RUNTIME)   // 保留到运行时，可以通过反射读取（框架都用这个）

// @Documented：是否出现在 Javadoc 中
@Documented

// @Inherited：子类是否继承父类的注解
@Inherited
```

### 1.4 自定义注解

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface LogExecution {
    String value() default "";       // 注解属性，有默认值
    boolean logArgs() default true;  // 是否记录参数
}

// 使用
public class UserService {
    @LogExecution(value = "查询用户", logArgs = false)
    public User getUser(String id) {
        return db.findById(id);
    }

    @LogExecution("删除用户")  // 只有一个属性名为 value 时，可以省略 "value ="
    public void deleteUser(String id) {
        db.delete(id);
    }
}
```

注解属性支持的类型：基本类型、String、Class、枚举、其他注解、以及以上类型的数组。不支持自定义对象。

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface ApiConfig {
    String url();
    int timeout() default 3000;
    String[] headers() default {};          // 数组类型
    RequestMethod method() default RequestMethod.GET;  // 枚举类型
}

@ApiConfig(
    url = "/api/users",
    timeout = 5000,
    headers = {"Content-Type: application/json", "Accept: */*"},
    method = RequestMethod.POST
)
public class UserApi { ... }
```

**为什么注解的属性要用方法的写法？** 因为 `@interface` 本质上就是一个接口，编译后会变成继承 `Annotation` 的普通接口：

```java
// 你写的
public @interface LogExecution {
    String value() default "";
}

// 编译器实际生成的
public interface LogExecution extends java.lang.annotation.Annotation {
    String value();  // 接口只能有方法，不能有实例字段，所以属性只能用方法表达
}
```

`default ""` 就是方法的默认返回值，使用注解时不传就用默认值：

```java
@LogExecution("查询用户")     // value() 返回 "查询用户"
@LogExecution                 // value() 返回 ""（默认值）
```

不用深究底层实现，记住用法就行：**注解的属性 = 接口的方法 = 用的时候像参数一样传值**。

## 2. 反射（Reflection）

### 2.1 反射是什么？

反射允许你在**运行时**动态地获取类的信息、创建对象、调用方法、读取注解——不需要在编译期知道具体类型。

**获取 Class 对象**（反射的起点，三种方式）：

```java
// 方式 1：Class.forName（运行时才知道类名，最常用于框架）
Class<?> clazz = Class.forName("com.example.User");
// Class<?> 表示"某个类的 Class 对象，但编译期不确定是哪个类"
// <?> 是通配符，告诉编译器"类型不确定是故意的"

// 方式 2：类名.class（编译期就确定了类型）
Class<User> clazz = User.class;

// 方式 3：对象.getClass()（从已有对象获取）
User user = new User("Alice");
Class<?> clazz = user.getClass();
```

**用反射创建对象和调用方法**（逐步解释）：

```java
// 正常写法：编译期就确定了类型
User user = new User("Alice");
String name = user.getName();

// 反射写法：运行时动态操作
// 第一步：获取 Class 对象（"我要操作 User 这个类"）
Class<?> clazz = Class.forName("com.example.User");

// 第二步：获取构造方法（"找到参数是 String 的构造方法"）
Constructor<?> constructor = clazz.getDeclaredConstructor(String.class);

// 第三步：创建对象（"用这个构造方法 new 一个对象，传入 Alice"）
Object user = constructor.newInstance("Alice");
// 等价于 new User("Alice")，但编译期不需要知道 User 类的存在

// 第四步：获取方法（"找到叫 getName 的方法"）
Method method = clazz.getMethod("getName");

// 第五步：调用方法（"在 user 对象上调用 getName()"）
String name = (String) method.invoke(user);
// 等价于 user.getName()，但返回的是 Object，需要强转
```

**用反射读取注解**（用前面定义的 `@LogExecution` 为例）：

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)  // 必须是 RUNTIME，否则反射读不到
public @interface LogExecution {
    String value() default "";
    boolean logArgs() default true;
}

public class UserService {
    @LogExecution(value = "查询用户", logArgs = false)
    public User getUser(String id) {
        return db.findById(id);
    }
}
```

```java
// 第一步：获取 Class 对象
Class<?> clazz = UserService.class;

// 第二步：获取方法
Method method = clazz.getMethod("getUser", String.class);

// 第三步：检查方法上有没有 @LogExecution 注解
if (method.isAnnotationPresent(LogExecution.class)) {

    // 第四步：获取注解对象
    LogExecution anno = method.getAnnotation(LogExecution.class);

    // 第五步：读取注解里的数据（调用注解的"方法"，返回你传入的值）
    String value = anno.value();       // "查询用户"
    boolean logArgs = anno.logArgs();  // false

    System.out.println("操作: " + value);
    System.out.println("记录参数: " + logArgs);
}
```

现在回头看 1.5 说的"注解本身不做任何事"就很清楚了——`@LogExecution` 只是一个标记，是上面这段反射代码去读取它、拿到里面的数据、然后执行日志逻辑。**没有反射去读，注解就是摆设。**

这也是为什么 `@Retention` 必须设为 `RUNTIME`——设为 `SOURCE`（如 `@Override`）编译后就丢了，反射根本看不到。


### 2.2 获取类的信息

**为什么要获取类的信息？**

想象你是 Spring 框架，用户写了一个类交给你管理，但你在编译期完全不知道这个类长什么样。你需要在运行时搞清楚三件事：

1. **这个类叫什么？** —— 用来打日志、报错信息
2. **它有哪些字段？** —— 用来注入依赖、序列化
3. **它有哪些方法？** —— 用来调用、生成代理

这些信息全部通过 Class 对象获取。

**搞清楚这个类是谁**：

```java
Class<?> clazz = Class.forName("com.example.User");

clazz.getName();          // "com.example.User"（全名，带包名）
clazz.getSimpleName();    // "User"（只有类名）
clazz.getSuperclass();    // Object.class（父类是谁）
clazz.getInterfaces();    // 实现了哪些接口
```

**搞清楚它有什么字段**：

```java
// 拿到所有字段
Field[] fields = clazz.getDeclaredFields();

for (Field f : fields) {
    System.out.println(f.getName() + " → " + f.getType().getSimpleName());
}
// 输出：
// name → String
// age → int
```

**搞清楚它有什么方法**：

```java
// 拿到所有方法
Method[] methods = clazz.getDeclaredMethods();

for (Method m : methods) {
    System.out.println(m.getName());
}
// 输出：
// getName
// setName
// getAge
// setAge
```

**搞清楚它有什么构造方法**：

```java
Constructor<?>[] constructors = clazz.getDeclaredConstructors();

for (Constructor<?> c : constructors) {
    System.out.println(c);
}
// 输出：
// public com.example.User()
// public com.example.User(String, int)
```

拿到这些信息之后，就可以进行下一步——动态创建对象、读写字段、调用方法（2.3~2.5 节）。

### 2.3 动态创建对象

上一节搞清楚了类有哪些构造方法，这一节用它来创建对象。

**先定义一个示例类**（后续 2.5、2.6 也用这个）：

```java
public class User {
    private String name;
    private int age;

    public User() { }                              // 无参构造（public）
    public User(String name, int age) {            // 有参构造（public）
        this.name = name;
        this.age = age;
    }
    private User(String name) {                    // 单参构造（private）
        this.name = name;
        this.age = 0;
    }
}
```

这个类有 3 个构造方法，参数不同。反射通过**参数类型列表**来区分同名的构造方法（构造方法都叫类名，只能靠参数区分）。

**获取构造方法**：

```java
Class<?> clazz = User.class;

// 获取 public 的无参构造
Constructor<?> c1 = clazz.getConstructor();

// 获取 public 的有参构造（通过参数类型区分）
Constructor<?> c2 = clazz.getConstructor(String.class, int.class);

// 获取 private 构造方法（getConstructor 只能拿 public 的，拿不到 private）
// 需要用 getDeclaredConstructor
Constructor<?> c3 = clazz.getDeclaredConstructor(String.class);
```

两个方法的区别：

| 方法 | 能拿到什么 |
|------|----------|
| `getConstructor(参数类型...)` | 只能拿 public 构造方法 |
| `getDeclaredConstructor(参数类型...)` | 能拿所有构造方法（包括 private） |

**使用newInstance方法创建对象**：

```java
// public 构造方法：直接 newInstance
Constructor<?> c1 = clazz.getConstructor();
Object user1 = c1.newInstance();                     // 等价于 new User()

Constructor<?> c2 = clazz.getConstructor(String.class, int.class);
Object user2 = c2.newInstance("Alice", 25);          // 等价于 new User("Alice", 25)

// private 构造方法：必须先 setAccessible(true) 打开权限
Constructor<?> c3 = clazz.getDeclaredConstructor(String.class);
c3.setAccessible(true);                              // 不写这行会抛 IllegalAccessException
Object user3 = c3.newInstance("Bob");                // 等价于 new User("Bob")
```

`setAccessible(true)` 的意思是"我知道这是 private 的，但我就是要用"。这也是反射的争议点——它能突破 private 的封装。框架经常这么干（Spring 注入 private 字段），但业务代码里不建议。

### 2.4 读写字段

创建完对象，下一步就是读写它的字段。User 的 `name` 和 `age` 都是 private 的，正常代码访问不了，但反射可以：

```java
// 接上一节，用无参构造创建一个空的 User 对象
Class<?> clazz = User.class;
Object user = clazz.getConstructor().newInstance();  // new User()
```

**获取字段**：

```java
// public 字段：用 getField
Field f1 = clazz.getField("publicField");

// private 字段：用 getDeclaredField
Field nameField = clazz.getDeclaredField("name");
Field ageField = clazz.getDeclaredField("age");
```

| 方法 | 能拿到什么 |
|------|----------|
| `getField("字段名")` | 只能拿 public 字段（包括从父类继承的） |
| `getDeclaredField("字段名")` | 能拿所有字段（包括 private，但不包括继承的） |

**写入值**：

```java
// private 字段必须先打开权限
nameField.setAccessible(true);
ageField.setAccessible(true);

// set(对象, 值)：等价于 user.name = "Alice"（但 private 正常写不了）
nameField.set(user, "Alice");
ageField.set(user, 25);
```

**读取值**：

```java
// get(对象)：等价于 user.name
// 注意：name 是 private 的，只有通过反射 + setAccessible(true) 才能读，直接写 user.name 编译报错
String name = (String) nameField.get(user);   // "Alice"
int age = (int) ageField.get(user);           // 25
```

**获取字段的类型信息**：

```java
nameField.getType();              // class java.lang.String
nameField.getType().getSimpleName();  // "String"
ageField.getType();               // int
```

这就是 Spring 依赖注入的底层原理——你在字段上标了 `@Autowired`，Spring 通过反射找到这个字段，`setAccessible(true)` 打开权限，然后 `field.set(bean, 依赖对象)` 把依赖塞进去，哪怕字段是 private 的。


### 2.5 调用方法

有了对象，就可以通过反射调用它的方法。和字段一样，反射能调用 private 方法。

**获取方法**：

方法通过**方法名 + 参数类型列表**来区分（因为方法可以重载，光靠名字不够）：

```java
Class<?> clazz = User.class;
Object user = clazz.getConstructor(String.class, int.class).newInstance("Alice", 25);

// public 方法：用 getMethod
Method getName = clazz.getMethod("getName");               // 无参方法
Method setName = clazz.getMethod("setName", String.class); // 有参方法，传参数类型区分重载

// private 方法：用 getDeclaredMethod
Method secret = clazz.getDeclaredMethod("secretMethod");
```

| 方法 | 能拿到什么 |
|------|----------|
| `getMethod("方法名", 参数类型...)` | 只能拿 public 方法（包括从父类继承的） |
| `getDeclaredMethod("方法名", 参数类型...)` | 能拿所有方法（包括 private，但不包括继承的） |

**调用无参方法**：

```java
Method getName = clazz.getMethod("getName");

// invoke(对象)：在 user 对象上调用 getName()
// 等价于 user.getName()，返回值是 Object，需要强转
String name = (String) getName.invoke(user);   // "Alice"
```

**调用有参方法**：

```java
Method setName = clazz.getMethod("setName", String.class);

// invoke(对象, 参数...)：在 user 对象上调用 setName("Bob")
// 等价于 user.setName("Bob")
setName.invoke(user, "Bob");
```

**调用 private 方法**：

```java
Method secret = clazz.getDeclaredMethod("secretMethod");
secret.setAccessible(true);   // 和字段一样，private 方法必须先打开权限
secret.invoke(user);           // 等价于 user.secretMethod()
```

**调用 static 方法**：

```java
// 假设 User 类有一个 static 方法：public static User create(String name)
Method create = clazz.getMethod("create", String.class);

// static 方法不属于某个对象，所以第一个参数传 null
Object newUser = create.invoke(null, "Charlie");
// 等价于 User.create("Charlie")
```

**invoke 的两个参数总结**：

| 调用类型 | 第一个参数 | 后续参数 |
|---------|----------|---------|
| 实例方法 | 调用方法的对象 | 方法的参数 |
| static 方法 | `null`（不需要对象） | 方法的参数 |
| 无参方法 | 对象 | 不传 |

### 2.6 getXxx vs getDeclaredXxx

这个命名规律贯穿所有反射 API：

| 方法 | 访问范围 | 包括继承的？ |
|------|---------|------------|
| `getFields()` | 仅 public | 是 |
| `getDeclaredFields()` | 所有（包括 private） | 否 |
| `getMethods()` | 仅 public | 是 |
| `getDeclaredMethods()` | 所有（包括 private） | 否 |

**"包括继承的"是什么意思？**

```java
public class Animal {
    public String species;        // public 字段
    private int lifespan;         // private 字段
    public void eat() { }        // public 方法
}

public class Dog extends Animal {
    public String breed;          // Dog 自己的 public 字段
    private String nickname;      // Dog 自己的 private 字段
    public void bark() { }       // Dog 自己的 public 方法
}
```

```java
Class<?> clazz = Dog.class;

// getFields()：所有 public，包括从父类继承的
clazz.getFields();
// → [breed, species]
//    Dog 自己的 + 从 Animal 继承的 public 字段
//    看不到 private 的 nickname 和 lifespan

// getDeclaredFields()：Dog 自己声明的所有字段，不管 public 还是 private
clazz.getDeclaredFields();
// → [breed, nickname]
//    只有 Dog 自己的，看不到父类 Animal 的任何字段
//    但 private 的 nickname 也能拿到
```

简单记忆：
- **get** = 只看 public，但**往上找**（包括父类、父类的父类...）
- **getDeclared** = 什么都能看，但**只看自己**（不往上找）

想访问 private 成员，用 `getDeclaredXxx` + `setAccessible(true)`。

## 3. 反射 + 注解：实战组合

### 3.1 手写一个简单的日志切面

之前定义的 `@LogExecution` 注解，现在用反射让它"生效"：

```java
public class LogProcessor {

    public static void processLogs(Object target) throws Exception {
        Class<?> clazz = target.getClass();

        for (Method method : clazz.getDeclaredMethods()) {
            // 检查方法上是否有 @LogExecution 注解
            if (method.isAnnotationPresent(LogExecution.class)) {
                LogExecution log = method.getAnnotation(LogExecution.class);
                System.out.println("[LOG] 发现注解方法：" + method.getName());
                System.out.println("[LOG] 描述：" + log.value());
                System.out.println("[LOG] 记录参数：" + log.logArgs());
            }
        }
    }
}

// 使用
LogProcessor.processLogs(new UserService());
// [LOG] 发现注解方法：getUser
// [LOG] 描述：查询用户
// [LOG] 记录参数：false
// [LOG] 发现注解方法：deleteUser
// [LOG] 描述：删除用户
// [LOG] 记录参数：true
```

### 3.2 手写一个简化版依赖注入

**什么是依赖注入？**

假设 `UserController` 需要用到 `UserService`，传统写法是自己 `new`：

```java
public class UserController {
    // 自己创建依赖，写死了，想换实现就要改代码
    private UserService userService = new UserService();
}
```

依赖注入的思路是：**你别自己 new，告诉框架你需要什么，框架帮你创建并塞进来**：

```java
public class UserController {
    // 只声明"我需要一个 UserService"，不自己 new
    @Autowired
    private UserService userService;
    // Spring 在运行时通过反射找到这个字段，帮你创建 UserService 并赋值进去
}
```

`@Autowired` 就是一个标记，告诉 Spring "这个字段需要你帮我注入"。Spring 的底层实现就是前面学的反射：

```
Spring 启动时扫描所有类
  → 发现 UserController 有一个字段标了 @Autowired
  → 通过反射读取注解：field.isAnnotationPresent(Autowired.class)
  → 通过反射打开权限：field.setAccessible(true)
  → 通过反射注入对象：field.set(controller, new UserService())
```

下面用前面学的注解 + 反射知识，手写一个简化版：

```java
// 定义注解
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface MyInject { }

// 服务类
public class UserRepository {
    public String find(String id) { return "User:" + id; }
}

public class UserService {
    @MyInject
    private UserRepository repo;  // 期望被自动注入

    public String getUser(String id) { return repo.find(id); }
}

// 简易容器：扫描 @MyInject 字段并注入实例
public class SimpleContainer {

    public static <T> T createBean(Class<T> clazz) throws Exception {
        T instance = clazz.getDeclaredConstructor().newInstance();

        for (Field field : clazz.getDeclaredFields()) {
            if (field.isAnnotationPresent(MyInject.class)) {
                // 根据字段类型创建依赖对象
                Object dependency = field.getType().getDeclaredConstructor().newInstance();
                field.setAccessible(true);
                field.set(instance, dependency);
                System.out.println("注入 " + field.getType().getSimpleName()
                    + " → " + clazz.getSimpleName() + "." + field.getName());
            }
        }
        return instance;
    }
}

// 使用
UserService service = SimpleContainer.createBean(UserService.class);
System.out.println(service.getUser("001"));
// 注入 UserRepository → UserService.repo
// User:001
```

这就是 Spring IoC 容器的核心原理——当然 Spring 的实际实现复杂得多（Bean 生命周期、作用域、循环依赖处理等），但本质就是**反射 + 注解**。

### 3.3 手写一个简化版 JSON 序列化

```java
// 注解：控制 JSON 字段名
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface JsonField {
    String value() default "";  // 自定义字段名，空则用原始字段名
}

public class User {
    @JsonField("user_name")
    private String name;

    @JsonField
    private int age;

    private String password;  // 没有注解，不序列化

    public User(String name, int age, String password) {
        this.name = name;
        this.age = age;
        this.password = password;
    }
}

// 序列化器
public class SimpleJsonSerializer {

    public static String toJson(Object obj) throws Exception {
        Class<?> clazz = obj.getClass();
        StringBuilder sb = new StringBuilder("{");
        boolean first = true;

        for (Field field : clazz.getDeclaredFields()) {
            if (!field.isAnnotationPresent(JsonField.class)) continue;

            field.setAccessible(true);
            JsonField annotation = field.getAnnotation(JsonField.class);

            // 确定 JSON 字段名
            String key = annotation.value().isEmpty() ? field.getName() : annotation.value();
            Object value = field.get(obj);

            if (!first) sb.append(",");
            sb.append("\"").append(key).append("\":");
            if (value instanceof String) {
                sb.append("\"").append(value).append("\"");
            } else {
                sb.append(value);
            }
            first = false;
        }
        sb.append("}");
        return sb.toString();
    }
}

// 使用
User user = new User("Alice", 25, "secret123");
System.out.println(SimpleJsonSerializer.toJson(user));
// {"user_name":"Alice","age":25}
// password 没有 @JsonField，被跳过了
```

这就是 Jackson/Gson 等 JSON 库的核心原理。

## 4. 反射的性能与注意事项

### 4.1 性能开销

```java
// 直接调用 vs 反射调用，性能差距大约 10-50 倍
// 原因：反射需要绕过编译期优化，进行安全检查、参数包装等

// 优化方式 1：缓存 Method / Field 对象，避免重复查找
private static final Method GET_NAME;
static {
    try {
        GET_NAME = User.class.getMethod("getName");
    } catch (NoSuchMethodException e) {
        throw new RuntimeException(e);
    }
}

// 优化方式 2：setAccessible(true) 跳过访问检查，略微提升性能
method.setAccessible(true);

// 优化方式 3：Java 7+ 的 MethodHandle（性能接近直接调用）
MethodHandles.Lookup lookup = MethodHandles.lookup();
MethodHandle handle = lookup.findVirtual(User.class, "getName",
    MethodType.methodType(String.class));
String name = (String) handle.invoke(user);
```

### 4.2 反射的代价

| 问题 | 说明 |
|------|------|
| 性能 | 比直接调用慢 10-50 倍，热点路径慎用 |
| 类型安全 | 绕过了编译期检查，错误推迟到运行时 |
| 封装破坏 | `setAccessible(true)` 可以访问 private 成员 |
| 可维护性 | 字段/方法名是字符串，重构时 IDE 不会自动更新 |

### 4.3 什么时候该用反射？

```
你在写框架或通用工具，需要处理未知类型？
├── 是 → 用反射（Spring、Jackson、MyBatis 都是这么干的）
└── 否 → 不要用反射
    你在做代码生成、动态代理、注解处理？
    ├── 是 → 用反射
    └── 否 → 几乎不需要反射，用正常的面向对象就好
```

日常业务代码中**极少**需要直接写反射，但理解它是读懂框架源码的前提。

### 4.4 反射 API 速查表

**获取 Class 对象**：

| 方式 | 写法 | 适用场景 |
|------|------|---------|
| 类名.class | `Class<User> clazz = User.class;` | 编译期知道类名 |
| Class.forName | `Class<?> clazz = Class.forName("com.example.User");` | 运行时动态加载（框架常用） |
| 对象.getClass | `Class<?> clazz = user.getClass();` | 已有对象，想知道它的类型 |

**获取类信息**：

| 方法 | 作用 | 示例返回值 |
|------|------|----------|
| `getName()` | 全限定名 | `"com.example.User"` |
| `getSimpleName()` | 类名 | `"User"` |
| `getSuperclass()` | 父类 | `Object.class` |
| `getInterfaces()` | 实现的接口 | `[Serializable.class]` |

**操作构造方法**：

| 方法 | 作用 |
|------|------|
| `clazz.getConstructor(参数类型...)` | 获取 public 构造方法 |
| `clazz.getDeclaredConstructor(参数类型...)` | 获取任意构造方法（包括 private） |
| `constructor.newInstance(参数...)` | 创建对象 |
| `constructor.setAccessible(true)` | 打开 private 权限 |

```java
Constructor<?> c = clazz.getDeclaredConstructor(String.class, int.class);
c.setAccessible(true);                    // private 才需要
Object user = c.newInstance("Alice", 25); // 等价于 new User("Alice", 25)
```

**操作字段**：

| 方法 | 作用 |
|------|------|
| `clazz.getField("字段名")` | 获取 public 字段（含继承） |
| `clazz.getDeclaredField("字段名")` | 获取任意字段（含 private，不含继承） |
| `field.get(对象)` | 读取值 |
| `field.set(对象, 值)` | 写入值 |
| `field.getType()` | 获取字段类型 |
| `field.setAccessible(true)` | 打开 private 权限 |

```java
Field f = clazz.getDeclaredField("name");
f.setAccessible(true);
f.set(user, "Alice");                     // 等价于 user.name = "Alice"
String name = (String) f.get(user);       // 等价于 user.name
```

**操作方法**：

| 方法 | 作用 |
|------|------|
| `clazz.getMethod("方法名", 参数类型...)` | 获取 public 方法（含继承） |
| `clazz.getDeclaredMethod("方法名", 参数类型...)` | 获取任意方法（含 private，不含继承） |
| `method.invoke(对象, 参数...)` | 调用实例方法 |
| `method.invoke(null, 参数...)` | 调用 static 方法 |
| `method.getReturnType()` | 获取返回值类型 |
| `method.setAccessible(true)` | 打开 private 权限 |

```java
Method m = clazz.getMethod("setName", String.class);
m.invoke(user, "Bob");                    // 等价于 user.setName("Bob")
```

**操作注解**：

| 方法 | 作用 |
|------|------|
| `clazz.getAnnotation(注解类.class)` | 获取类上的注解 |
| `method.getAnnotation(注解类.class)` | 获取方法上的注解 |
| `field.getAnnotation(注解类.class)` | 获取字段上的注解 |
| `xxx.isAnnotationPresent(注解类.class)` | 判断有没有某个注解 |

```java
if (method.isAnnotationPresent(LogExecution.class)) {
    LogExecution anno = method.getAnnotation(LogExecution.class);
    String value = anno.value();           // 读取注解属性
}
```

**getXxx vs getDeclaredXxx 统一规律**：

| | `getXxx` | `getDeclaredXxx` |
|---|---|---|
| 访问范围 | 仅 public | 所有（含 private） |
| 包括继承 | ✅ | ❌ |
| 访问 private | ❌ | 需要 `setAccessible(true)` |

## 5. 动态代理

### 5.1 什么是代理？

先不管"动态"，理解"代理"本身。生活中的代理：你找房产中介租房，中介帮你对接房东，但中介可以在中间加自己的服务（带你看房、审合同、收服务费）。

代码里也一样——你不直接调用目标对象，而是通过一个代理对象调用。代理对象可以在调用前后**加额外逻辑**，但目标对象本身的代码完全不用改：

```
不用代理：
  调用方 → 目标对象.方法()

用代理：
  调用方 → 代理对象.方法()
                ↓
           执行额外逻辑（记日志、开事务、权限检查...）
                ↓
           目标对象.方法()（真正的业务逻辑）
                ↓
           执行额外逻辑（记耗时、提交事务...）
                ↓
           返回结果给调用方
```

### 5.2 为什么需要动态代理？

假设你想给每个方法加日志，不用代理的话：

```java
public class UserServiceImpl implements UserService {
    public String getUser(String id) {
        System.out.println("[LOG] getUser 开始");    // 重复代码
        String result = "User:" + id;
        System.out.println("[LOG] getUser 结束");    // 重复代码
        return result;
    }

    public void deleteUser(String id) {
        System.out.println("[LOG] deleteUser 开始"); // 又是重复代码
        System.out.println("删除 " + id);
        System.out.println("[LOG] deleteUser 结束"); // 又是重复代码
    }
}
// 每个方法都要手动加日志，100 个方法就要写 200 行重复代码
// 而且日志逻辑和业务逻辑混在一起，违反单一职责
```

动态代理的解决思路：**把日志逻辑抽出来，自动应用到所有方法上**，业务代码一行不改。

### 5.3 怎么实现？

分四步走：

**第一步：定义接口和实现类**

```java
// 接口：定义有哪些方法
public interface UserService {
    String getUser(String id);
    void deleteUser(String id);
}

// 实现类：纯业务逻辑，不掺杂日志代码
public class UserServiceImpl implements UserService {
    public String getUser(String id) { return "User:" + id; }
    public void deleteUser(String id) { System.out.println("删除 " + id); }
}
```

**第二步：写一个 InvocationHandler（代理要做什么额外的事）**

`InvocationHandler` 是一个接口，只有一个方法 `invoke`。每次调用代理对象的任何方法，都会走到这里：

```java
public class LoggingHandler implements InvocationHandler {
    private final Object target;  // 被代理的真实对象

    public LoggingHandler(Object target) {
        this.target = target;
    }

    // proxy：代理对象本身（一般不用）
    // method：正在被调用的方法（反射的 Method 对象）
    // args：调用时传的参数
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // ===== 前置逻辑 =====
        System.out.println("[BEFORE] " + method.getName());

        // ===== 调用真实对象的方法 =====
        Object result = method.invoke(target, args);  // 反射调用 target 的同名方法

        // ===== 后置逻辑 =====
        System.out.println("[AFTER] " + method.getName());

        return result;
    }
}
```

**第三步：创建代理对象**

```java
UserService real = new UserServiceImpl();

UserService proxy = (UserService) Proxy.newProxyInstance(
    UserService.class.getClassLoader(),   // 类加载器（固定写法）
    new Class[]{UserService.class},       // 代理哪些接口（接口数组）
    new LoggingHandler(real)              // 用哪个 Handler 处理
);
```

**`Proxy.newProxyInstance` 底层到底做了什么？**

它在运行时**动态生成了一个全新的类**（你的代码里看不到，JVM 在内存中凭空造出来的），大致长这样：

```java
// JVM 自动生成的代理类（伪代码，帮助理解）
public class $Proxy0 implements UserService {

    private InvocationHandler handler;  // 就是你传入的 LoggingHandler

    // 构造方法：接收 handler
    public $Proxy0(InvocationHandler handler) {
        this.handler = handler;
    }

    // 实现接口的 getUser 方法
    @Override
    public String getUser(String id) {
        // 不写任何业务逻辑！
        // 直接把"调用了什么方法、传了什么参数"全部转发给 handler.invoke()
        Method method = UserService.class.getMethod("getUser", String.class);
        return (String) handler.invoke(this, method, new Object[]{id});
    }

    // 实现接口的 deleteUser 方法
    @Override
    public void deleteUser(String id) {
        // 同样，转发给 handler.invoke()
        Method method = UserService.class.getMethod("deleteUser", String.class);
        handler.invoke(this, method, new Object[]{id});
    }
}
```

注意关键点：**代理类不复制 UserServiceImpl 的代码**。代理类里没有任何业务逻辑，每个方法都只做一件事——把调用转发给 `handler.invoke()`。

真正的业务逻辑在哪执行？在 `handler.invoke()` 里面，你自己写的 `method.invoke(target, args)` 这一行通过反射调用了 `UserServiceImpl` 的方法。

**完整调用链**：

```
你写：proxy.getUser("001")

  → 实际调用的是 $Proxy0.getUser("001")（JVM 生成的代理类）

  → $Proxy0 什么都不做，转发给 handler.invoke(proxy, getUser方法, ["001"])

  → 你写的 LoggingHandler.invoke() 开始执行：
      1. 打印 [BEFORE] getUser
      2. method.invoke(target, args)  ← 这里才调用真实对象 UserServiceImpl.getUser("001")
      3. 打印 [AFTER] getUser
      4. 返回结果 "User:001"

  → 结果返回给调用方
```

所以整个流程是：**代理类是空壳，负责拦截 → handler 负责加额外逻辑 → 反射调用真实对象执行业务**。

**为什么必须有接口？** 因为 JVM 生成代理类时需要知道"要实现哪些方法"，接口就是方法的清单。没有接口，JVM 不知道代理类该长什么样。没有接口的情况用 CGLIB（原理是生成子类继承目标类，通过 `super.方法()` 调用真实逻辑）。

**第四步：使用代理对象（和使用真实对象完全一样）**

```java
proxy.getUser("001");
// [BEFORE] getUser
// [AFTER] getUser

proxy.deleteUser("002");
// [BEFORE] deleteUser
// 删除 002
// [AFTER] deleteUser
```

调用方完全感知不到自己用的是代理，但每个方法调用都自动加上了日志。

### 5.4 实际应用场景

动态代理不只是加日志，框架里到处都是：

| 场景 | 框架 | 代理做了什么 |
|------|------|------------|
| 事务管理 | Spring `@Transactional` | 方法前开启事务，成功提交，异常回滚 |
| 权限校验 | Spring Security | 方法前检查用户权限，没权限抛异常 |
| 性能监控 | Micrometer | 方法前后记录耗时 |
| RPC 调用 | Dubbo / Feign | 把方法调用转成网络请求发给远程服务 |
| SQL 映射 | MyBatis Mapper | 把接口方法转成 SQL 执行 |

```java
// Spring AOP 的 @Transactional 底层就是动态代理
@Transactional
public void transfer(String from, String to, double amount) {
    // Spring 生成代理对象，在方法前后自动开启/提交/回滚事务
    // 你写的代码里完全不需要 begin / commit / rollback
}
```

### 5.5 JDK 代理 vs CGLIB 代理

JDK 动态代理有一个限制：**目标类必须实现接口**。如果没有接口怎么办？用 CGLIB。

| | JDK 动态代理 | CGLIB 代理 |
|---|---|---|
| 要求 | 目标类必须实现接口 | 不需要接口 |
| 原理 | 运行时生成接口的实现类 | 运行时生成目标类的**子类** |
| 限制 | 只能代理接口方法 | 不能代理 final 类和 final 方法（子类不能重写 final） |
| Spring 选择 | 有接口时使用 | 无接口时使用（Spring Boot 2.0+ 默认 CGLIB） |

**一个常见的坑**：同一个类内部调用带 `@Transactional` 的方法，事务不生效：

```java
public class OrderService {
    public void createOrder() {
        this.bindCoupon();  // this 是真实对象，不是代理对象，不走代理逻辑
    }

    @Transactional
    public void bindCoupon() {
        // 事务不生效！因为是 this 直接调用，没经过代理
    }
}
```

原因是 `this.bindCoupon()` 走的是真实对象，不经过代理对象，所以代理加的事务逻辑不会执行。解决方案是注入自身或用 `AopContext.currentProxy()`。

## 6. 注解在框架中的实际应用

理解了注解 + 反射 + 动态代理，就能理解这些框架注解背后发生了什么：

| 注解 | 框架 | 背后的机制 |
|------|------|-----------|
| `@Autowired` | Spring | 反射扫描字段 → 从容器中查找匹配的 Bean → 反射注入 |
| `@RequestMapping` | Spring MVC | 反射扫描方法 → 建立 URL 到方法的映射 → 请求到达时反射调用 |
| `@Transactional` | Spring | 动态代理 → 方法前开启事务 → 方法后提交/回滚 |
| `@Column` | JPA/MyBatis | 反射读取注解 → 建立字段到数据库列的映射 |
| `@Test` | JUnit | 反射扫描带 @Test 的方法 → 逐个反射调用并收集结果 |
| `@Data` | Lombok | **编译期**注解处理器（APT），直接修改 AST，不用反射 |

注意最后一个：Lombok 的 `@Data` 不走反射，它在**编译期**通过注解处理器（Annotation Processing Tool）直接生成 getter/setter 的字节码，所以没有运行时性能损失。

## 7. 小结

| 主题 | 关键要点 |
|------|---------|
| 注解 | 本质是元数据标记，本身不包含逻辑；用 `@interface` 定义 |
| 元注解 | @Target（贴在哪）、@Retention（保留到何时）、@Inherited、@Documented |
| @Retention | SOURCE（编译期丢弃）→ CLASS（保留到 class）→ RUNTIME（反射可读，框架用这个） |
| 反射入口 | `Class.forName()` / `类名.class` / `对象.getClass()` |
| 反射操作 | Constructor（构造）、Field（字段）、Method（方法），配合 setAccessible 突破 private |
| getDeclaredXxx | 获取所有（含 private），不含继承的；getXxx 只获取 public，含继承的 |
| 注解 + 反射 | 注解做标记，反射读标记并执行逻辑——这就是 Spring 等框架的核心原理 |
| 动态代理 | JDK 代理（基于接口）、CGLIB（基于子类）；Spring AOP 的基础 |
| 性能 | 反射比直接调用慢 10-50 倍，缓存 Method/Field 可优化 |

---

> **下一篇预告**：枚举（Enum）——类型安全的常量与高级用法

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
