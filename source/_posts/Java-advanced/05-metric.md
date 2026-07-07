---
title: 'Java全貌(5) | 监控指标入门：Micrometer + Prometheus'
date: 2026-05-05
abbrlink: 05
tags:
  - Micrometer
  - Prometheus
  - 监控
  - 可观测性
  - Spring Boot
categories:
  - java-advanced
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

你的服务现在能查日志看每一条请求流水，但回答不了这类问题：过去 5 分钟下单 QPS 是多少？支付接口的超时率有没有突然飙高？整体下单成功率是多少？这些"聚合的、实时的、能盯着看的"数字，就是 metrics（指标）要解决的。这篇用一个常见的订单服务场景，把 Micrometer + Prometheus 从原理到埋点讲清楚。

<!-- more -->

## 1. 先想清楚：metrics 到底是什么

### 1.1 日志 vs 指标，解决不同的问题

你已经有 AOP 日志了，为什么还要 metrics？因为它俩回答的是不同维度的问题：

| | 日志（Logging） | 指标（Metrics） |
|---|---|---|
| 记录什么 | 一件一件具体的事 | 聚合后的数字 |
| 例子 | "13:05:01 req-123 下单成功，订单号 20260605..." | "过去 1 分钟下单 480 次，成功 460 次" |
| 回答的问题 | 某一次请求发生了什么 | 整体趋势怎么样、有没有异常 |
| 数据量 | 大（每件事一条） | 小（只存聚合值） |
| 适合 | 事后排查具体问题 | 实时监控、告警、看趋势 |

一个类比：日志是"监控摄像头录下的每一帧画面"，指标是"商场门口那块写着'今日客流 3201 人'的电子屏"。出了事要回看录像（日志），但平时盯着看的是电子屏（指标）。

### 1.2 可观测性（Observability）三件套

监控领域有个标准说法，叫可观测性的三大支柱：

| 支柱 | 是什么 | 你的项目现状 |
|------|--------|-------------|
| Logging（日志） | 离散的事件记录 | ✅ 已有 AOP 日志 |
| Metrics（指标） | 聚合的数值 | ⬅ 这篇要做 |
| Tracing（链路追踪） | 一个请求跨多个服务的完整路径 | 有 requestId，还没串成 trace |

做完 metrics，你的可观测性就补上一大块了。

---

## 2. 整体架构：谁负责什么

先建立全局认知，避免一上来陷进细节。整条链路有三个角色：

<pre style="display:none">
graph TB
    subgraph "你的应用（订单服务）"
        direction TB
        MC["Micrometer<br/>在代码里埋点，把指标存在内存里<br/>（下单 +1、记录耗时...）"]
        Endpoint["/actuator/prometheus<br/>← 暴露成 HTTP 端点，吐出指标文本"]
        MC --- Endpoint
    end
    Endpoint -->|Prometheus 定时来抓（pull）| Prom["Prometheus<br/>定时抓取 + 存储<br/>（时序数据库）"]
    Prom -->|查询| Grafana["Grafana<br/>画成可视化大盘"]

</pre>
![](/images/Java-advanced/IMG-20260707-000019.png)







| 角色 | 职责 | 类比 |
|------|------|------|
| **Micrometer** | 在 Java 代码里埋点、在内存里维护指标 | 商场里的计数器 |
| **`/actuator/prometheus`** | 把当前指标值暴露成一个网页 | 把计数器的数字写在门口的牌子上 |
| **Prometheus** | 定时来抓这个网页、存成时序数据 | 每隔 15 秒来抄一次牌子的人 |
| **Grafana** | 把存的数据画成图表（可选） | 把历史数字画成趋势图的大屏 |

**一个关键点：Prometheus 是"主动来抓"（pull 模式），不是你"推给它"。** 你的应用只负责把指标摆在 `/actuator/prometheus` 这个网页上，Prometheus 配好后每隔几秒自己来抓一次。这点和很多人想的"应用主动上报"相反。

