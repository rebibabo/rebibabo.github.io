---
title: 'java-basics(19) | 设计模式：Java 中最常见的几种模式实战'
date: 2026-05-19
tags:
  - Java
  - 设计模式
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

设计模式不是用来"背"的，而是用来解决具体问题的。这篇文章不追求 23 种模式大全，只讲 Java 开发中**真正高频遇到的几种**——你在阅读 Spring 源码、写业务代码、做系统设计时一定会碰到它们。每种模式都从"没有它会怎样"讲起，再给出 Java 实现。

<!-- more -->

## 1. 单例模式（Singleton）

### 1.1 问题

某些对象在系统中应该只有一个实例——数据库连接池、配置管理器、线程池。如果随意 new，会浪费资源或导致状态不一致。

### 1.2 实现方式对比

```java
// 方式 1：饿汉式（最简单，推荐）
// 类加载时就创建，天然线程安全
public class Config {
    private static final Config INSTANCE = new Config();
    private Config() {}  // 私有构造方法，防止外部 new
    public static Config getInstance() { return INSTANCE; }
}

// 方式 2：懒汉式 + 双重检查锁
// 延迟到第一次使用时创建
public class Config {
    private static volatile Config instance;  // volatile 防止指令重排
    private Config() {}

    public static Config getInstance() {
        if (instance == null) {                // 第一次检查，避免每次加锁
            synchronized (Config.class) {
                if (instance == null) {        // 第二次检查，防止重复创建
                    instance = new Config();
                }
            }
        }
        return instance;
    }
}

// 方式 3：静态内部类
// 懒加载 + 线程安全 + 无锁
public class Config {
    private Config() {}

    private static class Holder {
        private static final Config INSTANCE = new Config();
        // 内部类在第一次被引用时才加载，JVM 保证线程安全
    }

    public static Config getInstance() { return Holder.INSTANCE; }
}

// 方式 4：枚举（Effective Java 推荐）
// 天然线程安全 + 防反射 + 防反序列化
public enum Config {
    INSTANCE;

    private final Map<String, String> settings = new HashMap<>();

    public String get(String key) { return settings.get(key); }
    public void set(String key, String value) { settings.put(key, value); }
}
// 使用：Config.INSTANCE.get("key")
```

### 1.3 在框架中的应用

```java
// Spring 的 Bean 默认就是单例
@Service  // 整个容器只有一个 UserService 实例
public class UserService { ... }

// Runtime
Runtime runtime = Runtime.getRuntime();  // 单例
```

## 2. 工厂模式（Factory）

### 2.1 问题

创建对象的逻辑复杂或需要根据条件创建不同实现时，如果到处写 `if-else new`，每加一种类型就要改调用方代码。

### 2.2 简单工厂

```java
// 不用工厂：调用方和具体实现耦合
public class NotificationService {
    public void send(String type, String message) {
        if ("email".equals(type)) {
            new EmailSender().send(message);
        } else if ("sms".equals(type)) {
            new SmsSender().send(message);
        } else if ("push".equals(type)) {
            new PushSender().send(message);
        }
        // 每加一种渠道，这里就要改
    }
}
```

```java
// 用工厂：创建逻辑集中管理
public interface MessageSender {
    void send(String message);
}

public class EmailSender implements MessageSender {
    public void send(String message) { System.out.println("Email: " + message); }
}
public class SmsSender implements MessageSender {
    public void send(String message) { System.out.println("SMS: " + message); }
}
public class PushSender implements MessageSender {
    public void send(String message) { System.out.println("Push: " + message); }
}

// 简单工厂
public class SenderFactory {
    private static final Map<String, Supplier<MessageSender>> SENDERS = Map.of(
        "email", EmailSender::new,
        "sms", SmsSender::new,
        "push", PushSender::new
    );

    public static MessageSender create(String type) {
        Supplier<MessageSender> supplier = SENDERS.get(type);
        if (supplier == null) {
            throw new IllegalArgumentException("Unknown sender type: " + type);
        }
        return supplier.get();
    }
}

// 使用：调用方不再关心具体实现
MessageSender sender = SenderFactory.create("email");
sender.send("Hello!");
```

### 2.3 在框架中的应用

