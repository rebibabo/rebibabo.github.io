---
title: 'Java基础(21) | Redis 实战：Spring Data Redis 与缓存策略'
date: 2026-05-21
tags:
  - Java
  - Redis
  - 缓存
categories:
  - Java基础
---

## 前言

广告系统对性能要求极高——一次竞价请求必须在几十毫秒内完成，不可能每次都查数据库。Redis 作为内存数据库，是后端开发中最常用的缓存和高速数据存储方案。这篇文章覆盖 Redis 的核心数据结构、Spring Boot 整合方式、以及实际开发中的缓存模式。

<!-- more -->

## 1. Redis 五种数据结构

Redis 不是一个简单的 key-value 存储——根据 value 的类型不同，Redis 提供了 5 种核心数据结构，每种结构有自己专属的命令。选错数据结构往往意味着要写很多额外代码才能实现同样的功能，所以先搞清楚每种类型"是什么、有哪些操作、操作完结果长什么样"，再去看第 3 节里 Java 怎么调用会容易很多。

| 类型 | 说明 | 典型场景 |
|------|------|---------|
| String | 最基础，存字符串/数字/JSON | 缓存、计数器、分布式锁 |
| Hash | 字段-值映射（类似嵌套的 Map） | 对象属性存储 |
| List | 有序列表（双端队列） | 消息队列、最近浏览记录 |
| Set | 无序不重复集合 | 去重、标签、共同关注 |
| ZSet（Sorted Set） | 有序集合（按分数排序） | 排行榜、延迟队列 |

下面用 `redis-cli` 演示每种类型的常用命令，`>` 后面是 Redis 返回的结果。

### 1.1 String：最基础的键值对

一个 key 对应一个值，值可以是字符串、数字，或者序列化后的 JSON。

| 命令 | 作用 |
|------|------|
| `SET key value` | 设置值 |
| `GET key` | 取值 |
| `DEL key` | 删除 |
| `EXISTS key` | 判断是否存在 |
| `SETEX key seconds value` | 设置值并指定过期时间（秒） |
| `EXPIRE key seconds` | 给已存在的 key 设置过期时间 |
| `TTL key` | 查看剩余过期时间（秒） |
| `INCR key` / `DECR key` | 原子自增 / 自减 1 |
| `INCRBY key n` | 原子自增 n |
| `SETNX key value` | 仅当 key 不存在时才设置（分布式锁的基础） |

```bash
SET name "Alice"
> OK

GET name
> "Alice"

GET notexist
> (nil)                   # 不存在的 key 返回 nil

SETEX token:abc 3600 "user-1"
> OK

TTL token:abc
> (integer) 3600          # 剩余秒数；-1 表示永不过期，-2 表示 key 不存在

INCR counter
> (integer) 1             # counter 不存在时从 0 开始自增

INCR counter
> (integer) 2

SETNX lock:order-1 "1"
> (integer) 1             # 之前不存在，设置成功

SETNX lock:order-1 "1"
> (integer) 0             # 已经存在，设置失败——分布式锁靠这个返回值判断"是否抢到锁"
```

**典型场景**：缓存对象（JSON 字符串）、计数器（`INCR`）、分布式锁（`SETNX`）、限流（`INCR` + `EXPIRE`）。

### 1.2 Hash：一个 key 下的多个字段

Hash 相当于"key 对应一个 Map"，适合存一个对象的多个属性——比起把整个对象序列化成一个 String，Hash 可以单独读写某一个字段，不用每次都读出整个对象再写回去。

| 命令 | 作用 |
|------|------|
| `HSET key field value [field value ...]` | 设置一个或多个字段 |
| `HGET key field` | 取一个字段的值 |
| `HGETALL key` | 取所有字段和值 |
| `HDEL key field` | 删除一个字段 |
| `HEXISTS key field` | 判断字段是否存在 |
| `HINCRBY key field n` | 某个字段原子自增 n |
| `HKEYS key` / `HVALS key` | 取所有字段名 / 所有值 |
| `HLEN key` | 字段数量 |

```bash
HSET user:1 name "Alice" age 25
> (integer) 2             # 本次新增了 2 个字段

HGET user:1 name
> "Alice"

HGETALL user:1
> 1) "name"
  2) "Alice"
  3) "age"
  4) "25"                 # 字段名和值按顺序交替返回

HINCRBY user:1 loginCount 1
> (integer) 1             # loginCount 字段不存在时从 0 开始自增

HDEL user:1 age
> (integer) 1             # 返回删除成功的字段数

HEXISTS user:1 age
> (integer) 0             # 已删除，返回 0
```

