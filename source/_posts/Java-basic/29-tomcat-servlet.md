---
title: 'Java基础(番外) | Tomcat 与 Servlet：Spring Boot 背后的请求处理流程'
date: 2026-05-29
abbrlink: 29tags:
  - Tomcat
  - Servlet
  - Spring Boot
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

写了这么多 `@RestController`、`@GetMapping`，有没有想过：浏览器发出的一个 HTTP 请求，到底是怎么"走到"你写的方法里的？中间经过了谁？

答案是：**Tomcat（或者 Jetty/Undertow）+ Servlet**。`spring-boot-starter-web` 里自动内嵌的服务器就是 Tomcat，Spring MVC 的核心其实也是一个巨大的 Servlet——`DispatcherServlet`。

这篇按"够用就好"的程度来讲：不会教你怎么把项目打成 WAR 包部署到独立 Tomcat（现在几乎没人这么干了），但会讲清楚**一次请求从进入服务器到执行你的 Controller，中间经过了哪些环节**，以及 Filter、Interceptor 这两个常被混淆的概念。

<!-- more -->

## 1. Servlet 是什么

Servlet 是 Java EE（现在叫 Jakarta EE）定义的一套**规范**，规定了"如何处理 HTTP 请求"这件事应该长什么样。Tomcat 就是这套规范的一种**实现**（容器）。

简化理解：

> Servlet = 一个能处理 HTTP 请求、返回 HTTP 响应的 Java 类，必须实现 `javax.servlet.Servlet`（或 `jakarta.servlet.Servlet`）接口。

### 1.1 Servlet 生命周期

| 阶段 | 方法 | 调用时机 | 调用次数 |
|---|---|---|---|
| 初始化 | `init()` | 第一次被请求时（或容器启动时），创建实例并初始化 | **只调用一次** |
| 处理请求 | `service()` → `doGet()`/`doPost()`/... | 每次收到 HTTP 请求 | **每次请求都调用** |
| 销毁 | `destroy()` | 容器关闭、Servlet 被卸载时 | **只调用一次** |

**为什么 `init()` 只调用一次？** 因为 Servlet 容器对同一个 Servlet **只会创建一个实例**，所有请求共享这一个实例（这也是为什么 Servlet 里不要存"请求相关"的实例变量——会有线程安全问题，多个请求线程会同时读写同一份数据）。

```java
public class HelloServlet extends HttpServlet {
    @Override
    public void init() {
        System.out.println("Servlet 初始化，只打印一次");
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.getWriter().write("Hello");
    }
}
```

实际开发中，你几乎**不会自己写 Servlet**——Spring MVC 已经帮你封装好了，你写的 `@Controller` 方法本质上是被 `DispatcherServlet` 调用的。但理解这层概念，有助于理解后面的 Filter 和请求流程。

## 2. Tomcat 架构：容器是怎么组织的

Tomcat 内部是一层套一层的"容器"结构，从大到小：

```
Server (整个 Tomcat 实例)
 └── Service (一组 Connector + 一个 Engine)
      ├── Connector (监听端口、处理协议，比如 HTTP/1.1)
      └── Engine (处理请求的核心引擎)
           └── Host (一个虚拟主机，对应一个域名)
                └── Context (一个 Web 应用，对应一个 webapp / 你的 Spring Boot 应用)
                     └── Wrapper (对应一个 Servlet，比如 DispatcherServlet)
```

**作为后端开发者，需要记住的只有两层**：

- **Connector**：负责"听"——监听某个端口（比如 8080），接收 TCP 连接，解析 HTTP 协议
- **Context**：对应你的**一个应用**——里面注册了 `DispatcherServlet`、各种 `Filter`

其余层级（Engine/Host）在 Spring Boot 内嵌场景下基本是自动配置好的，平时不需要手动管理。

## 3. 一次 HTTP 请求的完整旅程

这是整篇最重要的一张图——把"浏览器发请求"到"你的方法被调用"之间发生的事情串起来：

