---
title: 'java-basics(20) | 单元测试：JUnit 5 + Mockito 实战'
date: 2026-05-20
tags:
  - Java
  - JUnit
  - Mockito
  - 测试
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

写完代码只是一半，另一半是证明它能正确工作。单元测试不只是"加分项"——在正规团队中，没有测试的代码不允许合并。这篇文章覆盖 JUnit 5 的核心用法和 Mockito 的 Mock 技巧，目标是让你入职第一天就能写出规范的测试。

<!-- more -->

## 1. 为什么要写单元测试？

```
不写测试的代码 →
  手动启动应用 → 用 Postman 请求 → 肉眼看结果 → 改了代码再来一遍
  问题：慢、不可重复、容易遗漏边界情况、别人改了你的代码不知道有没有破坏功能

写了测试的代码 →
  一条命令跑完所有测试 → 几秒钟知道结果 → CI/CD 自动执行
  改了代码 → 测试全过 → 安心提交
```

## 2. JUnit 5 基础

### 2.1 依赖

Spring Boot 项目里，`spring-boot-starter-test` 是一个"全家桶"：一次引入就包含了 JUnit 5、Mockito、AssertJ、MockMvc 等测试常用库，不需要单独引入。

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

`spring-boot-starter-test` 包含的主要库：

| 库 | 用途 |
|---|---|
| JUnit 5 (Jupiter) | 测试框架本身：`@Test`、生命周期注解、断言 |
| Mockito | Mock 依赖对象 |
| AssertJ | 更流畅的链式断言（`assertThat(...)`） |
| Spring Test / MockMvc | 测试 Controller、加载 Spring 上下文 |
| JSONassert / JsonPath | 验证 JSON 响应结构 |

### 2.2 第一个测试

```java
// 被测试的类
public class Calculator {
    public int add(int a, int b) { return a + b; }
    public int divide(int a, int b) {
        if (b == 0) throw new ArithmeticException("除数不能为 0");
        return a / b;
    }
}

// 测试类
class CalculatorTest {

    private Calculator calculator;

    @BeforeEach  // 每个测试方法执行前调用
    void setUp() {
        calculator = new Calculator();
    }

    @Test
    @DisplayName("两个正数相加")
    void shouldAddTwoPositiveNumbers() {
        int result = calculator.add(2, 3);
        assertEquals(5, result);
    }

    @Test
    @DisplayName("除以零应该抛异常")
    void shouldThrowWhenDivideByZero() {
        assertThrows(ArithmeticException.class, () -> calculator.divide(10, 0));
    }
}
```

### 2.3 生命周期注解

JUnit 5 用一组注解控制"在测试方法的什么时机执行什么代码"，常用来做初始化和清理：

| 注解 | 执行时机 | 是否要求 static | 典型用途 |
|---|---|---|---|
| `@BeforeAll` | 所有测试方法之前，只执行一次 | 是 | 启动共享资源（如内嵌数据库、容器） |
| `@BeforeEach` | 每个测试方法之前 | 否 | 初始化被测对象、重置数据 |
| `@AfterEach` | 每个测试方法之后 | 否 | 清理本次测试产生的数据 |
| `@AfterAll` | 所有测试方法之后，只执行一次 | 是 | 释放共享资源 |

`@BeforeAll`/`@AfterAll` 必须是 `static` 方法，因为它们在测试类**实例化之前/之后**执行，此时还没有（或已经没有）一个具体的测试对象可以调用实例方法。

```java
class LifecycleDemo {
    @BeforeAll   // 所有测试前执行一次（必须 static）
    static void beforeAll() { System.out.println("初始化共享资源"); }

    @BeforeEach  // 每个测试前执行
    void setUp() { System.out.println("初始化测试对象"); }

    @Test void test1() { System.out.println("测试 1"); }
    @Test void test2() { System.out.println("测试 2"); }

    @AfterEach   // 每个测试后执行
    void tearDown() { System.out.println("清理"); }

    @AfterAll    // 所有测试后执行一次（必须 static）
    static void afterAll() { System.out.println("释放共享资源"); }
}

// 输出顺序：
// 初始化共享资源
// 初始化测试对象 → 测试 1 → 清理
// 初始化测试对象 → 测试 2 → 清理
// 释放共享资源
```

### 2.4 常用断言

JUnit 5 的断言都是 `org.junit.jupiter.api.Assertions` 的静态方法，按用途可以分为四类：

| 分类 | 方法 | 说明 |
|---|---|---|
| 相等性 | `assertEquals` / `assertNotEquals` | 比较值是否相等（用 `equals`） |
| 浮点数 | `assertEquals(expected, actual, delta)` | 浮点数有精度误差，必须指定容差范围 |
| 布尔/空值 | `assertTrue` / `assertFalse` / `assertNull` / `assertNotNull` | 判断条件、判断对象是否为 null |
| 引用比较 | `assertSame` / `assertNotSame` | 比较是否为同一个对象（`==`，区别于 `equals`） |
| 异常 | `assertThrows` / `assertDoesNotThrow` | 验证是否抛出（或不抛出）异常 |
| 超时 | `assertTimeout` | 验证代码在指定时间内执行完成 |
| 分组 | `assertAll` | 一次执行多个断言，全部失败都报出来 |