**典型场景**：存对象的多个属性（用户信息、配置项），需要单独更新/自增某个字段时优于"整个对象存成一个 JSON 字符串"。

### 1.3 List：有序的双端队列

List 按插入顺序排列，可以从左端（头部）和右端（尾部）插入或弹出元素，本质是一个双端队列。

| 命令 | 作用 |
|------|------|
| `LPUSH key value` | 从左侧（头部）插入 |
| `RPUSH key value` | 从右侧（尾部）插入 |
| `LPOP key` | 从左侧弹出并删除 |
| `RPOP key` | 从右侧弹出并删除 |
| `LRANGE key start stop` | 按范围查看（不删除） |
| `LLEN key` | 列表长度 |
| `BRPOP key timeout` | 阻塞式弹出，没数据就等待 |
| `LREM key count value` | 删除列表中指定的值 |

```bash
LPUSH queue "task1"
> (integer) 1             # 返回值是 push 之后列表的长度

RPUSH queue "task2"
> (integer) 2

LRANGE queue 0 -1
> 1) "task1"
  2) "task2"               # 0 表示第一个元素，-1 表示最后一个，0 -1 即查询全部

RPOP queue
> "task2"                  # 从右侧取出；配合 LPUSH 就是 FIFO 队列

LLEN queue
> (integer) 1

BRPOP queue 5
> (nil)                    # 队列为空时阻塞等待 5 秒，超时返回 nil
```

**典型场景**：消息队列（`LPUSH` 生产 + `RPOP` 消费 = FIFO）、最近浏览/操作记录（`LPUSH` 写入新记录 + `LRANGE 0 9` 取最近 10 条）。

### 1.4 Set：无序不重复集合

Set 里的元素不能重复，添加重复元素会被自动忽略，类似 Java 的 `HashSet`。

| 命令 | 作用 |
|------|------|
| `SADD key member [member ...]` | 添加元素（自动去重） |
| `SMEMBERS key` | 取出所有元素 |
| `SISMEMBER key member` | 判断元素是否存在 |
| `SREM key member` | 删除元素 |
| `SCARD key` | 元素数量 |
| `SINTER key1 key2` | 交集 |
| `SUNION key1 key2` | 并集 |
| `SDIFF key1 key2` | 差集（在 key1 但不在 key2） |

```bash
SADD tags:post:1 "java" "redis" "spring"
> (integer) 3             # 返回实际新增的元素个数

SADD tags:post:1 "java"
> (integer) 0             # "java" 已存在，不会重复添加，返回 0

SMEMBERS tags:post:1
> 1) "java"
  2) "redis"
  3) "spring"              # 顺序不保证，Set 本身无序

SISMEMBER tags:post:1 "java"
> (integer) 1             # 1 表示存在，0 表示不存在

SADD tags:post:2 "java" "vue"
> (integer) 2

SINTER tags:post:1 tags:post:2
> 1) "java"                # 两篇文章共同的标签
```

**典型场景**：去重（`SADD` 天然去重）、标签系统、共同关注/好友关系（`SINTER` 求交集）。

### 1.5 ZSet（Sorted Set）：带分数的有序集合

ZSet 和 Set 一样元素不重复，但每个元素额外带一个 `score`（分数），Redis 按分数自动排序——这是实现排行榜最直接的数据结构。

| 命令 | 作用 |
|------|------|
| `ZADD key score member` | 添加元素及分数（已存在则更新分数） |
| `ZSCORE key member` | 查看某元素的分数 |
| `ZINCRBY key increment member` | 给某元素的分数累加 |
| `ZRANGE key start stop` | 按分数从低到高取范围 |
| `ZREVRANGE key start stop` | 按分数从高到低取范围 |
| `ZRANGE ... WITHSCORES` | 同时返回分数 |
| `ZRANK key member` | 查看排名（从低到高，从 0 开始） |
| `ZRANGEBYSCORE key min max` | 按分数区间查询 |
| `ZREM key member` | 删除元素 |

