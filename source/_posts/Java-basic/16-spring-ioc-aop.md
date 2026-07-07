---
title: 'Java基础(16) | Spring 核心思想：IoC 与 AOP 到底解决了什么问题'
date: 2026-05-16
abbrlink: 16tags:
  - Java
  - Spring
  - IoC
  - AOP
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

Spring 是 Java 后端开发的事实标准，但很多人只会用 `@Autowired`、`@Service` 这些注解，却说不清楚 Spring 到底在干什么。这篇文章不讲 API 使用细节，而是把两个核心问题讲透：**IoC（控制反转）解决了什么问题？AOP（面向切面编程）解决了什么问题？** 理解了这两个，Spring 的一切设计都顺理成章。

<!-- more -->

## 1. 没有 Spring 的世界

先看一个没有 Spring 的典型 Java 项目，感受痛点：

```java
public class UserController {
    public void handleRequest() {
        // 手动创建依赖
        UserService userService = new UserService();
        userService.getUser("001");
    }
}

public class UserService {
    public User getUser(String id) {
        // 手动创建依赖
        UserRepository repo = new UserRepository();
        // 手动创建依赖
        CacheService cache = new CacheService();
        // 手动创建依赖
        LogService log = new LogService();

        log.info("查询用户: " + id);
        User user = cache.get(id);
        if (user == null) {
            user = repo.findById(id);
            cache.put(id, user);
        }
        return user;
    }
}

public class UserRepository {
    public User findById(String id) {
        // 手动创建依赖
        DataSource ds = new DataSource("jdbc:mysql://localhost:3306/db", "root", "123456");
        Connection conn = ds.getConnection();
        // ...
    }
}
```

问题一目了然：

```
1. 硬编码依赖：每个类自己 new 依赖，耦合死了
   → 想把 MySQL 换成 PostgreSQL？改 UserRepository
   → 想把缓存从本地换成 Redis？改 UserService
   → 每换一个实现就要改调用方代码

2. 生命周期混乱：DataSource 被反复创建
   → 数据库连接池应该全局共享一个，不是每次 new

3. 测试困难：想单独测 UserService？
   → 它内部 new 了真实的 Repository、Cache、Log
   → 无法用 Mock 替换

4. 横切关注点散落：日志、事务、权限检查
   → 每个方法都要写一遍，到处重复
```

## 2. IoC：控制反转

### 2.1 什么是控制反转？

**"反转"的是"对象创建的控制权"。**

传统方式：对象自己创建（控制）自己的依赖。

```java
// 传统：UserService 自己控制依赖的创建
public class UserService {
    private UserRepository repo = new UserRepository();  // 我自己 new
}
```

IoC 方式：把创建权交给外部（Spring 容器），对象只声明"我需要什么"。

```java
// IoC：UserService 只声明依赖，由外部注入
public class UserService {
    private UserRepository repo;  // 我不管怎么创建，给我就行

    public UserService(UserRepository repo) {
        this.repo = repo;  // 外部传进来
    }
}
```

控制权从"对象内部"转移到了"外部容器"——这就是"反转"。

### 2.2 DI：依赖注入

DI（Dependency Injection）是 IoC 最主流的实现方式——**容器把依赖"注入"到对象中。** 日常说的 IoC 和 DI 基本可以画等号。

Spring 支持三种注入方式：

```java
// 方式 1：构造器注入（推荐）
@Service
public class UserService {
    private final UserRepository repo;
    private final CacheService cache;

    // Spring 看到构造方法的参数类型，自动从容器中找到对应的 Bean 注入
    // 只有一个构造方法时，@Autowired 可以省略
    public UserService(UserRepository repo, CacheService cache) {
        this.repo = repo;
        this.cache = cache;
    }
}

// 方式 2：字段注入（方便，但不推荐用于生产代码）
@Service
public class UserService {
    @Autowired
    private UserRepository repo;  // Spring 通过反射直接设置 private 字段
}

// 方式 3：Setter 注入（较少用）
@Service
public class UserService {
    private UserRepository repo;

    @Autowired
    public void setRepo(UserRepository repo) {
        this.repo = repo;
    }
}
```

