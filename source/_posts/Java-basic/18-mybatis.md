---
title: 'Java基础(18) | MyBatis 数据访问：SQL 映射、动态 SQL 与 MyBatis-Plus'
date: 2026-05-18
abbrlink: 18tags:
  - Java
  - MyBatis
  - 数据库
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

上一篇用 MyBatis-Plus 写了 Mapper 层，`BaseMapper` 提供的方法已经能覆盖大部分简单 CRUD。但实际项目中经常会遇到多表 join、复杂条件、聚合统计这类 `LambdaQueryWrapper` 写不出来的查询，这时就需要回到 MyBatis 本身——写 XML 或注解形式的 SQL。这篇文章覆盖原生 MyBatis 的核心用法，以及 MyBatis-Plus 在它基础上做了哪些增强。

<!-- more -->

## 1. JPA vs MyBatis：怎么选？

前面用的 MyBatis-Plus 属于 MyBatis 体系——SQL 由你控制（或用 `LambdaQueryWrapper` 自动生成），但底层执行的还是真实 SQL。另一个主流方向是 **JPA（Java Persistence Association，Java 持久化规范，常见实现是 Hibernate）**，思路完全不同：你不写 SQL，只定义 Entity 和方法名，框架自动生成 SQL。

```java
// JPA：只需要定义接口和方法名，不写 SQL
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    List<User> findByNameContaining(String keyword);
    // 框架根据方法名自动解析成：
    // SELECT * FROM user WHERE email = ?
    // SELECT * FROM user WHERE name LIKE '%?%'
}
```

```java
// MyBatis-Plus：写 LambdaQueryWrapper 或 XML，SQL 是显式的
userMapper.selectOne(
    new LambdaQueryWrapper<User>().eq(User::getEmail, email)
);
```

```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>3.5.7</version>
</dependency>
```

两者对比：

| 维度 | JPA (Hibernate) | MyBatis |
|------|-----------------|---------|
| SQL 控制 | 自动生成 SQL，可用 `@Query` 自定义 | **完全手写 SQL**，精确控制 |
| 学习曲线 | 低（方法名即查询） | 中（需要写 XML 或注解 SQL） |
| 复杂查询 | 多表关联、动态条件较痛苦 | 灵活，复杂 SQL 很自然 |
| 性能调优 | 黑盒较多，调优需要理解 Hibernate 内部机制 | SQL 透明，优化直接改 SQL |
| 国内使用 | 中小项目、快速开发 | **大厂主流**（阿里、美团、OPPO...） |
| ORM 程度 | 全自动 ORM | 半自动 ORM（SQL 手写，映射自动） |

**为什么国内大厂更偏好 MyBatis？** JPA 自动生成的 SQL 在简单场景下很方便，但遇到多表 join、动态拼接条件、批量操作、SQL 性能调优时，往往很难精确控制生成的 SQL（甚至需要倒过来去猜框架生成了什么）。MyBatis 把 SQL 写出来，所见即所得，出了性能问题直接改 SQL、加索引、用 `EXPLAIN` 分析，不需要先理解一层框架黑盒。


## 2. Spring Boot 整合 MyBatis

### 2.1 依赖引入

```kotlin
// build.gradle.kts
dependencies {
    implementation("org.mybatis.spring.boot:mybatis-spring-boot-starter:3.0.3")
    runtimeOnly("com.mysql:mysql-connector-j:8.2.0")
}
```

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.3</version>
</dependency>
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <version>8.2.0</version>
    <scope>runtime</scope>
</dependency>
```

### 2.2 配置

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=UTC
    username: root
    password: 123456
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis:
  mapper-locations: classpath:mapper/*.xml    # XML 映射文件位置
  type-aliases-package: com.example.entity    # 实体类包名（XML 中可以用简名）
  configuration:
    map-underscore-to-camel-case: true        # 下划线自动转驼峰（user_name → userName）
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl  # 打印 SQL（开发用）
```

### 2.3 项目结构

```
src/main/java/com/example/
├── entity/
│   └── User.java
├── mapper/
│   └── UserMapper.java          ← 接口
├── service/
│   └── UserService.java
└── controller/
    └── UserController.java

src/main/resources/
└── mapper/
    └── UserMapper.xml            ← SQL 映射文件
```

## 3. 基础 CRUD

### 3.1 实体类

```java
public class User {
    private Long id;
    private String name;
    private String email;
    private LocalDateTime createdAt;

    // 构造方法
    public User() {}
    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }

    // getter / setter
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
```

### 3.2 Mapper 接口

```java
@Mapper
public interface UserMapper {
    User selectById(Long id);
    List<User> selectAll();
    int insert(User user);
    int update(User user);
    int deleteById(Long id);
}
```

`@Mapper` 标记这是一个 MyBatis 接口。接口里只声明方法签名，**不写实现**——具体的 SQL 写在对应的 XML 文件里，MyBatis 在运行时通过反射把接口方法和 XML 里的 SQL 关联起来。

### 3.3 XML 映射文件

XML 文件和 Mapper 接口是一一对应的：文件名通常和接口名相同（`UserMapper.xml`），放在 `resources/mapper/` 目录下。`namespace` 指定对应哪个接口，文件里每个标签的 `id` 对应接口里的一个方法。

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="com.example.mapper.UserMapper">
    <!-- namespace 必须是 Mapper 接口的完整类名 -->
    <!-- 下面每个标签的 id 必须和接口里的方法名一致 -->
</mapper>
```

#### resultMap：数据库字段 → Java 属性的映射

```xml
<resultMap id="userMap" type="User">
    <id property="id" column="id"/>              <!-- 主键 -->
    <result property="name" column="name"/>       <!-- 普通字段 -->
    <result property="email" column="email"/>
    <result property="createdAt" column="created_at"/>  <!-- 字段名不一致时必须写 -->