```bash
ZADD leaderboard 100 "Alice" 85 "Bob" 92 "Charlie"
> (integer) 3             # 本次新增的元素个数

ZSCORE leaderboard "Alice"
> "100"

ZINCRBY leaderboard 10 "Alice"
> "110"                    # Alice 的分数变成 110

ZREVRANGE leaderboard 0 2
> 1) "Alice"
  2) "Charlie"
  3) "Bob"                 # 分数最高的前 3 名，按分数从高到低

ZREVRANGE leaderboard 0 2 WITHSCORES
> 1) "Alice"
  2) "110"
  3) "Charlie"
  4) "92"
  5) "Bob"
  6) "85"                  # 元素和分数交替返回

ZRANK leaderboard "Bob"
> (integer) 0             # 升序排名，分数最低的排第 0 名

ZRANGEBYSCORE leaderboard 90 120
> 1) "Charlie"
  2) "Alice"                # 分数在 90~120 之间的元素，按分数升序
```

**典型场景**：排行榜（分数=积分），延迟队列（分数=触发时间戳，定时用 `ZRANGEBYSCORE` 取到期任务）。

## 2. Spring Boot 整合 Redis

### 2.1 依赖与配置

```kotlin
// build.gradle.kts
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-data-redis")
}
```

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password:             # 没有密码就留空
      database: 0
      timeout: 3000ms
      lettuce:              # 默认的 Redis 客户端
        pool:
          max-active: 16
          max-idle: 8
          min-idle: 4
```

### 2.2 配置序列化方式

#### 为什么不能用默认序列化

`RedisTemplate<String, Object>` 默认用 JDK 原生序列化（`JdkSerializationRedisSerializer`），把对象转成 Java 的二进制字节流存进 Redis。两个问题：

1. **不可读**：`redis-cli` 执行 `GET key` 看到的是一堆乱码，调试时完全看不出存的是什么
2. **体积大**：JDK 序列化会带上类的元信息，同样的数据比 JSON 占用更多空间

所以实际项目里几乎都会换成 JSON 序列化，完整配置如下：

```java
@Configuration
public class RedisConfig {
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);

        // Key 用 String 序列化
        template.setKeySerializer(new StringRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());

        // Value 用 JSON 序列化
        ObjectMapper om = new ObjectMapper();
        om.registerModule(new JavaTimeModule());
        om.activateDefaultTyping(om.getPolymorphicTypeValidator(),
            ObjectMapper.DefaultTyping.NON_FINAL);
        GenericJackson2JsonRedisSerializer jsonSerializer =
            new GenericJackson2JsonRedisSerializer(om);

        template.setValueSerializer(jsonSerializer);
        template.setHashValueSerializer(jsonSerializer);

        template.afterPropertiesSet();
        return template;
    }
}
```

逐段拆解每一步在做什么、为什么这么配。

#### 为什么 Key 用 String，Value 用 JSON

`RedisTemplate` 一共有 4 个序列化器，分两类：

| 序列化器 | 序列化对象 | 用什么 |
|---|---|---|
| `keySerializer` | Redis key 本身（如 `"user:1"`） | `StringRedisSerializer` |
| `hashKeySerializer` | Hash 结构里的字段名（如 `HSET user:1 name ...` 里的 `name`） | `StringRedisSerializer` |
| `valueSerializer` | 存的值本身（String/List/Set/ZSet 的元素） | JSON |
| `hashValueSerializer` | Hash 结构里字段对应的值 | JSON |

**Key 和字段名用 `StringRedisSerializer` 的原因**：key 和 hash 字段名本质是"名字"，是用来定位数据的，不是数据本身。如果用 JSON 序列化器去处理一个字符串 `"user:1"`，结果会变成带引号甚至带类型信息的一长串——不仅浪费空间，还会导致 `redis-cli` 里 `KEYS user:*`、`HGETALL user:1` 看到的 key/字段名全是乱码，没法直接调试。

**Value 用 JSON 的原因**：value 才是真正要存的数据，往往是一个对象（如 `User`）。JSON 既能完整保留对象结构，又是可读文本，`redis-cli` 里 `GET` 出来能直接看懂内容，方便排查问题。

一句话：**Key/字段名是"路标"，要简单可读；Value 是"货物"，需要结构化存储。**

#### JavaTimeModule：解决 LocalDateTime 序列化问题

```java
ObjectMapper om = new ObjectMapper();
om.registerModule(new JavaTimeModule());
```

Jackson 默认不认识 Java 8 引入的 `LocalDateTime`、`LocalDate`、`Instant` 等时间类型——直接序列化会报错，或者把 `LocalDateTime` 序列化成一个奇怪的数组 `[2026,5,21,10,30,0]`，反序列化时再也转不回来。`JavaTimeModule` 是 Jackson 官方提供的扩展，注册后才能把这些类型正确序列化成 `"2026-05-21T10:30:00"` 这种 ISO 格式字符串，反序列化时也能准确还原成 `LocalDateTime`。

17 节里说新项目统一用 `LocalDateTime` 存时间——只要 Entity/VO 里有这个类型的字段，缓存时**这一行就是必须的**，漏了会在序列化时直接抛异常。

#### activateDefaultTyping：反序列化时怎么知道转成哪个类型

```java
om.activateDefaultTyping(om.getPolymorphicTypeValidator(),
    ObjectMapper.DefaultTyping.NON_FINAL);