为什么用 pull？因为 Prometheus 可以自己控制抓取频率、知道哪些目标活着（抓不到就是挂了），运维上更可控。

---

## 3. Micrometer 是什么

### 3.1 它是个"门面"

你应该还记得日志体系里的 SLF4J——它本身不打日志，只是一个统一的接口，背后可以接 Logback、Log4j 等不同实现。**Micrometer 之于监控，就像 SLF4J 之于日志**：

<pre style="display:none">
graph TB
    Code["你的代码"] -->|调用统一 API 埋点| Facade["Micrometer（门面，统一接口）"]
    Facade --> Prom["Prometheus<br/>（你选这个）"]
    Facade --> Other["其他监控系统<br/>（Datadog 等）"]
    Facade --> Another["又一个监控系统<br/>（CloudWatch 等）"]

</pre>
![](/images/Java-advanced/IMG-20260707-000020.png)







好处：你的埋点代码只调 Micrometer 的 API，将来要从 Prometheus 换成别的监控系统，**业务代码一行不用改**，只换底层依赖。

### 3.2 MeterRegistry：指标的"注册中心"

理解 Micrometer，核心就是理解一个对象——`MeterRegistry`。

**Meter（仪表）** 是 Micrometer 里"一个指标"的统称（Counter、Gauge、Timer 都是 Meter）。**Registry（注册表）** 就是管理所有这些指标的容器。

<pre style="display:none">
graph TB
    Registry["MeterRegistry（一个大容器，管理所有指标）"] --> Meters["Counter: 下单请求总数<br/>Counter: 下单失败次数<br/>Timer: 下单耗时<br/>Gauge: 当前队列长度<br/>..."]

</pre>
![](/images/Java-advanced/IMG-20260707-000021.png)







| 概念 | 是什么 | 类比 |
|------|--------|------|
| `Meter` | 单个指标的统称 | 一个仪表盘上的一个表 |
| `MeterRegistry` | 管理所有 Meter 的容器 | 整个仪表盘 |

**为什么所有指标都要"注册"到 MeterRegistry？** 因为 Prometheus 来抓取时，是问 MeterRegistry："把你管的所有指标的当前值给我。" 没注册进去的指标，Prometheus 就看不到。所以埋点的本质是：**创建一个指标 + 把它注册到 MeterRegistry**。

在 Spring Boot 里，`MeterRegistry` 是自动配置好的一个 Bean，你直接注入就能用：

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final MeterRegistry meterRegistry;  // 直接注入，Spring 已经准备好了
}
```

---

## 4. 四种核心指标类型

这是 Micrometer 的核心，也是最需要理解的部分。选错类型，指标就没意义。判断用哪种，就看你要记录的数字**有什么特性**。

| 类型 | 特性 | 一句话 | 例子 |
|------|------|--------|---------|
| **Counter** | 只增不减 | 累计发生了多少次 | 下单总次数、下单失败次数 |
| **Gauge** | 可增可减 | 此刻是多少 | 当前队列长度、活跃连接数 |
| **Timer** | 计时 + 计次 | 耗时多久、发生多频繁 | 下单耗时、支付接口响应时间 |
| **DistributionSummary** | 分布统计 | 数值的分布情况 | 订单金额分布、请求体大小 |

### 4.1 Counter：只增不减的计数器

最简单的指标，适合"累计次数"类的数据——只会往上加，永远不减。

```java
// 创建一个 Counter 并注册
Counter orderCounter = Counter.builder("order.create.total")  // 指标名
        .description("下单请求总数")
        .register(meterRegistry);                              // 注册到 registry

