---
title: 'Java基础(22) | HTTP 客户端：RestTemplate、WebClient 与远程调用'
date: 2026-05-22
abbrlink: 22
tags:
  - Java
  - HTTP
  - RestTemplate
  - WebClient
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

广告系统需要频繁调用外部接口——向 DSP 发送竞价请求、调用素材审核服务、对接第三方数据平台。Java 中发起 HTTP 请求的方式经历了 `HttpURLConnection` → `HttpClient` → `RestTemplate` → `WebClient` 的演进。这篇文章讲后两者——它们是 Spring 生态中的标准选择。

<!-- more -->

## 1. RestTemplate vs WebClient

| 维度 | RestTemplate | WebClient |
|------|-------------|-----------|
| 引入版本 | Spring 3（2009） | Spring 5（2017） |
| 请求模式 | 同步阻塞 | 异步非阻塞（也支持同步） |
| 底层 | JDK HttpURLConnection / Apache HttpClient | Reactor Netty |
| 官方态度 | 维护模式（不再新增功能） | **推荐**，未来方向 |
| 适用场景 | 简单同步调用、传统项目 | 高并发、响应式、新项目 |
| 学习曲线 | 低 | 中（需了解响应式概念） |

**怎么选？** 传统 Spring MVC 项目两个都行，RestTemplate 上手更快。新项目或高并发场景优先 WebClient。

## 2. RestTemplate

### 2.1 注册为 Bean

```java
@Configuration
public class RestClientConfig {
    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
            .connectTimeout(Duration.ofSeconds(3))
            .readTimeout(Duration.ofSeconds(10))
            .build();
    }
}
```

### 2.2 GET 请求

```java
@Service
public class UserClient {
    private final RestTemplate restTemplate;

    public UserClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    // 基础 GET
    public String getHtml() {
        return restTemplate.getForObject("https://example.com", String.class);
    }

    // GET + 返回 Java 对象（自动 JSON 反序列化）
    public User getUser(Long id) {
        return restTemplate.getForObject(
            "https://api.example.com/users/{id}",
            User.class,
            id    // 路径变量替换
        );
    }

    // GET + 获取完整响应（状态码、响应头、响应体）
    public User getUserWithStatus(Long id) {
        ResponseEntity<User> response = restTemplate.getForEntity(
            "https://api.example.com/users/{id}",
            User.class,
            id
        );
        HttpStatusCode status = response.getStatusCode();  // 200
        HttpHeaders headers = response.getHeaders();
        User body = response.getBody();
        return body;
    }

    // GET + 查询参数
    public List<User> searchUsers(String name, int page) {
        String url = UriComponentsBuilder
            .fromHttpUrl("https://api.example.com/users")
            .queryParam("name", name)
            .queryParam("page", page)
            .queryParam("size", 10)
            .toUriString();
        // https://api.example.com/users?name=Alice&page=1&size=10

        User[] users = restTemplate.getForObject(url, User[].class);
        return Arrays.asList(users);
    }
}
```

### 2.3 POST 请求

```java
// POST JSON
public User createUser(String name, String email) {
    Map<String, String> body = Map.of("name", name, "email", email);
    return restTemplate.postForObject(
        "https://api.example.com/users",
        body,       // 自动序列化为 JSON
        User.class  // 响应体反序列化为 User
    );
}

// POST + 自定义请求头
public User createUserWithHeaders(CreateUserRequest req, String token) {
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    headers.setBearerAuth(token);

    HttpEntity<CreateUserRequest> entity = new HttpEntity<>(req, headers);

    ResponseEntity<User> response = restTemplate.exchange(
        "https://api.example.com/users",
        HttpMethod.POST,
        entity,
        User.class
    );
    return response.getBody();
}

// POST 表单
public String submitForm(String username, String password) {
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

    MultiValueMap<String, String> form = new LinkedMultiValueMap<>();
    form.add("username", username);
    form.add("password", password);

    HttpEntity<MultiValueMap<String, String>> entity = new HttpEntity<>(form, headers);

    return restTemplate.postForObject(
        "https://api.example.com/login",
        entity,
        String.class
    );
}
```

#### 自定义请求头：postForObject 还是 exchange？

上面两个带请求头的例子，一个用 `exchange`、一个用 `postForObject`，容易让人以为"自定义请求头必须用 `exchange`"——其实不是。`postForObject` 本身也支持传 `HttpEntity`（"POST 表单"那个例子就是这么写的），所以 `createUserWithHeaders` 改成下面这样同样可以工作：