```

`RedisTemplate<String, Object>` 的 value 类型是 `Object`——存的时候可能是一个 `User`，也可能是 `List<DspConfig>`，类型五花八门。序列化成 JSON 后，字符串本身只有数据、没有类型信息，取出来反序列化时，Jackson 不知道该把这段 JSON 转成 `User` 还是别的类型。

`activateDefaultTyping` 让 Jackson 序列化时把 class 信息也写进 JSON（多一个 `"@class"` 字段），反序列化时就能按这个字段还原出正确的 Java 类型：

```json
{
  "@class": "com.example.entity.User",
  "id": 1,
  "name": "Alice",
  "createdAt": "2026-05-21T10:30:00"
}
```

`NON_FINAL` 表示"只给非 final 类加类型信息"——`String`、`Integer`、`Long` 这些 final 类型从 JSON 值的形态（字符串/数字）就能直接推断，不需要额外标注 `@class`。

#### afterPropertiesSet()：手动触发初始化

```java
template.afterPropertiesSet();
```

`RedisTemplate` 实现了 Spring 的 `InitializingBean` 接口——这个接口约定：所有 setter 调用完之后，Spring 容器会自动调一次 `afterPropertiesSet()`，让 Bean 基于已设置好的属性做初始化检查（这里会检查各个序列化器是否设置，没设置的用默认值兜底）。

正常情况下 **Spring 管理的 Bean 会自动调用这个方法，不需要手动写**。但这里是在 `@Bean` 方法里手动 `new RedisTemplate<>()`、手动调用一堆 `setXxxSerializer`——"设置属性"这一步是我们自己在方法体里做的，Spring 容器拿到的是一个已经构造好的对象，不会再帮它触发 `InitializingBean` 回调。所以需要在 `return` 之前手动调一次，确保初始化逻辑真正执行。

**一句话**：在 `@Bean` 方法里手动 `new` 出一个实现了 `InitializingBean` 的对象并设置完属性后，记得手动调用 `afterPropertiesSet()`。

## 3. RedisTemplate 操作

`RedisTemplate` 本身不直接提供 `GET`/`SET`/`HGET` 这类命令方法，而是按 1 节里的 5 种数据结构拆成 5 个"操作接口"，每个接口对应一种数据结构的命令集合：

| Operations 接口 | 对应数据结构 | 获取方式 |
|---|---|---|
| `ValueOperations` | String（1.1节） | `redisTemplate.opsForValue()` |
| `HashOperations` | Hash（1.2节） | `redisTemplate.opsForHash()` |
| `ListOperations` | List（1.3节） | `redisTemplate.opsForList()` |
| `SetOperations` | Set（1.4节） | `redisTemplate.opsForSet()` |
| `ZSetOperations` | ZSet（1.5节） | `redisTemplate.opsForZSet()` |

下面每一节用到的 `valueOps`、`hashOps`、`listOps` 等，都是先调用对应的 `opsForXxx()` 拿到这个接口的实现。

### 3.1 String 操作

```java
@Service
public class CacheService {
    private final RedisTemplate<String, Object> redisTemplate;
    private final ValueOperations<String, Object> valueOps;

    public CacheService(RedisTemplate<String, Object> redisTemplate) {
        this.redisTemplate = redisTemplate;
        // <String, Object> 和 RedisTemplate 的泛型一致：key 是 String，value 是 Object
        // 构造时提前拿到 valueOps，避免每次调用都重新 opsForValue()
        this.valueOps = redisTemplate.opsForValue();
    }

    // 存
    public void set(String key, Object value) {
        valueOps.set(key, value);
    }

    // 存 + 过期时间
    public void setWithExpire(String key, Object value, long seconds) {
        valueOps.set(key, value, seconds, TimeUnit.SECONDS);
    }

    // 取
    public Object get(String key) {
        return valueOps.get(key);
    }

    // 删
    public void delete(String key) {
        redisTemplate.delete(key);
    }