</resultMap>
```

**`<resultMap id="..." type="...">`**

定义一个"结果映射规则"，描述查询出来的数据库行该怎么转成 Java 对象。

- `id`：这个 resultMap 的名字，给后面的 `<select>` 引用用，可以随便起，只要文件内唯一
- `type`：转换成什么 Java 类型，这里是 `User`（如果配置了 `typeAliasesPackage`，可以直接写类名；否则要写全限定名 `com.example.User`）

**`<id property="..." column="..."/>`**

标记**主键字段**的映射规则：

- `property`：Java 对象的属性名，对应 `User` 类的 `id` 字段（实际调用 `setId()`）
- `column`：数据库结果集里的列名，对应 SQL 查出来的 `id` 列

为什么主键要单独用 `<id>` 而不是 `<result>`？因为 MyBatis 用主键来判断"这两行结果是不是同一个对象"——一对多场景下尤其重要（详见 6.2）。

**`<result property="..." column="..."/>`**

标记**普通字段**的映射规则，含义和 `<id>` 一样，区别只是它不是主键。`property` 是 Java 属性名，`column` 是数据库列名。

如果开启了 `map-underscore-to-camel-case`、且字段名能自动对应，这些 `<result>` 可以省略——但 join 查询经常涉及别名（`o.id AS order_id`），保险起见显式写出来更清楚。

#### select：查询，对应接口的查询方法

```xml
<!-- 对应 User selectById(Long id) -->
<select id="selectById" resultMap="userMap">
    SELECT id, name, email, created_at
    FROM users
    WHERE id = #{id}
</select>
```

- `id="selectById"` 对应接口里的 `selectById` 方法
- `resultMap="userMap"` 指定用上面定义的映射规则把查询结果转成 `User` 对象
- `#{id}` 是参数占位符，对应方法参数 `selectById(Long id)` 里的 `id`

```xml
<!-- 对应 List<User> selectAll() -->
<select id="selectAll" resultMap="userMap">
    SELECT id, name, email, created_at
    FROM users
    ORDER BY created_at DESC
</select>
```

返回 `List<User>` 时，`<select>` 标签写法不变，MyBatis 根据接口方法的返回类型自动判断返回单个对象还是列表。

#### insert：插入，对应接口的插入方法

```xml
<!-- 对应 int insert(User user) -->
<insert id="insert" useGeneratedKeys="true" keyProperty="id">
    INSERT INTO users (name, email, created_at)
    VALUES (#{name}, #{email}, NOW())
</insert>
```

- `#{name}`、`#{email}` 对应参数对象 `User user` 的属性 `user.getName()`、`user.getEmail()`
- `useGeneratedKeys="true"` + `keyProperty="id"`：插入后数据库自动生成的主键值会被写回 `user.id`，效果和 MyBatis-Plus 的 `IdType.AUTO` 一致

#### update：更新，对应接口的更新方法

```xml
<!-- 对应 int update(User user) -->
<update id="update">
    UPDATE users
    SET name = #{name}, email = #{email}
    WHERE id = #{id}
</update>
```

写法和普通 SQL 一致，`#{字段名}` 取传入对象对应的属性值。

#### delete：删除，对应接口的删除方法

```xml
<!-- 对应 int deleteById(Long id) -->
<delete id="deleteById">
    DELETE FROM users WHERE id = #{id}
</delete>
```

#### 五个标签和接口方法对应关系

| XML 标签 | 对应接口方法 | SQL 类型 |
|---------|------------|---------|
| `<select>` | 查询方法 | `SELECT` |
| `<insert>` | 插入方法 | `INSERT` |
| `<update>` | 更新方法 | `UPDATE` |
| `<delete>` | 删除方法 | `DELETE` |

标签的 `id` 属性 = 接口的方法名，是连接 Java 代码和 SQL 的桥梁。

#### `#{}` 参数引用：简单类型 vs 对象

`#{属性名}` 默认是从**参数对象**里取属性值（调用对应的 getter）。但参数类型不同，写法会不一样：

**参数是单个简单类型**（`Long`、`String` 等），`#{}` 里随便写什么名字都行，习惯上和参数名一致：

```java
User selectById(Long id);
```

```xml
<select id="selectById" resultMap="userMap">
    SELECT * FROM users WHERE id = #{id}
    <!-- 这里写 #{id}、#{xxx}、#{anything} 效果都一样，因为只有一个参数 -->
</select>
```

**参数是对象**，`#{}` 里必须是对象的**属性名**（对应 getter）：

```java
int insert(User user);
```

```xml
<insert id="insert">
    INSERT INTO users (name, email) VALUES (#{name}, #{email})
    <!-- #{name} 实际调用 user.getName()
         #{email} 实际调用 user.getEmail() -->
</insert>
```

**参数是多个**时，必须用 `@Param` 注解给每个参数命名，`#{}` 里写注解指定的名字：

```java
List<User> findByNameAndStatus(@Param("name") String name, @Param("status") int status);
```

```xml
<select id="findByNameAndStatus" resultMap="userMap">
    SELECT * FROM users WHERE name = #{name} AND status = #{status}
    <!-- #{name} 对应 @Param("name") 的那个参数
         #{status} 对应 @Param("status") 的那个参数 -->
</select>
```

不加 `@Param` 时多参数会报错（`Parameter 'xxx' not found`），因为 MyBatis 不知道 `#{}` 里的名字该对应哪个参数。

**一句话总结**：单个简单类型参数 → `#{}` 里名字随意；对象参数 → `#{}` 里写属性名；多个参数 → 必须 `@Param` 命名，`#{}` 里写注解里的名字。

### 3.4 #{} vs ${}

#### `#{}`：预编译参数，绝大多数场景用这个

```xml
<select id="selectById" resultType="User">
    SELECT * FROM users WHERE id = #{id}
</select>
```

MyBatis 把 `#{id}` 转成 `?` 占位符，参数单独传给数据库驱动：