```java
return restTemplate.postForObject(
    "https://api.example.com/users",
    entity,     // HttpEntity<CreateUserRequest>，带 headers
    User.class
);
```

两者真正的区别在**返回值**：

| 方法 | 返回值 | 能拿到什么 |
|------|--------|-----------|
| `postForObject` | `T`（只有响应体） | 反序列化后的 body |
| `exchange` | `ResponseEntity<T>` | body + 状态码 + 响应头 |

如果只要响应体，`postForObject` 更简洁；如果要读响应头（比如创建资源后从 `Location` 头取新资源地址）或检查状态码是不是 `201 Created`，就必须用 `exchange`，因为 `postForObject` 把这些信息都丢弃了。

另外，`exchange` 是唯一支持**所有 HTTP 方法**的方法——2.4 节的 `PATCH` 没有对应的 `patchForObject`，只能用 `exchange`。所以很多人习惯统一用 `exchange`，不用记 `postForObject`/`putForObject` 各自的参数顺序。

### 2.4 PUT / DELETE / PATCH

```java
// PUT
public void updateUser(Long id, User user) {
    restTemplate.put("https://api.example.com/users/{id}", user, id);
}

// DELETE
public void deleteUser(Long id) {
    restTemplate.delete("https://api.example.com/users/{id}", id);
}

// PATCH（需要用 exchange）
public User patchUser(Long id, Map<String, Object> fields) {
    HttpEntity<Map<String, Object>> entity = new HttpEntity<>(fields);
    ResponseEntity<User> response = restTemplate.exchange(
        "https://api.example.com/users/{id}",
        HttpMethod.PATCH,
        entity,
        User.class,
        id
    );
    return response.getBody();
}
```

### 2.5 异常处理

```java
// RestTemplate 在 4xx/5xx 时默认抛异常
try {
    User user = restTemplate.getForObject(url, User.class);
} catch (HttpClientErrorException e) {
    // 4xx 错误
    if (e.getStatusCode() == HttpStatus.NOT_FOUND) {
        return null;
    }
    throw e;
} catch (HttpServerErrorException e) {
    // 5xx 错误
    log.error("服务端错误: {}", e.getResponseBodyAsString());
    throw e;
} catch (ResourceAccessException e) {
    // 连接超时、读取超时
    log.error("请求超时: {}", e.getMessage());
    throw e;
}

// 或者自定义 ErrorHandler 统一处理
@Bean
public RestTemplate restTemplate() {
    RestTemplate rt = new RestTemplate();
    rt.setErrorHandler(new DefaultResponseErrorHandler() {
        @Override
        public void handleError(ClientHttpResponse response) throws IOException {
            if (response.getStatusCode().is4xxClientError()) {
                // 自定义 4xx 处理
            } else {
                super.handleError(response);
            }
        }
    });
    return rt;
}
```

### 2.6 拦截器（统一加请求头、日志）

```java
@Bean
public RestTemplate restTemplate() {
    RestTemplate rt = new RestTemplate();
    rt.setInterceptors(List.of((request, body, execution) -> {
        // 统一加请求头
        request.getHeaders().set("X-App-Name", "my-app");
        request.getHeaders().set("X-Request-Id", UUID.randomUUID().toString());

        // 日志
        log.info("HTTP {} {}", request.getMethod(), request.getURI());
        long start = System.currentTimeMillis();

        ClientHttpResponse response = execution.execute(request, body);

        log.info("HTTP {} {} → {} ({}ms)",
            request.getMethod(), request.getURI(),
            response.getStatusCode(), System.currentTimeMillis() - start);

        return response;
    }));
    return rt;
}
```

## 3. WebClient（Spring 5+）

### 3.1 依赖

`WebClient` 来自 `spring-webflux` 模块，所以要引入 `spring-boot-starter-webflux`：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```

Gradle 写法：

```kotlin
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-webflux")
}
```

> **注意**：引入 `webflux` 不代表你的项目变成了"响应式项目"——你完全可以在一个普通的 Spring MVC（`spring-boot-starter-web`）项目里，只用 `WebClient` 来发请求，其他部分照常写同步代码。两个 starter 可以共存，互不冲突。

### 3.2 创建 WebClient

`WebClient` 用 `WebClient.builder()` 这种"建造者模式"来配置——把所有公共配置（域名、默认请求头、日志/鉴权逻辑）在创建时一次性定好，之后每次发请求就不用重复写这些东西了。

```java
@Configuration
public class WebClientConfig {
    @Bean
    public WebClient webClient() {
        return WebClient.builder()
            .baseUrl("https://api.example.com")
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .defaultHeader("X-App-Name", "my-app")
            .filter(logFilter())     // 日志过滤器
            .build();
    }