```
浏览器
  │  HTTP 请求 (GET /api/users/1)
  ▼
Tomcat Connector（监听 8080 端口，接收连接、解析协议）
  │
  ▼
Filter 链（按注册顺序依次执行，比如：字符编码过滤器 → 鉴权过滤器 → ...）
  │
  ▼
DispatcherServlet（Spring MVC 的核心 Servlet，所有请求的统一入口）
  │
  ▼
HandlerMapping（根据 URL + 方法，找到该由哪个 Controller 的哪个方法处理）
  │
  ▼
Interceptor 链的 preHandle（按注册顺序依次执行）
  │
  ▼
你的 @Controller 方法（业务逻辑、调用 Service/Mapper）
  │
  ▼
Interceptor 链的 postHandle（按注册顺序的反向执行）
  │
  ▼
视图渲染 / JSON 序列化（@RestController 直接序列化返回值为 JSON）
  │
  ▼
Interceptor 链的 afterCompletion
  │
  ▼
Filter 链（反向执行，做收尾工作）
  │
  ▼
浏览器收到 HTTP 响应
```

看着复杂，但拆开看其实就两条主线：

1. **Filter 是最外层的"门卫"**——在请求进入 Spring MVC 之前、响应离开之前都会经过
2. **Interceptor 是 Spring MVC 内部的"安检"**——只对进入了 `DispatcherServlet` 的请求生效，且能感知到具体是哪个 Controller 方法

## 4. Filter vs Interceptor

这是新人最容易混的一对概念，因为它们功能上有重叠（都能做"鉴权"、"日志"这类横切逻辑），但所属层次完全不同。

| 维度 | Filter | Interceptor |
|---|---|---|
| 所属规范 | Servlet 规范（Java EE 标准） | Spring MVC 自己的机制 |
| 作用范围 | 所有进入 Tomcat 的请求（不限于 Spring MVC） | 只有被 `DispatcherServlet` 处理的请求 |
| 能否拿到 Controller 信息 | 不能，只能拿到 `HttpServletRequest`/`HttpServletResponse` | 能，可以拿到具体的 `HandlerMethod`（哪个类哪个方法） |
| 典型用途 | 字符编码设置、跨域 CORS、请求日志、Gzip 压缩、敏感词过滤 | 登录鉴权、权限校验、操作日志（记录调用了哪个接口）、统一参数处理 |
| 接口方法 | `doFilter(request, response, chain)` | `preHandle` / `postHandle` / `afterCompletion` |

### 4.1 Filter 写法

```java
@Component
public class RequestLogFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        long start = System.currentTimeMillis();
        chain.doFilter(request, response); // 必须调用，否则请求不会继续往下走
        long cost = System.currentTimeMillis() - start;
        System.out.println("请求耗时: " + cost + "ms");
    }
}
```

`chain.doFilter(request, response)` 是关键——调用它之前的代码在"请求进入时"执行，调用它之后的代码在"响应返回时"执行，这也是为什么 Filter 能"包裹"整个请求处理过程。

### 4.2 Interceptor 写法

```java
public class AuthInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        String token = request.getHeader("Authorization");
        if (token == null) {
            response.setStatus(401);
            return false; // 返回 false：直接拦截，不会进入 Controller
        }
        return true; // 返回 true：继续往下走
    }

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView mv) {
        // Controller 方法执行完之后、视图渲染之前
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        // 整个请求完成之后（包括视图渲染），常用于资源清理、记录最终日志
    }
}

@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new AuthInterceptor())
                .addPathPatterns("/api/**")        // 拦截哪些路径
                .excludePathPatterns("/api/login"); // 排除哪些路径
    }
}
```

### 4.3 该用 Filter 还是 Interceptor？

**经验法则**：

- 跟"Web容器层面"相关、和 Spring MVC 无关的（比如统一设置字符编码、CORS、压缩响应）→ **Filter**
- 跟"业务层面"相关、需要知道是哪个接口被调用的（比如登录鉴权、记录"用户A调用了创建订单接口"）→ **Interceptor**