```sql
-- 实际执行的 SQL
SELECT * FROM users WHERE id = ?
-- 参数 id = 1 单独传递，不会和 SQL 语句拼接在一起
```

这种方式叫**预编译（PreparedStatement）**——SQL 结构和参数是分开的，数据库先编译好 SQL 模板，再把参数当作纯数据填进去，参数里即使包含 `'`、`;` 等特殊字符也只会被当作普通字符串值，不会改变 SQL 的结构。

#### `${}`：字符串替换，有 SQL 注入风险

```xml
<select id="selectByColumn" resultType="User">
    SELECT * FROM users ORDER BY ${columnName}
</select>
```

`${columnName}` 是**直接把字符串拼接进 SQL**，不经过预编译：

```java
// 正常调用
selectByColumn("name")
// 拼接后：SELECT * FROM users ORDER BY name   ✅ 正常

// 恶意调用
selectByColumn("name; DROP TABLE users; --")
// 拼接后：SELECT * FROM users ORDER BY name; DROP TABLE users; --   ❌ 表被删了！
```

因为是字符串拼接，参数里的内容会直接成为 SQL 的一部分，恶意输入可以改变 SQL 的结构和语义——这就是 **SQL 注入**。

#### 什么时候必须用 `${}`

`#{}` 生成的是 `?` 占位符，只能用在**值**的位置（`WHERE id = ?`），不能用在**SQL 结构**的位置——表名、列名、`ORDER BY` 的字段名都不行：

```xml
<!-- ❌ 错的：表名不能用 #{}，会生成 WHERE table_name = ? 这种无意义的 SQL -->
<select id="selectFromTable" resultType="User">
    SELECT * FROM #{tableName} WHERE id = #{id}
</select>

<!-- ✅ 对的：动态表名/列名只能用 ${} -->
<select id="selectFromTable" resultType="User">
    SELECT * FROM ${tableName} WHERE id = #{id}
    <!--         ↑ 表名，只能 ${}        ↑ 值，用 #{} -->
</select>
```

这种场景下用 `${}` 是无法避免的，但**必须自己在 Java 代码里做白名单校验**，确保传入的值只能是预期范围内的几个固定字符串：

```java
private static final Set<String> ALLOWED_TABLES = Set.of("users", "orders", "products");

public List<User> selectFromTable(String tableName) {
    if (!ALLOWED_TABLES.contains(tableName)) {
        throw new BizException("Invalid table name: " + tableName);
    }
    return userMapper.selectFromTable(tableName);
}
```

**原则：永远优先用 `#{}`；只有动态表名/列名这种 SQL 结构本身需要变化的场景才用 `${}`，并且必须配合白名单校验。**

## 4. 注解方式（简单 SQL 可以不写 XML）

3.3 节用 XML 写 SQL，需要单独维护一个 XML 文件，Java 方法和 SQL 分散在两处。对于简单的单表 CRUD，MyBatis 提供注解方式，直接把 SQL 写在接口方法上：

```java
@Mapper
public interface UserMapper {

    @Select("SELECT * FROM users WHERE id = #{id}")
    User selectById(Long id);

    @Select("SELECT * FROM users")
    List<User> selectAll();

    @Insert("INSERT INTO users (name, email, created_at) VALUES (#{name}, #{email}, NOW())")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(User user);

    @Update("UPDATE users SET name = #{name}, email = #{email} WHERE id = #{id}")
    int update(User user);

    @Delete("DELETE FROM users WHERE id = #{id}")
    int deleteById(Long id);
}
```

注解和 XML 标签是一一对应的：

| 注解 | 对应 XML 标签 |
|------|-------------|
| `@Select` | `<select>` |
| `@Insert` | `<insert>` |
| `@Update` | `<update>` |
| `@Delete` | `<delete>` |
| `@Options(useGeneratedKeys=true, keyProperty="id")` | `<insert useGeneratedKeys="true" keyProperty="id">` |

`#{id}`、`#{name}` 的取值规则和 XML 里完全一样——单个简单类型参数随意命名，对象参数写属性名，多参数需要 `@Param`。

**XML vs 注解怎么选？**

| | 注解 | XML |
|---|---|---|
| 适合场景 | 简单单表 CRUD | 多表 join、动态条件、复杂统计 |
| SQL 和代码的关系 | SQL 和方法定义在一起，一眼看到 | SQL 和接口分离，需要切换文件 |
| 长 SQL 可读性 | SQL 写在字符串里，换行麻烦 | XML 天然支持换行和格式化 |
| 动态 SQL（if/where等） | 不支持 | 支持 |

实际项目中两者可以混用——同一个 Mapper 接口里，简单方法用注解，复杂方法写在对应的 XML 文件里，MyBatis 会自动识别。

## 5. 动态 SQL

MyBatis 最强大的特性之一——**根据传入参数的不同，动态拼接出不同的 SQL**。比如一个搜索接口，用户可能只传 name，也可能只传 email，也可能两者都传，对应的 SQL 条件需要动态变化，而不是写死。

### 5.1 if：条件存在时才加这段 SQL

```xml
<select id="search" resultMap="userMap">
    SELECT * FROM users
    WHERE 1 = 1
    <if test="name != null and name != ''">
        AND name LIKE CONCAT('%', #{name}, '%')
    </if>
    <if test="email != null and email != ''">
        AND email = #{email}
    </if>
</select>
```

`<if test="条件">` 里的 `test` 是判断表达式，判断**传入参数对象的属性**。条件为真时，标签内的 SQL 片段才会拼进最终的 SQL：

```
参数：name="Alice", email=null
拼接结果：SELECT * FROM users WHERE 1=1 AND name LIKE '%Alice%'

参数：name=null, email="a@b.com"
拼接结果：SELECT * FROM users WHERE 1=1 AND email = 'a@b.com'

参数：name=null, email=null
拼接结果：SELECT * FROM users WHERE 1=1
```

