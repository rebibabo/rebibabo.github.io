---
title: 'java-basics(17) | Spring Boot 快速上手：自动配置与 REST 服务实战'
date: 2026-05-17
tags:
  - Java
  - Spring Boot
  - REST
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

上一篇理解了 Spring 的 IoC 和 AOP，这篇直接进入实战——用 Spring Boot 从零搭建一个完整的 REST 服务。Spring Boot 的核心价值是**自动配置**：它把 Spring 生态中大量的样板配置变成了"开箱即用"，让你专注于业务代码。

<!-- more -->

## 1. Spring vs Spring Boot

| 维度 | Spring | Spring Boot |
|------|--------|-------------|
| 定位 | 框架（提供 IoC、AOP 等基础能力） | Spring 的脚手架（简化配置和启动） |
| 配置 | 大量 XML 或 Java Config | 自动配置，极少手动配 |
| 内嵌服务器 | 需要外部 Tomcat | 内嵌 Tomcat/Jetty/Undertow，直接 `java -jar` 启动 |
| 依赖管理 | 手动管理每个依赖版本 | Starter 一站式引入，版本自动协调 |
| 项目创建 | 手动搭建 | Spring Initializr 一键生成 |

Spring Boot 不是替代 Spring，而是站在 Spring 上面，帮你省掉 80% 的配置工作。

## 2. 创建项目

### 2.1 Spring Initializr