// 埋点：每次下单 +1
orderCounter.increment();
```

适合：下单总次数、下单失败次数、限流触发次数、各种"发生了多少次"。

**为什么 Counter 只增不减？** 因为 Prometheus 真正关心的不是"累计值"本身，而是**变化率**。比如累计下单数从 1000 涨到 1480，Prometheus 算出"每秒涨多少"就是 QPS。只增不减的特性让"算速率"这件事变得简单可靠（重启会归零，Prometheus 也能识别处理）。

### 4.2 Gauge：可上可下的"瞬时值"

适合"此刻是多少"类的数据，会上下波动。

```java
// 监控一个队列的当前长度
Gauge.builder("order.log.queue.size", orderLogQueue, Queue::size)
        .description("待写入的 order_log 队列长度")
        .register(meterRegistry);
```

注意 Gauge 的用法和 Counter 不一样——**你不手动设值，而是给它一个"取值的方法"**（上面的 `Queue::size`）。Prometheus 每次来抓取时，Gauge 就调用这个方法拿到此刻的值。

适合：当前队列长度、线程池活跃线程数、当前在线连接数、缓存里的条目数。

| | Counter | Gauge |
|---|---|---|
| 方向 | 只增 | 可增可减 |
| 怎么更新 | 你主动 `increment()` | 给个取值函数，抓取时自动调 |
| 问的问题 | 一共发生了多少次 | 现在是多少 |

### 4.3 Timer：又计时又计次

服务端最重要的指标类型之一——同时记录"耗时多久"和"发生多少次"。

```java
Timer orderTimer = Timer.builder("order.create.duration")
        .description("下单处理耗时")
        .register(meterRegistry);

// 用法一：包住一段代码计时
OrderResult result = orderTimer.record(() -> {
    return doCreateOrder(request);   // 这段代码的耗时被记录
});

// 用法二：手动记录一个已知耗时
orderTimer.record(Duration.ofMillis(cost));
```

Timer 一个指标同时产出三类数据：

| 产出 | 含义 |
|------|------|
| `count` | 一共记录了多少次（相当于内置了一个 Counter） |
| `sum` | 总耗时 |
| `max` | 最大耗时 |

有了 count 和 sum，Prometheus 就能算出平均耗时；开启分位数后还能算 P50/P95/P99。

适合：下单整体耗时、调用支付/库存等下游接口的响应时间、任何"既要知道多快、又要知道多频繁"的场景。

### 4.4 DistributionSummary：分布统计

和 Timer 很像，但记录的不是时间，而是**任意数值的分布**。

```java
DistributionSummary amountSummary = DistributionSummary.builder("order.amount")
        .description("订单金额分布")
        .register(meterRegistry);