    // 判断是否存在
    public boolean hasKey(String key) {
        return Boolean.TRUE.equals(redisTemplate.hasKey(key));
    }

    // 设置过期时间
    public void expire(String key, long seconds) {
        redisTemplate.expire(key, seconds, TimeUnit.SECONDS);
    }

    // 原子自增（计数器）
    public long increment(String key) {
        return valueOps.increment(key);
    }

    // setIfAbsent = SETNX（分布式锁基础）
    public boolean setIfAbsent(String key, Object value, long seconds) {
        return Boolean.TRUE.equals(
            valueOps.setIfAbsent(key, value, seconds, TimeUnit.SECONDS));
    }
}
```

#### Boolean.TRUE.equals(...)：为什么不直接返回结果

`hasKey`、`setIfAbsent` 返回的都是 `Boolean.TRUE.equals(...)` 而不是直接返回方法结果，原因是 Spring Data Redis 这类判断方法的返回类型是**装箱的 `Boolean`**，可能是 `Boolean.TRUE`、`Boolean.FALSE`，也可能是 `null`（用 `null` 表示"连接异常、无法确定结果"这种边界情况）。

而我们的方法签名是基本类型 `boolean`，如果直接返回：

```java
public boolean hasKey(String key) {
    return redisTemplate.hasKey(key);  // Boolean → boolean 隐式拆箱
}
```

一旦 `hasKey()` 返回 `null`，自动拆箱会调用 `null.booleanValue()`，直接抛 `NullPointerException`。

`Boolean.TRUE.equals(result)` 是反过来调用——在确定非 `null` 的 `Boolean.TRUE` 上调用 `.equals(result)`：

| `result` 的值 | `Boolean.TRUE.equals(result)` |
|---|---|
| `Boolean.TRUE` | `true` |
| `Boolean.FALSE` | `false` |
| `null` | `false`（不抛异常） |

这是 Spring Data Redis API 里的固定写法——`hasKey`、`setIfAbsent`、3.4 节的 `isMember` 都是同样的模式，只要方法返回 `Boolean` 并且要转成 `boolean`，就套这个写法。

### 3.2 Hash 操作

```java
HashOperations<String, String, Object> hashOps = redisTemplate.opsForHash();

// 存对象的各个字段
hashOps.put("user:1", "name", "Alice");
hashOps.put("user:1", "age", 25);

// 批量存
Map<String, Object> fields = Map.of("name", "Alice", "age", 25, "email", "a@b.com");
hashOps.putAll("user:1", fields);

// 取单个字段
String name = (String) hashOps.get("user:1", "name");

// 取全部
Map<String, Object> all = hashOps.entries("user:1");

// 字段自增
hashOps.increment("user:1", "loginCount", 1);

// 删除字段
hashOps.delete("user:1", "email");
```

### 3.3 List 操作

```java
ListOperations<String, Object> listOps = redisTemplate.opsForList();

// 左推入
listOps.leftPush("queue", "task1");
listOps.leftPush("queue", "task2");

// 右弹出（FIFO 队列）
Object task = listOps.rightPop("queue");                          // 立即返回
Object task2 = listOps.rightPop("queue", 10, TimeUnit.SECONDS);  // 阻塞等待

// 范围查询
List<Object> recent = listOps.range("recent:user:1", 0, 9);  // 最近 10 条
```

### 3.4 Set 和 ZSet 操作

```java
SetOperations<String, Object> setOps = redisTemplate.opsForSet();

// 添加
setOps.add("tags:post:1", "java", "spring", "redis");

// 判断是否存在
boolean isMember = Boolean.TRUE.equals(setOps.isMember("tags:post:1", "java"));

// 交集（共同标签）
Set<Object> common = setOps.intersect("tags:post:1", "tags:post:2");

// ZSet 排行榜
ZSetOperations<String, Object> zSetOps = redisTemplate.opsForZSet();
zSetOps.add("leaderboard", "Alice", 100);
zSetOps.add("leaderboard", "Bob", 85);
zSetOps.incrementScore("leaderboard", "Alice", 10);   // Alice → 110

// 获取排名前 3（降序）
Set<Object> top3 = zSetOps.reverseRange("leaderboard", 0, 2);

// 获取带分数的结果
Set<ZSetOperations.TypedTuple<Object>> top3WithScores =
    zSetOps.reverseRangeWithScores("leaderboard", 0, 2);