`WHERE 1=1` 是一个技巧——保证不管有没有 `AND` 条件，`WHERE` 后面始终有内容，SQL 语法不会出错。但这样写不优雅，所以有了下面的 `<where>`。

### 5.2 where：自动处理 WHERE 和多余的 AND

```xml
<select id="search" resultMap="userMap">
    SELECT * FROM users
    <where>
        <if test="name != null and name != ''">
            AND name LIKE CONCAT('%', #{name}, '%')
        </if>
        <if test="email != null">
            AND email = #{email}
        </if>
    </where>
    ORDER BY created_at DESC
</select>
```

`<where>` 标签做了三件事：

1. 如果里面有任意一个 `<if>` 命中，自动在最前面加上 `WHERE`
2. 自动去掉**第一个生效条件**开头多余的 `AND`（不管你写不写都行）
3. 如果所有 `<if>` 都没命中，整个 `WHERE` 都不会出现

注意：每个 `<if>` 内部的 SQL 片段都要以 `AND`（或 `OR`）开头，这是固定写法。`<where>` 只负责去掉最终拼接结果**最开头**那一个多余的 `AND`，中间的 `AND` 都要保留，否则多个条件之间无法正确连接：

```xml
<if test="name != null">AND name = #{name}</if>
<if test="email != null">AND email = #{email}</if>
```

```
两个都命中时拼接结果：AND name = 'Alice' AND email = 'a@x.com'
<where> 去掉最开头的 AND：name = 'Alice' AND email = 'a@x.com'
补上 WHERE：WHERE name = 'Alice' AND email = 'a@x.com'
```

**结论：每个 `<if>` 都要以 `AND` 开头，不要心存"反正是第一个就不用写"的想法**——`<where>` 只保证去掉最终结果开头的那一个 `AND`，不会帮你补全中间缺失的连接符。

用 `<where>` 替代手写 `WHERE 1=1`，是更规范的写法。

### 5.3 set：动态更新部分字段

更新操作经常遇到"只更新传了值的字段，其他字段保持不变"的需求：

```xml
<update id="updateSelective">
    UPDATE users
    <set>
        <if test="name != null">name = #{name},</if>
        <if test="email != null">email = #{email},</if>
    </set>
    WHERE id = #{id}
</update>
```

`<set>` 自动处理逗号——不管命中几个 `<if>`，最后一个字段后面多余的逗号会被自动去掉：

```
参数：name="Bob", email=null
结果：UPDATE users SET name = 'Bob' WHERE id = 1
      （email 那个 if 没命中，name 后面的逗号被自动去掉）

参数：name="Bob", email="bob@x.com"
结果：UPDATE users SET name = 'Bob', email = 'bob@x.com' WHERE id = 1
```

### 5.4 choose / when / otherwise：多选一，类似 switch

```xml
<select id="search" resultMap="userMap">
    SELECT * FROM users
    <where>
        <choose>
            <when test="id != null">
                AND id = #{id}
            </when>
            <when test="email != null">
                AND email = #{email}
            </when>
            <otherwise>
                AND created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
            </otherwise>
        </choose>
    </where>
</select>
```

和 `<if>` 最大的区别：`<if>` 是"每个条件独立判断，可能多个同时命中"；`<choose>` 是"按顺序判断，只命中第一个为真的分支"，剩下的全部跳过——就像 Java 的 `if-else if-else`：

```
参数：id=5
命中 <when test="id != null">，结果：... AND id = 5
（即使 email 也不为 null，也不会再判断第二个 when）

参数：id=null, email="a@b.com"
第一个 when 不命中，命中第二个，结果：... AND email = 'a@b.com'

参数：id=null, email=null
两个 when 都不命中，走 <otherwise>，结果：... AND created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
```

### 5.5 foreach：遍历集合，常用于 IN 查询和批量插入

**批量查询（IN 条件）**：

```xml
<select id="selectByIds" resultMap="userMap">
    SELECT * FROM users
    WHERE id IN
    <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</select>
```

```java
List<User> selectByIds(@Param("ids") List<Long> ids);
```

`<foreach>` 的属性含义：

| 属性 | 作用 |
|------|------|
| `collection` | 要遍历的集合，对应 `@Param` 指定的名字 |
| `item` | 遍历时每个元素的临时变量名，循环体内用 `#{item}` 引用 |
| `open` | 拼接结果的开头 |
| `separator` | 每个元素之间的分隔符 |
| `close` | 拼接结果的结尾 |

```
参数：ids = [1, 2, 3]
拼接结果：WHERE id IN ( 1 , 2 , 3 )
                    ↑open       ↑close
```

**批量插入**：

```xml
<insert id="batchInsert">
    INSERT INTO users (name, email, created_at)
    VALUES
    <foreach collection="users" item="user" separator=",">
        (#{user.name}, #{user.email}, NOW())
    </foreach>
</insert>
```

```java
int batchInsert(@Param("users") List<User> users);
```

注意这里 `item="user"` 是一个**对象**，所以循环体里用 `#{user.name}`、`#{user.email}` 取对象的属性（和 3.3 节"`#{}` 引用对象属性"的规则一致）：

```
参数：users = [User("Alice","a@x.com"), User("Bob","b@x.com")]
拼接结果：
INSERT INTO users (name, email, created_at)
VALUES ('Alice', 'a@x.com', NOW()), ('Bob', 'b@x.com', NOW())
```

一条 SQL 插入多行，比循环调用单条 `insert` 性能好得多。

### 5.6 sql 片段复用

多个查询经常需要返回同样的几个字段，重复写容易遗漏或不一致，可以提取成公共片段：