**基础断言**

```java
assertEquals(expected, actual);
assertEquals(3.14, result, 0.001);  // 浮点数断言需要指定精度
assertNotEquals(a, b);
assertTrue(condition);
assertFalse(condition);
assertNull(obj);
assertNotNull(obj);
assertSame(obj1, obj2);           // 引用相同（==）
```

**异常断言**：`assertThrows` 返回捕获到的异常对象，可以继续断言异常信息：

```java
Exception ex = assertThrows(IllegalArgumentException.class, () -> {
    service.setAge(-1);
});
assertEquals("Invalid age: -1", ex.getMessage());

// 不抛异常
assertDoesNotThrow(() -> service.setAge(25));
```

**超时断言**：超过指定时间测试直接失败，用于验证性能或防止死循环：

```java
assertTimeout(Duration.ofSeconds(2), () -> {
    slowOperation();
});
```

**分组断言**：普通断言遇到第一个失败就会中断，后面的断言不会执行；`assertAll` 会把所有断言都跑一遍，把所有失败信息汇总报出来——适合一次验证一个对象的多个字段：

```java
assertAll("用户信息校验",
    () -> assertEquals("Alice", user.getName()),
    () -> assertEquals(25, user.getAge()),
    () -> assertNotNull(user.getEmail())
);
```

### 2.5 AssertJ（更流畅的断言，Spring Boot 默认包含）

JUnit 5 自带的断言每个条件都是一个独立方法调用（`assertEquals`、`assertTrue`...），AssertJ 把同一个对象的多个断言串成一条链，可读性更接近自然语言，而且失败信息更详细。统一以 `assertThat(目标)` 开头：

| 目标类型 | 常用链式方法 |
|---|---|
| 字符串 | `isNotNull` / `startsWith` / `endsWith` / `hasSize` / `contains` |
| 数字 | `isPositive` / `isNegative` / `isGreaterThan` / `isBetween` |
| 集合 | `hasSize` / `contains` / `containsExactly` / `extracting`（取出字段再断言） |
| 异常 | `isInstanceOf` / `hasMessageContaining` |

```java
import static org.assertj.core.api.Assertions.*;

// 字符串
assertThat(name).isNotNull()
    .startsWith("Ali")
    .endsWith("ce")
    .hasSize(5);

// 数字
assertThat(age).isPositive()
    .isGreaterThan(18)
    .isBetween(20, 30);

// 集合：先取出每个元素的 name 字段，再断言这组 name 的顺序
assertThat(users).hasSize(3)
    .extracting(User::getName)
    .containsExactly("Alice", "Bob", "Charlie");

// 异常
assertThatThrownBy(() -> service.setAge(-1))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessageContaining("Invalid age");
```

### 2.6 参数化测试

`@ParameterizedTest` 让同一段测试逻辑跑多组数据，不用为每组数据复制一个 `@Test` 方法。区别在于数据从哪里来：

| 数据源注解 | 数据来源 | 适用场景 |
|---|---|---|
| `@ValueSource` | 直接写一组同类型的值 | 简单值列表（int/String/...） |
| `@NullAndEmptySource` | 自动补充 `null` 和 `""` | 测试边界值（空输入） |
| `@CsvSource` | 逐行写 CSV 格式的多参数数据 | 多个参数的简单组合 |
| `@MethodSource` | 引用一个返回 `Stream<Arguments>` 的静态方法 | 复杂对象、需要构造逻辑的数据 |

#### @ValueSource：单参数简单值列表

最基础的形式：方法只有一个参数，`@ValueSource` 提供一组同类型的值，方法会被依次调用，每次传入一个值。

```java
@ParameterizedTest
@ValueSource(ints = {1, 2, 3, 4, 5})
void shouldBePositive(int number) {
    assertTrue(number > 0);
}
// 执行 5 次：number 依次为 1, 2, 3, 4, 5
```

#### 组合多个数据源：@NullAndEmptySource + @ValueSource

JUnit 5 允许在同一个方法上叠加多个 `@...Source` 注解，**最终的数据是所有来源的并集**，不是只取其中一个：

```java
@ParameterizedTest
@NullAndEmptySource
@ValueSource(strings = {"  ", "\t", "\n"})
void shouldRejectBlankInput(String input) {
    assertThrows(IllegalArgumentException.class, () -> service.process(input));
}
```

这个例子一共会执行 **5 次**：

| 来源 | 提供的值 | 个数 |
|---|---|---|
| `@NullAndEmptySource` | `null`、`""` | 2 |
| `@ValueSource(strings = {"  ", "\t", "\n"})` | `"  "`（空格）、`"\t"`（tab）、`"\n"`（换行） | 3 |
| **合计** | | **5** |

