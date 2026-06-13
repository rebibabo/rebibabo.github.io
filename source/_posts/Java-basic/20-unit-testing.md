---
title: 'Java全貌(20) | 单元测试：JUnit 5 + Mockito 实战'
date: 2026-05-20
tags:
  - Java
  - JUnit
  - Mockito
  - 测试
categories:
  - Java全貌
---

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

```kotlin
// Spring Boot 项目：starter-test 已经包含了 JUnit 5 + Mockito + AssertJ
dependencies {
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

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

```java
// 基础断言
assertEquals(expected, actual);
assertEquals(3.14, result, 0.001);  // 浮点数断言需要指定精度
assertNotEquals(a, b);
assertTrue(condition);
assertFalse(condition);
assertNull(obj);
assertNotNull(obj);
assertSame(obj1, obj2);           // 引用相同（==）

// 异常断言
Exception ex = assertThrows(IllegalArgumentException.class, () -> {
    service.setAge(-1);
});
assertEquals("Invalid age: -1", ex.getMessage());

// 不抛异常
assertDoesNotThrow(() -> service.setAge(25));

// 超时断言
assertTimeout(Duration.ofSeconds(2), () -> {
    slowOperation();
});

// 分组断言：一次验证多个条件，全部失败都会报出来
assertAll("用户信息校验",
    () -> assertEquals("Alice", user.getName()),
    () -> assertEquals(25, user.getAge()),
    () -> assertNotNull(user.getEmail())
);
```

### 2.5 AssertJ（更流畅的断言，Spring Boot 默认包含）

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

// 集合
assertThat(users).hasSize(3)
    .extracting(User::getName)
    .containsExactly("Alice", "Bob", "Charlie");

// 异常
assertThatThrownBy(() -> service.setAge(-1))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessageContaining("Invalid age");
```

### 2.6 参数化测试

```java
// 同一个测试逻辑，跑多组数据
@ParameterizedTest
@ValueSource(ints = {1, 2, 3, 4, 5})
void shouldBePositive(int number) {
    assertTrue(number > 0);
}

@ParameterizedTest
@NullAndEmptySource   // null 和 "" 两组
@ValueSource(strings = {"  ", "\t", "\n"})
void shouldRejectBlankInput(String input) {
    assertThrows(IllegalArgumentException.class, () -> service.process(input));
}

// CSV 数据源
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

// 方法数据源（复杂数据）
@ParameterizedTest
@MethodSource("userProvider")
void shouldValidateUser(User user, boolean expected) {
    assertEquals(expected, validator.isValid(user));
}

static Stream<Arguments> userProvider() {
    return Stream.of(
        Arguments.of(new User("Alice", "alice@test.com"), true),
        Arguments.of(new User("", "alice@test.com"), false),
        Arguments.of(new User("Alice", "invalid"), false)
    );
}
```

### 2.7 条件执行与禁用

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
// UserService 依赖 UserRepository
// 测试 UserService 时，不想连真实数据库
// → 用 Mock 的 UserRepository，控制它返回什么数据
```

### 3.2 基本用法

```java
@ExtendWith(MockitoExtension.class)  // 启用 Mockito
class UserServiceTest {

    @Mock                      // 创建 Mock 对象
    private UserRepository userRepo;

    @InjectMocks               // 创建被测对象，自动注入上面的 Mock
    private UserService userService;

    @Test
    void shouldReturnUserById() {
        // 1. 设置 Mock 行为（when...thenReturn）
        User mockUser = new User("Alice", "alice@test.com");
        when(userRepo.findById(1L)).thenReturn(Optional.of(mockUser));

        // 2. 调用被测方法
        User result = userService.getById(1L);

        // 3. 验证结果
        assertEquals("Alice", result.getName());

        // 4. 验证 Mock 的方法确实被调用了
        verify(userRepo).findById(1L);
        verify(userRepo, times(1)).findById(1L);   // 验证调用次数
        verify(userRepo, never()).deleteById(any()); // 验证没有调用过 delete
    }
}
```

### 3.3 Mock 的常用设置

```java
// 返回值
when(repo.findById(1L)).thenReturn(Optional.of(user));
when(repo.findAll()).thenReturn(List.of(user1, user2));
when(repo.existsByEmail("a@b.com")).thenReturn(true);

// 抛异常
when(repo.findById(999L)).thenThrow(new RuntimeException("DB error"));