```xml
<!-- 定义可复用的 SQL 片段，id 是这个片段的名字 -->
<sql id="baseColumns">
    id, name, email, created_at
</sql>

<!-- 用 <include refid="片段id"/> 引用 -->
<select id="selectById" resultMap="userMap">
    SELECT <include refid="baseColumns"/>
    FROM users
    WHERE id = #{id}
</select>

<select id="selectAll" resultMap="userMap">
    SELECT <include refid="baseColumns"/>
    FROM users
</select>
```

两个 `<select>` 实际执行的 SQL 是：

```sql
SELECT id, name, email, created_at FROM users WHERE id = ?
SELECT id, name, email, created_at FROM users
```

以后要加一个字段，只需要改 `<sql id="baseColumns">` 这一处，所有引用它的查询都会同步更新。

## 6. 多表关联

### 6.1 一对一

**数据库表**：

```sql
-- users 表
| id | name  |
|----|-------|
| 1  | Alice |

-- user_profiles 表
| user_id | bio        | avatar       |
|---------|------------|--------------|
| 1       | developer  | avatar1.jpg  |
```

一个用户对应一条 profile 记录——一对一关系。

**JOIN 查询结果**：

```sql
SELECT u.id, u.name, p.user_id, p.bio, p.avatar
FROM users u
LEFT JOIN user_profiles p ON u.id = p.user_id
WHERE u.id = 1
```

```
| id | name  | user_id | bio        | avatar       |
|----|-------|---------|------------|--------------|
| 1  | Alice | 1       | developer  | avatar1.jpg  |
```

数据库返回的是**一行扁平的数据**，但 Java 里 `User` 想要的是嵌套结构：

```java
public class User {
    private Long id;
    private String name;
    private UserProfile profile;  // 嵌套对象
}

public class UserProfile {
    private Long userId;
    private String bio;
    private String avatar;
}
```

`<association>` 就是用来做这个转换的——把结果行里的某几列，组装成一个嵌套对象：

**XML 标签和属性详解**：

```xml
<resultMap id="userWithProfile" type="User">
    <id property="id" column="id"/>
    <result property="name" column="name"/>

    <association property="profile" javaType="UserProfile">
        <result property="userId" column="user_id"/>
        <result property="bio" column="bio"/>
        <result property="avatar" column="avatar"/>
    </association>
</resultMap>

<select id="selectWithProfile" resultMap="userWithProfile">
    SELECT u.id, u.name, p.user_id, p.bio, p.avatar
    FROM users u
    LEFT JOIN user_profiles p ON u.id = p.user_id
    WHERE u.id = #{id}
</select>
```

逐个解释：

**`<association property="..." javaType="...">`**

定义"嵌套对象"的映射规则：

- `property`：嵌套对象赋给外层对象的哪个字段，这里是 `profile`，实际调用 `User.setProfile(...)`
- `javaType`：这个嵌套对象本身的类型，这里是 `UserProfile`

`<association>` 标签内部又写了一组 `<result>`，规则和外层一样——`property` 是 `UserProfile` 类的属性名，`column` 是 SQL 结果中对应的列名。

**`<select id="..." resultMap="...">`**

定义一个查询语句。

- `id`：必须和 Mapper 接口里的方法名完全一致（这里对应 `User selectWithProfile(Long id)`）
- `resultMap`：用哪个 `<resultMap>` 来组装结果，这里引用上面定义的 `userWithProfile`

也可以用 `resultType="User"` 替代 `resultMap`——`resultType` 适合"字段名能自动映射"的简单场景，`resultMap` 适合"需要自定义映射规则"或"涉及嵌套对象"的复杂场景。

**整体流程**：

```
1. <select> 执行 SQL，从数据库拿到一行扁平数据：
   [id=1, name="Alice", user_id=1, bio="后端开发者", avatar="avatar1.jpg"]

2. resultMap="userWithProfile" 告诉 MyBatis 用哪套规则转换

3. MyBatis 按规则组装：
   - 创建一个 User 对象（type="User"）
   - 用 column="id" 的值赋给 property="id"（setId(1)）
   - 用 column="name" 的值赋给 property="name"（setName("Alice")）
   - 遇到 <association>：创建一个 UserProfile 对象（javaType="UserProfile"）
     - 用 column="user_id" 的值赋给 property="userId"（setUserId(1)）
     - ... 类似地处理 bio 和 avatar
   - 把 UserProfile 对象赋给 User 的 profile 字段（setProfile(...)）

4. 最终返回一个嵌套好的 User 对象
```

最终组装出来的 Java 对象：

```java
User {
    id = 1,
    name = "Alice",
    profile = UserProfile {
        userId = 1,
        bio = "developer",
        avatar = "avatar1.jpg"
    }
}
```

**一句话**：`<association>` 用于"一个对象里嵌套另一个对象"的场景（一对一）。

### 6.2 一对多

**数据库表**：

```sql
-- users 表
| id | name  |
|----|-------|
| 1  | Alice |

-- orders 表
| id | user_id | amount | status |
|----|---------|--------|--------|
| 101| 1       | 99.00  | PAID   |
| 102| 1       | 50.00  | PENDING|
```

一个用户对应多条订单——一对多关系。

**JOIN 查询结果**：

```sql
SELECT u.id, u.name, o.id AS order_id, o.amount, o.status
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.id = 1
```

```
| id | name  | order_id | amount | status  |
|----|-------|----------|--------|---------|
| 1  | Alice | 101      | 99.00  | PAID    |
| 1  | Alice | 102      | 50.00  | PENDING |
```

数据库返回**两行**（因为 JOIN 后一个用户对应多条订单各占一行），但 Java 里 `User` 想要的是"一个用户对象，里面包含一个订单列表"：

```java
public class User {
    private Long id;
    private String name;
    private List<Order> orders;  // 一个用户对应多个订单
}
```

`<collection>` 就是用来做这个转换的——把多行结果中重复的部分**合并成一个对象**，把变化的部分**收集成一个列表**：

