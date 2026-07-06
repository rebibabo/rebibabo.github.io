---
title: Java 基础词汇表
tags:
  - wiki
  - glossary
  - java
  - java-basic
type: glossary
source_series: Java-basic
status: seed
---

# Java 基础词汇表

[[wiki/index|返回 Wiki 首页]]
[[wiki/series/java-basic|返回 Java 基础系列]]

Java 基础知识体系包含大量语言特性、运行时概念和工程术语。这个词汇表提供每个术语的**简短定义**和**快速索引**，不做深度展开——想深入了解任何术语，请跳转到对应的概念页或原始文章。

## 语言基础

| 术语 | 一句话 |
|------|--------|
| [[JDK]] | Java Development Kit，包含编译器、JVM 和核心类库的开发工具包 |
| JRE | Java Runtime Environment，运行 Java 程序的必备环境 |
| [[JVM]] | Java Virtual Machine，执行 Java 字节码的虚拟机 |
| [[原始类型]] | byte/short/int/long/float/double/char/boolean 八种基本数据类型 |
| [[包装类型]] | 原始类型对应的对象类型：Integer、Long、Double 等 |
| [[自动装箱]] | 编译器自动将原始类型转换为包装类型 |
| 自动拆箱 | 编译器自动将包装类型转换为原始类型 |
| [[String]] | 不可变字符序列，底层为 final 的 byte[] 数组 |
| [[String-Pool]] | JVM 中维护的字符串常量池，字面量优先从池中获取 |
| [[StringBuilder]] | 可变字符序列，非线程安全，单线程拼接首选 |
| StringBuffer | 可变字符序列，线程安全（方法加 synchronized） |
| [[equals-和-==]] | equals 比较对象内容是否相等，== 比较引用地址（原始类型比较值） |
| [[hashCode]] | 返回对象的哈希码，equals 相等的对象 hashCode 必须相等 |

## 类与对象

| 术语 | 一句话 |
|------|--------|
| [[构造方法]] | 创建对象时自动调用的特殊方法，用于初始化对象状态 |
| [[访问控制]] | public/protected/default/private 四种修饰符控制类与成员的可见性 |
| [[static]] | 静态修饰符，使成员属于类本身而非实例 |
| [[final]] | 修饰类则不可继承，修饰方法则不可重写，修饰变量则不可修改 |
| [[继承]] | extends 关键字，子类复用父类的字段和方法 |
| [[多态]] | 同一方法调用在不同子类上表现出不同行为 |
| [[方法重写]] | 子类重新定义父类方法，要求签名一致、返回值兼容、访问权限不更严 |
| 方法重载 | 同一类中方法名相同但参数列表不同 |
| [[抽象类]] | abstract 修饰的类，不能实例化，可以有抽象方法和具体方法 |
| [[接口]] | 定义行为契约，Java 8+ 支持 default/static 方法 |
| 内部类 | 定义在另一个类内部的类，包括成员内部类、局部内部类、匿名内部类、静态内部类 |

## 集合框架

| 术语 | 一句话 |
|------|--------|
| [[集合框架]] | Java 提供的统一数据结构 API：Collection、List、Set、Queue、Map |
| [[ArrayList]] | 基于动态数组的 List 实现，随机访问 O(1)，插入删除 O(n) |
| [[LinkedList]] | 基于双向链表的 List/Deque 实现，插入删除 O(1)，随机访问 O(n) |
| [[HashMap]] | 基于数组+链表+红黑树的哈希表，get/put O(1)~O(n) |
| [[HashSet]] | 基于 HashMap 的 Set 实现，元素不重复 |
| [[TreeMap]] | 基于红黑树的 NavigableMap 实现，key 有序 |
| TreeSet | 基于 TreeMap 的 NavigableSet 实现，元素有序 |
| [[LinkedHashMap]] | 继承 HashMap，维护双向链表保证插入/访问顺序 |
| Queue | 队列接口，FIFO；Deque 为双端队列 |
| [[PriorityQueue]] | 基于二叉堆的优先队列，按优先级出队 |
| Collections | 集合工具类，提供排序、查找、同步包装等静态方法 |
| Comparable | 自然排序接口，实现 compareTo 方法 |
| Comparator | 外部比较器，用于自定义排序逻辑 |

## 泛型

| 术语 | 一句话 |
|------|--------|
| [[泛型]] | Java 5 引入的类型参数化机制，编译期做类型检查 |
| [[类型擦除]] | 编译器将泛型类型参数擦除为边界类型（默认 Object） |
| [[PECS]] | Producer Extends, Consumer Super：读取用 ? extends，写入用 ? super |
| [[通配符]] | ? 表示未知类型，配合 extends/super 限定上下界 |
| 泛型方法 | 在方法返回值前声明类型参数的方法 |
| 泛型擦除的影响 | 泛型在运行时不可获取具体类型，不能 new 泛型数组、不能 instanceof 泛型 |

## 异常