```

## 4. StringRedisTemplate

如果只存字符串（不需要 JSON 序列化），用 `StringRedisTemplate` 更简单：

```java
@Service
public class SimpleCache {
    private final StringRedisTemplate stringRedis;

    public SimpleCache(StringRedisTemplate stringRedis) {
        this.stringRedis = stringRedis;
    }

    public void cacheUser(User user) {
        String json = objectMapper.writeValueAsString(user);
        stringRedis.opsForValue().set("user:" + user.getId(), json, 1, TimeUnit.HOURS);
    }

    public User getUser(Long id) {
        String json = stringRedis.opsForValue().get("user:" + id);
        return json != null ? objectMapper.readValue(json, User.class) : null;
    }
}
```

## 5. Spring Cache 注解（声明式缓存）

手动操作 RedisTemplate 很灵活，但简单的缓存场景可以用注解一行搞定：

### 5.1 启用缓存

```java
@SpringBootApplication
@EnableCaching
public class MyAppApplication { ... }
```

```yaml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 3600000   # 默认 TTL：1 小时（毫秒）
      key-prefix: "myapp:"
      cache-null-values: false  # 不缓存 null 值
```

### 5.2 注解使用

```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserMapper userMapper;

    // 查询时缓存：第一次查数据库，之后直接返回缓存
    @Cacheable(value = "users", key = "#id")
    public User getById(Long id) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BizException("User not found: " + id);
        }
        return user;
    }

    // 更新时同步更新缓存
    @CachePut(value = "users", key = "#user.id")
    public User update(User user) {
        userMapper.updateById(user);
        return user;
    }

    // 删除时清除缓存
    @CacheEvict(value = "users", key = "#id")
    public void delete(Long id) {
        userMapper.deleteById(id);
    }

    // 清除该缓存名下的所有条目
    @CacheEvict(value = "users", allEntries = true)
    public void clearCache() {}
}
```

`userMapper` 就是 18 节里 `extends BaseMapper<User>` 的那个 Mapper，`selectById`/`updateById`/`deleteById` 都是它自带的方法——缓存注解只是包了一层，Mapper 本身不需要做任何改动。

#### 执行流程：从第一次查询到缓存过期

`@Cacheable` 不是直接改了 `getById` 方法本身，而是 Spring 在它外面套了一个**代理对象**——调用方实际调的是代理，代理先检查缓存，需要时才把请求转发给真正的方法体。整个生命周期分三种情况：

**1. 第一次查询（缓存未命中）**

```
调用 userService.getById(1L)
    ↓
代理检查 Redis：key = "users::1" 存在吗？
    ↓ 不存在
执行真正的方法体：userMapper.selectById(1) 查数据库
    ↓
拿到 User 对象后，代理把结果写入 Redis：
  key = "users::1"
  value = 序列化后的 User
  TTL = 5.1 节配置的 time-to-live（如 1 小时）
    ↓
把 User 对象返回给调用方
```

**2. 后续查询（缓存命中）**

```
调用 userService.getById(1L)
    ↓
代理检查 Redis：key = "users::1" 存在吗？
    ↓ 存在
直接从 Redis 读出来反序列化成 User，返回
    ↓