**为什么推荐构造器注入？**

| | 构造器注入 | 字段注入 |
|--|----------|---------|
| 不可变性 | 字段可以是 `final` | 不能是 `final` |
| 必要依赖 | 编译器保证不为 null | 可能忘记注入导致 NPE |
| 测试友好 | 直接 new 传参即可测试 | 必须用反射或 Spring 容器 |
| 循环依赖 | 启动时立即报错（好事） | 可能隐藏循环依赖问题 |
### 2.3 Spring 容器（ApplicationContext）

![Spring ApplicationContext 工作原理](images/Java-basic/spring-container.png)

Spring 容器本质就是一个**大 Map**——key 是 Bean 的名字，value 是 Bean 的实例对象。

容器启动时做了三件事：

1. **扫描注解**：扫描所有带 `@Component` / `@Service` / `@Repository` / `@Controller` 的类，这些类都会被容器管理
2. **创建对象**：通过反射（`clazz.newInstance()`）为每个类创建实例，这就是为什么前面要学反射
3. **注入依赖**：扫描每个 Bean 的字段，发现 `@Autowired` 就通过反射（`field.set(bean, 依赖对象)`）把对应的 Bean 塞进去

```java
// 你只需要写声明，不需要自己 new
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;  // 容器自动注入，不需要你写 = new UserRepository()
}

// 容器内部大致做了这些事（伪代码）：
Map<String, Object> container = new HashMap<>();

// 1. 反射创建所有 Bean
Object repo = UserRepository.class.newInstance();
Object service = UserService.class.newInstance();

// 2. 扫描 @Autowired 字段，注入依赖
Field f = UserService.class.getDeclaredField("userRepository");
f.setAccessible(true);
f.set(service, repo);  // 把 repo 塞进 service 的 userRepository 字段

// 3. 放入容器
container.put("userRepository", repo);
container.put("userService", service);
```
### 2.4 Bean 的注册方式

```java
// 方式 1：组件扫描 + 注解（最常用）
@Service        // 业务层
@Repository     // 数据访问层
@Controller     // 控制层
@Component      // 通用组件
// 以上四个功能完全一样，区别只是语义，方便分层

@Service
public class UserService { ... }

// 方式 2：@Bean 方法（适合注册第三方库的类）
@Configuration
public class AppConfig {
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        return mapper;
    }
}
```

### 2.5 Bean 的作用域

| 作用域 | 含义 | 使用场景 |
|--------|------|---------|
| `singleton`（默认） | 整个容器只有一个实例 | 绝大多数情况 |
| `prototype` | 每次获取都创建新实例 | 有状态的 Bean |
| `request` | 每个 HTTP 请求一个实例 | Web 应用 |
| `session` | 每个 HTTP Session 一个实例 | Web 应用 |

```java
@Service
@Scope("prototype")  // 每次注入都是新对象
public class TaskProcessor { ... }
```

99% 的 Bean 用默认的 `singleton` 就好。

### 2.6 Bean 的生命周期

```
实例化（new）
  → 属性注入（@Autowired）
  → @PostConstruct 方法
  → 就绪，可以使用
  → ...
  → @PreDestroy 方法
  → 销毁
```

```java
@Service
public class CacheService {
    @PostConstruct
    public void init() {
        // 容器创建完 Bean 并注入依赖后执行
        // 适合做初始化操作：加载缓存、建立连接
        System.out.println("CacheService 初始化完成");
    }

    @PreDestroy
    public void cleanup() {
        // 容器关闭前执行
        // 适合做清理操作：关闭连接、释放资源
        System.out.println("CacheService 清理资源");
    }
}
```

## 3. AOP：面向切面编程

### 3.1 问题：横切关注点

有些逻辑散布在大量方法中，和业务逻辑纠缠在一起：

