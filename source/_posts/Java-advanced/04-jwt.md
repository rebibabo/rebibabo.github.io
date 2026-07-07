---
title: 'Java进阶(4) | Spring Security + JWT：认证授权入门'
date: 2026-05-04
abbrlink: 04
tags:
  - Spring Security
  - JWT
  - 认证授权
  - Spring Boot
categories:
  - java-advanced
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

到目前为止 Mini-SSP 的接口是"裸奔"的——任何人知道 URL 就能调用管理后台增删广告位。真实项目里，接口必须先确认"你是谁"（认证）、再判断"你能不能做这件事"（授权）。Spring Security 是 Spring 生态里做这件事的标准方案，JWT 是目前最主流的认证凭证格式。这篇用尽量少的代码、尽量多的图表，讲清楚它们怎么配合工作。

<!-- more -->

## 1. 先分清两个词：认证 vs 授权

这两个词经常被混用，但完全是两件事：

| | 认证（Authentication） | 授权（Authorization） |
|---|---|---|
| 回答的问题 | 你是谁？ | 你能做什么？ |
| 时机 | 先发生 | 后发生 |
| 类比 | 进公司刷工牌证明身份 | 工牌权限决定能进哪些门 |
| 例子 | 用户名密码登录成功 | 普通员工不能访问管理后台 |

流程永远是先认证、后授权——先确认身份，再根据身份判断权限。

---

## 2. 为什么用 JWT？先看传统 Session 的问题

### 2.1 传统 Session 方案

```
用户登录成功后：
  服务端创建一个 Session（存用户信息），生成一个 sessionId
  把 sessionId 通过 Cookie 返回给浏览器
  
之后每次请求：
  浏览器自动带上 sessionId
  服务端用 sessionId 在【自己的内存/Redis】里找到对应的 Session
  → 知道是哪个用户
```

核心特点：**用户信息存在服务端**，客户端只拿一个 sessionId。

### 2.2 Session 在分布式下的麻烦

```
单机时：Session 存在这台服务器内存里，没问题

多机时：
  请求第一次打到 服务器A，Session 存在 A 的内存
  下次请求被负载均衡打到 服务器B
  → B 的内存里没有这个 Session → 认为你没登录！
```

解决办法是把 Session 集中存到 Redis 让多台共享，但这又引入了额外依赖和网络开销。

### 2.3 JWT 方案：信息存在客户端

JWT（JSON Web Token）反过来——**把用户信息直接编码进 token 本身**，服务端不存任何东西：

```
用户登录成功后：
  服务端把用户信息（id、角色等）打包、签名，生成一个 JWT 字符串
  返回给客户端
  
之后每次请求：
  客户端带上这个 JWT
  服务端【验证签名】，直接从 JWT 里读出用户信息
  → 不需要查任何存储
```

### 2.4 两者对比

| 维度 | Session | JWT |
|------|---------|-----|
| 用户信息存在哪 | 服务端 | 客户端（token 里） |
| 服务端是否有状态 | 有状态（要存 Session） | 无状态（什么都不存） |
| 多机部署 | 需要共享 Session（Redis） | 天然支持，无需共享 |
| 每次请求是否查存储 | 要查 | 不查，验签即可 |
| 注销/失效 | 简单，删 Session 即可 | 麻烦，token 有效期内一直有效 |
| 安全性 | sessionId 泄露风险 | token 泄露风险，且无法主动失效 |

无状态、天然支持多机，是 JWT 在微服务架构里流行的主要原因。

---

## 3. JWT 长什么样

### 3.1 三段式结构

一个 JWT 就是一个用两个点分隔的字符串：

![](/images/Java-advanced/IMG-20260707-000013.png)




| 部分 | 内容 | 说明 |
|------|------|------|
| Header（头部） | 签名算法、token 类型 | 比如 `{"alg":"HS256","typ":"JWT"}` |
| Payload（载荷） | 用户信息、过期时间等 | 比如 `{"sub":"1001","role":"admin","exp":...}` |
| Signature（签名） | 防篡改的校验值 | 用密钥对前两部分签名得到 |

前两部分只是 Base64 编码（**不是加密**，任何人都能解开看到内容），所以**不能往 Payload 里放密码等敏感信息**。

### 3.2 签名怎么防篡改

签名是 JWT 安全的核心：

![](/images/Java-advanced/IMG-20260707-000014.png)




关键点：**密钥只有服务端知道**。攻击者即使改了 Payload（比如把 `role` 从 user 改成 admin），也没有密钥算出正确的签名，服务端一验就发现对不上。

![](/images/Java-advanced/IMG-20260707-000015.png)




---

## 4. Spring Security 核心概念

Spring Security 的工作方式是在请求到达 Controller **之前**，先经过一条"过滤器链"层层检查。

### 4.1 过滤器链（Filter Chain）

![](/images/Java-advanced/IMG-20260707-000016.png)