最快的方式是用 [start.spring.io](https://start.spring.io/)：

```
1. 选择 Gradle - Kotlin 或 Maven
2. Language: Java
3. Spring Boot 版本：选最新的稳定版（非 SNAPSHOT）
4. 填写 Group、Artifact
5. 添加依赖：Spring Web、Spring Data JPA、MySQL Driver 等
6. 点 Generate，下载 zip 解压
```

IntelliJ IDEA 中也可以直接 `File → New → Project → Spring Initializr`。

### 2.2 生成的项目结构

```
my-app/
├── build.gradle.kts           ← 构建配置
├── settings.gradle.kts
├── src/
│   ├── main/
│   │   ├── java/com/example/myapp/
│   │   │   └── MyAppApplication.java    ← 启动类
│   │   └── resources/
│   │       ├── application.yml          ← 配置文件
│   │       ├── static/                  ← 静态资源
│   │       └── templates/               ← 模板文件
│   └── test/
│       └── java/com/example/myapp/
│           └── MyAppApplicationTests.java
```

### 2.3 启动类

```java
@SpringBootApplication
public class MyAppApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyAppApplication.class, args);
    }
}
```

`@SpringBootApplication` 是一个组合注解，等价于：

```java
@SpringBootConfiguration    // 标记为配置类（等同 @Configuration）
@EnableAutoConfiguration    // 开启自动配置（核心）
@ComponentScan              // 扫描当前包及子包下的组件
```

## 3. 自动配置原理

### 3.1 Starter 机制

Spring Boot 通过 Starter 把一组相关依赖打包在一起：

```kotlin
// 你只需要引入一个 Starter
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
}

// 它帮你引入了：
// spring-web、spring-webmvc
// 内嵌 Tomcat
// Jackson（JSON 序列化）
// 参数校验
// 日志（Logback + SLF4J）
```

常用 Starter：

| Starter | 提供的能力 |
|---------|-----------|
| `spring-boot-starter-web` | Web 开发（MVC + 内嵌 Tomcat） |
| `spring-boot-starter-data-jpa` | JPA 数据访问 |
| `spring-boot-starter-data-redis` | Redis 操作 |
| `spring-boot-starter-test` | 测试（JUnit 5 + Mockito + AssertJ） |
| `spring-boot-starter-validation` | 参数校验（Hibernate Validator） |
| `spring-boot-starter-security` | 安全认证 |
| `spring-boot-starter-actuator` | 应用监控和健康检查 |

### 3.2 自动配置做了什么？

以 `spring-boot-starter-web` 为例：

```
Spring Boot 启动时：
1. 发现 classpath 上有 Tomcat、Spring MVC 的类
2. 自动创建并配置内嵌 Tomcat（端口 8080）
3. 自动注册 DispatcherServlet
4. 自动配置 Jackson 做 JSON 序列化
5. 自动配置默认的错误处理页面

你什么都不用配，启动就能接受 HTTP 请求
```

自动配置的核心逻辑是 `@ConditionalOnXxx`：

```java
// Spring Boot 内部的自动配置类（简化版）
@Configuration
@ConditionalOnClass(DataSource.class)                    // classpath 上有 DataSource 类才生效
@ConditionalOnProperty(name = "spring.datasource.url")   // 配置了数据源 URL 才生效
public class DataSourceAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean(DataSource.class)          // 用户没有自己定义 DataSource 才创建默认的
    public DataSource dataSource(DataSourceProperties props) {
        return createDataSource(props);
    }
}

// 规则：自动配置总是可以被你的手动配置覆盖
// 你自己定义了 @Bean DataSource，自动配置就不生效
```

## 4. 配置文件

### 4.1 application.yml

```yaml
# 服务端口
server:
  port: 8080

# 数据源
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=UTC
    username: root
    password: 123456
    driver-class-name: com.mysql.cj.jdbc.Driver

  # JPA
  jpa:
    hibernate:
      ddl-auto: update         # 自动建表（开发用，生产环境禁止）
    show-sql: true             # 控制台打印 SQL
    open-in-view: false        # 关闭 OSIV，避免懒加载陷阱

# 自定义配置
app:
  name: MyApp
  api-key: abc123
  cache:
    ttl: 3600
    max-size: 1000

# 日志级别
logging:
  level:
    root: INFO
    com.example.myapp: DEBUG
    org.hibernate.SQL: DEBUG
```

### 4.2 多环境配置

```
src/main/resources/
├── application.yml          ← 公共配置
├── application-dev.yml      ← 开发环境
├── application-staging.yml  ← 预发布环境
└── application-prod.yml     ← 生产环境
```

```yaml
# application.yml 中指定激活哪个环境
spring:
  profiles:
    active: dev
```

```bash
# 或者启动时指定
java -jar app.jar --spring.profiles.active=prod
```

```yaml
# application-dev.yml
server:
  port: 8080
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb_dev

# application-prod.yml
server:
  port: 80
spring:
  datasource:
    url: jdbc:mysql://prod-db:3306/mydb_prod
```

### 4.3 读取自定义配置

前面看到的 `${server.port}`、`${spring.datasource.url}` 都是 Spring Boot 内置的配置项。实际开发中经常需要在 `application.yml` 里自定义配置，再在代码里读取：

```yaml
# application.yml
app:
  name: mini-ssp
  api-key: secret-123
  cache:
    ttl: 600
    max-size: 1000
```

**方式 1：`@Value` 逐个读取**

适合读取少量、独立的配置项：

```java
@Service
public class MyService {

    @Value("${app.name}")
    private String appName;          // 读取 app.name → "mini-ssp"

    @Value("${app.api-key:default-key}")
    private String apiKey;           // 读取 app.api-key，冒号后是默认值（key不存在时使用）
}
```

**方式 2：`@ConfigurationProperties` 批量绑定（推荐）**

当一组配置项有共同前缀（比如 `app.cache.*`）时，批量绑定到一个类，比写一堆 `@Value` 更清晰：

```java
@ConfigurationProperties(prefix = "app.cache")  // 指定前缀
@Component                                       // 注册为 Bean，才能被注入
public class CacheProperties {
    private int ttl;       // 自动绑定 app.cache.ttl → 600
    private int maxSize;   // 自动绑定 app.cache.max-size → 1000（kebab-case 自动转驼峰）

    // getter / setter（必须有，Spring 通过 setter 注入值）
    public int getTtl() { return ttl; }
    public void setTtl(int ttl) { this.ttl = ttl; }
    public int getMaxSize() { return maxSize; }
    public void setMaxSize(int maxSize) { this.maxSize = maxSize; }
}
```

绑定完成后，像普通 Bean 一样注入使用：

```java
@Service
public class CacheService {
    private final CacheProperties props;

    public CacheService(CacheProperties props) {
        this.props = props;
    }

    public void example() {
        props.getTtl();      // 600
        props.getMaxSize();  // 1000
    }
}
```

**两种方式怎么选**：单个、零散的配置用 `@Value`；一组相关配置（比如某个模块的所有参数）用 `@ConfigurationProperties`，改动配置时只需改 YAML，不用动代码。

## 5. 构建 REST 服务

### 5.1 分层架构

```text
Controller（接收请求、参数校验）
    ↓
Service（业务逻辑）
    ↓
Mapper / Repository（数据访问）
    ↓
Database
```

这一层的命名取决于用的持久化框架：

| 框架 | 命名 | 写法 |
|------|------|------|
| MyBatis / MyBatis-Plus | Mapper | `interface UserMapper extends BaseMapper<User>` |
| Spring Data JPA | Repository | `interface UserRepository extends JpaRepository<User, Long>` |

两者职责完全一样——只负责数据库读写，不写业务逻辑。本系列后续示例统一用 MyBatis-Plus 的 Mapper。

### 5.2 实体类（Entity）

**为什么需要实体类？**

数据库里的一张表，对应 Java 代码里的一个类——这个类就是 Entity。每一行数据对应一个 Entity 对象，每一列对应对象的一个字段。MyBatis-Plus 通过这个映射关系，把"操作数据库"变成"操作 Java 对象"。

```sql
-- 数据库表
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    user_email VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

```java
@Data                              // Lombok：自动生成 getter/setter/toString
@TableName("users")                // 对应的表名，命名一致时可省略
public class User {

    @TableId(type = IdType.AUTO)   // 主键，AUTO 表示数据库自增
    private Long id;

    private String name;           // 自动映射 name 列

    @TableField("user_email")      // 列名是 user_email，和字段名不一致，需显式指定
    private String email;

    private LocalDateTime createdAt;  // 自动映射 created_at 列（驼峰转下划线）
}
```

逐个解释：

**`@Data`（Lombok）**

不加这个注解，就要手写 getter、setter、构造方法、`toString()`，一个字段对应好几行代码。`@Data` 一行注解自动生成全部：

```java
// 不用 Lombok，要手写
public Long getId() { return id; }
public String getName() { return name; }
public void setName(String name) { this.name = name; }
// ... 每个字段都要写一遍

// 用 @Data，一行搞定，效果完全一样
@Data
public class User { ... }
```

实体类、DTO、VO 都建议加 `@Data`，这是 Spring Boot 项目里最常见的注解之一。

**`@TableName("users")`**

告诉 MyBatis-Plus 这个类对应数据库的哪张表。如果类名是 `User`，表名是 `user`（驼峰转小写下划线后一致），可以省略这个注解，MyBatis-Plus 会自动推断。表名不一致时（比如类名 `User` 但表名 `users`）必须显式指定。

**`@TableId(type = IdType.AUTO)`**

标记主键字段。`IdType.AUTO` 表示主键由数据库自增生成（对应 SQL 里的 `AUTO_INCREMENT`），插入时不需要自己赋值 `id`，数据库会自动分配。

```java
User user = new User();
user.setName("Alice");
user.setEmail("alice@example.com");
// 不设置 id，插入后 MyBatis-Plus 会自动把数据库生成的 id 填回 user.id
userMapper.insert(user);
System.out.println(user.getId());  // 数据库自动生成的 id，比如 1
```

**字段名自动映射，不一致时用 `@TableField`**

数据库列名是下划线命名（`created_at`），Java 字段是驼峰命名（`createdAt`）。配置 `map-underscore-to-camel-case: true`（Spring Boot 默认开启）后，MyBatis-Plus 自动完成两种命名风格的转换，不需要额外配置。

但如果字段名按驼峰转下划线后和列名还是不一致（比如历史原因导致命名不规则），自动转换规则套不上，需要 `@TableField` 显式指定：

| 情况 | 是否需要注解 |
|------|------------|
| `email` ↔ `email` | 不需要，名字相同 |
| `createdAt` ↔ `created_at` | 不需要，驼峰自动转下划线 |
| `email` ↔ `user_email` | 需要 `@TableField("user_email")`，自动转换规则套不上 |

`@TableName`、`@TableId`、`@TableField` 是同一套思路：默认按命名规则自动映射，命名不一致时用注解显式指定。

### 5.3 数据访问层（Mapper）

```java
@Mapper
public interface UserMapper extends BaseMapper<User> {
    // BaseMapper 已经提供了常用的增删改查方法：
    // insert(), deleteById(), updateById(), selectById(),
    // selectList(wrapper), selectOne(wrapper), selectPage(page, wrapper) ...

    // 复杂 SQL（多表 join、聚合统计）才需要写 XML，
    // 简单查询用 LambdaQueryWrapper 拼条件即可，不用写 SQL
}
```

`BaseMapper<User>` 是 MyBatis-Plus 提供的通用接口，继承它就自动获得一整套基础方法，绝大多数 CRUD 不需要再写一行 SQL：

```java
// 增
User user = new User();
user.setName("Alice");
user.setEmail("alice@example.com");
userMapper.insert(user);

// 查（按主键）
User user = userMapper.selectById(1L);

// 改（按主键）
user.setName("Bob");
userMapper.updateById(user);

// 删（按主键）
userMapper.deleteById(1L);

// 条件查询（用 LambdaQueryWrapper 拼 WHERE，避免手写字段名字符串）
User user = userMapper.selectOne(
    new LambdaQueryWrapper<User>().eq(User::getEmail, "alice@example.com")
);

List<User> users = userMapper.selectList(
    new LambdaQueryWrapper<User>().like(User::getName, "Ali")
);

// 分页查询
Page<User> page = userMapper.selectPage(
    new Page<>(1, 10),  // 第1页，每页10条
    new LambdaQueryWrapper<User>().orderByDesc(User::getCreatedAt)
);
```

`LambdaQueryWrapper` 的具体语法（`.eq`、`.like`、`.in`、`.orderByDesc` 等）和 XML 写法，会在 **下一篇 MyBatis** 详细展开。

### 5.4 业务层（Service）

Service 调用 Mapper 完成业务逻辑，用"构造方法注入 + final 字段"的推荐写法：

```java
@Service
@RequiredArgsConstructor   // Lombok：为所有 final 字段生成构造方法
public class UserService {

    private final UserMapper userMapper;

    public List<User> listAll() {
        return userMapper.selectList(null);  // 条件传 null 表示查全部
    }

    public User getById(Long id) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BizException("User not found: " + id);
        }
        return user;
    }
}
```

#### 依赖注入：构造方法注入 vs 字段注入

上面用的是**构造方法注入**，还有一种更常见但不推荐的写法——**字段注入**：

```java
// 字段注入（不推荐）
@Service
public class UserService {
    @Autowired
    private UserMapper userMapper;
}