方法体完全不执行，不会再查数据库
```

**3. 缓存过期之后**

TTL 到期后，Redis 会自动删除这个 key（和手动 `SETEX` 设置过期时间的 key 是同一种过期机制）。下一次调用 `getById(1L)` 时，代理发现 `users::1` 已经不存在，又走回"未命中"的流程：查数据库 → 重新写入缓存 → 重新开始计时 TTL。整个过程对调用方完全透明，不需要任何额外代码。

**缓存 key 的格式**：`@Cacheable` 生成的 Redis key 是 `value::key` 拼接而成，比如 `value = "users"`、`key = "#id"`（取方法参数 `id` 的值），`getById(1L)` 对应的 key 就是 `users::1`。如果配置了 `key-prefix: "myapp:"`，最终 key 是 `myapp:users::1`。

**`@CachePut` 和 `@Cacheable` 的区别**：`@CachePut` 标注的 `update` 方法**每次都会执行方法体**（不会先查缓存），执行完之后用返回值覆盖 Redis 里的缓存——这样数据库和缓存里的数据始终是更新后的最新值，不需要走"删除缓存等下次重新加载"这一步。

#### 不用注解，手动用 RedisTemplate 实现同样的效果

注解本质上是 Spring 帮你生成了"查缓存 → 未命中查 DB → 写缓存"这套逻辑。如果自己手写，就是把上面流程图里的每一步都变成显式代码：

```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserMapper userMapper;
    private final RedisTemplate<String, Object> redisTemplate;

    private static final String CACHE_PREFIX = "users::";
    private static final long TTL_HOURS = 1;

    // 对应 @Cacheable
    public User getById(Long id) {
        String key = CACHE_PREFIX + id;

        // 1. 先查缓存
        User cached = (User) redisTemplate.opsForValue().get(key);
        if (cached != null) {
            return cached;
        }

        // 2. 缓存未命中，查数据库
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BizException("User not found: " + id);
        }

        // 3. 写入缓存，设置 TTL
        redisTemplate.opsForValue().set(key, user, TTL_HOURS, TimeUnit.HOURS);
        return user;
    }

    // 对应 @CachePut：不查缓存，执行完直接覆盖
    public User update(User user) {
        userMapper.updateById(user);
        redisTemplate.opsForValue().set(
            CACHE_PREFIX + user.getId(), user, TTL_HOURS, TimeUnit.HOURS);
        return user;
    }

    // 对应 @CacheEvict(key = "#id")
    public void delete(Long id) {
        userMapper.deleteById(id);
        redisTemplate.delete(CACHE_PREFIX + id);
    }

    // 对应 @CacheEvict(allEntries = true)
    public void clearCache() {
        Set<String> keys = redisTemplate.keys(CACHE_PREFIX + "*");
        if (keys != null && !keys.isEmpty()) {
            redisTemplate.delete(keys);
        }
    }
}
```

逐个对比：

| 注解版 | 手动版 | 说明 |
|------|------|------|
| `@Cacheable(value="users", key="#id")` | `get(key)` → 命中返回，未命中查库再 `set(key, ..., ttl)` | 注解把"判断命中"这一步隐藏了 |
| `@CachePut(value="users", key="#user.id")` | 更新数据库后 `set(key, user, ttl)` | 都是"无条件覆盖缓存" |
| `@CacheEvict(key="#id")` | `delete(key)` | 完全等价 |
| `@CacheEvict(allEntries=true)` | `keys(pattern)` + `delete(keys)` | 注解一次调用搞定，手动需要先找出所有 key |

> `clearCache()` 里的 `redisTemplate.keys(pattern)` 在 Redis 数据量大时是一个**阻塞**操作（`KEYS` 命令会扫描全部 key），生产环境通常用 `SCAN` 命令代替，避免阻塞其他请求。

### 5.3 注解速查

| 注解 | 作用 | key 示例 |
|------|------|---------|
| `@Cacheable` | 有缓存则返回缓存，没有则执行方法并缓存结果 | `#id`、`#user.email` |
| `@CachePut` | 执行方法并更新缓存 | `#result.id` |
| `@CacheEvict` | 删除缓存 | `#id`、`allEntries=true` |
| `@Caching` | 组合多个缓存操作 | |

### 5.4 @Cacheable 的常见陷阱

```java
// 陷阱 1：同类内部调用不走缓存（和 @Transactional 同理，因为走的是 this 不是代理）
public User getById(Long id) { ... }
public User getByIdTwice(Long id) {
    this.getById(id);  // 不走缓存！
}

// 陷阱 2：缓存 null 值导致"缓存穿透"
// 配置 cache-null-values: false 或在方法中抛异常而非返回 null

// 陷阱 3：缓存雪崩（大量 key 同时过期）
// 解决：给 TTL 加随机偏移
```

## 6. 广告系统中的缓存实战

### 6.1 频控（Frequency Capping）

```java
// 每个用户每天最多看同一个广告 3 次
public boolean checkFrequencyCap(String userId, String adId, int maxPerDay) {
    String key = "freq:" + userId + ":" + adId + ":" + LocalDate.now();
    Long count = stringRedis.opsForValue().increment(key);

    if (count == 1) {
        // 第一次设置过期时间（当天结束时失效）
        stringRedis.expire(key, Duration.between(LocalTime.now(), LocalTime.MAX));
    }

    return count <= maxPerDay;
}
```

### 6.2 预算控制

```java
// 广告预算扣减（原子操作）
public boolean deductBudget(String campaignId, double cost) {
    String key = "budget:" + campaignId;
    // Lua 脚本保证原子性：读余额 → 判断 → 扣减
    String script = """
        local balance = tonumber(redis.call('GET', KEYS[1]) or '0')
        local cost = tonumber(ARGV[1])
        if balance >= cost then
            redis.call('DECRBY', KEYS[1], ARGV[1])
            return 1
        else
            return 0
        end
    """;
    Long result = stringRedis.execute(
        new DefaultRedisScript<>(script, Long.class),
        List.of(key),
        String.valueOf((long)(cost * 100))  // 用分为单位避免浮点精度问题
    );
    return result != null && result == 1;
}
```