amountSummary.record(99.00);  // 记录一笔订单金额
```

适合：订单金额分布、请求体大小、批量处理的条数。用得比前三个少，了解即可。

---

## 5. 标签（Tag）：指标的"维度"

这是 Prometheus 体系的精髓，也是 metrics 比"几个全局计数器"强大的地方。

### 5.1 先看痛点：没有标签会怎样

假设你想统计每个支付渠道的下单次数。**没有标签的话**，你只能为每个渠道单独建一个 Counter，每个还得用不同的指标名：

```java
// 笨办法：每个渠道一个指标，连指标名都不一样
Counter alipayCount   = Counter.builder("order.create.alipay").register(meterRegistry);
Counter wechatCount   = Counter.builder("order.create.wechat").register(meterRegistry);
Counter unionpayCount = Counter.builder("order.create.unionpay").register(meterRegistry);  // 新增渠道还要改代码！
```

调用时还得自己 `if/else` 判断该加哪个：

```java
if (channel.equals("alipay"))   alipayCount.increment();
else if (channel.equals("wechat")) wechatCount.increment();
// ... 每加一个渠道，这里和上面都要改
```

问题很明显：指标名爆炸、每加一个渠道都要改代码、想"把所有渠道加起来"还得自己手动相加。标签就是来解决这个的。

### 5.2 标签是什么：给同一个指标加一个"分类维度"

**标签（Tag）= 给一个指标补上一个"按什么分类"的维度。** 用一张表来理解最直观：

<pre style="display:none">
graph TB
    Metric["指标名: order.create.total<br/>← 相当于一张表的表名"] --> R1["channel: alipay<br/>计数: 1200"]
    Metric --> R2["channel: wechat<br/>计数: 980"]
    Metric --> R3["channel: unionpay<br/>计数: 450"]

</pre>
![](/images/Java-advanced/IMG-20260707-000022.png)







- **指标名**（`order.create.total`）：相当于表名，整张表共用一个。
- **标签的名字**（`channel`）：相当于**列名**，是固定写死的字符串，表示"我按哪个维度分类"。
- **标签的值**（`alipay`/`wechat`/...）：相当于**单元格里的内容**，运行时变化，表示"这一行是哪个渠道"。

对应到代码里的 `.tag("channel", channel)`，**两个参数就是"列名"和"这一行的值"**：

```java
.tag("channel", channel)
//    ↑第一个     ↑第二个
//    标签名      标签值
//    固定字符串   一个变量，运行时取 "alipay" / "wechat" / "unionpay"
```

- **第一个参数 `"channel"`**：标签的名字，是你写死的固定字符串，永远是 `"channel"`，表示"这个维度叫渠道"。
- **第二个参数 `channel`**：注意这是个**变量**（不是字符串字面量），它的值在运行时由当前这次下单走的是哪个渠道决定——这次是支付宝，它就是 `"alipay"`；下次是微信，它就是 `"wechat"`。

> 一句话回答"为什么要有第一个参数 `channel`"：因为光有值 `"alipay"` 是没意义的——**`"alipay"` 是"什么"的值？** 是渠道？是地区？是用户等级？必须有个名字（列名）说清楚它是哪个维度。而且一个指标常常要按多个维度分类（见 5.4，比如同时按 `channel` 和 `status`），没有名字就分不清哪个值属于哪个维度。所以标签必须是"**名字 = 值**"成对出现。

### 5.3 那到底怎么记录？还是 increment 吗

是的，**记录方式没变，还是 `increment()`，只是在 `increment` 之前先用标签把"这次是哪个渠道"标出来**。完整写法：

```java
public void onOrderCreated(String channel) {   // channel 运行时传进来，比如 "alipay"
    Counter.builder("order.create.total")
            .tag("channel", channel)            // 标出这次的渠道
            .register(meterRegistry)            // ← 关键见下方说明
            .increment();                       // 给"这个渠道对应的那个计数器" +1
}
```

这里有个容易误解的点：**`register()` 不是"每次都新建一个计数器"。** Micrometer 的逻辑是——"指标名 + 全部标签值"唯一确定一个计数器：

- 第一次遇到 `order.create.total{channel="alipay"}`，它创建一个新计数器；
- 之后再遇到同样的 `order.create.total{channel="alipay"}`，它**找到上次那个**，直接 `+1`，不会重建。

所以你每次下单都照常调用上面这段，传入当次的 `channel`，Micrometer 会自动把它累加到对应渠道的那个计数器上。**支付宝走支付宝的计数、微信走微信的计数，互不干扰。** 新增一个 `"unionpay"` 渠道，第一次出现时自动建一条，代码一行都不用改——这就是标签相比 5.1 笨办法的核心好处。

如果嫌 builder 写法长，Micrometer 还有等价的简写：

```java
meterRegistry.counter("order.create.total", "channel", channel).increment();
//                     指标名                 标签名      标签值
```

### 5.4 抓取出来 & 多个标签

被 Prometheus 抓取出来，就是 5.2 那张表的文本形式——**同一个指标名，靠 `{}` 里的标签区分成多条**：

```
order_create_total{channel="alipay"}    1200
order_create_total{channel="wechat"}     980
order_create_total{channel="unionpay"}   450
```

之后在 Prometheus 里可以按标签随意切分、聚合：看单个渠道（`{channel="alipay"}`）、看所有渠道之和（`sum`）、按渠道分组排序——**全靠查询，不用改代码**。

一个指标也可以打**多个标签**，每多一个维度就多一个"列"：

```java
// 同时按 渠道 + 结果 两个维度分类
meterRegistry.counter("order.create.total",
        "channel", channel,            // 维度1：哪个渠道
        "result", success ? "success" : "failed")   // 维度2：成功还是失败
        .increment();