// 构造方法注入（推荐）
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserMapper userMapper;
}
```

`@RequiredArgsConstructor` 自动生成一个包含所有 `final` 字段的构造方法。Spring 启动时识别到这个构造方法，自动把 `UserMapper` 的 Bean 传进来。等价于手写：

```java
public UserService(UserMapper userMapper) {
    this.userMapper = userMapper;
}
```

两种方式对比：

| | 字段注入 `@Autowired` | 构造方法注入 |
|---|---|---|
| 字段是否 `final` | 不能是 `final` | 可以是 `final`，更安全 |
| 单元测试 | 必须用 Spring 容器或反射设值 | `new UserService(mockMapper)` 直接传 mock |
| 依赖关系是否清晰 | 不清晰，运行时才知道依赖了什么 | 构造方法签名一目了然 |
| 循环依赖 | 编译期不报错，运行时才发现 | 编译期就会报错，能更早发现问题 |

**底层都是反射**：不管哪种方式，Spring 容器启动时都是通过反射创建 Bean、设置字段或调用构造方法（前面 Spring 容器那一节讲过）。区别只是注入的时机和方式，字段注入是创建对象后用 `field.set()` 强行赋值（即使是 private），构造方法注入是 `newInstance(参数)` 时一次性传入。

实际开发中**优先用构造方法注入**，`@RequiredArgsConstructor` 让这种写法和字段注入一样简洁，没有理由不用。

---

**新增、修改、删除**：

```java
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserMapper userMapper;

    @Transactional
    public User create(String name, String email) {
        // 业务校验：email 唯一
        Long count = userMapper.selectCount(
            new LambdaQueryWrapper<User>().eq(User::getEmail, email)
        );
        if (count > 0) {
            throw new BizException("Email already exists: " + email);
        }

        User user = new User();
        user.setName(name);
        user.setEmail(email);
        userMapper.insert(user);   // insert 后 user.id 会被自动填充
        return user;
    }

    @Transactional
    public User update(Long id, String name, String email) {
        User user = getById(id);   // 复用上面的方法，查不到会抛异常
        user.setName(name);
        user.setEmail(email);
        userMapper.updateById(user);
        return user;
    }

    @Transactional
    public void delete(Long id) {
        getById(id);  // 先确认存在，不存在会抛异常
        userMapper.deleteById(id);
    }
}
```

#### `@Transactional` 的实现机制：动态代理

`@Transactional` 标注在写操作的方法上，保证方法内的多个数据库操作是一个整体——全部成功才提交，任意一步失败就全部回滚。比如 `create` 里"查重复 + 插入"是两步，加了 `@Transactional` 后这两步在数据库层面是原子的。

这个注解本身**什么都不做**——和之前注解篇讲过的一样，注解只是标记，真正的逻辑由别的代码读取并执行。`@Transactional` 的执行者就是**动态代理**：

```
你写的代码：
userService.create("Alice", "alice@example.com")