    private ExchangeFilterFunction logFilter() {
        return ExchangeFilterFunction.ofRequestProcessor(request -> {
            log.info("HTTP {} {}", request.method(), request.url());
            return Mono.just(request);
        });
    }
}
```

逐项拆解 `builder()` 上配置的几个方法：

| 方法 | 作用 | 为什么要配置它 |
|---|---|---|
| `baseUrl("https://api.example.com")` | 设置这个 `WebClient` 实例的"基础域名" | 之后每次请求只需要写 `/users/{id}` 这种相对路径，不用每次都拼完整 URL；更重要的是，**域名可以做成配置项**（`@Value` 注入），不同环境（测试/预发/生产）指向不同的 DSP 地址，代码完全不用改 |
| `defaultHeader(...)` | 给这个 `WebClient` 发出的**所有**请求都自动加上某个请求头 | 比如 `Content-Type: application/json`、自定义的 `X-App-Name` 标识——这些是"每次请求都一样"的信息，写一次，所有请求自动带上，避免每个方法里重复写 |
| `.filter(...)` | 注册一个"请求/响应处理函数"，所有请求都会经过它 | 用于日志、鉴权、统一处理这类"横切逻辑"，下面单独讲 |

#### ExchangeFilterFunction 是什么

`ExchangeFilterFunction` 可以理解为 **WebClient 专属的"过滤器"**——和 [29 Tomcat 与 Servlet](/2026/05/29/Java-basic/29-tomcat-servlet/) 里讲的 `Filter` 是同一个思路：**每个请求发出去之前、响应回来之后，都会先经过这一层，可以在这里"加点东西"或者"看一眼"**。

它本质上是一个函数式接口，长这样：

```java
Mono<ClientResponse> filter(ClientRequest request, ExchangeFunction next);
```

- `request`：即将发出的请求
- `next`：调用 `next.exchange(request)` 才会真正把请求发出去
- 返回值：最终的响应

为了不用每次都写这么复杂的签名，Spring 提供了两个常用的静态工厂方法：

| 方法 | 时机 | 典型用途 |
|---|---|---|
| `ExchangeFilterFunction.ofRequestProcessor(req -> ...)` | **请求发出前** | 打印请求日志、注入 token/签名、记录开始时间 |
| `ExchangeFilterFunction.ofResponseProcessor(resp -> ...)` | **响应返回后** | 打印响应日志、记录耗时、统一处理某些状态码 |

上面例子里的 `logFilter()` 用的是 `ofRequestProcessor`——每次请求发出前，打印一行 `HTTP GET /users/1` 的日志，然后 `return Mono.just(request)` 把请求原样传给下一环节（不修改它）。

**什么时候调用？** 和 Filter 链一样，**注册了几个 `.filter(...)`，就有几层"包裹"**，按注册顺序依次执行"请求前"逻辑，再发出真实请求，响应回来后再按相反顺序执行"响应后"逻辑。日常最常见的用法就是**统一打日志**和**统一往请求头里塞鉴权 token**（比如调用第三方接口需要签名时）。

### 3.3 同步调用（block）

#### 调用链每一步返回的是什么

`webClient.get().uri(...).retrieve().bodyToMono(User.class).block()` 这一长串，**每个方法返回的对象都不一样**，是一步步"换挡"的过程：

| 调用 | 返回类型 | 这一步在干什么 |
|---|---|---|
| `.get()` | `RequestHeadersUriSpec` | 声明这是一个 GET 请求，还没指定地址 |
| `.uri("/users/{id}", id)` | `RequestHeadersSpec` | 指定了请求地址，可以继续加请求头，但**还没真正发出请求** |
| `.retrieve()` | `ResponseSpec` | 表示"配置完了，准备发起请求并处理响应"——但这一步**返回的还不是响应数据**，而是一个"响应规格"，可以在它上面声明"4xx/5xx 时怎么处理"（即 3.5 节的 `onStatus`） |
| `.bodyToMono(User.class)` | `Mono<User>` | **这一步才是真正"取数据"的关键**：告诉 WebClient"把响应体的 JSON 反序列化成 `User` 对象"，并包装成 `Mono<User>` |
| `.block()` | `User` | 阻塞等待，把 `Mono<User>` 拆开，拿到真正的 `User` 对象 |

**为什么 `retrieve()` 后面一定要接一个 `bodyTo...`？** 因为 `retrieve()` 本身只是"发起请求 + 准备好处理响应状态码"，它**不知道你想把响应体解析成什么类型**——是单个对象（`User`）还是列表（`List<User>`）、还是干脆不需要返回体（`Void`）。`bodyToMono(Class)` / `bodyToFlux(Class)` / `toBodilessEntity()` 这些方法的作用就是**告诉 WebClient 该用哪种方式解析响应体**，所以 `retrieve()` 必须搭配其中一个一起用，缺了它，请求虽然能发出去，但你拿不到任何结果。

#### Mono 与 Flux 的区别

可以类比"取餐小票"：请求刚发出去，菜还没做好，WebClient 先给你一张小票，等结果真的回来了，再把值"填"进这张小票里。区别在于**小票对应几份餐**：

| | `Mono<T>` | `Flux<T>` |
|---|---|---|
| 代表多少个结果 | **0 或 1 个** | **0 到 N 个**（一个序列/数据流） |
| 类比 | 一张小票，对应一份餐 | 一张小票，对应一筐餐——会一份一份地往外发 |
| 典型用法 | 请求一个用户，响应体是单个 JSON 对象 → `bodyToMono(User.class)` | 请求用户列表，响应体是 JSON 数组 → `bodyToFlux(User.class)`，每个数组元素就是流里的一个元素 |
| 拆出最终值 | `.block()` 拿到一个 `T`（或 `null`） | `.collectList().block()` 把流里所有元素收集成 `List<T>` 再拿出来；也可以 `.toStream()` 等方式逐个处理 |

**为什么要区分这两种？** 因为"一个结果"和"一连串结果"在响应式编程里处理方式不同——`Mono` 只需要关心"有没有/到了没"，`Flux` 还需要关心"还有没有下一个、什么时候算结束"。把这两种情况用不同的类型表达出来，编译器和 API 就能帮你避免"把单个结果当成列表处理"之类的错误。

| 方法 | 作用 |
|---|---|
| `.retrieve()` | 发起请求，并声明"我要处理这个响应"。如果响应是 4xx/5xx，`retrieve()` 会自动抛异常（3.5 节会细讲） |
| `.bodyToMono(User.class)` | 把响应体的 JSON 反序列化成一个 `User` 对象，包装成 `Mono<User>` |
| `.bodyToFlux(User.class)` | 响应是一个 JSON 数组时，反序列化成多个 `User`，包装成 `Flux<User>` |
| `.block()` | **阻塞当前线程**，等待 `Mono`/`Flux` 真正拿到结果，再把值"拆出来"返回 |

在传统的 Spring MVC 项目里（每个请求一个线程，本身就是同步模型），调用 `.block()` 把异步结果转换成同步返回值是很常见的——`Controller` 方法本身要 `return User`，不能返回一个"小票"给前端。

```java
@Service
public class UserClient {
    private final WebClient webClient;