| 术语 | 一句话 |
|------|--------|
| [[Throwable]] | 异常体系根类，子类 Error 和 Exception |
| [[Checked-Exception]] | 编译期强制处理的异常（extends Exception），必须 try-catch 或 throws |
| [[Unchecked-Exception]] | 运行时异常（extends RuntimeException），不强制处理 |
| Error | 严重错误（OutOfMemoryError、StackOverflowError），程序通常无法恢复 |
| [[try-with-resources]] | 自动关闭实现了 AutoCloseable 的资源 |
| finally | 无论是否抛异常都会执行的代码块 |
| [[异常链]] | 通过 cause 将底层异常包装为上层异常，保留根因信息 |

## Lambda 与 Stream

| 术语 | 一句话 |
|------|--------|
| [[Lambda]] | 函数式接口的简洁实现：(参数) -> { 方法体 } |
| [[函数式接口]] | 只有一个抽象方法的接口，标注 @FunctionalInterface |
| [[Stream-API]] | 对集合进行函数式操作的流水线：filter/map/reduce/collect |
| [[中间操作]] | 返回 Stream 的惰性操作：filter、map、sorted、distinct、limit 等 |
| [[终端操作]] | 触发流水线执行的操作：collect、forEach、reduce、count、findFirst 等 |
| [[Optional]] | 可能为 null 的容器对象，避免空指针异常 |
| [[方法引用]] | Class::method 语法，Lambda 的简化写法 |
| [[Collectors]] | 收集器工具类：toList、toMap、groupingBy、partitioningBy、joining |

## I/O

| 术语 | 一句话 |
|------|--------|
| [[字节流]] | InputStream/OutputStream，以字节为单位读写 |
| [[字符流]] | Reader/Writer，以字符为单位读写，内置编解码 |
| [[缓冲流]] | BufferedInputStream/BufferedReader，带缓冲的包装流 |
| 对象序列化 | ObjectOutputStream/ObjectInputStream，将对象转为字节流并恢复 |
| [[NIO]] | New I/O，基于 Channel 和 Buffer 的非阻塞 I/O |
| [[Files]] | Java 7 引入的工具类，提供文件读写、复制、遍历等便捷方法 |
| [[Path]] | Java 7 引入的路径抽象，替代 java.io.File |

## JVM

| 术语 | 一句话 |
|------|--------|
| [[类加载]] | 将 .class 文件的字节码加载到 JVM 内存并生成 Class 对象的过程 |
| [[双亲委派]] | 类加载器优先委托父加载器加载，保证核心类的安全性和唯一性 |
| [[堆]] | JVM 最大内存区域，存放对象实例和数组，GC 主要工作区 |
| [[栈]] | 线程私有，存放栈帧（局部变量表、操作数栈、返回地址） |
| [[方法区]] | 存储类信息、常量、静态变量、JIT 编译后的代码缓存（元空间） |
| 程序计数器 | 线程私有，记录当前线程执行的字节码行号 |
| [[垃圾回收]] | 自动回收不再使用的对象内存 |
| [[新生代]] | 堆的分代区域，存放新创建对象，发生 Minor GC |
| [[老年代]] | 堆的分代区域，长期存活对象，发生 Major/Full GC |
| [[GC-算法]] | 标记-清除、标记-复制、标记-整理三种基本算法 |

## 注解与反射

| 术语 | 一句话 |
|------|--------|
| [[注解]] | 代码中的元数据标记，@interface 定义，编译期或运行时处理 |
| [[元注解]] | 修饰注解的注解：@Target、@Retention、@Documented、@Inherited、@Repeatable |
| [[反射]] | 运行时动态获取类信息、创建对象、调用方法和访问字段的能力 |
| [[动态代理]] | 运行时生成代理类，JDK 动态代理（接口）和 CGLIB 代理（类） |

## 枚举与日期

| 术语 | 一句话 |
|------|--------|
| [[枚举]] | enum 关键字，限定个数的类型安全的常量集合 |
| 枚举方法 | 枚举可以有构造方法、字段和普通方法 |
| LocalDate | 不可变日期对象（不包含时间） |
| LocalTime | 不可变时间对象（不包含日期） |
| [[LocalDateTime]] | 不可变日期时间对象 |
| [[ZonedDateTime]] | 带时区的完整日期时间 |
| [[Instant]] | 时间线上的瞬时点，Unix 纪元起纳秒计数 |
| [[DateTimeFormatter]] | 线程安全的日期格式化器 |

## 构建工具

| 术语 | 一句话 |
|------|--------|
| [[Maven]] | 基于 pom.xml 的项目构建和依赖管理工具 |
| [[Gradle]] | 基于 Groovy/Kotlin DSL 的构建工具，增量构建更灵活 |
| [[依赖传递]] | Maven/Gradle 自动引入依赖所需的传递性依赖 |
| [[依赖冲突]] | 不同版本的同名依赖同时存在时的冲突与仲裁 |
| scope | Maven 依赖范围：compile/provided/runtime/test/system |

## Spring