为什么要这么写：判断一个字符串是否"为空"，光测试 `null` 和 `""` 是不够的——还有"看起来是空的但不是空字符串"的情况（纯空格、tab、换行符）。`@NullAndEmptySource` 专门覆盖前两种最常见的边界值，`@ValueSource` 再补充几种容易被忽略的"伪空白"输入，组合起来就能一次性把 `isBlank` 类逻辑的边界都测到。

#### @CsvSource：多参数组合

如果方法有多个参数，`@ValueSource` 就不够用了（它只能提供一列值）。`@CsvSource` 每一行对应一次方法调用，行内用逗号分隔的每一列对应一个参数：

```java
@ParameterizedTest
@CsvSource({
    "1, 2, 3",
    "0, 0, 0",
    "-1, 1, 0",
    "100, 200, 300"
})
void shouldAdd(int a, int b, int expected) {
    assertEquals(expected, calculator.add(a, b));
}
```

| 第几次执行 | a | b | expected |
|---|---|---|---|
| 1 | 1 | 2 | 3 |
| 2 | 0 | 0 | 0 |
| 3 | -1 | 1 | 0 |
| 4 | 100 | 200 | 300 |

#### @MethodSource：复杂对象数据源

`@ValueSource`/`@CsvSource` 只能写基本类型和字符串。如果测试数据是对象（比如要构造一个 `User`），就需要 `@MethodSource`：引用一个**静态方法**，该方法返回 `Stream<Arguments>`，每个 `Arguments.of(...)` 对应一次调用的参数列表：

```java
@ParameterizedTest
@MethodSource("userProvider")
void shouldValidateUser(User user, boolean expected) {
    assertEquals(expected, validator.isValid(user));
}

// 方法名要和 @MethodSource 中的字符串一致，且必须是 static
static Stream<Arguments> userProvider() {
    return Stream.of(
        Arguments.of(new User("Alice", "alice@test.com"), true),   // 合法用户
        Arguments.of(new User("", "alice@test.com"), false),       // 名字为空
        Arguments.of(new User("Alice", "invalid"), false)          // email 格式错误
    );
}
```

`shouldValidateUser` 会被执行 3 次，每次传入 `userProvider()` 返回的一组 `(user, expected)`。

### 2.7 条件执行与禁用

有些测试不应该一直运行——比如临时跳过一个还没修复的用例，或者某个测试只在特定操作系统/环境下才有意义：

| 注解 | 效果 |
|---|---|
| `@Disabled("原因")` | 跳过该测试，原因会显示在测试报告中 |
| `@EnabledOnOs(OS.LINUX)` | 只在指定操作系统上运行 |
| `@EnabledIfEnvironmentVariable(named=..., matches=...)` | 只在指定环境变量满足条件时运行（如仅 CI 环境） |

```java
@Test
@Disabled("等待 bug #123 修复后启用")
void skippedTest() { }

@Test
@EnabledOnOs(OS.LINUX)
void onlyOnLinux() { }

@Test
@EnabledIfEnvironmentVariable(named = "ENV", matches = "ci")
void onlyInCI() { }
```

## 3. Mockito：隔离依赖

### 3.1 为什么需要 Mock？

单元测试只测当前类的逻辑，不应该依赖真实的数据库、网络、外部服务。Mock 就是用"假对象"替代真实依赖：

```java
// UserService 依赖 UserMapper
// 测试 UserService 时，不想连真实数据库
// → 用 Mock 的 UserMapper，控制它返回什么数据
```

### 3.2 基本用法

```java
@ExtendWith(MockitoExtension.class)  // 启用 Mockito
class UserServiceTest {

    @Mock                      // 创建 Mock 对象
    private UserMapper userMapper;

    @InjectMocks               // 创建被测对象，自动注入上面的 Mock
    private UserService userService;

    @Test
    void shouldReturnUserById() {
        // 1. 设置 Mock 行为（when...thenReturn）
        User mockUser = new User();
        mockUser.setId(1L);
        mockUser.setName("Alice");
        mockUser.setEmail("alice@test.com");
        when(userMapper.selectById(1L)).thenReturn(mockUser);

        // 2. 调用被测方法
        User result = userService.getById(1L);

        // 3. 验证结果
        assertEquals("Alice", result.getName());

        // 4. 验证 Mock 的方法确实被调用了
        verify(userMapper).selectById(1L);
        verify(userMapper, times(1)).selectById(1L);   // 验证调用次数
        verify(userMapper, never()).deleteById(any()); // 验证没有调用过 delete
    }
}
```