```java
// Calendar.getInstance() —— 根据 Locale 返回不同的 Calendar 实现
Calendar cal = Calendar.getInstance();

// Spring 的 BeanFactory —— 根据名字/类型获取 Bean
UserService service = context.getBean(UserService.class);

// JDBC DriverManager —— 根据 URL 创建不同数据库的 Connection
Connection conn = DriverManager.getConnection("jdbc:mysql://...");

// Spring Boot 的自动配置本身就是工厂：
// 根据 classpath 上的类和配置文件，自动创建合适的 Bean
```

## 3. 策略模式（Strategy）

### 3.1 问题

同一个操作有多种算法/策略，用 if-else 选择会导致代码膨胀，且每加一种策略都要改调用方。

### 3.2 实现

```java
// 场景：广告竞价，不同广告主使用不同的出价策略

// 策略接口
public interface BiddingStrategy {
    double calculateBid(AdRequest request);
}

// 策略实现
public class FixedBidStrategy implements BiddingStrategy {
    private final double fixedPrice;
    public FixedBidStrategy(double fixedPrice) { this.fixedPrice = fixedPrice; }
    public double calculateBid(AdRequest request) { return fixedPrice; }
}

public class CpmBidStrategy implements BiddingStrategy {
    public double calculateBid(AdRequest request) {
        return request.getEstimatedImpressions() * 0.005;
    }
}

public class SmartBidStrategy implements BiddingStrategy {
    public double calculateBid(AdRequest request) {
        return request.getHistoricalCtr() * request.getConversionValue() * 0.8;
    }
}

// 上下文：持有策略引用，不关心具体是哪种
public class BidEngine {
    private final BiddingStrategy strategy;

    public BidEngine(BiddingStrategy strategy) {
        this.strategy = strategy;
    }

    public double bid(AdRequest request) {
        return strategy.calculateBid(request);
    }
}

// 使用
BidEngine engine = new BidEngine(new SmartBidStrategy());
double bidPrice = engine.bid(request);
```

### 3.3 策略模式 + Spring：消除 if-else

```java
// 每种策略注册为一个 Bean
@Component("fixed")
public class FixedBidStrategy implements BiddingStrategy { ... }

@Component("cpm")
public class CpmBidStrategy implements BiddingStrategy { ... }

@Component("smart")
public class SmartBidStrategy implements BiddingStrategy { ... }

// Spring 自动注入所有实现到 Map 中（key 是 Bean 名称）
@Service
public class BidEngine {
    private final Map<String, BiddingStrategy> strategyMap;

    public BidEngine(Map<String, BiddingStrategy> strategyMap) {
        this.strategyMap = strategyMap;
    }

    public double bid(String strategyType, AdRequest request) {
        BiddingStrategy strategy = strategyMap.get(strategyType);
        if (strategy == null) {
            throw new IllegalArgumentException("Unknown strategy: " + strategyType);
        }
        return strategy.calculateBid(request);
    }
}

// 新增策略：只需要加一个 @Component 类，不用改 BidEngine
```

### 3.4 枚举也能做策略

在第 13 篇枚举中已经讲过——每个枚举值实现接口方法，适合策略数量固定的场景。

## 4. 观察者模式（Observer）

### 4.1 问题

一个对象状态变化时，需要通知多个其他对象做出反应。如果直接调用，发布者和订阅者就耦合了。

### 4.2 实现

```java
// 场景：订单状态变化后，需要发邮件、扣库存、记日志

// 事件
public class OrderEvent {
    private final String orderId;
    private final String status;

    public OrderEvent(String orderId, String status) {
        this.orderId = orderId;
        this.status = status;
    }

    public String getOrderId() { return orderId; }
    public String getStatus() { return status; }
}

// 观察者接口
public interface OrderEventListener {
    void onOrderEvent(OrderEvent event);
}

// 具体观察者
public class EmailNotifier implements OrderEventListener {
    public void onOrderEvent(OrderEvent event) {
        System.out.println("发送邮件：订单 " + event.getOrderId() + " 状态变为 " + event.getStatus());
    }
}

public class InventoryManager implements OrderEventListener {
    public void onOrderEvent(OrderEvent event) {
        if ("PAID".equals(event.getStatus())) {
            System.out.println("扣减库存：订单 " + event.getOrderId());
        }
    }
}

// 发布者
public class OrderService {
    private final List<OrderEventListener> listeners = new ArrayList<>();

    public void addListener(OrderEventListener listener) {
        listeners.add(listener);
    }

    public void changeStatus(String orderId, String newStatus) {
        // 业务逻辑...
        OrderEvent event = new OrderEvent(orderId, newStatus);
        listeners.forEach(l -> l.onOrderEvent(event));  // 通知所有观察者
    }
}
```