```xml
<resultMap id="userWithOrders" type="User">
    <id property="id" column="id"/>           <!-- id 列 → User.id（两行的 id 都是 1，合并为同一个 User） -->
    <result property="name" column="name"/>   <!-- name 列 → User.name -->

    <!-- collection：把每一行的这几列组装成一个 Order 对象，收集进 List -->
    <collection property="orders" ofType="Order">
        <id property="id" column="order_id"/>
        <result property="amount" column="amount"/>
        <result property="status" column="status"/>
    </collection>
</resultMap>

<select id="selectWithOrders" resultMap="userWithOrders">
    SELECT u.id, u.name, o.id AS order_id, o.amount, o.status
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.id = #{id}
</select>
```

MyBatis 处理这两行数据时的逻辑：

```
第一行：id=1, name="Alice", order_id=101, amount=99.00, status="PAID"
  → User.id 和 User.name 相同的行，会被识别为"同一个 User"
  → 把 order_id/amount/status 组装成一个 Order，放进 orders 列表

第二行：id=1, name="Alice", order_id=102, amount=50.00, status="PENDING"
  → id=1 和上一行相同，还是"同一个 User"，不会创建第二个 User 对象
  → 把这一行的 order_id/amount/status 组装成另一个 Order，加进同一个 orders 列表
```

最终组装出来的 Java 对象：

```java
User {
    id = 1,
    name = "Alice",
    orders = [
        Order { id = 101, amount = 99.00, status = "PAID" },
        Order { id = 102, amount = 50.00, status = "PENDING" }
    ]
}
```

**一句话**：`<collection>` 用于"一个对象里嵌套一个列表"的场景（一对多），`<resultMap>` 里的 `<id>` 标签是判断"哪几行属于同一个对象"的依据——`id` 相同的行会被合并。

### `<association>` vs `<collection>`

| | `<association>` | `<collection>` |
|---|---|---|
| 关系 | 一对一 | 一对多 |
| 结果 | 嵌套一个对象 | 嵌套一个列表 |
| 属性 | `javaType="目标类型"` | `ofType="列表元素类型"` |

## 7. 分页

### 7.1 手动分页

```xml
<select id="selectPage" resultMap="userMap">
    SELECT * FROM users
    ORDER BY created_at DESC
    LIMIT #{offset}, #{size}
</select>

<select id="countAll" resultType="long">
    SELECT COUNT(*) FROM users
</select>
```

### 7.2 PageHelper 插件（推荐）

```kotlin
dependencies {
    implementation("com.github.pagehelper:pagehelper-spring-boot-starter:1.4.7")
}
```

```xml
<dependency>
    <groupId>com.github.pagehelper</groupId>
    <artifactId>pagehelper-spring-boot-starter</artifactId>
    <version>1.4.7</version>
</dependency>
```

```java
// 使用方式：在查询前调用 PageHelper.startPage
public PageInfo<User> listPage(int pageNum, int pageSize) {
    PageHelper.startPage(pageNum, pageSize);  // 自动拦截下一条查询，追加 LIMIT
    List<User> list = userMapper.selectAll();  // 正常的查询，不需要改 SQL
    return new PageInfo<>(list);               // 包含总数、总页数、当前页等信息
}
```

```java
// PageInfo 包含的信息
PageInfo<User> page = listPage(1, 10);
page.getTotal();      // 总记录数
page.getPages();      // 总页数
page.getPageNum();    // 当前页码
page.getPageSize();   // 每页大小
page.getList();       // 当前页数据
page.isHasNextPage(); // 是否有下一页
```

## 8. MyBatis-Plus：MyBatis 的增强工具

MyBatis-Plus 不改变 MyBatis 的任何东西，只在它基础上做增强——**单表 CRUD 零 SQL，复杂查询仍然用 MyBatis 原生方式。**

### 8.1 引入依赖

```kotlin
// MyBatis-Plus 替代 mybatis-spring-boot-starter，不需要同时引入
dependencies {
    implementation("com.baomidou:mybatis-plus-spring-boot3-starter:3.5.5")
    runtimeOnly("com.mysql:mysql-connector-j:8.2.0")
}
```

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.12</version>
</dependency>
```

### 8.2 实体类注解

```java
@TableName("users")
public class User {
    @TableId(type = IdType.AUTO)
    private Long id;

    private String name;        // 自动映射 name 列
    private String email;

    @TableField("created_at")   // 列名和字段名不一致时指定
    private LocalDateTime createdAt;

    @TableField(exist = false)  // 标记非数据库字段
    private String extra;

    @TableLogic                 // 逻辑删除标记（0=未删除，1=已删除）
    private Integer deleted;

    // getter / setter
}
```

### 8.3 Mapper 接口

```java
@Mapper
public interface UserMapper extends BaseMapper<User> {
    // 继承 BaseMapper 后，自动拥有以下方法：
    // insert(entity)
    // deleteById(id)
    // deleteBatchIds(idList)
    // updateById(entity)
    // selectById(id)
    // selectBatchIds(idList)
    // selectList(wrapper)
    // selectCount(wrapper)
    // selectPage(page, wrapper)
    // ... 共 17 个通用方法

    // 如果需要自定义复杂 SQL，仍然可以写 XML 或注解
    @Select("SELECT * FROM users WHERE name LIKE CONCAT('%', #{keyword}, '%')")
    List<User> customSearch(String keyword);
}
```

### 8.4 Service 层

8.3 节的 `BaseMapper<User>` 是 Mapper 层的通用封装；MyBatis-Plus 在 Service 层也提供了一套对应的通用封装——`IService` 和 `ServiceImpl`。

```java
// 1. Service 接口继承 IService<User>
public interface UserService extends IService<User> {
    // IService<User> 已经声明了 save / removeById / updateById
    // getById / list / page / count 等通用方法，不需要自己写
}