需要的 import：

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.never;
import static org.mockito.ArgumentMatchers.any;
```

#### 逐步拆解：这段代码到底在干什么

**1. `@Mock` 创建的是什么**

`userMapper` 不是真实的 `UserMapper` 实现（不会连数据库）。Mockito 用字节码技术生成了一个"假的 `UserMapper`"——它的所有方法默认什么都不做，返回值是该类型的默认值（对象返回 `null`，`int` 返回 `0`，集合返回空集合）。也就是说，**如果不设置，`userMapper.selectById(1L)` 默认返回 `null`**。

**2. `@InjectMocks` 做了什么**

它创建一个**真实的** `UserService` 对象（不是假的），但把上面那个假的 `userMapper` 注入进去（通过构造函数，因为 `UserService` 用了 `@RequiredArgsConstructor`）。所以 `userService` 里面跑的是真代码，只是它依赖的 `userMapper` 是假的。

**3. `when(...).thenReturn(...)`：设定剧本**

```java
when(userMapper.selectById(1L)).thenReturn(mockUser);
```

直译：**"当 `userMapper.selectById(1L)` 被调用时，返回 `mockUser`"**。相当于给这个假对象写了一条规则：以后任何代码调用 `userMapper.selectById(1L)`，Mockito 都不会真的执行什么逻辑，而是直接把 `mockUser` 这个对象吐出来。

注意：这一行**没有调用 `UserService` 的任何方法**，纯粹是在配置 `userMapper` 这个假对象的行为。

**4. `userService.getById(1L)` 时发生了什么**

这是真代码在跑：

```java
public User getById(Long id) {
    User user = userMapper.selectById(id);  // ← 调用到第 3 步设定好的假对象
    if (user == null) {
        throw new ResourceNotFoundException("User not found: " + id);
    }
    return user;
}
```

`userMapper.selectById(1L)` 因为第 3 步的设定，返回的是 `mockUser`（不是 `null`）。所以 `user` 就是 `mockUser`，`if` 判断不成立，直接 `return mockUser`。

因此 `result` 就是 `mockUser`，`result.getName()` 就是 `"Alice"`——`assertEquals("Alice", result.getName())` 通过。

**5. `verify(...)`：事后检查有没有发生过某个调用**

这和 `when` 完全是两件事：`when` 是**测试开始前**配置假对象的行为；`verify` 是**测试跑完后**检查代码到底有没有调用过某个方法。

```java
verify(userMapper).selectById(1L);
```
检查 `userMapper.selectById(1L)` 这个调用**至少发生过一次**。为什么需要它？因为光看 `assertEquals` 只能证明"最终结果对了"，不能证明"是通过查数据库得到的"——万一 `getById` 写错了，比如直接 `return new User("Alice", ...)` 硬编码返回，`assertEquals` 一样会通过，但根本没查数据库。`verify` 就是用来确认"这个方法确实走了预期的路径"。

```java
verify(userMapper, times(1)).selectById(1L);   // 验证调用次数
```
和上一行基本一样，只是显式写出"恰好调用 1 次"。`verify(x).method()` 默认就是 `times(1)`，这里写出来只是为了示范 `times` 的用法。

```java
verify(userMapper, never()).deleteById(any()); // 验证没有调用过 delete
```
检查 `userMapper.deleteById(...)`（无论传什么参数）**一次都没被调用过**。这是个查询操作，正常逻辑下绝不应该触发删除——如果代码里不小心多写了一行 `userMapper.deleteById(id)`，光靠 `assertEquals` 测不出来（返回值可能还是对的），但这行 `verify` 能保证"没有发生不该发生的副作用"。`any()` 表示"不管传的是什么参数"。

> 一句话总结：**`when/thenReturn` 是"告诉假对象遇到这个调用该怎么回应"，`verify` 是"检查真代码到底有没有调用假对象的某个方法"——两者操作的都是 `@Mock` 标注的那个假对象，互不影响。**

### 3.3 Mock 的常用设置

`when(...).thenXxx(...)` 这一整套，本质上都是在回答同一个问题：**"`userMapper` 这个假对象的某个方法被调用时，应该怎么表现？"** —— 返回什么值、抛什么异常、还是动态计算。下面按场景拆开讲。

#### 1. `thenReturn`：固定返回一个值

最常用的写法，直接指定返回值：

```java
when(userMapper.selectById(1L)).thenReturn(user);
when(userMapper.selectById(999L)).thenReturn(null);          // 模拟"查不到"
when(userMapper.selectList(any())).thenReturn(List.of(user1, user2));
```

这三行是三条独立的规则：
- "调用 `selectById(1L)` → 返回 `user`"
- "调用 `selectById(999L)` → 返回 `null`"（模拟数据库里没有 id=999 的记录）
- "调用 `selectList(任意参数)` → 返回一个包含 `user1`、`user2` 的列表"

> MyBatis-Plus 的 `BaseMapper` 方法直接返回对象、`null` 或受影响行数（`int`/`long`），不像 JPA 那样包一层 `Optional`。所以"查不到"在这里就是 `thenReturn(null)`，不需要 `Optional.empty()`。

#### 2. `thenThrow`：让方法抛异常

```java
when(userMapper.selectById(1L)).thenThrow(new RuntimeException("DB error"));
```

意思：调用 `userMapper.selectById(1L)` 时，不返回任何值，而是直接抛出这个 `RuntimeException`。

**用途**：测试"数据库报错时，Service 层会怎么处理"——比如你想验证 `UserService` 是否会把这个异常包装成自己的业务异常、或者记录日志。不用这一行的话，正常情况下是测不到"数据库异常"这种场景的，因为 Mock 默认不会抛异常。

#### 3. `thenAnswer`：根据传入的参数动态计算返回值

前两种是"固定值"，但有时候你希望返回值跟调用时传入的参数相关——比如"不管传哪个 id，都返回一个 id 和名字对应的 `User`"：

```java
when(userMapper.selectById(anyLong())).thenAnswer(invocation -> {
    Long id = invocation.getArgument(0);   // 取出本次调用的第 1 个参数（0 是下标）
    User u = new User();
    u.setId(id);
    u.setName("User" + id);
    return u;
});
```

逐步拆解：
- `anyLong()` 表示"不管传入什么 `Long` 值都匹配这条规则"（区别于 `thenReturn` 通常配合固定参数，比如 `selectById(1L)`）
- `invocation` 是 Mockito 传进来的"本次调用信息"对象，`invocation.getArgument(0)` 就是取出调用时传的第一个参数（比如 `userMapper.selectById(5L)` 里的 `5L`）
- 这个 lambda 会在**每次**调用 `selectById(任意id)` 时执行一遍，所以 `selectById(5L)` 会返回 `id=5, name="User5"` 的对象，`selectById(7L)` 会返回 `id=7, name="User7"`

**用途**：当你要在一个测试里用很多不同的 id 调用同一个方法，又不想为每个 id 单独写一行 `thenReturn` 时。

#### 4. insert / update / delete：返回的是"影响行数"

MyBatis-Plus 的写操作（`insert`、`updateById`、`deleteById`）返回的是 `int` —— 表示这次操作影响了几行数据，**不是布尔值，也不是 void**：

```java
when(userMapper.insert(any(User.class))).thenReturn(1);  // 模拟"插入成功，影响 1 行"
when(userMapper.deleteById(1L)).thenReturn(1);           // 模拟"删除成功，影响 1 行"
```

如果 Mock 没有显式设置这两行，`userMapper.insert(...)` 默认会返回 `0`（`int` 的默认值）。大多数测试场景下 `0` 也够用（因为 Service 通常不检查返回值），但如果你的业务逻辑会判断"`insert` 返回值是不是 `> 0`"，就必须显式 `thenReturn(1)`，否则会被判定为"插入失败"。

#### 5. 连续调用返回不同值

```java
when(userMapper.selectCount(any())).thenReturn(10L, 20L, 30L);
// 第一次调用返回 10，第二次 20，第三次及之后 30
```

`thenReturn` 可以传多个参数，效果是**按顺序消费**：第 1 次调用 `selectCount(...)` 返回 `10L`，第 2 次返回 `20L`，第 3 次及以后都返回 `30L`（最后一个值会一直重复，不会越界报错）。

**用途**：测试"先查一次数量、做点操作、再查一次数量"这种场景——比如验证"插入前 count=10，插入后 count 变成 11"，但因为这里整个 `selectCount` 都是 Mock，没有真的插入，所以只能用这种"手动指定第二次返回什么"的方式模拟数量变化。

---

> **小结**：MyBatis-Plus 的 CRUD 方法都有返回值（对象/集合/行数），没有 `void` 方法，所以一般用 `when().thenReturn()` / `thenThrow()` / `thenAnswer()` 就够了，不需要 `doNothing()` / `doThrow()`（那两个是专门给 `void` 方法用的，MyBatis-Plus 里基本不会用到）。

### 3.4 参数匹配器（ArgumentMatchers）

3.3 里的例子都是写死的参数，比如 `when(userMapper.selectById(1L))`——这条规则**只对 `selectById(1L)` 生效**，如果代码传的是 `selectById(2L)`，就不会命中这条规则，会落回 Mock 的默认行为（返回 `null`）。

但很多时候我们不关心测试里到底传了哪个具体值，只关心"不管传什么，都按这个规则处理"，这时就需要**参数匹配器**：

| 匹配器 | 匹配范围 |
|---|---|
| `anyLong()` / `anyString()` / `anyInt()` | 该类型的任意值 |
| `any(User.class)` | 任意 `User` 对象 |
| `eq(value)` | 精确等于某个值（效果和直接写字面值一样，用于和其他匹配器混用的场景） |
| `argThat(predicate)` | 自定义条件——传入一个 lambda，返回 `true` 才算匹配 |

```java
when(userMapper.selectById(anyLong())).thenReturn(user);
when(userMapper.selectByEmail(anyString())).thenReturn(null);
when(userMapper.insert(any(User.class))).thenReturn(1);
```

这三行的意思是："不管 `selectById` 传的是哪个 id，都返回 `user`"、"不管 `selectByEmail` 传的是哪个字符串，都返回 `null`"、"不管 `insert` 传的是哪个 `User` 对象，都返回 `1`"。

#### 一个容易踩的坑：匹配器不能和字面值混用

```java
// 错误：第一个参数用字面值 1L，第二个参数用匹配器 anyString()
when(userMapper.selectByNameAndEmail(1L, anyString()))...