### 4.3 Spring 的事件机制（生产级用法）

Spring 内置了观察者模式，不用自己维护监听器列表：

```java
// 1. 定义事件
public class OrderPaidEvent extends ApplicationEvent {
    private final String orderId;

    public OrderPaidEvent(Object source, String orderId) {
        super(source);
        this.orderId = orderId;
    }

    public String getOrderId() { return orderId; }
}

// 2. 发布事件
@Service
public class OrderService {
    private final ApplicationEventPublisher publisher;

    public OrderService(ApplicationEventPublisher publisher) {
        this.publisher = publisher;
    }

    @Transactional
    public void pay(String orderId) {
        // 业务逻辑...
        publisher.publishEvent(new OrderPaidEvent(this, orderId));
    }
}

// 3. 监听事件（可以有多个监听器，互相解耦）
@Component
public class EmailListener {
    @EventListener
    public void onOrderPaid(OrderPaidEvent event) {
        System.out.println("发送支付确认邮件：" + event.getOrderId());
    }
}

@Component
public class InventoryListener {
    @EventListener
    public void onOrderPaid(OrderPaidEvent event) {
        System.out.println("扣减库存：" + event.getOrderId());
    }
}

// 异步监听（不阻塞主流程）
@Component
public class AnalyticsListener {
    @Async
    @EventListener
    public void onOrderPaid(OrderPaidEvent event) {
        System.out.println("记录分析数据：" + event.getOrderId());
    }
}
```

OrderService 完全不知道有哪些监听器——新增监听器只需要加一个 `@EventListener` 方法，不用改 OrderService。

## 5. 代理模式（Proxy）

### 5.1 问题

想在不修改原有代码的前提下，给方法添加额外功能（日志、缓存、权限检查、事务）。

### 5.2 静态代理

```java
public interface UserService {
    User getUser(String id);
}

public class UserServiceImpl implements UserService {
    public User getUser(String id) {
        return repo.findById(id);
    }
}

// 代理类：手动编写
public class UserServiceProxy implements UserService {
    private final UserService target;

    public UserServiceProxy(UserService target) {
        this.target = target;
    }

    public User getUser(String id) {
        System.out.println("[LOG] getUser called with id=" + id);
        long start = System.currentTimeMillis();

        User result = target.getUser(id);  // 调用真实方法

        System.out.println("[LOG] getUser took " + (System.currentTimeMillis() - start) + "ms");
        return result;
    }
}

// 问题：每个方法都要手动写代理逻辑，方法多了维护成本极高
```

### 5.3 动态代理

在第 12 篇（注解与反射）中已经详细讲过 JDK 动态代理和 CGLIB。这里回顾核心用法：

```java
// JDK 动态代理：运行时自动生成代理类
public class LoggingHandler implements InvocationHandler {
    private final Object target;

    public LoggingHandler(Object target) { this.target = target; }

    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        System.out.println("[LOG] " + method.getName() + " called");
        long start = System.currentTimeMillis();
        Object result = method.invoke(target, args);
        System.out.println("[LOG] " + method.getName() + " took "
            + (System.currentTimeMillis() - start) + "ms");
        return result;
    }
}

// 创建代理
UserService proxy = (UserService) Proxy.newProxyInstance(
    UserService.class.getClassLoader(),
    new Class[]{UserService.class},
    new LoggingHandler(new UserServiceImpl())
);
proxy.getUser("001");  // 自动带上日志
```

### 5.4 在框架中的应用

```
Spring AOP           → 动态代理（JDK / CGLIB）
@Transactional       → 代理拦截方法，自动管理事务
@Cacheable           → 代理拦截方法，自动查缓存
MyBatis Mapper       → JDK 动态代理（接口没有实现类，全靠代理）
Feign Client         → 动态代理（接口定义 HTTP 调用，代理生成实际请求）
```

## 6. 模板方法模式（Template Method）

### 6.1 问题

多个类有相同的流程骨架，但某些步骤的实现不同。如果每个类都完整实现一遍，流程变了就要改所有类。

### 6.2 实现