```

抓取出来就变成"渠道 × 结果"的组合，每个组合一条独立时间序列：

```
order_create_total{channel="alipay",result="success"}  1150
order_create_total{channel="alipay",result="failed"}     50
order_create_total{channel="wechat",result="success"}   960
...
```

这下你能体会到第一个参数（维度名）的必要性了——有了 `channel`、`result` 这两个名字，Prometheus 才能让你查"支付宝的失败率""所有渠道的总成功数"等等。

Timer 打标签也是一样的套路，只是最后从 `increment()` 换成 `record()`：

```java
// 下游接口响应耗时按 接口名 + 状态打标签
Timer.builder("downstream.response.duration")
        .tag("api", apiName)      // 维度1：payment / inventory / coupon
        .tag("status", status)    // 维度2：success / timeout / error
        .register(meterRegistry)
        .record(cost, TimeUnit.MILLISECONDS);
```

### 5.5 标签的坑：不要用高基数的值

标签的值如果种类太多（高基数），会撑爆 Prometheus 的内存。每个不同的标签值组合都是一条独立的时间序列。

| 适合做标签（值有限） | 不要做标签（值无限） |
|---------------------|---------------------|
| channel（就几个） | requestId（每次都不同！）|
| status（成功/超时/异常） | userId（千万级）|
| 订单类型（几种） | 时间戳、IP |

**铁律：标签值的种类要可控（几个到几十个），绝不能用 requestId、userId 这种近乎无限的值。** 这是新手最容易踩的生产事故。

---

## 6. 实战：给订单服务埋点

### 6.1 加依赖

```xml
<!-- Actuator：暴露监控端点 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>

<!-- Prometheus 注册表：让指标以 Prometheus 格式暴露 -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

加了这两个依赖，Spring Boot 会**自动**做两件事：自动配置好 `MeterRegistry` Bean、自动暴露 `/actuator/prometheus` 端点。

### 6.2 配置暴露端点

`application.yml` 里放行 Prometheus 端点（默认很多端点是关闭的）：

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus   # 放行这几个端点
```

启动后访问 `http://localhost:8080/actuator/prometheus`，能看到一大堆指标（JVM 内存、HTTP 请求、线程池……这些是自动就有的，不用你埋点）。

### 6.3 给下单埋点

在 `OrderService` 里加业务指标。先在构造时创建好指标：

```java
@Service
public class OrderService {

    private final Counter orderTotalCounter;    // 下单总数
    private final Counter orderFailedCounter;   // 下单失败次数
    private final Timer orderTimer;             // 下单耗时
    private final MeterRegistry meterRegistry;  // 留着给带标签的指标用

    public OrderService(MeterRegistry meterRegistry, ...) {
        this.meterRegistry = meterRegistry;
        this.orderTotalCounter = Counter.builder("order.create.total")
                .description("下单请求总数").register(meterRegistry);
        this.orderFailedCounter = Counter.builder("order.create.failed")
                .description("下单失败次数").register(meterRegistry);
        this.orderTimer = Timer.builder("order.create.duration")
                .description("下单处理耗时").register(meterRegistry);
    }
}
```

然后在下单逻辑里埋点：

```java
public OrderResult createOrder(OrderRequest request) {
    orderTotalCounter.increment();                 // 下单 +1

    return orderTimer.record(() -> {               // 整个下单过程计时
        OrderResult result = doCreateOrder(request);

        if (!result.isSuccess()) {
            orderFailedCounter.increment();        // 下单失败 +1
        }
        return result;
    });
}
```

给每个下游接口的调用结果埋带标签的指标：

```java
// 在调用下游接口处，记录每个接口的响应耗时和状态
Timer.builder("downstream.response.duration")
        .tag("api", apiName)          // payment / inventory / coupon
        .tag("status", status)        // success / timeout / error / rate_limited
        .register(meterRegistry)
        .record(costMs, TimeUnit.MILLISECONDS);
```