实际发生的：
Spring 在启动时给 UserService 生成一个代理对象
你拿到的 userService 其实是代理对象，不是真实的 UserService

调用 create() 时：
代理对象.create()
  → 检测到目标方法有 @Transactional
  → 开启事务（connection.setAutoCommit(false)）
  → 调用真实对象.create()（你写的业务逻辑）
      → 查重复
      → insert
  → 没有异常 → 提交事务（connection.commit()）
  → 有异常   → 回滚事务（connection.rollback()）
```

对照前面"动态代理"那一节的结构：`InvocationHandler.invoke()` 里，前置逻辑是"开启事务"，`method.invoke(target, args)` 是真正执行业务代码，后置逻辑是"提交或回滚"。`@Transactional` 就是 Spring 内置的一个 `InvocationHandler`。

**这也解释了一个常见的坑**：类内部方法互相调用时事务不生效——

```java
@Service
public class UserService {

    public void batchCreate(List<User> users) {
        for (User user : users) {
            this.createOne(user);  // this 是真实对象，不经过代理，事务不生效！
        }
    }

    @Transactional
    public void createOne(User user) {
        userMapper.insert(user);
    }
}
```

原因和之前讲的一样：`this.createOne()` 直接调用了真实对象的方法，没有经过那个负责开启/提交事务的代理对象，`@Transactional` 的拦截逻辑根本没被触发。

### 5.5 控制层（Controller）

Controller 是后端和前端之间的"门面"——负责接收 HTTP 请求、解析参数、调用 Service、把结果包装成统一格式返回。它不写业务逻辑，业务逻辑全部丢给 Service。

#### 类级别注解

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;
}
```