// 正确：第一个参数也要用匹配器 eq(1L)
when(userMapper.selectByNameAndEmail(eq(1L), anyString()))...
```

Mockito 的规则是：**一个方法调用里，只要有一个参数用了匹配器（`any`/`eq`/`argThat`...），其他所有参数也必须用匹配器**，不能混用字面值。如果某个参数本来就是固定值，就用 `eq(固定值)` 包一层。原因是 Mockito 内部用统一的方式记录"这次调用每个参数该怎么匹配"，字面值和匹配器混在一起会导致它无法正确解析参数列表，运行时会直接抛 `InvalidUseOfMatchersException`。

#### `argThat`：自定义匹配条件

如果内置的 `any`/`eq` 不够用，可以用 `argThat` 传一个 lambda，自己写判断逻辑：

```java
when(userMapper.selectByEmail(argThat(email -> email.endsWith("@test.com"))))
    .thenReturn(user);
```

意思："只要传进来的 `email` 是以 `@test.com` 结尾的字符串，就返回 `user`"——不管具体是 `alice@test.com` 还是 `bob@test.com`，都命中这条规则。

`argThat` 不仅能用在 `when` 里，`verify` 里也能用，用来检查"调用时传的参数是否符合某个条件"：

```java
verify(userMapper).insert(argThat(u -> u.getName().equals("Alice") && u.getEmail() != null));
```

意思：检查 `userMapper.insert(...)` 被调用过，并且传入的 `User` 对象满足"`name` 是 `Alice`，且 `email` 不为 `null`"。这比 `verify(userMapper).insert(any())` 更严格——不仅要确认调用发生了，还要确认传的对象内容是对的。

### 3.5 验证调用：调用次数与调用顺序

3.2 已经介绍过最基础的 `verify(x).method()`（恰好 1 次）和 `never()`（一次都没调用）。这里补充更精细的次数控制，以及"按顺序调用"的验证。

| 写法 | 含义 |
|---|---|
| `verify(x).method()` | 恰好调用 1 次，等价于 `times(1)` |
| `verify(x, times(n)).method()` | 恰好调用 n 次 |
| `verify(x, atLeast(n)).method()` | 至少调用 n 次 |
| `verify(x, atMost(n)).method()` | 最多调用 n 次 |
| `verify(x, never()).method()` | 一次都没调用，等价于 `times(0)` |

```java
verify(userMapper, times(1)).insert(any());          // 恰好 1 次
verify(userMapper, times(2)).selectById(anyLong());  // 恰好 2 次
verify(userMapper, atLeast(1)).selectList(any());    // 至少 1 次
verify(userMapper, atMost(3)).selectList(any());     // 最多 3 次
```

#### `InOrder`：验证调用的先后顺序

普通的 `verify` 只关心"有没有调用过"，不关心顺序。但有些逻辑必须按特定顺序执行——比如缓存场景：先查缓存，缓存没有再查数据库，查到之后再写回缓存（参考 [21 节 Redis 缓存](/2026/05/21/Java-basic/21-redis/) 的 Cache-Aside 模式）。这种"先后关系"要用 `InOrder` 验证：

```java
InOrder inOrder = inOrder(userMapper, cache);
inOrder.verify(cache).get("user:1");              // 第 1 步：先查缓存
inOrder.verify(userMapper).selectById(1L);        // 第 2 步：缓存没命中再查数据库
inOrder.verify(cache).put(eq("user:1"), any());   // 第 3 步：最后写回缓存
```

逐步拆解：
- `inOrder(userMapper, cache)` 创建一个"顺序检查器"，告诉它要监控这两个 Mock 对象上发生的调用
- 接下来每一行 `inOrder.verify(...)` 都必须按代码里写的顺序依次匹配——如果实际执行顺序是"先查数据库再查缓存"，这里会报错，即使三个方法都确实被调用过

#### `verifyNoMoreInteractions`：确认没有"意外的"调用

```java
verifyNoMoreInteractions(userMapper);
```

意思：在前面所有 `verify(userMapper)...` 验证过的调用之外，**`userMapper` 不应该再有任何其他方法被调用过**。

用途：防止代码里有"漏网之鱼"——比如你只验证了 `selectById` 和 `insert`，但代码里其实还偷偷调用了一次 `deleteById`，光靠前面两个 `verify` 是发现不了的，加上这一行就能暴露出来。一般写在测试方法的最后一行。

### 3.6 @Spy：部分 Mock

| | `@Mock` | `@Spy` |
|---|---|---|
| 真实方法 | 全部替换为假实现（默认返回 null/0/空） | 默认调用真实方法 |
| 可以覆盖部分方法 | 是（所有方法本来就是假的） | 是（用 `when/thenReturn` 单独覆盖某个方法） |
| 适用场景 | 完全隔离依赖（如 `UserMapper`，不想连数据库） | 大部分逻辑要用真实实现，只想替换其中一两个方法 |

```java
@Spy
private List<String> spyList = new ArrayList<>();