// 根据参数动态返回
when(repo.findById(anyLong())).thenAnswer(invocation -> {
    Long id = invocation.getArgument(0);
    return Optional.of(new User("User" + id, id + "@test.com"));
});

// void 方法抛异常
doThrow(new RuntimeException("fail")).when(repo).deleteById(999L);

// void 方法什么都不做（默认行为，通常不需要写）
doNothing().when(repo).deleteById(1L);

// 连续调用返回不同值
when(repo.count()).thenReturn(10L, 20L, 30L);
// 第一次调用返回 10，第二次 20，第三次及之后 30
```

### 3.4 参数匹配器

```java
// 精确匹配
when(repo.findById(1L)).thenReturn(Optional.of(user));

// 任意参数
when(repo.findById(anyLong())).thenReturn(Optional.of(user));
when(repo.findByEmail(anyString())).thenReturn(Optional.empty());
when(repo.save(any(User.class))).thenReturn(user);

// 注意：使用了匹配器，所有参数都必须用匹配器
// 错误：when(repo.find(1L, anyString()))
// 正确：when(repo.find(eq(1L), anyString()))

// 自定义匹配
when(repo.findByEmail(argThat(email -> email.endsWith("@test.com"))))
    .thenReturn(Optional.of(user));

// verify 中的匹配器
verify(repo).save(argThat(u -> u.getName().equals("Alice") && u.getEmail() != null));
```

### 3.5 验证调用

```java
// 验证调用次数
verify(repo, times(1)).save(any());        // 恰好 1 次
verify(repo, times(2)).findById(anyLong()); // 恰好 2 次
verify(repo, atLeast(1)).findAll();        // 至少 1 次
verify(repo, atMost(3)).findAll();         // 最多 3 次
verify(repo, never()).deleteById(any());   // 从未调用

// 验证调用顺序
InOrder inOrder = inOrder(repo, cache);
inOrder.verify(cache).get("user:1");       // 先查缓存
inOrder.verify(repo).findById(1L);         // 缓存没命中再查数据库
inOrder.verify(cache).put(eq("user:1"), any()); // 最后写缓存

// 验证没有更多交互
verifyNoMoreInteractions(repo);
```

### 3.6 @Spy：部分 Mock

Mock 会替换所有方法，Spy 保留真实实现，只覆盖指定方法：

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

## 4. 测试 Service 层完整示例

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepo;

    @InjectMocks
    private UserService userService;

    private User testUser;

    @BeforeEach
    void setUp() {
        testUser = new User("Alice", "alice@test.com");
        testUser.setId(1L);
    }

    @Test
    @DisplayName("根据 ID 查询 - 存在")
    void getById_shouldReturnUser_whenExists() {
        when(userRepo.findById(1L)).thenReturn(Optional.of(testUser));

        User result = userService.getById(1L);

        assertThat(result.getName()).isEqualTo("Alice");
        verify(userRepo).findById(1L);
    }

    @Test
    @DisplayName("根据 ID 查询 - 不存在应抛异常")
    void getById_shouldThrow_whenNotExists() {
        when(userRepo.findById(999L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> userService.getById(999L))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessageContaining("999");
    }

    @Test
    @DisplayName("创建用户 - 成功")
    void create_shouldSaveAndReturnUser() {
        when(userRepo.existsByEmail("alice@test.com")).thenReturn(false);
        when(userRepo.save(any(User.class))).thenReturn(testUser);

        User result = userService.create("Alice", "alice@test.com");

        assertThat(result.getName()).isEqualTo("Alice");
        verify(userRepo).existsByEmail("alice@test.com");
        verify(userRepo).save(any(User.class));
    }

    @Test
    @DisplayName("创建用户 - 邮箱已存在应抛异常")
    void create_shouldThrow_whenEmailExists() {
        when(userRepo.existsByEmail("alice@test.com")).thenReturn(true);

        assertThatThrownBy(() -> userService.create("Alice", "alice@test.com"))
            .isInstanceOf(BusinessException.class)
            .hasMessageContaining("already exists");

        verify(userRepo, never()).save(any());  // 确认没有执行保存
    }

    @Test
    @DisplayName("删除用户 - 不存在应抛异常")
    void delete_shouldThrow_whenNotExists() {
        when(userRepo.existsById(999L)).thenReturn(false);

        assertThatThrownBy(() -> userService.delete(999L))
            .isInstanceOf(ResourceNotFoundException.class);

        verify(userRepo, never()).deleteById(any());
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