// 2. 实现类继承 ServiceImpl<UserMapper, User>
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
    // ServiceImpl 已经实现了 IService 的所有通用方法
    // 这里留空也能直接用；自定义业务方法写在这里
}
```

`ServiceImpl<UserMapper, User>` 这一长串拆开看：

- `ServiceImpl<M, T>` 是一个**泛型类**，`M` 是 Mapper 类型、`T` 是实体类型——和 `BaseMapper<User>` 是同一种写法，只是这里要传两个类型参数
- 传入 `<UserMapper, User>` 后，`ServiceImpl` 内部就知道"该用 `UserMapper` 操作 `User` 表"，自动注入 `UserMapper`，并基于它实现 `save`、`getById`、`list`、`page` 等方法的具体逻辑
- `implements UserService` 是为了满足第 1 步定义的接口，这样其他类只需要依赖 `UserService` 接口，不用关心具体实现

写完这两段代码后，`UserServiceImpl` 就自动拥有了一整套 CRUD 方法，不需要再手写：

```java
@Autowired
private UserService userService;

userService.getById(1L);          // 等价于 mapper.selectById(1L)
userService.save(user);           // 等价于 mapper.insert(user)
userService.list();               // 等价于 mapper.selectList(null)，查全部
userService.removeById(1L);       // 等价于 mapper.deleteById(1L)
```

这一层的意义：业务代码统一面向 `UserService` 编程，简单 CRUD 直接调用 `IService` 现成的方法；遇到自定义业务逻辑，就在 `UserServiceImpl` 里加新方法。

### 8.5 条件构造器（Wrapper）：用代码拼 WHERE 条件

#### 为什么需要 Wrapper

`BaseMapper` 提供的方法基本都是围绕**主键**的（`selectById`、`updateById`、`deleteById`），但实际业务里经常要按别的字段查询——比如"按邮箱查用户"是按 `email` 查，不是按主键 `id` 查。这种"自定义 WHERE 条件"就是 Wrapper（条件构造器）要解决的问题：**用 Java 代码拼出 WHERE 子句，不用写 SQL 或 XML**。

```java
new LambdaQueryWrapper<User>()
    .eq(User::getEmail, "alice@example.com")
// 等价于 SELECT * FROM users WHERE email = ?
```

构造好的 wrapper 直接传给 `BaseMapper` 的方法：

```java
User user = userMapper.selectOne(wrapper);   // 查一条
List<User> users = userMapper.selectList(wrapper); // 查多条
```

#### QueryWrapper vs LambdaQueryWrapper

两者功能完全一样，区别只在**字段怎么写**：

```java
// QueryWrapper：字段名是字符串
new QueryWrapper<User>().eq("email", email)

// LambdaQueryWrapper：字段是方法引用
new LambdaQueryWrapper<User>().eq(User::getEmail, email)
```

| | QueryWrapper | LambdaQueryWrapper |
|---|---|---|
| 字段写法 | 字符串 `"email"` | 方法引用 `User::getEmail` |
| 写错字段名 | 编译通过，运行时才报 SQL 错误 | **编译失败**，IDE 直接标红 |
| 字段重命名 | 字符串不会跟着改，容易漏改 | IDE 重构方法名时一起改 |
| 写的是什么 | 数据库列名（下划线） | Java 属性名（驼峰），框架自动转列名 |

**结论：优先用 `LambdaQueryWrapper`**——多写一点 `::getXxx`，换来的是字段改名、打错字都能在编译期发现。

#### 常用条件方法

每个方法对应一段 `WHERE` 条件，链式调用多个方法时，默认用 `AND` 连接：

| 方法 | 生成的 SQL 片段 | 说明 |
|------|---------------|------|
| `.eq(字段, 值)` | `字段 = ?` | 等于，最常用 |
| `.ne(字段, 值)` | `字段 != ?` | 不等于 |
| `.gt(字段, 值)` / `.ge(字段, 值)` | `字段 > ?` / `字段 >= ?` | 大于 / 大于等于 |
| `.lt(字段, 值)` / `.le(字段, 值)` | `字段 < ?` / `字段 <= ?` | 小于 / 小于等于 |
| `.like(字段, 值)` | `字段 LIKE '%值%'` | 模糊匹配，两边自动加 `%` |
| `.likeLeft(字段, 值)` / `.likeRight(字段, 值)` | `字段 LIKE '%值'` / `字段 LIKE '值%'` | 只在一侧加 `%` |
| `.in(字段, 集合)` / `.notIn(字段, 集合)` | `字段 IN (...)` / `字段 NOT IN (...)` | 属于 / 不属于集合中的值 |
| `.isNull(字段)` / `.isNotNull(字段)` | `字段 IS NULL` / `字段 IS NOT NULL` | 是否为空 |
| `.between(字段, 起, 止)` | `字段 BETWEEN ? AND ?` | 闭区间 |
| `.orderByDesc(字段)` / `.orderByAsc(字段)` | `ORDER BY 字段 DESC/ASC` | 排序 |

```java
List<User> users = new LambdaQueryWrapper<User>()
    .eq(User::getStatus, 1)                               // status = 1
    .in(User::getId, List.of(1L, 2L, 3L))                 // AND id IN (1,2,3)
    .like(User::getName, "Ali")                           // AND name LIKE '%Ali%'
    .orderByDesc(User::getCreatedAt)                      // ORDER BY created_at DESC
    .list();
```

对应的 SQL：

```sql
SELECT * FROM users
WHERE status = 1
  AND id IN (1, 2, 3)
  AND name LIKE '%Ali%'
ORDER BY created_at DESC
```

#### 动态条件：第一个参数是 boolean

5.1 节讲过 XML 用 `<if test="...">` 实现"参数存在才拼这段 SQL"。Wrapper 里每个条件方法都有一个重载版本，**第一个参数是 `boolean condition`，为 `false` 时这个条件直接不会拼进 SQL**——这就是 Wrapper 版本的 `<if>`：

```java
public List<User> search(String name, Integer status, List<Long> ids) {
    return new LambdaQueryWrapper<User>()
        .like(StringUtils.hasText(name), User::getName, name)   // name 有值才加这个条件
        .eq(status != null, User::getStatus, status)            // status 不为 null 才加
        .in(ids != null && !ids.isEmpty(), User::getId, ids)
        .list();
}
```

```
调用 search("Alice", null, null)
→ SELECT * FROM users WHERE name LIKE '%Alice%'