| 注解 | 作用 |
|------|------|
| `@RestController` | 标记这是一个 Controller，并且方法返回值自动转成 JSON（等价于 `@Controller + @ResponseBody`） |
| `@RequestMapping("/api/users")` | 这个类下所有接口的统一路径前缀，下面的方法只需要写后缀 |

加了 `@RequestMapping("/api/users")` 后，`@GetMapping("/{id}")` 实际对应的完整路径是 `/api/users/{id}`。

#### HTTP 方法注解

REST 风格用不同的 HTTP 方法表示不同操作，Spring 提供对应的注解：

| 注解 | HTTP 方法 | 用途 | 示例路径 |
|------|----------|------|---------|
| `@GetMapping` | GET | 查询 | `GET /api/users` |
| `@PostMapping` | POST | 新增 | `POST /api/users` |
| `@PutMapping` | PUT | 修改（整体替换） | `PUT /api/users/1` |
| `@DeleteMapping` | DELETE | 删除 | `DELETE /api/users/1` |

```java
@GetMapping
public ApiResponse<List<User>> list() {
    return ApiResponse.success(userService.listAll());
}

@PostMapping
public ApiResponse<User> create(@RequestBody @Valid CreateUserRequest req) {
    return ApiResponse.success(userService.create(req.getName(), req.getEmail()));
}
```

#### 三种取参数的方式

这是最容易混淆的部分，三者取值的位置完全不同：

| 注解 | 从哪取值 | 示例 |
|------|---------|------|
| `@PathVariable` | URL 路径的一部分 | `/api/users/1` 中的 `1` |
| `@RequestParam` | URL 的查询字符串（`?` 后面） | `/api/users?page=1` 中的 `page=1` |
| `@RequestBody` | HTTP 请求体（JSON） | POST/PUT 请求中携带的 JSON 数据 |

```java
// @PathVariable：路径变量，路径里的 {id} 对应方法参数
// GET /api/users/1 → id = 1
@GetMapping("/{id}")
public ApiResponse<User> getById(@PathVariable Long id) {
    return ApiResponse.success(userService.getById(id));
}

// @RequestParam：URL 查询参数
// GET /api/users/list?page=1&pageSize=10 → page=1, pageSize=10
@GetMapping("/list")
public ApiResponse<List<User>> listByPage(
        @RequestParam int page,
        @RequestParam(defaultValue = "10") int pageSize) {
    return ApiResponse.success(userService.listByPage(page, pageSize));
}

// @RequestBody：请求体中的 JSON，自动转成 Java 对象
// POST /api/users  body: {"name": "Alice", "email": "alice@example.com"}
@PostMapping
public ApiResponse<User> create(@RequestBody @Valid CreateUserRequest req) {
    return ApiResponse.success(userService.create(req.getName(), req.getEmail()));
}
```

`@RequestParam(defaultValue = "10")` 表示这个参数可选，不传时用默认值；没写 `defaultValue` 则该参数必填，不传会返回 400。

`@Valid` 配合 `@RequestBody` 使用，触发 DTO 上的校验注解（`@NotBlank`、`@Email` 等），校验失败时 Spring 自动抛异常，由全局异常处理器统一处理。

#### 完整示例

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    // GET /api/users
    @GetMapping
    public ApiResponse<List<User>> list() {
        return ApiResponse.success(userService.listAll());
    }

    // GET /api/users/1
    @GetMapping("/{id}")
    public ApiResponse<User> getById(@PathVariable Long id) {
        return ApiResponse.success(userService.getById(id));
    }

    // POST /api/users
    @PostMapping
    public ApiResponse<User> create(@RequestBody @Valid CreateUserRequest req) {
        return ApiResponse.success(userService.create(req.getName(), req.getEmail()));
    }

    // PUT /api/users/1
    @PutMapping("/{id}")
    public ApiResponse<User> update(@PathVariable Long id, @RequestBody @Valid UpdateUserRequest req) {
        return ApiResponse.success(userService.update(id, req.getName(), req.getEmail()));
    }

    // DELETE /api/users/1
    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        userService.delete(id);
        return ApiResponse.success(null);
    }
}
```

#### 统一响应格式 ApiResponse

所有接口都返回 `ApiResponse<T>`，不管业务上返回什么类型（`User`、`List<User>`、`Void`），前端拿到的 JSON 结构始终一致：

```json
{
    "code": 0,
    "message": "success",
    "data": { "id": 1, "name": "Alice", "email": "alice@example.com" }
}
```

```java
@Data
public class ApiResponse<T> {
    private int code;
    private String message;
    private T data;