    public UserClient(WebClient webClient) {
        this.webClient = webClient;
    }

    // GET
    public User getUser(Long id) {
        return webClient.get()
            .uri("/users/{id}", id)
            .retrieve()
            .bodyToMono(User.class)
            .block();  // 阻塞等待结果（在传统 MVC 项目中常用）
    }

    // GET 列表
    public List<User> listUsers() {
        return webClient.get()
            .uri("/users")
            .retrieve()
            .bodyToFlux(User.class)
            .collectList()
            .block();
    }

    // POST
    public User createUser(CreateUserRequest req) {
        return webClient.post()
            .uri("/users")
            .bodyValue(req)
            .retrieve()
            .bodyToMono(User.class)
            .block();
    }

    // PUT
    public User updateUser(Long id, UpdateUserRequest req) {
        return webClient.put()
            .uri("/users/{id}", id)
            .bodyValue(req)
            .retrieve()
            .bodyToMono(User.class)
            .block();
    }

    // DELETE
    public void deleteUser(Long id) {
        webClient.delete()
            .uri("/users/{id}", id)
            .retrieve()
            .toBodilessEntity()
            .block();
    }
}
```

### 3.4 异步调用（不阻塞）

如果项目本身是响应式的（比如用 WebFlux 写 Controller），就不应该调用 `.block()`——一旦 `block()`，当前线程就被"卡住"等结果，违背了响应式"不阻塞线程"的初衷。这种场景下，方法直接返回 `Mono`/`Flux`，把"什么时候要结果"的决定权交给调用者（最终由 WebFlux 框架在合适的时机去"拆小票"）。

```java
// 返回 Mono / Flux，由调用者决定何时获取结果
public Mono<User> getUserAsync(Long id) {
    return webClient.get()
        .uri("/users/{id}", id)
        .retrieve()
        .bodyToMono(User.class);
}