我们做 JWT 认证，就是往这条链里加一个**自定义过滤器**，专门负责解析和验证请求里的 JWT。

### 4.2 几个核心组件

| 组件 | 作用 |
|------|------|
| `SecurityFilterChain` | 配置整条过滤器链的规则（哪些接口要登录、哪些放行） |
| `Authentication` | 代表"当前认证信息"（是谁、有什么权限） |
| `SecurityContext` | 存放当前请求的 `Authentication`，全局可取 |
| `UserDetailsService` | 根据用户名加载用户信息（查数据库） |
| `PasswordEncoder` | 密码加密/校验（密码绝不能明文存） |

---

## 5. 完整流程：从登录到访问受保护接口

把整个链路拆成两个阶段看：

### 5.1 阶段一：登录拿 token

![](/images/Java-advanced/IMG-20260707-000017.png)




### 5.2 阶段二：带 token 访问接口

![](/images/Java-advanced/IMG-20260707-000018.png)




注意阶段二**全程不查数据库**——验签 + 解析 token 即可，这就是 JWT "无状态"的体现。

---

## 6. 实战：给 Mini-SSP 加上 JWT 认证

下面分步骤实现，每步只看关键部分。

### 6.1 引入依赖

```xml
<!-- Spring Security -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>

<!-- JWT 库（jjwt） -->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.6</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.12.6</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.12.6</version>
    <scope>runtime</scope>
</dependency>
```

> 注意：只要引入了 `spring-boot-starter-security`，**所有接口默认都需要登录**——这是 Spring Security 的默认行为，后面要在配置里显式放行登录接口。

### 6.2 JWT 工具类：负责生成和解析 token

这个类做两件事：生成 token、从 token 解析信息。先看生成：

```java
@Component
public class JwtUtil {

    // 密钥：实际项目从配置读取，不要硬编码
    private final SecretKey key = Keys.hmacShaKeyFor(
        "your-256-bit-secret-key-must-be-long-enough".getBytes()
    );

    private final long EXPIRATION = 24 * 60 * 60 * 1000;  // 24 小时

    // 生成 token：把用户信息打包签名
    public String generateToken(String userId, String role) {
        return Jwts.builder()
                .subject(userId)                          // 放入用户 id
                .claim("role", role)                      // 放入角色
                .issuedAt(new Date())                     // 签发时间
                .expiration(new Date(System.currentTimeMillis() + EXPIRATION))  // 过期时间
                .signWith(key)                            // 用密钥签名
                .compact();                               // 生成最终字符串
    }
}
```

再看解析和验证：

```java
    // 从 token 解析出用户 id（同时会验证签名和过期，失败抛异常）
    public String parseUserId(String token) {
        return Jwts.parser()
                .verifyWith(key)          // 用密钥验证签名
                .build()
                .parseSignedClaims(token) // 解析（签名错误或过期会抛异常）
                .getPayload()
                .getSubject();            // 取出 subject（用户 id）
    }

    // 验证 token 是否有效
    public boolean validate(String token) {
        try {
            Jwts.parser().verifyWith(key).build().parseSignedClaims(token);
            return true;
        } catch (Exception e) {
            return false;  // 签名错误、过期、格式不对都会到这里
        }
    }
}
```

| 方法 | 作用 |
|------|------|
| `generateToken` | 登录成功后调用，生成 JWT |
| `parseUserId` | 从 token 取出用户 id |
| `validate` | 判断 token 是否合法（验签 + 没过期） |

### 6.3 登录接口：校验密码，返回 token

```java
@RestController
@RequiredArgsConstructor
public class AuthController {

    private final JwtUtil jwtUtil;
    private final PasswordEncoder passwordEncoder;
    private final UserMapper userMapper;

    @PostMapping("/login")
    public ApiResponse<String> login(@RequestBody @Valid LoginRequest req) {
        // 1. 查用户
        User user = userMapper.selectByUsername(req.getUsername());
        if (user == null) {
            throw new BizException("用户不存在");
        }

        // 2. 校验密码（数据库存的是加密后的密码）
        if (!passwordEncoder.matches(req.getPassword(), user.getPassword())) {
            throw new BizException("密码错误");
        }

        // 3. 生成 token 返回
        String token = jwtUtil.generateToken(user.getId().toString(), user.getRole());
        return ApiResponse.success(token);
    }
}
```

重点是第 2 步——数据库里**绝不能明文存密码**，存的是 `PasswordEncoder` 加密后的哈希值，校验时用 `matches` 比对，而不是直接 `equals`。

### 6.4 JWT 过滤器：拦截每个请求验证 token

这是核心——往过滤器链里加一个自己的过滤器，每个请求都先过它：

