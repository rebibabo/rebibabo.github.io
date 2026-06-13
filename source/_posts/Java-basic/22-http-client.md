---
title: 'Java全貌(22) | HTTP 客户端：RestTemplate、WebClient 与远程调用'
date: 2026-05-22
tags:
  - Java
  - HTTP
  - RestTemplate
  - WebClient
categories:
  - Java全貌
---

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

```kotlin
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-webflux")
    // 如果只用 WebClient 不用响应式 Web，加 spring-boot-starter-web 也行
}
```

### 3.2 创建 WebClient

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

### 3.3 同步调用（block）

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

### 3.5 异常处理

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