// 并发调用多个接口
public Mono<UserPage> getUserPage(Long userId) {
    Mono<User> userMono = webClient.get()
        .uri("/users/{id}", userId)
        .retrieve().bodyToMono(User.class);

    Mono<List<Order>> ordersMono = webClient.get()
        .uri("/users/{id}/orders", userId)
        .retrieve().bodyToFlux(Order.class).collectList();

    // 两个请求并发执行，全部完成后合并
    return Mono.zip(userMono, ordersMono, (user, orders) ->
        new UserPage(user, orders));
}
```

`Mono.zip(...)` 的作用：手里有两张"小票"（两个还没到的结果），**等两张小票都兑换成功后**，用提供的函数把两个结果合并成一个新对象，再包成一张新的"小票"返回。两个请求是**并发发出**的，不是"等第一个完成再发第二个"——这正是异步调用相比 `block()` 的优势：不需要为了等第一个结果而占用线程。

### 3.5 异常处理

`.retrieve()` 本身就有"默认的异常处理"——响应状态码是 4xx 或 5xx 时，会自动抛出 `WebClientResponseException`（不需要你手动判断状态码）。`.onStatus(...)` 是用来**覆盖默认行为**的：对特定的状态码，转换成你自己定义的异常类型，方便上层用 `catch` 区分处理。

```java
public User getUser(Long id) {
    return webClient.get()
        .uri("/users/{id}", id)
        .retrieve()
        .onStatus(HttpStatusCode::is4xxClientError, response -> {
            if (response.statusCode() == HttpStatus.NOT_FOUND) {
                return Mono.error(new ResourceNotFoundException("User not found: " + id));
            }
            return response.bodyToMono(String.class)
                .flatMap(body -> Mono.error(new RuntimeException("Client error: " + body)));
        })
        .onStatus(HttpStatusCode::is5xxServerError, response ->
            Mono.error(new RuntimeException("Server error: " + response.statusCode())))
        .bodyToMono(User.class)
        .block();
}
```

### 3.6 超时设置

超时其实分两个层次，作用范围不一样：

| 层次 | 设置方式 | 含义 |
|---|---|---|
| **WebClient 级别**（创建时配置一次） | `HttpClient.create().option(CONNECT_TIMEOUT_MILLIS, ...)` + `.responseTimeout(...)` | 对这个 `WebClient` 发出的**所有**请求生效——`CONNECT_TIMEOUT`是"建立TCP连接"的超时，`responseTimeout`是"等响应头返回"的超时 |
| **单次请求级别** | 在调用链上加 `.timeout(Duration...)` | 只对**这一次**调用生效，控制"从发出请求到拿到完整响应体"的端到端总时间 |

实际项目里通常两者都配：WebClient 级别设置一个"兜底"的较大值，单次请求再根据具体接口的 SLA 设置更精确的超时（比如竞价请求要求 100ms 内必须返回，远小于全局默认值）。

```java
@Bean
public WebClient webClient() {
    HttpClient httpClient = HttpClient.create()
        .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 3000)
        .responseTimeout(Duration.ofSeconds(10));

    return WebClient.builder()
        .baseUrl("https://api.example.com")
        .clientConnector(new ReactorClientHttpConnector(httpClient))
        .build();
}

// 单个请求设置超时
webClient.get()
    .uri("/slow-endpoint")
    .retrieve()
    .bodyToMono(String.class)
    .timeout(Duration.ofSeconds(5))   // 5 秒超时
    .block();