    public static <T> ApiResponse<T> success(T data) {
        ApiResponse<T> response = new ApiResponse<>();
        response.code = 0;
        response.message = "success";
        response.data = data;
        return response;
    }
}
```

前端不用针对每个接口写不同的解析逻辑——永远先看 `code`，再取 `data`。

### 5.6 请求对象（DTO）

DTO 是前端传给后端的参数。和 Entity（对应数据库表）不同，DTO 只是"请求参数的载体"，不直接存数据库，所以可以加各种校验注解，限制前端传来的数据必须符合什么格式。

```java
@Data
public class CreateUserRequest {

    @NotBlank(message = "name 不能为空")
    @Size(max = 50, message = "name 长度不能超过 50")
    private String name;

    @NotBlank(message = "email 不能为空")
    @Email(message = "email 格式不正确")
    private String email;
}
```

加了 `@Data`（Lombok）后不需要再手写 getter/setter，和 5.2 节的 Entity 是同一个套路。

#### `@NotBlank` 到底检查什么

```java
@NotBlank
private String name;
```

`@NotBlank` 检查三种情况，三种都算"空"：

```java
name = null;       // ❌ 不通过：null
name = "";         // ❌ 不通过：空字符串
name = "   ";      // ❌ 不通过：纯空格
name = "Alice";    // ✅ 通过
name = " Alice ";  // ✅ 通过（前后空格不影响，只要去除空格后非空）
```

和它相近的还有 `@NotNull` 和 `@NotEmpty`，三者区别：

| 注解 | null | `""` | `"   "` | 适用类型 |
|------|------|------|---------|---------|
| `@NotNull` | ❌ | ✅ | ✅ | 任意类型 |
| `@NotEmpty` | ❌ | ❌ | ✅ | String、集合、数组 |
| `@NotBlank` | ❌ | ❌ | ❌ | 仅 String |

简单记：`@NotNull` 只挡 `null`；`@NotEmpty` 再挡空字符串/空集合；`@NotBlank` 再挡纯空格字符串。校验用户输入的字符串字段，基本都用 `@NotBlank`。

#### `@Valid` 是怎么触发校验的

```java
@PostMapping
public ApiResponse<User> create(@RequestBody @Valid CreateUserRequest req) {
    return ApiResponse.success(userService.create(req.getName(), req.getEmail()));
}
```

`@RequestBody` 只负责把请求体的 JSON 转成 `CreateUserRequest` 对象，**不会**自动检查字段是否合法。`@Valid` 才是触发校验的开关——Spring 在调用 `create` 方法之前，先检查 `req` 对象上所有的校验注解（`@NotBlank`、`@Email` 等）是否都满足。

```
请求进来 → @RequestBody 把 JSON 转成 CreateUserRequest 对象
        → @Valid 检查这个对象上的所有校验注解
            → 全部通过 → 执行 create 方法体
            → 有不通过 → 抛出 MethodArgumentNotValidException，方法体根本不会执行
```

所以两者缺一不可：没有 `@RequestBody`，参数收不到 JSON；没有 `@Valid`，收到了但不会校验，非法数据会一路传到 Service 层甚至数据库。

```java
@Data
public class UpdateUserRequest {

    @NotBlank
    @Size(max = 50)
    private String name;

    @NotBlank
    @Email
    private String email;
}
```

**校验注解速查**：

| 注解 | 作用 |
|------|------|
| `@NotBlank` | 字符串不能为 `null`、`""`、纯空格 |
| `@NotNull` | 不能为 `null`（不检查内部字段） |
| `@NotEmpty` | 不能为 `null` 或空（字符串/集合） |
| `@Size(max=50)` | 长度/大小限制 |
| `@Email` | 必须是合法邮箱格式 |

校验失败时，`@Valid` 会让 Spring 自动抛出 `MethodArgumentNotValidException`，由全局异常处理器统一转换成 `ApiResponse`（返回码 400），Controller 方法体里不需要写任何判断逻辑。

## 6. 统一异常处理

### 6.1 为什么需要全局异常处理

不加处理时，Service 抛出异常会一直往上传，最终 Spring 返回一个**默认的错误页面/JSON**，格式和你定义的 `ApiResponse` 完全不一样：

```json
{
    "timestamp": "2026-06-17T14:30:00.123+00:00",
    "status": 500,
    "error": "Internal Server Error",
    "path": "/api/users/999"
}
```

前端拿到的成功响应是 `{code, message, data}`，但异常时是上面这种格式——前端要写两套解析逻辑，非常麻烦。

**全局异常处理的目的**：不管 Service 抛出什么异常，统一拦截、统一转换成 `ApiResponse` 格式返回，前端永远只需要处理一种结构。

```
没有全局异常处理：
Service 抛异常 → Spring 默认处理 → 格式混乱的错误响应