| 术语 | 一句话 |
|------|--------|
| [[IoC]] | Inversion of Control，将对象创建和管理的控制权交给容器 |
| [[DI]] | Dependency Injection，容器自动将依赖注入到需要它们的对象中 |
| [[Bean]] | Spring IoC 容器管理的对象 |
| ApplicationContext | Spring 核心容器，负责 Bean 的创建、配置和生命周期管理 |
| [[AOP]] | Aspect-Oriented Programming，将横切关注点（日志、事务）模块化 |
| 切面 | 横切关注点的模块化单元 |
| 通知 | Before、After、Around、AfterReturning、AfterThrowing |
| 切入点 | 表达式指定在何处应用通知 |
| [[SpringBoot]] | 简化 Spring 应用创建的框架，核心是自动配置和 Starter |
| [[自动配置]] | @EnableAutoConfiguration，根据类路径 jar 依赖自动配置 Bean |
| [[Starter]] | 一站式依赖描述符，引入即用（如 spring-boot-starter-web） |
| application.yml | Spring Boot 配置文件，集中管理应用参数 |
| @SpringBootApplication | 组合注解：@Configuration + @EnableAutoConfiguration + @ComponentScan |

## 数据访问

| 术语 | 一句话 |
|------|--------|
| [[MyBatis]] | 半自动 ORM 框架，SQL 与 Java 代码解耦 |
| [[动态SQL]] | MyBatis 的 if/choose/foreach/where/set 标签，灵活拼接 SQL |
| MyBatis-Plus | MyBatis 增强工具，提供通用 CRUD、分页、条件构造器 |
| [[事务]] | 一组数据库操作要么全部成功要么全部回滚（ACID） |
| 事务隔离级别 | READ_UNCOMMITTED / READ_COMMITTED / REPEATABLE_READ / SERIALIZABLE |
| 事务传播 | REQUIRED/REQUIRES_NEW/NESTED 等，控制事务嵌套行为 |
| [[索引]] | 加速查询的数据结构，常用 B+ 树 |
| 聚簇索引 | InnoDB 主键索引，叶子节点存储完整行数据 |
| 覆盖索引 | 查询列全部在索引中，不需要回表 |
| 最左前缀 | 联合索引中只有从最左列开始的查询条件才能利用索引 |
| [[Redis]] | 基于内存的键值存储，用作缓存、分布式锁、消息队列 |
| [[缓存穿透]] | 查询不存在的数据，大量请求直达 DB |
| 缓存击穿 | 热点 key 过期瞬间，大量请求同时打到 DB |
| [[缓存雪崩]] | 大量 key 同时过期或 Redis 宕机，请求全部打到 DB |

## 工程实践

| 术语 | 一句话 |
|------|--------|
| [[设计模式]] | 经过验证的可复用解决方案，创建型/结构型/行为型三大类 |
| [[单例模式]] | 确保类只有一个实例，提供全局访问点 |
| [[工厂模式]] | 将对象创建逻辑封装在工厂方法中 |
| [[策略模式]] | 定义算法族，运行时选择具体策略 |
| [[JUnit-5]] | Java 主流单元测试框架，标注 @Test/@BeforeEach/@AfterEach |
| [[Mockito]] | Mock 框架，模拟依赖对象行为，验证方法调用 |
| [[Git]] | 分布式版本控制系统 |
| commit | 将暂存区变更保存到本地仓库 |
| branch | 分支，独立开发线 |
| merge | 合并分支变更 |
| rebase | 变基，将提交应用到另一个分支顶部 |
| [[Tomcat]] | 开源的 Servlet 容器，Spring Boot 内嵌的默认 Web 服务器 |
| [[Servlet]] | Java Web 组件，处理 HTTP 请求和响应 |
| [[Filter]] | 在请求到达 Servlet 前/响应返回前执行过滤逻辑 |
| [[RabbitMQ]] | 基于 AMQP 协议的消息中间件，支持多种交换机类型 |
| [[Kafka]] | 高吞吐的分布式消息系统，基于日志的发布-订阅模式 |
| [[partition]] | Kafka 分区，消息并行和顺序保证的基本单元 |
| [[消费者组]] | Kafka 消费模型，组内每个消费者消费不同分区 |

## 数据结构底层

| 术语 | 一句话 |
|------|--------|
| [[红黑树]] | 自平衡二叉查找树，HashMap 链表转树的数据结构 |
| [[负载因子]] | HashMap 扩容阈值：元素数量 > 容量 × 负载因子时扩容 |
| [[哈希冲突]] | 不同 key 计算得到相同哈希值，用链表/红黑树解决 |
| [[扩容]] | HashMap 容量翻倍并重新计算所有元素位置 |
| [[ArrayList-扩容]] | 默认扩容为原容量的 1.5 倍 |

## 使用说明

- 每个词条都是**快速参考**，1-2 分钟读完
- 想看完整上下文：跳到词条末尾的"深入阅读"链接
- 想看原始文章：从 [[wiki/series/java-basic|系列主页]] 按推荐顺序阅读
- 想看学习路径图：打开 [[wiki/maps/java-basic|Java 基础学习路径]]