### 6.4 验证

启动应用，打几次下单请求，再访问 `/actuator/prometheus`，搜索你的指标名：

```
# HELP order_create_total 下单请求总数
# TYPE order_create_total counter
order_create_total 42.0

# HELP downstream_response_seconds 下游接口响应耗时
# TYPE downstream_response_seconds summary
downstream_response_seconds_count{api="payment",status="success"} 38.0
downstream_response_seconds_sum{api="payment",status="success"} 2.85
downstream_response_seconds_count{api="payment",status="timeout"} 9.0
```

能看到这些，说明埋点成功了。

> 注意命名：你代码里写 `order.create.total`（点号），暴露出来变成 `order_create_total`（下划线）——Micrometer 自动按 Prometheus 的命名规范转换了，这是正常的。

### 6.5 接 Prometheus 抓取

Prometheus 用一个 `prometheus.yml` 配置去哪抓：

```yaml
scrape_configs:
  - job_name: 'order-service'
    metrics_path: '/actuator/prometheus'   # 抓这个端点
    scrape_interval: 15s                    # 每 15 秒抓一次
    static_configs:
      - targets: ['localhost:8080']         # 抓哪个地址
```

用 Docker 跑 Prometheus（接上你之前的 Docker 知识）：

```yaml
# docker-compose.yml 里加一段
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

访问 `http://localhost:9090` 进 Prometheus 自带的查询界面，输入指标名就能看到曲线。

---

## 7. PromQL：从原始指标算出有用的数字

埋点埋好、Prometheus 也抓到了，但你打开一看，存进去的都是 `order_create_total 12345` 这种**原始累计值**——它本身没什么用，你真正想看的"每秒多少单（QPS）""成功率""P99 耗时"，都得**算**出来。算这些，靠的就是 Prometheus 的查询语言 **PromQL**。

这一节从零把 PromQL 的语法讲清楚，看完你能自己写查询，而不是只会抄。

### 7.1 先搞懂：Prometheus 里的数据长什么样

PromQL 操作的不是一个数字，而是**时间序列（time series）**。回忆第 5、6 节：每个"指标名 + 一组标签"唯一确定一条序列，Prometheus 每隔 15 秒抓一次，就给这条序列**追加一个 (时间, 值) 的点**。所以一条序列实际是这样一串带时间戳的点：

```
order_create_total{channel="alipay"}
   13:00:00 → 1000
   13:00:15 → 1003
   13:00:30 → 1009     ← 每隔 15 秒一个点，值在不断累加（Counter 只增）
   13:00:45 → 1015
```

理解了"数据 = 一条条随时间增长的点串"，下面的语法才好懂。

### 7.2 四种最基础的写法

**① 直接写指标名 → 取每条序列"此刻最新的值"**

```promql
order_create_total
```

这会返回**所有** `order_create_total` 序列当前最新的值（每个 channel 一条）。这种"每条序列一个当前值"的结果，叫**瞬时向量（instant vector）**。

**② 加 `{}` 按标签筛选 → 只要符合条件的序列**

`{}` 里写标签条件，就是第 6 节那些标签在这里发挥作用：

```promql
order_create_total{channel="alipay"}              # 只看支付宝这条
order_create_total{channel="alipay", result="failed"}  # 多个条件是"且"
order_create_total{channel!="alipay"}             # != 表示"不等于"
order_create_total{channel=~"alipay|wechat"}      # =~ 是正则匹配，看这两个
```

| 写法 | 含义 |
|---|---|
| `=` | 标签值等于 |
| `!=` | 不等于 |
| `=~` | 正则匹配 |
| `!~` | 正则不匹配 |

**③ 加 `[时间]` → 取一段时间内的"一串点"**

```promql
order_create_total{channel="alipay"}[1m]
```