调用 search(null, 1, null)
→ SELECT * FROM users WHERE status = 1

调用 search(null, null, null)
→ SELECT * FROM users   （没有任何条件）
```

不需要写 `if-else` 拼字符串，就实现了"传了什么条件就用什么条件"，比 XML 动态 SQL 更直观。

#### and / or：条件分组（带括号的逻辑）

链式调用的多个条件默认是 `AND`。如果要表达 `status = 1 AND (id = 1 OR id = 2)` 这种带括号的逻辑，用 `.and()` 配合 Lambda：

```java
new LambdaQueryWrapper<User>()
    .eq(User::getStatus, 1)
    .and(w -> w.eq(User::getId, 1L).or().eq(User::getId, 2L));
// WHERE status = 1 AND (id = 1 OR id = 2)
```

`.and(w -> ...)` 里的 `w` 是一个独立的子条件构造器，它内部拼出的条件会被括号包裹，再整体用 `AND` 接到外层条件后面；`.or()` 把它前后两个条件之间的连接符从默认的 `AND` 换成 `OR`。

#### UpdateWrapper：更新条件

```java
LambdaUpdateWrapper<User> wrapper = new LambdaUpdateWrapper<>();
wrapper.set(User::getName, "NewName")
       .set(User::getEmail, "new@example.com")
       .eq(User::getId, 1L);

userMapper.update(null, wrapper);
// UPDATE users SET name = 'NewName', email = 'new@example.com' WHERE id = 1
```

`.set(字段, 新值)` 指定要更新成什么；`.eq()` 等条件方法指定 `WHERE`。`update()` 第一个参数是要更新的实体对象，传 `null` 表示"更新内容全部由 wrapper 的 `.set()` 指定，不需要再传一个实体"。

#### selectOne / selectList / selectCount 怎么选

| 方法 | 返回值 | 适用场景 | 结果命中多行时 |
|------|--------|---------|--------------|
| `selectOne(wrapper)` | 单个对象或 `null` | 业务上唯一的查询，如按 `slotId` 查广告位 | **抛异常**（`TooManyResultsException`） |
| `selectList(wrapper)` | `List<T>` | 查多条记录，如查某广告位关联的所有 DSP | 正常返回多条 |
| `selectCount(wrapper)` | `Long` | 只要数量，不要数据本身（分页总数、判断是否存在） | - |

**`selectOne` 的关键点**：它不是"取第一条"，而是"断言只有一条"——如果 `WHERE` 条件命中了多行，MyBatis-Plus 会直接抛异常而不是悄悄返回第一行。只在业务上能保证唯一（如 `slotId` 是唯一索引）的场景用它；如果不确定是否唯一，用 `selectList` 再在 Service 层处理多条的情况。

### 8.6 分页

```java
// 1. 配置分页插件
@Configuration
public class MyBatisPlusConfig {
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }
}

// 2. 使用
Page<User> page = new Page<>(1, 10);  // 第 1 页，每页 10 条

LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
wrapper.like(User::getName, keyword);

Page<User> result = userMapper.selectPage(page, wrapper);

result.getRecords();   // 当前页数据
result.getTotal();     // 总记录数
result.getPages();     // 总页数
result.getCurrent();   // 当前页码
result.getSize();      // 每页大小
```

### 8.7 自动填充

```java
// 自动填充创建时间和更新时间
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {
    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createdAt", LocalDateTime::now, LocalDateTime.class);
        this.strictInsertFill(metaObject, "updatedAt", LocalDateTime::now, LocalDateTime.class);
    }

    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updatedAt", LocalDateTime::now, LocalDateTime.class);
    }
}

// 实体类中标记
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createdAt;

@TableField(fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updatedAt;
```

## 9. MyBatis vs MyBatis-Plus 选型

| 场景 | 推荐 |
|------|------|
| 单表 CRUD | MyBatis-Plus（零 SQL） |
| 动态查询条件 | MyBatis-Plus（LambdaQueryWrapper 比 XML 动态 SQL 简洁） |
| 复杂多表关联 | 原生 MyBatis XML |
| 存储过程 / 复杂报表 SQL | 原生 MyBatis XML |
| 新项目 | MyBatis-Plus（兼容原生 MyBatis，按需用 XML） |

两者不是二选一——MyBatis-Plus 内部就是 MyBatis，简单查询用 Wrapper，复杂查询写 XML，完美共存。

## 10. 小结

| 主题 | 关键要点 |
|------|---------|
| MyBatis 定位 | 半自动 ORM，SQL 手写，结果映射自动 |
| #{} vs ${} | #{} 预编译防注入（默认用这个），${} 字符串拼接（仅用于动态表名/列名） |
| XML vs 注解 | 简单用注解，复杂用 XML，可以混用 |
| 动态 SQL | if、where、set、choose、foreach、sql 片段 |
| 多表关联 | association（一对一）、collection（一对多） |
| 分页 | PageHelper 插件或 MyBatis-Plus 分页插件 |
| MyBatis-Plus | 继承 BaseMapper 零 SQL，LambdaQueryWrapper 动态查询 |
| 条件构造 | 第一个参数传 boolean condition，false 时不拼接——替代 XML 的 if 标签 |
| 自动填充 | MetaObjectHandler 自动设置创建/更新时间 |
| 共存策略 | 单表用 Plus，复杂 SQL 用原生 XML |

---

> **下一篇预告**：设计模式在 Java 中的典型应用——工厂、策略、观察者、代理

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