```java
public class OrderService {
    public void createOrder(Order order) {
        long start = System.currentTimeMillis();           // 性能监控
        log.info("创建订单: {}", order.getId());             // 日志
        checkPermission();                                  // 权限检查
        TransactionManager.begin();                         // 事务
        try {
            // === 真正的业务逻辑只有这几行 ===
            validateOrder(order);
            orderRepo.save(order);
            inventoryService.deduct(order.getItems());
            // === 业务逻辑结束 ===
            TransactionManager.commit();                    // 事务
        } catch (Exception e) {
            TransactionManager.rollback();                  // 事务
            throw e;
        }
        log.info("订单创建完成，耗时: {}ms",
            System.currentTimeMillis() - start);            // 性能监控
    }

    // 其他每个方法都要写一遍日志、事务、权限检查...
}
```

日志、事务、权限检查、性能监控——这些叫**横切关注点**，它们跨越多个模块，和业务逻辑无关但又必须存在。AOP 的目标就是把它们从业务代码中剥离出来。

### 3.2 AOP 的核心概念

**用"高速公路收费站"来理解 AOP：**

你开车从 A 到 B，路上有收费站。你的目的是开车（业务逻辑），收费站是额外加的（切面逻辑）。你不需要改开车的方式，收费站自己装在那里。

```java
@Aspect
@Component
public class LogAspect {

    // 切点（Pointcut）：哪些路口装收费站？
    // 这里是 controller 包下的所有方法
    @Around("execution(* com.xxx.ad.controller..*(..))")
    
    // 通知（Advice）：收费站做什么事？
    // 这里是记录耗时
    public Object log(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = joinPoint.proceed();  // 放行，让车继续走（执行真实方法）
        log.info("耗时 {}ms", System.currentTimeMillis() - start);
        return result;
    }
}
```

| 概念 | 一句话 | 对应代码中的什么 |
|------|--------|----------------|
| **切面（Aspect）** | 这整个类 | `LogAspect` 这个类 |
| **切点（Pointcut）** | 在哪些方法上生效 | `execution(* com.oppo.ad.controller..*(..))` |
| **通知（Advice）** | 生效时执行什么逻辑 | `log()` 这个方法体 |
| **连接点（JoinPoint）** | 当前正在被拦截的那个方法 | `joinPoint`，可以拿到方法名、参数等信息 |
| **织入（Weaving）** | Spring 启动时自动把切面装上去 | 你不用写，Spring 自动做（底层就是动态代理） |

不用死记这些术语，实际写代码就两步：**定义切点（在哪生效）+ 写通知（做什么事）**。

### 3.3 五种通知类型

```java
@Aspect
@Component
public class LoggingAspect {

    // @Before：方法执行前
    @Before("execution(* com.example.service.*.*(..))")
    public void logBefore(JoinPoint jp) {
        log.info("[BEFORE] {}", jp.getSignature().getName());
    }

    // @After：方法执行后（无论成功失败）
    @After("execution(* com.example.service.*.*(..))")
    public void logAfter(JoinPoint jp) {
        log.info("[AFTER] {}", jp.getSignature().getName());
    }

    // @AfterReturning：方法正常返回后
    @AfterReturning(pointcut = "execution(* com.example.service.*.*(..))",
                    returning = "result")
    public void logReturn(JoinPoint jp, Object result) {
        log.info("[RETURN] {} → {}", jp.getSignature().getName(), result);
    }

    // @AfterThrowing：方法抛异常后
    @AfterThrowing(pointcut = "execution(* com.example.service.*.*(..))",
                   throwing = "ex")
    public void logException(JoinPoint jp, Exception ex) {
        log.error("[ERROR] {} → {}", jp.getSignature().getName(), ex.getMessage());
    }

    // @Around：环绕通知，最强大，可以控制是否执行目标方法
    @Around("execution(* com.example.service.*.*(..))")
    public Object logAround(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        log.info("[START] {}", pjp.getSignature().getName());

        Object result = pjp.proceed();  // 执行目标方法

        long cost = System.currentTimeMillis() - start;
        log.info("[END] {} 耗时: {}ms", pjp.getSignature().getName(), cost);
        return result;
    }
}
```