@Test
void spyTest() {
    spyList.add("one");
    spyList.add("two");
    assertEquals(2, spyList.size());     // 真实方法

    when(spyList.size()).thenReturn(100); // 覆盖 size() 方法
    assertEquals(100, spyList.size());    // 返回假值
    assertEquals("one", spyList.get(0)); // 其他方法仍然是真实的
}
```

逐步拆解：
1. `spyList` 是一个**真实的** `ArrayList`，`@Spy` 只是让 Mockito 能"包一层"以便后续按需覆盖某些方法
2. `spyList.add("one")` / `add("two")` 是真实的 `ArrayList.add`，数据真的被存进去了，所以 `spyList.size()` 一开始确实是 `2`
3. `when(spyList.size()).thenReturn(100)` 之后，**只有 `size()` 这一个方法被替换成假的**，其他方法（比如 `get(0)`）仍然是真实实现，所以最后 `spyList.get(0)` 还能正确返回 `"one"`

实际项目中 `@Spy` 用得不多——`UserMapper` 这类外部依赖通常直接 `@Mock` 完全隔离；`@Spy` 更适合"测试一个工具类的大部分逻辑，但想覆盖其中调用了系统时间/随机数的那一个方法"这类场景。

## 4. 测试 Service 层完整示例

被测的 `UserService` 依赖 `UserMapper`（继承 `BaseMapper<User>`，`selectByEmail` 是自定义查询方法）：

```java
public interface UserMapper extends BaseMapper<User> {
    User selectByEmail(@Param("email") String email);
}

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserMapper userMapper;

    public User getById(Long id) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new ResourceNotFoundException("User not found: " + id);
        }
        return user;
    }

    public User create(String name, String email) {
        if (userMapper.selectByEmail(email) != null) {
            throw new BusinessException("Email already exists: " + email);
        }
        User user = new User();
        user.setName(name);
        user.setEmail(email);
        userMapper.insert(user);
        return user;
    }

    public void delete(Long id) {
        if (userMapper.selectById(id) == null) {
            throw new ResourceNotFoundException("User not found: " + id);
        }
        userMapper.deleteById(id);
    }
}
```

对应的测试：

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserMapper userMapper;

    @InjectMocks
    private UserService userService;

    private User testUser;

    @BeforeEach
    void setUp() {
        testUser = new User();
        testUser.setId(1L);
        testUser.setName("Alice");
        testUser.setEmail("alice@test.com");
    }

    @Test
    @DisplayName("根据 ID 查询 - 存在")
    void getById_shouldReturnUser_whenExists() {
        when(userMapper.selectById(1L)).thenReturn(testUser);

        User result = userService.getById(1L);

        assertThat(result.getName()).isEqualTo("Alice");
        verify(userMapper).selectById(1L);
    }

    @Test
    @DisplayName("根据 ID 查询 - 不存在应抛异常")
    void getById_shouldThrow_whenNotExists() {
        when(userMapper.selectById(999L)).thenReturn(null);

        assertThatThrownBy(() -> userService.getById(999L))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessageContaining("999");
    }

    @Test
    @DisplayName("创建用户 - 成功")
    void create_shouldSaveAndReturnUser() {
        when(userMapper.selectByEmail("alice@test.com")).thenReturn(null);
        when(userMapper.insert(any(User.class))).thenReturn(1);

        User result = userService.create("Alice", "alice@test.com");

        assertThat(result.getName()).isEqualTo("Alice");
        verify(userMapper).selectByEmail("alice@test.com");
        verify(userMapper).insert(any(User.class));
    }

    @Test
    @DisplayName("创建用户 - 邮箱已存在应抛异常")
    void create_shouldThrow_whenEmailExists() {
        when(userMapper.selectByEmail("alice@test.com")).thenReturn(testUser);

        assertThatThrownBy(() -> userService.create("Alice", "alice@test.com"))
            .isInstanceOf(BusinessException.class)
            .hasMessageContaining("already exists");

        verify(userMapper, never()).insert(any());  // 确认没有执行插入
    }

    @Test
    @DisplayName("删除用户 - 不存在应抛异常")
    void delete_shouldThrow_whenNotExists() {
        when(userMapper.selectById(999L)).thenReturn(null);

        assertThatThrownBy(() -> userService.delete(999L))
            .isInstanceOf(ResourceNotFoundException.class);

        verify(userMapper, never()).deleteById(any());
    }
}
```

