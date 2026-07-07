---
title: ObjectMapper
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# ObjectMapper

[[wiki/glossary/java-basic/index|返回词汇表]]

## 定义

ObjectMapper 是 Jackson 库的核心类，负责 Java 对象与 JSON 之间的序列化和反序列化。Spring Boot 默认集成 Jackson，Controller 返回对象自动转 JSON、`@RequestBody` 自动解析 JSON 的背后都是 ObjectMapper 在工作。

## 上下文

基本用法：`writeValueAsString(obj)` 将对象序列化为 JSON 字符串，`readValue(json, Class)` 将 JSON 反序列化为对象。泛型反序列化必须使用 `TypeReference<List<User>>() {}` 而非 `List.class`，因为 Java 泛型在运行时擦除，Jackson 拿到原始 `List.class` 不知道元素类型，只能用 LinkedHashMap 兜底。`convertValue(obj, Type)` 将已经是 Object（如从 Redis 取出的 LinkedHashMap）直接转换为目标类型，不需中转 JSON 字符串。常用注解：`@JsonProperty` 指定 JSON 字段名、`@JsonIgnore` 忽略字段、`@JsonInclude(NON_NULL)` 过滤 null 值、`@JsonFormat(pattern)` 格式化日期。处理 LocalDateTime 需要注册 `JavaTimeModule`（Spring Boot 自动配置的 ObjectMapper 已注册，手动 new 时才需要）。可通过 `setPropertyNamingStrategy(SNAKE_CASE)` 全局配置 camelCase 与 snake_case 的自动转换。常见异常：`UnrecognizedPropertyException`（JSON 有多余字段，加 `@JsonIgnoreProperties(ignoreUnknown=true)`）、`InvalidDefinitionException`（类缺少无参构造）。

## 相关术语
- [[wiki/glossary/java-basic/序列化|序列化]] — ObjectMapper 是 Java 原生序列化的现代替代方案，基于 JSON 格式

## 深入阅读

- [[_posts/Java-basic/09-io|java-basics(9) | I/O 与文件操作：从 BIO 到 NIO 与 Files 工具类]]