```java
// 场景：数据导出，流程相同（查询 → 转换 → 写文件），但格式不同

public abstract class DataExporter {
    // 模板方法：定义流程骨架，用 final 防止子类修改流程
    public final void export(String query) {
        List<Map<String, Object>> data = queryData(query);  // 步骤 1：查询
        String content = format(data);                       // 步骤 2：格式化（子类实现）
        writeFile(content);                                  // 步骤 3：写文件

        if (needNotify()) {                                  // 钩子方法
            notify(content);
        }
    }

    // 公共步骤
    private List<Map<String, Object>> queryData(String query) {
        System.out.println("查询数据: " + query);
        return List.of(Map.of("name", "Alice", "age", 25));
    }

    private void writeFile(String content) {
        System.out.println("写入文件: " + content.substring(0, Math.min(50, content.length())));
    }

    // 抽象方法：子类必须实现
    protected abstract String format(List<Map<String, Object>> data);

    // 钩子方法：子类可以选择性覆盖
    protected boolean needNotify() { return false; }
    protected void notify(String content) {}
}

// CSV 导出
public class CsvExporter extends DataExporter {
    protected String format(List<Map<String, Object>> data) {
        StringBuilder sb = new StringBuilder("name,age\n");
        data.forEach(row -> sb.append(row.get("name")).append(",").append(row.get("age")).append("\n"));
        return sb.toString();
    }
}

// JSON 导出
public class JsonExporter extends DataExporter {
    protected String format(List<Map<String, Object>> data) {
        return new ObjectMapper().writeValueAsString(data);
    }

    protected boolean needNotify() { return true; }   // 覆盖钩子
    protected void notify(String content) {
        System.out.println("发送通知：JSON 导出完成");
    }
}

// 使用
new CsvExporter().export("SELECT * FROM users");
new JsonExporter().export("SELECT * FROM users");
```

### 6.3 在框架中的应用

```java
// JdbcTemplate —— 模板处理连接获取、异常转译、资源释放，你只需要写 SQL 和映射逻辑
jdbcTemplate.query("SELECT * FROM users", (rs, rowNum) -> {
    User user = new User();
    user.setName(rs.getString("name"));
    return user;
});

// HttpServlet —— doGet / doPost 是子类实现的步骤，service() 是模板方法
// AbstractList —— get() 是抽象方法，indexOf / contains 等基于 get() 实现
```

## 7. 建造者模式（Builder）

### 7.1 问题

构造一个对象需要很多参数，构造方法参数列表很长，容易搞混顺序。

### 7.2 实现

```java
public class HttpRequest {
    private final String url;
    private final String method;
    private final Map<String, String> headers;
    private final String body;
    private final int timeout;

    private HttpRequest(Builder builder) {
        this.url = builder.url;
        this.method = builder.method;
        this.headers = builder.headers;
        this.body = builder.body;
        this.timeout = builder.timeout;
    }

    // getter 省略

    public static class Builder {
        private final String url;              // 必填
        private String method = "GET";         // 选填，有默认值
        private Map<String, String> headers = new HashMap<>();
        private String body;
        private int timeout = 3000;

        public Builder(String url) {
            this.url = url;
        }

        public Builder method(String method) { this.method = method; return this; }
        public Builder header(String key, String value) { this.headers.put(key, value); return this; }
        public Builder body(String body) { this.body = body; return this; }
        public Builder timeout(int timeout) { this.timeout = timeout; return this; }

        public HttpRequest build() {
            // 可以在这里做参数校验
            if (url == null || url.isEmpty()) {
                throw new IllegalArgumentException("URL is required");
            }
            return new HttpRequest(this);
        }
    }
}

// 使用：链式调用，可读性极好
HttpRequest request = new HttpRequest.Builder("https://api.example.com/users")
    .method("POST")
    .header("Content-Type", "application/json")
    .header("Authorization", "Bearer token123")
    .body("{\"name\": \"Alice\"}")
    .timeout(5000)
    .build();
```

### 7.3 Lombok @Builder

```java
// Lombok 自动生成 Builder
@Builder
public class HttpRequest {
    private final String url;
    @Builder.Default private String method = "GET";
    @Singular private Map<String, String> headers;  // @Singular 支持逐个添加
    private String body;
    @Builder.Default private int timeout = 3000;
}

// 使用
HttpRequest request = HttpRequest.builder()
    .url("https://api.example.com/users")
    .method("POST")
    .header("Content-Type", "application/json")
    .body("{\"name\": \"Alice\"}")
    .build();
```