## 5. 测试 Controller 层（MockMvc）

```java
@WebMvcTest(UserController.class)  // 只加载 Web 层，不启动完整容器
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean                      // Spring 容器中的 Mock（区别于 @Mock）
    private UserService userService;

    @Test
    @DisplayName("GET /api/users/1 - 成功")
    void getById_shouldReturnUser() throws Exception {
        User user = new User("Alice", "alice@test.com");
        user.setId(1L);
        when(userService.getById(1L)).thenReturn(user);

        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Alice"))
            .andExpect(jsonPath("$.email").value("alice@test.com"));
    }

    @Test
    @DisplayName("GET /api/users/999 - 不存在返回 404")
    void getById_shouldReturn404_whenNotExists() throws Exception {
        when(userService.getById(999L)).thenThrow(new ResourceNotFoundException("User not found"));

        mockMvc.perform(get("/api/users/999"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.message").value("User not found"));
    }

    @Test
    @DisplayName("POST /api/users - 参数校验失败返回 400")
    void create_shouldReturn400_whenInvalidInput() throws Exception {
        String invalidJson = "{\"name\": \"\", \"email\": \"not-an-email\"}";

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidJson))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.message").exists());

        verify(userService, never()).create(any(), any());
    }

    @Test
    @DisplayName("POST /api/users - 成功创建返回 201")
    void create_shouldReturn201() throws Exception {
        User user = new User("Alice", "alice@test.com");
        user.setId(1L);
        when(userService.create("Alice", "alice@test.com")).thenReturn(user);

        String json = "{\"name\": \"Alice\", \"email\": \"alice@test.com\"}";

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(json))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").value(1))
            .andExpect(jsonPath("$.name").value("Alice"));
    }
}
```