末尾的 `[1m]` 叫**范围选择器（range selector）**，意思是"取过去 1 分钟内的所有点"（不是一个值，而是一串）。`1m`=1分钟、`5m`=5分钟、`1h`=1小时。这种"每条序列带一串点"的结果叫**范围向量（range vector）**，它是 `rate()` 这类函数的输入。

> 关键区别：不带 `[ ]` 是**一个**当前值（瞬时向量），带 `[5m]` 是**一段时间的一串值**（范围向量）。后面的 `rate()` 必须喂范围向量，因为"算变化率"得至少有两个点才能算。

**④ 用函数和运算 → 把原始值变成有用的数字**

这就是 PromQL 的重头戏，下面几小节专门讲。

### 7.3 `rate()`：把"累计值"变成"每秒速率"（最常用）

Counter 存的是只增的累计值（13:00 是 1000，13:01 是 1060），这个数字本身没意义，你关心的是"**这一分钟涨了多快**"。`rate()` 就干这个：

```promql
rate(order_create_total[1m])
```

它做的事：取过去 1 分钟那一串点，用"(末值 − 始值) ÷ 时间"算出**平均每秒增长了多少**。1 分钟涨了 60，`rate` 就得出 `1（每秒1单）`，这就是 **QPS**。

```
过去 1 分钟：1000 → 1060，涨了 60
rate = 60 / 60秒 = 1   →  即 1 QPS
```

**这就是为什么 Counter 一定要设计成只增不减**：只有单调递增，`rate()` 才能可靠地算速率（它还能自动识别"应用重启导致归零"的情况并修正）。

`[1m]` 这个窗口怎么选？窗口越大曲线越平滑但越迟钝，越小越灵敏但越抖。一般取抓取间隔的 4 倍以上，15s 抓一次就用 `[1m]` 起步。

### 7.4 算"比率"：两个 rate 相除

成功率、失败率、超时率，本质都是"**某一类 ÷ 总数**"。PromQL 里加减乘除直接写：

```promql
# 下单失败率 = 每秒失败数 / 每秒总数
rate(order_create_failed[5m]) / rate(order_create_total[5m])
```

注意分子分母都要先 `rate()` 再相除——**不能拿两个累计值直接除**（那是"开天辟地以来的总失败率"，看不出当下波动）。先各自算成速率，再相除，得到的才是"最近这段时间的失败率"。

### 7.5 聚合：`sum`、`by`、`without`

一个指标按标签拆成了很多条序列（每个 channel 一条），你常常想"**合起来看**"或"**按某个维度分组看**"。这就用聚合函数，最常用 `sum`（求和），还有 `avg`、`max`、`count` 等。

```promql
# 不分组：把所有渠道的 QPS 加成一个总 QPS
sum(rate(order_create_total[1m]))

# 按 channel 分组：每个渠道各算一条（by 保留哪个标签）
sum(rate(order_create_total[1m])) by (channel)
```

`by (channel)` 的意思是"**分组时只保留 channel 这个维度**，其余标签合并掉"。结果就是每个渠道一条线。它的反义词是 `without`（指定要丢掉哪些标签，其余保留）。

把聚合和筛选组合起来，就能写出"各下游接口的超时率"：

```promql
# 分子：每个接口"超时的"速率   分母：每个接口"全部的"速率   相除得各接口超时率
sum(rate(downstream_response_seconds_count{status="timeout"}[5m])) by (api)
  / sum(rate(downstream_response_seconds_count[5m])) by (api)
```

读法：从里往外——先 `{status="timeout"}` 筛出超时的、`rate` 算速率、`sum by (api)` 按接口汇总；分母同理但不筛 status（是全部）；两者相除，得到每个 `api` 各自的超时率。**PromQL 都是这样一层套一层、从内到外读。**

### 7.6 分位数：`histogram_quantile` 算 P99

第 4 节说过 Timer 会用"分桶直方图"统计耗时，桶数据的指标名后缀是 `_bucket`。要算 P99（99% 的请求都比这个值快），用专门的函数：