```

## 4. 重试与熔断

### 4.1 WebClient 内置重试

```java
public User getUserWithRetry(Long id) {
    return webClient.get()
        .uri("/users/{id}", id)
        .retrieve()
        .bodyToMono(User.class)
        .retryWhen(Retry.backoff(3, Duration.ofSeconds(1))  // 最多重试 3 次，指数退避
            .filter(ex -> ex instanceof WebClientResponseException.ServiceUnavailable)
            .onRetryExhaustedThrow((spec, signal) ->
                new RuntimeException("重试 3 次后仍然失败")))
        .block();
}
```

### 4.2 RestTemplate 重试（Spring Retry）

```kotlin
dependencies {
    implementation("org.springframework.retry:spring-retry")
    implementation("org.springframework:spring-aspects")
}
```

```java
@Service
public class UserClient {
    private final RestTemplate restTemplate;

    @Retryable(
        retryFor = ResourceAccessException.class,   // 只对超时重试
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2)  // 1s → 2s → 4s
    )
    public User getUser(Long id) {
        return restTemplate.getForObject(
            "https://api.example.com/users/{id}", User.class, id);
    }

    @Recover  // 重试全部失败后的兜底方法
    public User getUserFallback(ResourceAccessException e, Long id) {
        log.error("获取用户失败，返回默认值: id={}", id);
        return new User("Unknown", "unknown@example.com");
    }
}
```

## 5. 广告系统中的 HTTP 调用实战

### 5.1 竞价请求（低延迟要求）

```java
@Service
public class BidClient {
    private final WebClient webClient;

    public BidClient(WebClient.Builder builder) {
        HttpClient httpClient = HttpClient.create()
            .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 500)   // 连接超时 500ms
            .responseTimeout(Duration.ofMillis(100));            // 响应超时 100ms

        this.webClient = builder
            .clientConnector(new ReactorClientHttpConnector(httpClient))
            .build();
    }

    // 并发向多个 DSP 发送竞价请求
    public List<BidResponse> sendBidRequests(BidRequest request, List<String> dspUrls) {
        List<Mono<BidResponse>> monos = dspUrls.stream()
            .map(url -> webClient.post()
                .uri(url)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(BidResponse.class)
                .timeout(Duration.ofMillis(150))
                .onErrorResume(e -> {
                    log.warn("DSP {} 请求失败: {}", url, e.getMessage());
                    return Mono.empty();  // 某个 DSP 失败不影响其他
                }))
            .collect(Collectors.toList());

        return Flux.merge(monos)
            .collectList()
            .block(Duration.ofMillis(200));  // 最多等 200ms
    }
}
```

### 5.2 素材审核回调（可靠性要求）

```java
@Service
public class AuditCallbackClient {
    private final RestTemplate restTemplate;

    @Retryable(maxAttempts = 5, backoff = @Backoff(delay = 2000, multiplier = 2))
    public void notifyAuditResult(String callbackUrl, AuditResult result) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-Signature", sign(result));

        HttpEntity<AuditResult> entity = new HttpEntity<>(result, headers);
        restTemplate.postForEntity(callbackUrl, entity, Void.class);
    }
}
```

## 6. RestTemplate vs WebClient 选型速查

| 场景 | 推荐 |
|------|------|
| 简单的同步调用 | RestTemplate（代码最少） |
| 需要并发调用多个接口 | WebClient（Mono.zip / Flux.merge） |
| 低延迟高并发（竞价） | WebClient（非阻塞，不占线程） |
| 传统 Spring MVC 项目 | 都行，WebClient + block() 也可以 |
| 响应式项目（WebFlux） | 只能用 WebClient |
| 需要重试 / 熔断 | WebClient 内置 retryWhen；RestTemplate 用 Spring Retry |

## 7. 小结

| 主题 | 关键要点 |
|------|---------|
| RestTemplate | 同步阻塞，API 直观；getForObject / postForObject / exchange |
| 请求定制 | HttpHeaders + HttpEntity 控制请求头和请求体 |
| 异常处理 | 4xx → HttpClientErrorException，5xx → HttpServerErrorException |
| 拦截器 | 统一加请求头、日志、监控 |
| WebClient | 异步非阻塞，链式 API；.block() 可以当同步用 |
| 并发调用 | Mono.zip 合并多个请求，Flux.merge 取最快返回的 |
| 超时设置 | 连接超时 + 响应超时分开设置 |
| 重试 | WebClient 用 retryWhen，RestTemplate 用 @Retryable |
| 广告场景 | 竞价请求用 WebClient 并发 + 短超时；回调通知用 RestTemplate + 重试 |

---

> **系列完结**。从 Java 语言基础到 Spring Boot 实战、缓存、HTTP 客户端，整个系列覆盖了一个 Java 后端开发者入职前需要掌握的完整知识体系。

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