```java
@Component
@RequiredArgsConstructor
public class JwtFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ... {
        // 1. 从请求头取 token
        String header = request.getHeader("Authorization");

        // 2. 没有 token 或格式不对，直接放行给后续过滤器（由它们决定拦不拦）
        if (header == null || !header.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }

        // 3. 取出 "Bearer " 后面的真正 token
        String token = header.substring(7);

        // 4. 验证 token，通过则把用户信息放进 SecurityContext
        if (jwtUtil.validate(token)) {
            String userId = jwtUtil.parseUserId(token);
            // 构造一个"已认证"的对象放进上下文
            UsernamePasswordAuthenticationToken auth =
                new UsernamePasswordAuthenticationToken(userId, null, List.of());
            SecurityContextHolder.getContext().setAuthentication(auth);
        }

        // 5. 继续后续流程
        chain.doFilter(request, response);
    }
}
```

| 请求头格式 | 说明 |
|-----------|------|
| `Authorization: Bearer eyJhbGci...` | 标准格式，`Bearer ` 是固定前缀，后面跟 token |

第 4 步是关键：验证通过后，把用户信息存进 `SecurityContextHolder`，这样后续 Controller 就能拿到"当前是谁"。

### 6.5 安全配置：定义哪些接口放行、哪些要登录

```java
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtFilter jwtFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // JWT 是无状态的，关闭 CSRF 和 Session
            .csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            // 配置接口权限
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/login").permitAll()         // 登录接口放行
                .requestMatchers("/api/v1/bid").permitAll()    // 竞价接口放行（对外）
                .requestMatchers("/api/v1/admin/**").authenticated()  // 管理接口要登录
                .anyRequest().authenticated()                  // 其余都要登录
            )
            // 把自定义 JWT 过滤器加到链里
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    // 密码加密器
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

配置里几个关键决定：

| 配置 | 作用 | 为什么 |
|------|------|--------|
| `csrf.disable()` | 关闭 CSRF 防护 | JWT 不依赖 Cookie，不需要 CSRF 防护 |
| `STATELESS` | 不创建 Session | JWT 无状态，用不到 Session |
| `permitAll()` | 放行指定接口 | 登录接口本身不能要求登录 |
| `authenticated()` | 要求登录 | 管理接口必须先认证 |
| `addFilterBefore` | 插入 JWT 过滤器 | 让它在 Spring 默认认证过滤器之前执行 |

### 6.6 基于角色的授权

光认证（知道是谁）还不够，有时要按角色控制（授权）。在方法上加注解即可：

```java
@RestController
@RequestMapping("/api/v1/admin")
public class SlotAdminController {

    // 只有 admin 角色能删除
    @PreAuthorize("hasRole('ADMIN')")
    @DeleteMapping("/slots/{id}")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        // ...
    }
}
```

要让 `@PreAuthorize` 生效，需要在配置类上加 `@EnableMethodSecurity`。背后的机制和你前面学过的一样——**动态代理**：Spring 给 Controller 生成代理对象，在方法执行前检查当前用户角色是否满足。

---

## 7. 整体串起来

```
【登录阶段】
POST /login (username + password)
    → AuthController 校验密码
    → JwtUtil 生成 token
    → 返回 token 给客户端

【访问阶段】
GET /api/v1/admin/slots (Header: Authorization: Bearer xxx)
    → JwtFilter 拦截，取出 token
    → JwtUtil.validate() 验签 + 验过期
    → 通过：用户信息存入 SecurityContext，放行
    → SecurityConfig 检查这个接口要不要登录/什么角色
    → @PreAuthorize 检查角色
    → 全通过 → 进入 Controller
    → 任一步失败 → 返回 401/403
```

---

## 8. 小结

| 主题 | 关键要点 |
|------|---------|
| 认证 vs 授权 | 认证=你是谁，授权=你能做什么，先认证后授权 |
| Session vs JWT | Session 信息在服务端（有状态），JWT 信息在 token 里（无状态） |
| JWT 为什么流行 | 无状态、天然支持多机部署，适合微服务 |
| JWT 结构 | Header.Payload.Signature，前两部分只是编码不是加密 |
| 签名防篡改 | 密钥只有服务端知道，改了内容算不出正确签名 |
| Spring Security 工作方式 | 请求先过过滤器链，再到 Controller |
| 核心实现 | JwtUtil（生成/解析）+ JwtFilter（拦截验证）+ SecurityConfig（规则） |
| 授权 | `@PreAuthorize("hasRole('ADMIN')")`，底层是动态代理 |
| 安全红线 | 密码加密存储、敏感信息不放 Payload、密钥不硬编码 |

JWT 也有短板——token 签发后在有效期内无法主动失效（比如用户登出、被封号）。生产环境常配合 Redis 维护一个"黑名单"或用短期 token + refresh token 机制来弥补，这部分等基础熟练后再深入。

对 Mini-SSP 来说，给管理后台接口加上 JWT 认证后，就不再是"裸奔"状态——这也是任何对外服务上线前的必备一环。

---

> **下一篇预告**：CI/CD 入门——用 GitHub Actions 自动构建镜像并部署到 K8s

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
