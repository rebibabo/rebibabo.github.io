---
title: 'Java基础(番外) | 开发规范全集：命名、代码、目录、文档、Git 一站式速查'
date: 2026-05-26
abbrlink: 26
tags:
  - 开发规范
  - 代码风格
  - 最佳实践
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

代码是写给人看的，其次才是给机器执行的。入职后你写的每一行代码都会被同事 Review、被后人维护。遵循统一的规范不是形式主义，而是团队高效协作的基础。这篇文章汇总了 Java 后端开发中最常见的规范，大部分参考了阿里巴巴 Java 开发手册，并结合了实际开发中的经验。

<!-- more -->

## 1. 命名规范

### 1.1 总原则

**名字是最好的注释。** 看到名字就应该知道它是什么、做什么，不需要去看实现。

````java
// 反面教材
int d;                    // 什么的天数？
String s;                 // 什么字符串？
List<int[]> list1;        // 什么列表？
void process();           // 处理什么？
boolean flag;             // 什么标志？

// 正面教材
int elapsedDays;
String userName;
List<int[]> dailyClickCounts;
void validateOrder();
boolean isExpired;
````

### 1.2 各种元素的命名规则

| 元素 | 风格 | 示例 | 说明 |
|------|------|------|------|
| 包名 | 全小写，点分隔 | `com.oppo.ads.ssp.service` | 反转域名 + 项目 + 模块 |
| 类名 | UpperCamelCase | `UserService`, `BidRequest` | 名词或名词短语 |
| 接口名 | UpperCamelCase | `Serializable`, `BiddingStrategy` | 形容词或名词 |
| 方法名 | lowerCamelCase | `getUserById`, `calculateBid` | 动词或动词短语 |
| 变量名 | lowerCamelCase | `userName`, `maxRetryCount` | 名词 |
| 常量名 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` | static final |
| 枚举值 | UPPER_SNAKE_CASE | `PENDING`, `PAID`, `ORDER_CREATED` | |
| 泛型参数 | 单个大写字母 | `T`, `E`, `K`, `V`, `R` | |
| 测试类 | 被测类名 + Test | `UserServiceTest` | |
| 测试方法 | 描述行为 | `shouldThrow_whenEmailExists` | |

### 1.3 类名的命名模式

| 类型 | 后缀/模式 | 示例 |
|------|----------|------|
| 控制器 | `XxxController` | `UserController` |
| 服务 | `XxxService` / `XxxServiceImpl` | `UserService` |
| 数据访问 | `XxxMapper` / `XxxRepository` | `UserMapper` |
| 数据传输对象 | `XxxDTO` / `XxxVO` / `XxxRequest` / `XxxResponse` | `CreateUserRequest` |
| 实体类 | `Xxx`（无后缀）或 `XxxEntity` | `User`, `Order` |
| 配置类 | `XxxConfig` / `XxxConfiguration` | `RedisConfig` |
| 工具类 | `XxxUtil` / `XxxUtils` / `XxxHelper` | `DateUtils`, `JsonHelper` |
| 异常类 | `XxxException` | `BusinessException` |
| 枚举 | `XxxEnum` 或直接名词 | `OrderStatus` |
| 常量类 | `XxxConstants` | `HttpConstants` |
| 切面 | `XxxAspect` | `LoggingAspect` |
| 过滤器 | `XxxFilter` | `AuthFilter` |
| 拦截器 | `XxxInterceptor` | `RateLimitInterceptor` |
| 监听器 | `XxxListener` | `OrderEventListener` |
| 工厂 | `XxxFactory` | `SenderFactory` |
| 建造者 | `XxxBuilder` 或内部类 `Builder` | `HttpRequest.Builder` |

### 1.4 方法命名约定

| 用途 | 前缀/模式 | 示例 |
|------|----------|------|
| 获取单个对象 | `getXxx` / `findXxx` | `getUserById` |
| 获取列表 | `listXxx` / `findAllXxx` | `listActiveUsers` |
| 获取数量 | `countXxx` | `countByStatus` |
| 判断是否 | `isXxx` / `hasXxx` / `canXxx` / `existsXxx` | `isExpired`, `hasPermission` |
| 插入 | `save` / `insert` / `add` / `create` | `createUser` |
| 更新 | `update` / `modify` | `updateStatus` |
| 删除 | `delete` / `remove` | `deleteById` |
| 转换 | `toXxx` / `fromXxx` / `convertXxx` | `toDTO`, `fromEntity` |
| 初始化 | `initXxx` | `initCache` |
| 校验 | `validateXxx` / `checkXxx` | `validateOrder` |
| 处理 | `handleXxx` / `processXxx` | `handleRequest` |
| 回调 | `onXxx` | `onOrderPaid` |

### 1.5 布尔变量和方法的命名

````java
// 变量：用 is / has / can / should / need 开头（或形容词）
boolean isActive;
boolean hasPermission;
boolean canRetry;
boolean expired;      // 形容词也可以，但加 is 更清晰

// 方法：返回 boolean 的方法同理
public boolean isExpired() { ... }
public boolean hasNext() { ... }
public boolean canAfford(double price) { ... }

// 不要用否定命名，双重否定读起来很痛苦
boolean isNotEmpty;         // 不好
boolean isEmpty;            // 好
if (!isNotEmpty) { ... }    // 脑壳疼
if (isEmpty) { ... }        // 清晰
````

### 1.6 数据库命名

| 元素 | 风格 | 示例 |
|------|------|------|
| 表名 | lower_snake_case，复数 | `users`, `ad_campaigns` |
| 列名 | lower_snake_case | `user_name`, `created_at` |
| 主键 | `id` | `id` |
| 外键 | `关联表单数_id` | `user_id`, `campaign_id` |
| 索引 | `idx_表名_列名` | `idx_users_email` |
| 唯一索引 | `uk_表名_列名` | `uk_users_email` |
| 布尔字段 | `is_xxx` | `is_deleted`, `is_active` |
| 时间字段 | `xxx_at` 或 `xxx_time` | `created_at`, `updated_at` |

````sql
CREATE TABLE ad_placements (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)  NOT NULL COMMENT '广告位名称',
    site_id     BIGINT        NOT NULL COMMENT '关联站点 ID',
    ad_format   VARCHAR(20)   NOT NULL COMMENT '广告格式：banner/native/video',
    floor_price DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '底价（元）',
    is_active   TINYINT(1)    NOT NULL DEFAULT 1 COMMENT '是否启用',
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ad_placements_site_id (site_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='广告位表';
````

### 1.7 Redis Key 命名

````
格式：业务:对象:标识[:维度]
分隔符统一用冒号

user:profile:12345              用户画像
ad:budget:campaign_001          广告预算
freq:user_123:ad_456:20260620   频控计数
lock:bid:req_789                分布式锁
cache:ad_list:banner:active     缓存
````

## 2. 代码规范

### 2.1 格式与排版

````java
// 缩进：4 个空格，不用 Tab
// 行宽：不超过 120 字符
// 大括号：左括号不换行（Java 标准风格）

// 正确
if (condition) {
    doSomething();
} else {
    doOtherThing();
}

// 错误（C# 风格，Java 不用）
if (condition)
{
    doSomething();
}

// 空行的使用：
// - 方法之间空一行
// - 方法内按逻辑段落空一行
// - 类的字段声明和第一个方法之间空一行
// - 不要连续空两行以上
````

### 2.2 方法设计原则

````java
// 1. 方法只做一件事（单一职责）
// 反面
public void createOrderAndSendEmailAndDeductInventory(Order order) { ... }

// 正面
public void createOrder(Order order) {
    validateOrder(order);
    orderRepo.save(order);
    eventPublisher.publishEvent(new OrderCreatedEvent(order));
}

// 2. 方法不超过 50 行（超了就该拆分）

// 3. 参数不超过 5 个（超了用对象封装）
// 反面
public User createUser(String name, String email, int age,
    String phone, String address, String city) { ... }

// 正面
public User createUser(CreateUserRequest request) { ... }

// 4. 不要用 boolean 参数控制分支
// 反面
public List<User> getUsers(boolean includeDeleted) { ... }

// 正面
public List<User> getActiveUsers() { ... }
public List<User> getAllUsersIncludeDeleted() { ... }

// 5. 尽早返回，减少嵌套
// 反面
public String process(Order order) {
    if (order != null) {
        if (order.isValid()) {
            if (order.isPaid()) {
                return "success";
            } else {
                return "unpaid";
            }
        } else {
            return "invalid";
        }
    } else {
        return "null";
    }
}

// 正面
public String process(Order order) {
    if (order == null) return "null";
    if (!order.isValid()) return "invalid";
    if (!order.isPaid()) return "unpaid";
    return "success";
}
````

### 2.3 注释规范

````java
// 1. 好代码自解释，注释写"为什么"，不写"是什么"

// 反面：注释是废话
int age = 25; // 设置年龄为 25
list.add(user); // 将用户添加到列表

// 正面：解释业务逻辑和设计决策
// 频控窗口使用自然天而非 24 小时滑窗，因为广告主按日预算结算
String key = "freq:" + userId + ":" + adId + ":" + LocalDate.now();

// 2. TODO / FIXME / HACK 注明责任人和日期
// TODO(lionelvd, 2026-06-20): 当前是遍历查找，用户量大后需要改为索引查找
// FIXME(lionelvd): 并发场景下可能有竞态条件，需要加锁
// HACK: MySQL 5.7 不支持窗口函数，临时用子查询实现

// 3. 类的 Javadoc
/**
 * 广告竞价服务。
 * <p>
 * 接收来自 SSP 的广告请求，向已注册的 DSP 发送竞价请求，
 * 选出最高出价者并返回广告素材。
 *
 * @author lionelvd
 * @since 1.0.0
 */
@Service
public class BidService { ... }

// 4. 复杂方法的 Javadoc
/**
 * 执行二价竞价（Second-Price Auction）。
 *
 * @param bids 所有 DSP 的出价列表，不能为空
 * @param floorPrice 底价，低于此价格的出价会被过滤
 * @return 胜出的出价，如果没有有效出价则返回 empty
 * @throws IllegalArgumentException 如果 bids 为 null
 */
public Optional<Bid> runSecondPriceAuction(List<Bid> bids, double floorPrice) { ... }

// 5. 不需要 Javadoc 的情况
// getter / setter / 简单的 CRUD 方法 / 含义一目了然的方法
````

### 2.4 异常处理规范

````java
// 1. 不要吞掉异常
try {
    riskyOperation();
} catch (Exception e) {
    // 什么都不做 ← 绝对禁止
}

// 2. 不要用 e.printStackTrace()（用日志框架）
try {
    riskyOperation();
} catch (Exception e) {
    log.error("操作失败, orderId={}", orderId, e);  // 正确
}

// 3. 不要捕获 Exception，要捕获具体异常
try {
    parseJson(data);
} catch (JsonParseException e) {    // 正确：精确捕获
    log.warn("JSON 解析失败: {}", data, e);
}

// 4. 不要在 finally 中 return 或抛异常

// 5. 自定义异常要有业务含义
throw new InsufficientBudgetException(campaignId, remaining, cost);
// 而不是
throw new RuntimeException("budget not enough");

// 6. 面向调用方决定是 Checked 还是 Unchecked
// 调用方能恢复 → Checked
// 程序员的 bug → Unchecked（RuntimeException）
````

### 2.5 日志规范

````java
// 1. 用 SLF4J + 占位符，不要字符串拼接
log.info("查询用户: id={}", id);                    // 正确
log.info("查询用户: id=" + id);                     // 错误（无论是否打印都会拼接）

// 2. 日志级别选择
log.error("...");   // 系统错误，需要立即关注（告警）
log.warn("...");    // 预期之外但可处理的情况（频控触发、参数不合法）
log.info("...");    // 关键业务操作（用户创建、订单支付、竞价结果）
log.debug("...");   // 开发调试信息（方法入参、中间变量）
log.trace("...");   // 最详细的追踪信息（循环内每一步）

// 3. 关键操作必须记日志
log.info("竞价请求: requestId={}, adSlot={}, dspCount={}", requestId, slotId, dspCount);
log.info("竞价结果: requestId={}, winner={}, price={}", requestId, winnerId, price);

// 4. 错误日志要带上下文
log.error("扣减预算失败: campaignId={}, cost={}, balance={}", campaignId, cost, balance, e);
// 而不是
log.error("扣减预算失败");  // 出了问题完全无法排查

// 5. 不要在循环中打 info 日志（日志洪水）
for (User user : users) {
    log.info("处理用户: {}", user.getId());  // 1000 个用户就是 1000 行日志
}
// 改为
log.info("开始批量处理用户, count={}", users.size());
// ... 循环处理
log.info("批量处理完成, successCount={}, failCount={}", success, fail);

// 6. 敏感信息不要打到日志里
log.info("用户登录: phone={}", phone);           // 泄露手机号
log.info("用户登录: phone={}****{}", phone.substring(0, 3), phone.substring(7));
````

### 2.6 空值处理

````java
// 1. 方法参数校验
public User getUser(Long id) {
    Objects.requireNonNull(id, "id must not be null");
    // 或者用 Spring 的 Assert
    Assert.notNull(id, "id must not be null");
}

// 2. 返回空集合而非 null
// 反面
public List<User> listUsers() {
    List<User> result = query();
    if (result.isEmpty()) return null;  // 调用者要判空
    return result;
}

// 正面
public List<User> listUsers() {
    return query();  // 空列表就返回空列表，不返回 null
}

// 3. Optional 用于返回值
public Optional<User> findByEmail(String email) {
    return Optional.ofNullable(repo.findByEmail(email));
}

// 4. 集合操作前判空
if (CollectionUtils.isNotEmpty(list)) { ... }      // Spring 工具类
if (list != null && !list.isEmpty()) { ... }        // 原生写法
if (StringUtils.isNotBlank(str)) { ... }            // 字符串判空

// 5. 链式调用防空指针
// 反面
String city = user.getAddress().getCity().toUpperCase();  // 三个地方可能 NPE

// 正面
String city = Optional.ofNullable(user)
    .map(User::getAddress)
    .map(Address::getCity)
    .map(String::toUpperCase)
    .orElse("UNKNOWN");
````

### 2.7 并发安全

````java
// 1. SimpleDateFormat 线程不安全，用 DateTimeFormatter
private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd");

// 2. HashMap 线程不安全，多线程用 ConcurrentHashMap

// 3. 共享可变状态加锁或用原子类
private final AtomicInteger counter = new AtomicInteger(0);

// 4. 不要在 Spring Bean（singleton）中使用实例变量存请求级别的数据
@Service
public class UserService {
    private User currentUser;  // 严重错误！所有请求共享这一个实例
}

// 5. 线程池不用 Executors 工厂方法，手动创建 ThreadPoolExecutor
````

### 2.8 集合使用

````java
// 1. 创建集合时指定初始容量（减少扩容）
List<User> list = new ArrayList<>(expectedSize);
Map<String, User> map = new HashMap<>(expectedSize * 4 / 3 + 1);  // 考虑负载因子

// 2. 用 Collections.unmodifiableList / List.of 返回不可修改的集合
public List<String> getSupportedFormats() {
    return List.of("banner", "native", "video");  // 外部无法修改
}

// 3. 遍历时不要用 for 循环删除元素
// 反面（ConcurrentModificationException）
for (User user : list) {
    if (user.isExpired()) list.remove(user);
}

// 正面
list.removeIf(User::isExpired);
// 或者
Iterator<User> it = list.iterator();
while (it.hasNext()) {
    if (it.next().isExpired()) it.remove();
}

// 4. Map 的 computeIfAbsent 替代先 get 再 put
// 反面
List<Order> orders = map.get(userId);
if (orders == null) {
    orders = new ArrayList<>();
    map.put(userId, orders);
}
orders.add(order);

// 正面
map.computeIfAbsent(userId, k -> new ArrayList<>()).add(order);
````

## 3. 项目目录结构

### 3.1 标准分层结构

````
src/main/java/com/oppo/ads/ssp/
├── SspApplication.java              ← 启动类
│
├── config/                          ← 配置类
│   ├── RedisConfig.java
│   ├── WebClientConfig.java
│   └── MyBatisPlusConfig.java
│
├── controller/                      ← 控制层（接收请求、参数校验）
│   ├── AdController.java
│   └── ReportController.java
│
├── service/                         ← 业务层（核心逻辑）
│   ├── BidService.java
│   ├── FrequencyCapService.java
│   └── impl/                        ← 接口实现（如果用接口 + 实现分离）
│       └── BidServiceImpl.java
│
├── mapper/                          ← 数据访问层（MyBatis）
│   ├── AdPlacementMapper.java
│   └── BidRecordMapper.java
│
├── entity/                          ← 数据库实体类
│   ├── AdPlacement.java
│   └── BidRecord.java
│
├── dto/                             ← 数据传输对象
│   ├── request/
│   │   ├── BidRequest.java
│   │   └── CreatePlacementRequest.java
│   └── response/
│       ├── BidResponse.java
│       └── PlacementResponse.java
│
├── enums/                           ← 枚举
│   ├── AdFormat.java
│   └── BidStatus.java
│
├── exception/                       ← 自定义异常
│   ├── BusinessException.java
│   ├── ResourceNotFoundException.java
│   └── GlobalExceptionHandler.java
│
├── util/                            ← 工具类
│   ├── JsonUtils.java
│   └── SignatureUtils.java
│
├── aspect/                          ← AOP 切面
│   └── LoggingAspect.java
│
├── filter/                          ← 过滤器
│   └── RequestIdFilter.java
│
├── client/                          ← 外部服务调用
│   ├── DspClient.java
│   └── AuditClient.java
│
└── constant/                        ← 常量
    └── RedisKeyConstants.java

src/main/resources/
├── application.yml
├── application-dev.yml
├── application-prod.yml
├── mapper/                          ← MyBatis XML
│   ├── AdPlacementMapper.xml
│   └── BidRecordMapper.xml
└── db/migration/                    ← 数据库迁移脚本（Flyway）
    ├── V1__create_ad_placements.sql
    └── V2__create_bid_records.sql

src/test/java/com/oppo/ads/ssp/
├── service/
│   └── BidServiceTest.java
├── controller/
│   └── AdControllerTest.java
└── mapper/
    └── AdPlacementMapperTest.java
````

### 3.2 分层职责边界

````
Controller：
├── 接收 HTTP 请求
├── 参数校验（@Valid）
├── 调用 Service
├── 返回响应
└── 不包含业务逻辑

Service：
├── 核心业务逻辑
├── 事务管理（@Transactional）
├── 调用 Mapper / Client
├── 组合多个数据源的数据
└── 不依赖 HttpServletRequest 等 Web 层对象

Mapper / Repository：
├── 纯数据访问
├── SQL 查询
└── 不包含业务逻辑

Client：
├── 封装外部服务调用
├── 超时、重试、异常处理
└── 返回领域对象（不要返回原始 HTTP 响应）

DTO：
├── Request：接收前端/调用方参数
├── Response：返回给前端/调用方的数据
└── 和 Entity 分离（不要直接把 Entity 暴露给前端）
````

### 3.3 为什么 DTO 要和 Entity 分离？

````java
// Entity 是数据库模型
@TableName("users")
public class User {
    private Long id;
    private String name;
    private String email;
    private String passwordHash;     // 密码哈希，不能暴露给前端
    private Integer isDeleted;       // 内部字段
    private LocalDateTime createdAt;
}

// Response DTO 是给前端看的
public class UserResponse {
    private Long id;
    private String name;
    private String email;
    private String createdAt;        // 格式化后的字符串
    // 没有 passwordHash 和 isDeleted
}

// Request DTO 是前端传入的
public class CreateUserRequest {
    @NotBlank
    private String name;
    @Email
    private String email;
    @Size(min = 8)
    private String password;
    // 没有 id、createdAt（由后端生成）
}
````

## 4. API 设计规范

### 4.1 URL 设计

````
RESTful 风格：
GET    /api/v1/users          获取用户列表
GET    /api/v1/users/123      获取单个用户
POST   /api/v1/users          创建用户
PUT    /api/v1/users/123      全量更新用户
PATCH  /api/v1/users/123      部分更新用户
DELETE /api/v1/users/123      删除用户

规则：
├── 用名词复数（users 不是 user）
├── 用 HTTP 方法表示操作（不要 /api/getUser、/api/deleteUser）
├── 层级关系用嵌套（/api/v1/users/123/orders → 某用户的订单）
├── 版本号放在 URL 中（/api/v1/...）
├── 过滤、排序、分页用查询参数
│   GET /api/v1/users?status=active&sort=createdAt,desc&page=0&size=20
└── 非 CRUD 操作用动词子资源
    POST /api/v1/orders/123/cancel
    POST /api/v1/users/123/reset-password
````

### 4.2 统一响应格式

````java
// 成功响应
{
    "code": 0,
    "message": "success",
    "data": { ... }
}

// 失败响应
{
    "code": 40001,
    "message": "邮箱已被注册",
    "data": null
}

// 分页响应
{
    "code": 0,
    "message": "success",
    "data": {
        "records": [ ... ],
        "total": 100,
        "page": 1,
        "size": 20,
        "pages": 5
    }
}
````

````java
// 统一响应封装类
public class Result<T> {
    private int code;
    private String message;
    private T data;

    public static <T> Result<T> success(T data) {
        return new Result<>(0, "success", data);
    }

    public static Result<Void> success() {
        return new Result<>(0, "success", null);
    }

    public static Result<Void> error(int code, String message) {
        return new Result<>(code, message, null);
    }
}
````

### 4.3 错误码设计

````java
// 按模块划分错误码范围
public class ErrorCodes {
    // 通用：10000-19999
    public static final int PARAM_INVALID = 10001;
    public static final int UNAUTHORIZED = 10002;
    public static final int FORBIDDEN = 10003;
    public static final int NOT_FOUND = 10004;

    // 用户模块：20000-29999
    public static final int USER_NOT_FOUND = 20001;
    public static final int EMAIL_EXISTS = 20002;

    // 广告模块：30000-39999
    public static final int AD_PLACEMENT_NOT_FOUND = 30001;
    public static final int BUDGET_EXHAUSTED = 30002;
    public static final int BID_TIMEOUT = 30003;
}
````

## 5. Git 规范

### 5.1 分支命名

````
feature/add-frequency-cap        功能开发
bugfix/fix-bid-timeout           Bug 修复
hotfix/fix-production-crash      紧急线上修复
refactor/optimize-bid-service    重构
chore/upgrade-spring-boot        杂项
release/v1.2.0                   发布分支
````

### 5.2 Commit 消息

````bash
# 格式
<type>(<scope>): <subject>

# 示例
feat(bid): 实现二价竞价逻辑
fix(freq): 修复跨天频控计数未重置的问题
refactor(service): 将出价策略重构为策略模式
test(bid): 补充 BidService 边界条件测试
docs(api): 更新竞价接口文档
perf(cache): 优化广告位缓存预加载
chore(deps): 升级 Spring Boot 到 3.2.1
````

### 5.3 PR 规范

````
标题：和 commit 格式一致

描述模板：
## 改动说明
简述做了什么、为什么要做

## 关联
- 需求：JIRA-1234
- 设计文档：[链接]

## 改动范围
- 新增/修改/删除了哪些文件
- 影响了哪些模块

## 测试情况
- [ ] 单元测试通过
- [ ] 本地自测通过
- [ ] 边界情况已覆盖

## 部署注意
- 是否需要数据库变更
- 是否需要新增配置项
- 是否有不兼容的改动
````

## 6. 文档规范

### 6.1 必须有的文档

````
README.md             ← 项目概述、快速启动、架构简介
CONTRIBUTING.md       ← 开发环境搭建、提交规范
CHANGELOG.md          ← 版本变更记录
API 文档              ← Swagger / Apifox / 手写 Markdown
数据库设计文档          ← ER 图 + 表字段说明
技术方案文档            ← 每个重要功能一份
````

### 6.2 README 模板

````markdown
# SSP 广告服务

## 项目简介
一句话说清楚项目是什么。

## 技术栈
- Java 17 + Spring Boot 3.2
- MyBatis-Plus + MySQL 8.0
- Redis 7 + Lettuce
- Gradle 8.5

## 快速启动

### 环境要求
- JDK 17+
- MySQL 8.0+
- Redis 7+

### 本地运行
```bash
git clone xxx
cd ssp-service
cp src/main/resources/application-dev.yml.example src/main/resources/application-dev.yml
# 编辑 application-dev.yml，配置数据库和 Redis 连接
./gradlew bootRun
```

### 运行测试
```bash
./gradlew test
```

## 项目结构
（简要说明各个包的职责）

## 接口文档
启动后访问 http://localhost:8080/swagger-ui.html

## 联系人
- 负责人：xxx
- 技术问题：xxx
````

### 6.3 CHANGELOG 格式

````markdown
# Changelog

## [1.2.0] - 2026-06-20
### Added
- 广告频控功能（每用户每天限制展示次数）
- 竞价结果异步回调通知

### Changed
- 竞价超时时间从 200ms 调整为 150ms
- 优化广告位缓存预加载逻辑

### Fixed
- 修复跨天预算未重置的问题
- 修复并发竞价时偶发的空指针异常

## [1.1.0] - 2026-06-10
### Added
- DSP 接入管理功能
- 基础竞价流程
````

## 7. 安全规范

````
代码层面：
├── SQL 查询用 #{} 预编译，不用 ${}
├── 接口加入鉴权（Token / API Key）
├── 敏感数据不打日志（密码、Token、手机号）
├── 密码用 BCrypt 哈希存储，不要明文或 MD5
├── 不要在代码中硬编码密码、密钥（用配置中心或环境变量）
└── 接口做限流防刷（Sentinel / Guava RateLimiter）

配置层面：
├── 配置文件不提交到 Git（application-prod.yml 在 .gitignore 中）
├── 敏感配置用环境变量或配置中心（Nacos / Apollo）
└── 数据库账号按最小权限原则（应用账号不给 DROP 权限）

接口层面：
├── 输入校验（@Valid + 自定义校验）
├── 输出脱敏（手机号、邮箱部分隐藏）
├── 防重复提交（幂等性设计）
└── HTTPS（生产环境强制）
````

## 8. 代码审查 Checklist

每次提交 PR 前，对照检查：

````
功能正确性：
├── 正常流程是否跑通？
├── 异常流程是否处理？（参数非法、依赖不可用、超时）
├── 边界情况是否考虑？（空集合、null、最大值）
└── 并发场景是否安全？

代码质量：
├── 命名是否清晰？
├── 方法是否过长？（>50 行要拆）
├── 是否有重复代码？（提取公共方法）
├── 是否有硬编码的魔法值？（提取为常量）
└── 是否有不必要的注释或注释掉的代码？

规范遵守：
├── 日志是否规范？（级别正确、有上下文、无敏感信息）
├── 异常处理是否规范？（不吞异常、精确捕获）
├── 接口设计是否 RESTful？
├── Commit 消息是否规范？
└── 是否有单元测试？

性能：
├── 有没有 N+1 查询？
├── 有没有循环中的数据库/Redis 调用？（批量操作）
├── 大集合是否用 Stream 惰性处理？
├── 是否需要加缓存？
└── 索引是否合理？
````

## 9. 小结

| 类别 | 核心原则 |
|------|---------|
| 命名 | 名字即文档，看名字知含义；统一风格不混用 |
| 代码 | 方法只做一件事、不超过 50 行；尽早返回减少嵌套 |
| 注释 | 写"为什么"不写"是什么"；TODO 注明责任人 |
| 日志 | 用占位符不拼接；关键操作必记；不打敏感信息 |
| 异常 | 不吞异常、精确捕获、自定义异常有业务含义 |
| 空值 | 返回空集合不返回 null；Optional 用于返回值 |
| 目录 | 按职责分层（controller/service/mapper/dto/entity） |
| API | RESTful URL + 统一响应格式 + 错误码体系 |
| Git | 功能分支开发、规范的 commit 消息、PR 描述完整 |
| 文档 | README 必须有、CHANGELOG 跟着版本走 |
| 安全 | 参数校验、SQL 防注入、密码哈希、配置不入库 |

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