实际项目里，**登录鉴权用 Interceptor 更常见**，因为可以通过 `@Target`/反射拿到方法上的自定义注解（比如 `@RequireLogin`），做更细粒度的控制；而 Filter 由于在 Servlet 层，拿不到这些 Spring 层的信息。

## 5. 内嵌 Tomcat：Spring Boot 是怎么做到 `java -jar` 直接跑的

传统 Java Web 开发：写好代码 → 打成 `.war` 包 → 部署到一个独立安装的 Tomcat 的 `webapps` 目录 → 启动 Tomcat。

Spring Boot 的做法：**把 Tomcat 的核心代码作为依赖打进你的 jar 包里**，启动类的 `main()` 方法里会创建一个 Tomcat 实例并启动它：

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args); // 内部会启动内嵌 Tomcat
    }
}
```

| 对比项 | 传统部署（WAR） | Spring Boot（内嵌，JAR） |
|---|---|---|
| 启动方式 | 需要先安装 Tomcat，再把 war 丢进 webapps | `java -jar app.jar` 一条命令 |
| Tomcat 版本 | 由运维统一管理，所有应用共用 | 每个应用自带一个版本，互不影响 |
| 多应用部署 | 一个 Tomcat 可以跑多个 war（共享内存） | 一个进程一个应用（更适合容器化/微服务） |
| 现在用得多吗 | 老系统、传统企业应用还在用 | **新项目几乎都用这种**，尤其配合 Docker |

**作为新人，了解到这个程度就够了**：知道 `server.port`、`server.servlet.context-path` 这些配置项实际上是在配置内嵌 Tomcat，知道"内嵌"和"独立部署"的区别，不需要去手动操作独立 Tomcat 的 `webapps`/`conf` 目录。

## 6. 常用配置项

```yaml
server:
  port: 8080                          # 监听端口
  servlet:
    context-path: /api                # 应用的根路径，所有接口都会加上这个前缀
  tomcat:
    threads:
      max: 200                        # 最大工作线程数，决定能同时处理多少请求
      min-spare: 10                   # 最小空闲线程数
    max-connections: 8192             # 最大连接数
    accept-count: 100                 # 等待队列长度，超过这个数的请求会被拒绝
    connection-timeout: 20000         # 连接超时时间（毫秒）
```

**为什么要关心 `threads.max`？** Tomcat 用线程池处理请求——每个请求占用一个线程直到处理完成。如果你的接口里有耗时的同步调用（比如等待外部接口响应），线程池满了之后新请求就只能排队（`accept-count`），队列也满了就直接拒绝连接。这也是为什么"接口响应慢"有时会引发"整个服务都连不上"的连锁反应——线程池被慢请求占满了。

这个问题的根本解法是异步化（比如 [22 HTTP 客户端](/2026/05/22/Java-basic/22-http-client/) 里提到的 WebClient 响应式调用），但这属于进阶话题，新人先知道"线程池会被占满"这个现象即可。

## 7. 小结

| 主题 | 核心要点 |
|---|---|
| Servlet | Java EE 规范，定义了"如何处理 HTTP 请求"；生命周期 `init`(一次) → `service`(每次请求) → `destroy`(一次) |
| Tomcat 架构 | Connector(监听端口) + Context(你的应用)，作为开发者主要关心这两层 |
| 请求流程 | 浏览器 → Connector → Filter链 → DispatcherServlet → HandlerMapping → Interceptor链 → Controller |
| Filter vs Interceptor | Filter 是 Servlet 层、范围更广；Interceptor 是 Spring MVC 层、能拿到 Controller 信息，鉴权常用它 |
| 内嵌 Tomcat | Spring Boot 把 Tomcat 打进 jar，`java -jar` 直接跑，不需要手动部署 |
| 线程池配置 | `server.tomcat.threads.max` 决定并发处理能力，慢请求会占满线程池影响整体可用性 |

**这个程度对新人来说够用**：理解请求的完整链路、能正确选择 Filter 还是 Interceptor、知道线程池配置会影响什么。至于 Tomcat 源码、NIO 连接器原理、独立部署的 `server.xml` 配置——这些等工作中真的遇到性能调优或者部署问题时再深入也不迟。

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