### 7.4 在框架中的应用

```java
// StringBuilder
String s = new StringBuilder().append("Hello").append(" ").append("World").toString();

// Stream API
List<String> result = list.stream().filter(...).map(...).collect(Collectors.toList());

// OkHttp
Request request = new Request.Builder().url("...").addHeader("...").build();

// Spring WebClient
WebClient.builder().baseUrl("...").defaultHeader("...").build();

// Protobuf
User user = User.newBuilder().setName("Alice").setAge(25).build();
```

## 8. 适配器模式（Adapter）

### 8.1 问题

两个已有接口不兼容，但你需要让它们协同工作，又不想修改原有代码。

### 8.2 实现

```java
// 旧系统的日志接口
public interface OldLogger {
    void writeLog(String message);
}

public class FileLogger implements OldLogger {
    public void writeLog(String message) {
        System.out.println("[FILE] " + message);
    }
}

// 新系统期望的接口
public interface NewLogger {
    void info(String message);
    void error(String message, Throwable t);
}

// 适配器：让旧的 FileLogger 满足新接口
public class LoggerAdapter implements NewLogger {
    private final OldLogger oldLogger;

    public LoggerAdapter(OldLogger oldLogger) {
        this.oldLogger = oldLogger;
    }

    public void info(String message) {
        oldLogger.writeLog("[INFO] " + message);
    }

    public void error(String message, Throwable t) {
        oldLogger.writeLog("[ERROR] " + message + " - " + t.getMessage());
    }
}

// 使用：新系统代码面向 NewLogger 编程，旧的 FileLogger 通过适配器无缝接入
NewLogger logger = new LoggerAdapter(new FileLogger());
logger.info("服务启动");
```

### 8.3 在框架中的应用

```java
// SLF4J 整个设计就是适配器模式
// SLF4J 是统一接口，slf4j-log4j12 / logback-classic 是适配器
// 底层可以是 Log4j、Logback、JUL 任意实现

// InputStreamReader：把 InputStream（字节流）适配成 Reader（字符流）
Reader reader = new InputStreamReader(new FileInputStream("data.txt"), "UTF-8");

// Arrays.asList()：把数组适配成 List
List<String> list = Arrays.asList(array);

// Spring MVC 的 HandlerAdapter：
// 不同类型的 Controller（注解、函数式）通过 Adapter 统一处理
```

## 9. 模式选型速查

| 问题 | 模式 | 一句话 |
|------|------|--------|
| 全局只要一个实例 | 单例 | Spring Bean 默认就是 |
| 根据条件创建不同对象 | 工厂 | Map + Supplier 比 if-else 优雅 |
| 同一操作有多种算法 | 策略 | Spring Map 注入消除 if-else |
| 状态变化通知多方 | 观察者 | Spring @EventListener |
| 不改原有代码加功能 | 代理 | Spring AOP / @Transactional |
| 固定流程不同实现 | 模板方法 | 抽象类定义骨架，子类实现步骤 |
| 复杂对象构造 | 建造者 | 链式调用，Lombok @Builder |
| 接口不兼容 | 适配器 | 包一层转换 |

## 10. 小结

| 主题 | 关键要点 |
|------|---------|
| 单例 | 枚举最优；Spring Bean 默认单例，通常不需要自己写 |
| 工厂 | 用 Map + Supplier/Function 替代 if-else new；Spring 的 BeanFactory 就是工厂 |
| 策略 | 接口 + 多实现；Spring 注入 Map\<String, Interface\> 自动收集所有实现 |
| 观察者 | 发布者不知道订阅者是谁；Spring @EventListener + @Async |
| 代理 | 静态代理手动写，动态代理运行时生成；Spring AOP 的底层 |
| 模板方法 | 抽象类定义流程骨架 + final 防覆盖 + 钩子方法可选覆盖 |
| 建造者 | 链式构造复杂对象；Lombok @Builder 零样板代码 |
| 适配器 | 包一层让不兼容的接口协同工作；SLF4J 是典型 |

---

> **系列总结**：到这里，"Java 全貌"系列的核心内容就完成了——从语言基础、面向对象、泛型、异常、函数式编程、I/O、并发、JVM，到工程化的构建工具、Spring、MyBatis、设计模式，覆盖了一个 Java 后端开发者需要掌握的完整知识体系。

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