### 6.3 分布式锁

```java
// 简易分布式锁（生产环境建议用 Redisson）
public boolean tryLock(String lockKey, String requestId, long expireSeconds) {
    return Boolean.TRUE.equals(
        stringRedis.opsForValue().setIfAbsent(
            "lock:" + lockKey, requestId, expireSeconds, TimeUnit.SECONDS));
}

public void unlock(String lockKey, String requestId) {
    // Lua 脚本保证"检查 + 删除"的原子性
    String script = """
        if redis.call('GET', KEYS[1]) == ARGV[1] then
            return redis.call('DEL', KEYS[1])
        else
            return 0
        end
    """;
    stringRedis.execute(
        new DefaultRedisScript<>(script, Long.class),
        List.of("lock:" + lockKey),
        requestId);
}
```

### 6.4 实时计数（广告展示/点击统计）

```java
// 按小时维度统计广告点击数
public void recordClick(String adId) {
    String hourKey = "clicks:" + adId + ":" +
        LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHH"));

    stringRedis.opsForValue().increment(hourKey);
    stringRedis.expire(hourKey, 48, TimeUnit.HOURS);  // 保留 48 小时
}

// 查询某个广告过去 24 小时的点击数
public long getClicks24h(String adId) {
    LocalDateTime now = LocalDateTime.now();
    long total = 0;
    for (int i = 0; i < 24; i++) {
        String hourKey = "clicks:" + adId + ":" +
            now.minusHours(i).format(DateTimeFormatter.ofPattern("yyyyMMddHH"));
        String val = stringRedis.opsForValue().get(hourKey);
        if (val != null) total += Long.parseLong(val);
    }
    return total;
}
```

## 7. 缓存常见问题与解决方案

| 问题 | 含义 | 解决方案 |
|------|------|---------|
| 缓存穿透 | 查询不存在的数据，每次都打到数据库 | 缓存空值 / 布隆过滤器 |
| 缓存击穿 | 热点 key 过期瞬间大量请求打到数据库 | 互斥锁重建 / 热点 key 不过期 |
| 缓存雪崩 | 大量 key 同时过期 | TTL 加随机偏移 / 多级缓存 |
| 数据一致性 | 数据库更新了但缓存没更新 | Cache Aside 模式（先更新 DB，再删缓存） |

### Cache Aside 模式

```java
// 读：先查缓存 → 没有再查数据库 → 写入缓存
public User getUser(Long id) {
    String key = "user:" + id;
    User user = (User) redisTemplate.opsForValue().get(key);
    if (user != null) return user;

    user = userRepo.findById(id).orElse(null);
    if (user != null) {
        redisTemplate.opsForValue().set(key, user, 1, TimeUnit.HOURS);
    }
    return user;
}

// 写：先更新数据库 → 再删除缓存（不是更新缓存）
@Transactional
public User updateUser(User user) {
    User saved = userRepo.save(user);
    redisTemplate.delete("user:" + user.getId());
    return saved;
}
```

为什么是"删除缓存"而不是"更新缓存"？因为并发场景下，两个线程同时更新数据库再更新缓存，可能导致缓存是旧值。删除缓存让下次读取时重新从数据库加载，更安全。

## 8. 小结

| 主题 | 关键要点 |
|------|---------|
| 五种数据结构 | String（缓存/计数器）、Hash（对象）、List（队列）、Set（去重）、ZSet（排行榜） |
| RedisTemplate | opsForValue / opsForHash / opsForList / opsForSet / opsForZSet |
| 序列化 | 默认 JDK 序列化不可用，换 JSON 或用 StringRedisTemplate |
| Spring Cache | @Cacheable / @CachePut / @CacheEvict，简单场景一行注解 |
| 缓存模式 | Cache Aside（先更新 DB 再删缓存）是最常用模式 |
| 常见问题 | 穿透（缓存空值）、击穿（互斥锁）、雪崩（TTL 随机偏移） |
| 分布式锁 | SETNX + 过期时间 + Lua 脚本保证原子性；生产用 Redisson |
| 广告场景 | 频控、预算控制、实时计数 |

---

> **下一篇预告**：HTTP 客户端——RestTemplate、WebClient 与远程接口调用