## 6. 测试命名与组织规范

### 6.1 命名规范

```java
// 推荐格式：方法名_应该做什么_在什么条件下
void getById_shouldReturnUser_whenExists()
void getById_shouldThrow_whenNotExists()
void create_shouldSaveUser_whenEmailIsNew()
void create_shouldThrow_whenEmailExists()

// 或者用 @DisplayName 写中文描述
@Test @DisplayName("邮箱已存在时创建用户应抛出 BusinessException")
void create_shouldThrow_whenEmailExists() { ... }
```

### 6.2 测试结构：Given-When-Then

```java
@Test
void shouldApplyDiscount_whenUserIsVip() {
    // Given（准备数据和 Mock）
    User vipUser = new User("Alice", UserType.VIP);
    when(userRepo.findById(1L)).thenReturn(Optional.of(vipUser));

    // When（执行被测方法）
    double price = orderService.calculatePrice(1L, 100.0);

    // Then（验证结果）
    assertThat(price).isEqualTo(80.0);  // VIP 打 8 折
}
```

### 6.3 目录结构

```
src/test/java/com/example/
├── service/
│   ├── UserServiceTest.java        ← 和被测类同包名
│   └── OrderServiceTest.java
├── controller/
│   └── UserControllerTest.java
└── repository/
    └── UserRepositoryTest.java     ← 数据访问层用 @DataJpaTest
```

## 7. 常用测试注解速查

| 注解 | 用途 |
|------|------|
| `@Test` | 标记测试方法 |
| `@DisplayName` | 测试显示名称 |
| `@BeforeEach / @AfterEach` | 每个测试前后执行 |
| `@BeforeAll / @AfterAll` | 所有测试前后执行（static） |
| `@Disabled` | 跳过测试 |
| `@ParameterizedTest` | 参数化测试 |
| `@ExtendWith(MockitoExtension.class)` | 启用 Mockito |
| `@Mock` | 创建 Mock 对象 |
| `@InjectMocks` | 创建被测对象并注入 Mock |
| `@Spy` | 部分 Mock（保留真实实现） |
| `@WebMvcTest` | 只测 Controller 层 |
| `@MockBean` | Spring 容器级别的 Mock |
| `@DataJpaTest` | 只测 Repository 层（内嵌 H2 数据库） |
| `@SpringBootTest` | 启动完整容器的集成测试 |

## 8. 小结

| 主题 | 关键要点 |
|------|---------|
| JUnit 5 | @Test + @BeforeEach + 断言；@ParameterizedTest 跑多组数据 |
| AssertJ | assertThat 链式断言，比 assertEquals 可读性更好 |
| Mockito 核心 | @Mock 创建假对象、when/thenReturn 设置行为、verify 验证调用 |
| @Mock vs @MockBean | @Mock 用于纯单元测试，@MockBean 用于 Spring 容器测试 |
| @Spy | 保留真实实现，只覆盖部分方法 |
| MockMvc | 不启动服务器测试 Controller，验证状态码和 JSON 响应 |
| 测试命名 | 方法名_应该做什么_在什么条件下；Given-When-Then 结构 |
| 测试粒度 | Service → @Mock + @InjectMocks；Controller → @WebMvcTest + @MockBean |

---

> **下一篇预告**：Redis 实战——Spring Data Redis 与广告系统中的缓存策略

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
