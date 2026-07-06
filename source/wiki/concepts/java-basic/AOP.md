---
title: AOP
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# AOP

[[wiki/concepts/java-basic/Spring|返回 Spring]]

## 这一层回答什么问题

> AOP 解决什么？@Before、@After、@Around 怎么选？内部调用 this 为什么会让 AOP 失效？

AOP 把散落在各处的横切逻辑（日志、事务、权限）抽成一个"切面"，织入到指定的"切点"。你不用在每个方法里写 `log.info("begin")`，AOP 帮你统一处理。

## 五个概念

```
@Aspect               ← 切面（这是一个日志切面）
@Around("@annotation(Log)")  ← 切点（在标注了 @Log 的方法上生效）
public Object log(ProceedingJoinPoint pjp) {  ← 通知（做什么、何时做）
    Object result = pjp.proceed();  ← 连接点（目标方法的执行点）
    return result;
}
```

## 五种通知

| 通知 | 执行时机 | 能改返回值 | 能阻止执行 |
|------|----------|-----------|-----------|
| `@Before` | 方法前 | 不能 | 不能 |
| `@After` | 方法后（不论成败） | 不能 | 不能 |
| `@AfterReturning` | 正常返回后 | 可改 | 不能 |
| `@AfterThrowing` | 抛异常后 | 不能 | 不能 |
| **`@Around`** | 包裹方法 | **能** | **能** |

`@Around` 最强大——你能决定是否调用目标方法、修改返回值、包装异常。90% 的场景用 `@Around` 就够了。

## 底层实现

目标类有接口 → JDK 动态代理。目标类没接口 → CGLIB 生成子类代理。

Spring Boot 2.x 开始默认使用 CGLIB——即使有接口也用 CGLIB。

## 为什么内部调用 this 失效

这是 AOP 的第一大坑：

```java
public void methodA() {
    this.methodB();  // ❌ AOP 不生效
}
@Transactional
public void methodB() { ... }
```

AOP 通过**代理对象**生效。外部调用者拿到的是代理，调 `methodA` 时进切面。但 `this` 指向原始对象——`this.methodB()` 绕过了代理。`@Transactional`、`@Cacheable` 都有这个问题。

## 在系列里的位置

post 16 的第二核心。

## 推荐回看原文

- [[_posts/Java-basic/16-spring-ioc-aop|16-Spring 核心思想]]

## 相关概念

- [[wiki/concepts/java-basic/IoC与DI|IoC 与 DI]]
- [[wiki/concepts/java-basic/动态代理|动态代理]] — AOP 的底层机制
- [[wiki/concepts/java-basic/Spring-Boot|Spring Boot]]