执行顺序：

```
@Around（前半段）
  → @Before
    → 目标方法执行
  → @AfterReturning（或 @AfterThrowing）
  → @After
→ @Around（后半段）
```

### 3.4 切点表达式

切点表达式定义"哪些方法被拦截"：

```java
// execution 表达式语法：
// execution(修饰符? 返回类型 包名.类名.方法名(参数类型) 异常?)

// 匹配 service 包下所有类的所有方法
@Pointcut("execution(* com.example.service.*.*(..))")

// 匹配所有 public 方法
@Pointcut("execution(public * *(..))")

// 匹配所有以 get 开头的方法
@Pointcut("execution(* com.example..*.get*(..))")

// 匹配特定参数类型
@Pointcut("execution(* com.example.service.UserService.getUser(String))")

// 基于注解的切点（更常用、更灵活）
@Pointcut("@annotation(com.example.annotation.LogExecution)")

// 匹配某个类上有特定注解的所有方法
@Pointcut("@within(org.springframework.stereotype.Service)")

// 组合切点
@Pointcut("execution(* com.example.service..*(..)) && !execution(* com.example.service.*.get*(..))")
```

### 3.5 自定义注解 + AOP：最优雅的用法

```java
// 1. 定义注解
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Timer {
    String value() default "";
}

// 2. 定义切面
@Aspect
@Component
public class TimerAspect {
    @Around("@annotation(timer)")
    public Object around(ProceedingJoinPoint pjp, Timer timer) throws Throwable {
        String name = timer.value().isEmpty()
            ? pjp.getSignature().getName()
            : timer.value();

        long start = System.currentTimeMillis();
        Object result = pjp.proceed();
        long cost = System.currentTimeMillis() - start;

        log.info("[Timer] {} 耗时: {}ms", name, cost);
        return result;
    }
}

// 3. 使用：在任何方法上贴一个注解就有计时功能
@Service
public class UserService {
    @Timer("查询用户")
    public User getUser(String id) {
        return repo.findById(id);
    }

    @Timer
    public List<User> listAll() {
        return repo.findAll();
    }
}
```

这就是 `@Transactional`、`@Cacheable`、`@Async` 等 Spring 注解的工作方式——注解做标记，AOP 切面读注解并执行逻辑。

### 3.6 AOP 的底层实现

在第 12 篇（注解与反射）中我们讲过动态代理，AOP 的底层就是它：

```
Spring 发现 UserService 上有 AOP 切面
  → 创建 UserService 的代理对象
  → 代理对象拦截方法调用
  → 执行 @Before → 调用真实方法 → 执行 @After
  → 返回结果

代理方式：
├── 目标类实现了接口 → JDK 动态代理
└── 目标类没有接口 → CGLIB 代理（生成子类）
    └── Spring Boot 2.0+ 默认使用 CGLIB
```

这也解释了一个常见陷阱——同一个类内部的方法调用，AOP 不生效：

```java
@Service
public class UserService {
    @Transactional
    public void createUser(User user) {
        repo.save(user);
    }

    public void batchCreate(List<User> users) {
        for (User u : users) {
            this.createUser(u);  // 内部调用走的是 this，不经过代理，@Transactional 不生效！
        }
    }
}

// 解决方案：
// 1. 把 createUser 移到另一个 Bean 中
// 2. 注入自身的代理（不推荐）
// 3. 使用 TransactionTemplate 手动控制事务
```

## 4. Spring 的注解体系速查

### 4.1 组件注册

| 注解 | 用途 |
|------|------|
| `@Component` | 通用组件 |
| `@Service` | 业务层 |
| `@Repository` | 数据访问层（额外提供数据库异常转译） |
| `@Controller` | Web 控制层 |
| `@Configuration` | 配置类（内部的 @Bean 方法注册 Bean） |
| `@Bean` | 在 @Configuration 中注册第三方类的实例 |

### 4.2 依赖注入