有全局异常处理：
Service 抛异常 → GlobalExceptionHandler 拦截 → 转成 ApiResponse(code, message, null)
```

### 6.2 自定义业务异常：BizException

业务逻辑中"正常的错误情况"（比如"用户不存在"、"邮箱已被注册"），用自定义异常表示：

```java
public class BizException extends RuntimeException {
    public BizException(String message) {
        super(message);
    }
}
```

继承 `RuntimeException`（而不是 `Exception`）是关键——`RuntimeException` 是 unchecked 异常，`throw` 时不需要在方法签名上写 `throws`，调用方也不需要 try-catch：

```java
// 继承 RuntimeException：直接 throw，没有任何额外语法
public User getById(Long id) {
    User user = userMapper.selectById(id);
    if (user == null) {
        throw new BizException("User not found: " + id);
    }
    return user;
}

// 如果继承 Exception（checked 异常），每个调用方都要处理，非常繁琐
public User getById(Long id) throws BizException { ... }  // 方法签名要加 throws
// 调用方：
try {
    User user = userService.getById(1L);
} catch (BizException e) { ... }  // 被迫写 try-catch
```

Service 层正常抛出 `BizException` 即可，不用关心谁来处理它。

### 6.3 全局捕获：@RestControllerAdvice

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BizException.class)
    public ApiResponse<Void> handleBizException(BizException e) {
        return ApiResponse.error(400, e.getMessage());
    }
}
```

`@RestControllerAdvice` 标记这个类是"全局的"——不管异常是从哪个 Controller 的哪个方法抛出来的，只要类型匹配，都会被这里的方法捕获。

`@ExceptionHandler(BizException.class)` 表示"这个方法专门处理 `BizException` 类型的异常"。一旦 Service 里 `throw new BizException(...)`，不管调用链多深，最终都会被这个方法接住。

### 6.4 检测到异常后做什么

拿到异常后，做的事情就是**把异常信息转换成 `ApiResponse`**，按异常类型决定 `code` 和 `message`：

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    // 业务异常：Service 主动抛出，表示"正常的业务错误"
    @ExceptionHandler(BizException.class)
    public ApiResponse<Void> handleBizException(BizException e) {
        return ApiResponse.error(400, e.getMessage());
    }

    // 参数校验失败：@Valid 检查不通过时 Spring 自动抛出
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ApiResponse<Void> handleValidation(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
            .map(err -> err.getField() + ": " + err.getDefaultMessage())
            .collect(Collectors.joining("; "));
        return ApiResponse.error(400, message);
    }

    // 兜底：所有没被上面捕获的异常（程序 bug、空指针等未预期错误）
    @ExceptionHandler(Exception.class)
    public ApiResponse<Void> handleUnexpected(Exception e) {
        log.error("Unexpected error", e);  // 服务器日志记录详细堆栈，方便排查
        return ApiResponse.error(500, "Internal Server Error");  // 给前端的信息不暴露内部细节
    }
}
```

三类异常对应三种"检测到后做什么"：

| 异常类型 | 触发场景 | 处理方式 |
|---------|---------|---------|
| `BizException` | Service 主动 `throw`，正常业务错误 | 直接把 `e.getMessage()` 返回给前端 |
| `MethodArgumentNotValidException` | `@Valid` 校验失败 | 提取所有字段的错误信息，拼成一句话 |
| `Exception`（兜底） | 未预期的程序错误 | 服务器记录详细日志，但**不**把异常细节暴露给前端，统一返回"Internal Server Error" |

最后一条很重要——兜底异常如果直接把 `e.getMessage()` 或堆栈信息返回给前端，可能暴露数据库结构、内部路径等敏感信息，安全风险很高。

### 6.5 响应示例

参数校验失败时：

```json
{
    "code": 400,
    "message": "name: name 不能为空; email: email 格式不正确",
    "data": null
}
```

业务异常时：

```json
{
    "code": 400,
    "message": "Email already exists: alice@example.com",
    "data": null
}
```

无论哪种异常，响应结构都和正常成功时的 `ApiResponse` 一致，前端用同一套逻辑处理。

## 7. 常用注解速查

### 7.1 请求映射

| 注解 | 说明 |
|------|------|
| `@RestController` | `@Controller` + `@ResponseBody`，方法返回值自动序列化为 JSON |
| `@RequestMapping("/api")` | 类/方法级别的路径前缀 |
| `@GetMapping` | GET 请求 |
| `@PostMapping` | POST 请求 |
| `@PutMapping` | PUT 请求 |
| `@DeleteMapping` | DELETE 请求 |
| `@PatchMapping` | PATCH 请求 |

### 7.2 参数绑定

| 注解 | 取值位置 | 示例 |
|------|---------|------|
| `@PathVariable` | URL 路径 | `/users/{id}` 中的 `id` |
| `@RequestParam` | URL 查询字符串 | `?name=xxx&page=1` |
| `@RequestBody` | 请求体 JSON | POST/PUT 携带的数据 |
| `@RequestHeader` | HTTP 请求头 | `Authorization: Bearer xxx` |

```java
// 路径变量
@GetMapping("/users/{id}")
public ApiResponse<User> get(@PathVariable Long id) { ... }