```promql
histogram_quantile(0.99, rate(order_create_duration_seconds_bucket[5m]))
#                  ↑要算的分位数        ↑对各个桶先算速率
```

`0.99` 换成 `0.5` 就是 P50（中位数）、`0.95` 就是 P95。**为什么 P99 比平均值更有用？** 平均值会被大量快请求"拉平"，掩盖掉少数卡顿的用户；P99 直接告诉你"最慢的那 1% 有多慢"，更能反映真实体验。

### 7.7 小结这一节的套路

写 PromQL 基本就是这套组合拳，按需叠加：

<pre style="display:none">
graph LR
    M["指标名<br/>选哪个指标"] --> L["{标签筛选}<br/>选哪些序列"]
    L --> R["[时间范围]<br/>取一段"]
    R --> Rate["rate() 算速率<br/>变成 QPS"]
    Rate --> Sum["sum() by() 聚合<br/>按维度汇总"]
    Sum --> Div["相除/比较<br/>算比率"]

</pre>
![](/images/Java-advanced/IMG-20260707-000023.png)







记住几个最高频的就够日常用了：`rate()` 算速率（QPS）、两个 rate 相除算比率（成功率）、`sum by()` 按维度汇总、`histogram_quantile` 算 P99。Grafana 大盘里每个面板背后，写的就是这样一行 PromQL（下一篇会讲）。

---

## 8. 原理：Micrometer 怎么做到低开销

埋点是在每个请求的热路径上执行的，如果埋点本身很慢，反而拖累性能。Micrometer 的设计目标就是把开销压到最低：

| 机制 | 说明 |
|------|------|
| 内存存储 | 指标值存在内存里，用线程安全的原子结构（类似你学过的 `LongAdder`） |
| 不阻塞主线程 | Counter 的 `increment()` 本质是原子加，几乎无锁、不阻塞 |
| Timer 用桶（bucket）而非存每条记录 | 不保存每次的原始耗时，而是用直方图分桶统计，省内存还能算分位数 |
| pull 模式 | 应用只在被抓取时才把内存里的值序列化成文本，平时零网络开销 |

这里能看到你之前学过的东西在起作用：Counter 的高并发计数用的就是 `LongAdder` 这类原子结构（并发篇讲过），保证多线程同时 `increment()` 不出错又快。Timer 用分桶直方图而非存原始值，是典型的"用精度换内存"——和 KV Cache 那种"用空间换时间"是相反方向的取舍思维。

---

## 9. 小结

| 主题 | 关键要点 |
|------|---------|
| 日志 vs 指标 | 日志记录每件事，指标是聚合数字；一个事后排查，一个实时监控 |
| 架构 | 应用埋点 → 暴露端点 → Prometheus 主动来抓（pull）→ Grafana 画图 |
| Micrometer | 监控领域的"门面"，类比 SLF4J；核心是 MeterRegistry |
| MeterRegistry | 管理所有指标的容器，指标必须注册进去才能被抓取 |
| 四种类型 | Counter（只增）、Gauge（可增减）、Timer（计时+计次）、Summary（分布） |
| 标签 Tag | 一个指标名 + 多维标签，按维度切分；**绝不用 requestId 等高基数值** |
| 实战 | 加 actuator + prometheus 依赖 → 暴露端点 → 注入 MeterRegistry 埋点 |
| PromQL | `rate()` 把累计 Counter 算成速率（QPS），分位数算 P99 |
| 低开销原理 | 内存原子结构（LongAdder）、Timer 分桶、pull 模式 |

对订单服务来说，加上 metrics 后，下单 QPS、各支付渠道/下游接口的成功率和超时率、整体下单成功率这些最关心的指标就能实时监控了——这也是真实服务端每天盯着的核心数据。

下一步可以用 Grafana 把这些指标画成可视化大盘，配色和布局都是现成模板，效果直观，适合放进项目展示。

---

> **下一篇预告**：用 Grafana 搭建订单服务监控大盘

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