| 注解 | 用途 |
|------|------|
| `@Autowired` | 按类型注入（Spring 原生） |
| `@Qualifier("name")` | 配合 @Autowired，按名称指定注入哪个 Bean |
| `@Resource` | 按名称注入（JSR-250 标准） |
| `@Value("${key}")` | 注入配置文件中的值 |

```java
// 当同一个接口有多个实现时
public interface MessageSender {
    void send(String msg);
}

@Service("emailSender")
public class EmailSender implements MessageSender { ... }

@Service("smsSender")
public class SmsSender implements MessageSender { ... }

@Service
public class NotificationService {
    // 方式 1：@Qualifier 指定
    @Autowired
    @Qualifier("emailSender")
    private MessageSender sender;

    // 方式 2：参数名匹配（构造器注入时，参数名和 Bean 名一致就能自动匹配）
    public NotificationService(MessageSender emailSender) {
        this.sender = emailSender;
    }
}
```

### 4.3 配置相关

```java
// 读取 application.yml 中的配置
@Value("${server.port:8080}")     // 冒号后是默认值
private int port;

// 批量绑定配置
@ConfigurationProperties(prefix = "app.cache")
@Component
public class CacheConfig {
    private int ttl;
    private int maxSize;
    // getter/setter
}
```

```yaml
# application.yml
app:
  cache:
    ttl: 3600
    max-size: 1000
```

### 4.4 条件装配

```java
// 按条件决定是否注册 Bean
@Bean
@ConditionalOnProperty(name = "cache.enabled", havingValue = "true")
public CacheService cacheService() { ... }

@Bean
@ConditionalOnMissingBean(CacheService.class)  // 容器中没有 CacheService 时才注册
public CacheService defaultCacheService() { ... }

@Bean
@Profile("dev")  // 只在 dev 环境下注册
public DataSource devDataSource() { ... }
```

## 5. IoC + AOP 如何协同工作

用一张完整的流程图把所有概念串起来：

```
Spring 启动
  │
  ├── 扫描 @Component / @Service / @Repository / @Controller
  │   → 发现 UserService、UserRepository、LoggingAspect ...
  │
  ├── 创建 Bean 实例
  │   → new UserRepository()
  │   → new UserService(userRepository)   ← 依赖注入
  │   → new LoggingAspect()
  │
  ├── 发现 UserService 被 AOP 切面匹配
  │   → 创建 UserService 的 CGLIB 代理
  │   → 容器中存放的是代理对象，不是原始对象
  │
  ├── 调用 @PostConstruct 方法
  │
  └── 容器就绪
      │
      │  有请求进来
      ▼
      调用 userService.getUser("001")
        → 实际调用代理对象的 getUser
        → 代理执行 @Before 通知
        → 代理执行真实的 getUser 方法
        → 代理执行 @AfterReturning 通知
        → 返回结果
```

## 6. 小结

| 主题 | 关键要点 |
|------|---------|
| IoC 本质 | 把对象创建的控制权从类内部转移到外部容器 |
| DI | IoC 的实现方式——容器把依赖注入到对象中 |
| 注入方式 | 构造器注入（推荐）、字段注入、Setter 注入 |
| Bean 注册 | @Component 扫描（自己写的类）、@Bean 方法（第三方类） |
| Bean 作用域 | 默认 singleton，99% 场景够用 |
| Bean 生命周期 | 实例化 → 注入 → @PostConstruct → 使用 → @PreDestroy → 销毁 |
| AOP 本质 | 把横切关注点（日志/事务/权限）从业务代码中剥离 |
| 五种通知 | @Before、@After、@AfterReturning、@AfterThrowing、@Around |
| 切点表达式 | execution 匹配方法签名、@annotation 匹配注解 |
| AOP 底层 | 动态代理（JDK / CGLIB），内部调用不经过代理 |
| 自定义注解 + AOP | 最优雅的方式，也是 @Transactional 等注解的原理 |

---

> **下一篇预告**：Spring Boot 快速上手——自动配置原理与一个完整的 REST 服务

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
