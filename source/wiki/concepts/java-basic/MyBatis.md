---
title: MyBatis
tags:
  - wiki
  - concept
  - java
  - java-basic
type: concept
source_series: Java-basic
status: seed
---

# MyBatis

[[wiki/concepts/java-basic/数据访问|返回数据访问]]

## 这一层回答什么问题

> MyBatis 和 JPA 有什么本质区别？`#{}` 和 `${}` 什么时候用？动态 SQL 怎么避免硬编码？

MyBatis 是半自动 ORM——你写 SQL，框架做结果映射。和 JPA 的全自动不同，MyBatis 让你对 SQL 有绝对控制权。这也是国内大厂偏好 MyBatis 的核心原因：复杂查询的 SQL 是 DBA 调优过的，不能交给框架自动生成。

## `#{}` vs `${}`

```xml
<!-- #{} → PreparedStatement 参数绑定，防 SQL 注入 -->
SELECT * FROM user WHERE id = #{id}

<!-- ${} → 字符串拼接，有 SQL 注入风险 -->
SELECT * FROM ${tableName}  <!-- 动态表名没别的办法，但务必白名单校验 -->
```

**规则**：99% 的场景用 `#{}`。`${}` 只用于表名、列名、ORDER BY 字段等无法预编译的场景，且必须白名单校验。

## 动态 SQL

```xml
<select id="findUsers" resultType="User">
    SELECT * FROM user
    <where>
        <if test="name != null and name != ''">
            AND name LIKE CONCAT('%', #{name}, '%')
        </if>
        <if test="status != null">
            AND status = #{status}
        </if>
    </where>
</select>
```

核心标签：
- `<where>` — 自动处理首个 AND/OR（没有条件时去掉 WHERE）
- `<set>` — 动态 UPDATE 列
- `<foreach>` — IN 查询和批量插入
- `<choose>/<when>/<otherwise>` — 多条件选一

## `<resultMap>` 关联映射

一对一用 `<association>`，一对多用 `<collection>`。MyBatis 的"高级映射"不是让你把所有关联都映射出来——小心 N+1 查询问题（查主表 1 次 + 每条记录又查关联表 N 次）。解决：懒加载 + `fetchType` 或直接写关联查询 SQL。

## MyBatis-Plus

MyBatis 的增强工具，核心价值：
- `BaseMapper<T>` — 通用 CRUD，不用写一行 SQL
- `LambdaQueryWrapper` — 类型安全的查询条件构造（字段名写错编译报错）
- 分页插件 — 一行配置，`Page<T>` 直接分页
- 自动填充 — `@TableField(fill = FieldFill.INSERT)` 自动填创建时间

MyBatis-Plus 适合标准 CRUD；复杂多表查询仍然用 MyBatis XML。

## 在系列里的位置

post 18。

## 推荐回看原文

- [[_posts/Java-basic/18-mybatis|18-MyBatis 数据访问]]

## 相关概念

- [[wiki/concepts/java-basic/MySQL事务与索引|MySQL 事务与索引]]
- [[wiki/concepts/java-basic/Spring-Boot|Spring Boot]] — Spring Boot 集成 MyBatis