// 查询参数 ?name=xxx&page=1
@GetMapping("/users")
public ApiResponse<List<User>> search(
    @RequestParam String name,
    @RequestParam(defaultValue = "0") int page,   // 不传时用默认值
    @RequestParam(required = false) String sort   // 可选参数
) { ... }

// 请求体（JSON → Java 对象），配合 @Valid 触发校验
@PostMapping("/users")
public ApiResponse<User> create(@RequestBody @Valid CreateUserRequest req) { ... }

// 请求头
@GetMapping("/info")
public ApiResponse<String> info(@RequestHeader("Authorization") String token) { ... }
```

### 7.3 参数校验

需要引入 `spring-boot-starter-validation` 依赖。

| 注解 | 作用 | 适用类型 |
|------|------|---------|
| `@NotNull` | 不能为 `null` | 任意类型 |
| `@NotEmpty` | 不能为 `null` 或空 | String / 集合 / 数组 |
| `@NotBlank` | 不能为 `null`、空字符串、纯空格 | String |
| `@Size(min=1, max=50)` | 长度/大小范围 | String / 集合 / 数组 |
| `@Min(0)` / `@Max(100)` | 数值范围 | 数字类型 |
| `@Email` | 邮箱格式 | String |
| `@Pattern(regexp="")` | 正则匹配 | String |
| `@Past` / `@Future` | 日期在过去/未来 | 日期类型 |

```java
@Data
public class CreateUserRequest {
    @NotBlank
    @Size(max = 50)
    private String name;

    @NotBlank
    @Email
    private String email;
}

// Controller 方法参数上加 @Valid 触发校验
public ApiResponse<User> create(@RequestBody @Valid CreateUserRequest req) { ... }
```

**嵌套对象校验**：`@Valid` 默认只校验当前对象的字段，不会递归检查嵌套对象内部的注解。需要嵌套校验时，在嵌套字段上也加 `@Valid`：

```java
@Data
public class OrderRequest {
    @Valid              // 不加这个，items 里每个 ItemRequest 内部的校验注解不会生效
    @NotEmpty
    private List<ItemRequest> items;
}

@Data
public class ItemRequest {
    @NotBlank
    private String productId;

    @Min(1)
    private int quantity;
}
```

## 8. 打包与部署

```bash
# Maven
mvn clean package
java -jar target/my-app-1.0.0.jar

# Gradle
./gradlew bootJar
java -jar build/libs/my-app-1.0.0.jar

# 指定端口和环境
java -jar app.jar --server.port=9090 --spring.profiles.active=prod

# Docker（典型 Dockerfile）
FROM eclipse-temurin:17-jre
COPY build/libs/my-app-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## 9. Spring Boot 开发常用技巧

### 9.1 热重启（DevTools）

```kotlin
dependencies {
    developmentOnly("org.springframework.boot:spring-boot-devtools")
}
```

代码修改后自动重启应用，开发时省去手动重启的时间。

### 9.2 Actuator 健康检查

```kotlin
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-actuator")
}
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
```

```bash
curl http://localhost:8080/actuator/health
# {"status":"UP"}
```

### 9.3 日志配置

```yaml
logging:
  level:
    root: INFO
    com.example: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: logs/app.log
```

```java
// 使用 SLF4J（Spring Boot 默认）
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class UserService {
    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    public User getById(Long id) {
        log.debug("查询用户: id={}", id);     // {} 占位符，避免字符串拼接
        User user = repo.findById(id).orElse(null);
        if (user == null) {
            log.warn("用户不存在: id={}", id);
        }
        return user;
    }
}
```

## 10. 小结

| 主题 | 关键要点 |
|------|---------|
| Spring Boot 定位 | Spring 的脚手架，自动配置 + 内嵌服务器 + Starter 依赖 |
| 自动配置原理 | @ConditionalOnXxx 按条件注册 Bean，用户配置优先于自动配置 |
| 配置文件 | application.yml，多环境用 application-{profile}.yml |
| 读取配置 | @Value 逐个、@ConfigurationProperties 批量绑定 |
| REST 分层 | Controller → Service → Repository → Database |
| Controller 注解 | @RestController、@GetMapping、@PathVariable、@RequestBody |
| 参数校验 | @Valid + @NotBlank / @Email / @Size 等，全局异常处理器捕获 |
| 异常处理 | @RestControllerAdvice + @ExceptionHandler 统一格式 |
| 打包部署 | `java -jar app.jar`，内嵌 Tomcat 无需外部容器 |

---

> **下一篇预告**：MyBatis 数据访问——SQL 映射、动态 SQL 与 MyBatis-Plus

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
