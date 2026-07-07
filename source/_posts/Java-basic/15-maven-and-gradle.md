---
title: 'Java基础(15) | 构建工具：Maven vs Gradle，依赖管理与项目结构'
date: 2026-05-15
tags:
  - Java
  - Maven
  - Gradle
categories:
  - java-basics
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

Java 项目不像 Python 那样一个 `.py` 文件就能跑——真实项目涉及依赖管理、编译、测试、打包、发布等一系列工程化流程。构建工具就是把这些事情自动化的基础设施。这篇文章把 Maven 和 Gradle 两个主流工具都讲清楚，重点放在日常开发中最常用的操作。

<!-- more -->

## 1. 为什么需要构建工具？

一个真实的 Java 项目，手动操作会是这样：

```
1. 去各个网站下载依赖 jar 包，放到 lib 目录
2. javac -cp lib/*.jar src/**/*.java -d out/
3. 跑测试：java -cp out:lib/* org.junit.runner.JUnitCore ...
4. 打 jar 包：jar cvf app.jar -C out/ .
5. 部署到服务器
6. 依赖更新了？重新下载，重复上面所有步骤...
```

构建工具做的事情就是：**用一个配置文件描述项目结构和依赖，然后一条命令搞定所有。**

## 2. Maven

### 2.1 核心概念

Maven 的哲学是**约定优于配置**——它预定义了标准的项目结构和构建流程，你只需要写一个 `pom.xml` 描述项目信息和依赖。

标准项目结构：

```
my-project/
├── pom.xml                  ← 项目配置文件（核心）
├── src/
│   ├── main/
│   │   ├── java/            ← 源代码
│   │   │   └── com/example/
│   │   │       └── App.java
│   │   └── resources/       ← 配置文件（application.yml 等）
│   └── test/
│       ├── java/            ← 测试代码
│       └── resources/       ← 测试配置
└── target/                  ← 编译输出（自动生成）
```

### 2.2 pom.xml 详解

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- 项目坐标：唯一标识一个项目/模块 -->
    <groupId>com.example</groupId>       <!-- 组织/公司（反转域名） -->
    <artifactId>my-app</artifactId>      <!-- 项目名 -->
    <version>1.0.0</version>             <!-- 版本号 -->
    <packaging>jar</packaging>           <!-- 打包方式：jar / war / pom -->

    <!-- 属性：集中管理版本号和配置 -->
    <properties>
        <java.version>17</java.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <spring-boot.version>3.2.0</spring-boot.version>
    </properties>

    <!-- 依赖声明 -->
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>${spring-boot.version}</version>
        </dependency>

        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.10.0</version>
            <scope>test</scope>   <!-- 只在测试时使用 -->
        </dependency>
    </dependencies>
</project>
```

### 2.3 坐标（GAV）

每个 Maven 依赖由三个要素唯一确定：

```
groupId:artifactId:version
```

```xml
<!-- 就像收件地址：国家:城市:门牌号 -->
<groupId>com.google.guava</groupId>     <!-- 谁开发的 -->
<artifactId>guava</artifactId>           <!-- 叫什么名字 -->
<version>32.1.3-jre</version>            <!-- 哪个版本 -->
```

去哪找坐标？[Maven Central](https://search.maven.org/) 或 [mvnrepository.com](https://mvnrepository.com/)，搜索库名直接复制 XML 片段。

### 2.4 依赖范围（Scope）

| Scope | 编译 | 测试 | 运行 | 打包 | 典型依赖 |
|-------|------|------|------|------|---------|
| `compile`（默认） | ✅ | ✅ | ✅ | ✅ | Spring、Guava |
| `test` | ❌ | ✅ | ❌ | ❌ | JUnit、Mockito |
| `provided` | ✅ | ✅ | ❌ | ❌ | Servlet API（容器提供） |
| `runtime` | ❌ | ✅ | ✅ | ✅ | JDBC 驱动 |
| `system` | ✅ | ✅ | ❌ | ❌ | 本地 jar（不推荐） |

```xml
<!-- JUnit 只在测试时用 -->
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>
</dependency>

<!-- MySQL 驱动：编译时不需要，运行时才加载 -->
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <version>8.2.0</version>
    <scope>runtime</scope>
</dependency>
```

### 2.5 依赖传递与冲突

```
你的项目 → 依赖 A → 依赖 C 1.0
你的项目 → 依赖 B → 依赖 C 2.0
```

Maven 的解决策略：**最短路径优先**，路径相同时**先声明优先**。

```xml
<!-- 如果自动选择的版本不对，可以手动排除 + 显式指定 -->
<dependency>
    <groupId>com.example</groupId>
    <artifactId>lib-a</artifactId>
    <version>1.0</version>
    <exclusions>
        <exclusion>
            <groupId>com.example</groupId>
            <artifactId>lib-c</artifactId>  <!-- 排除 A 传递过来的 C -->
        </exclusion>
    </exclusions>
</dependency>

<!-- 显式声明你要用的版本 -->
<dependency>
    <groupId>com.example</groupId>
    <artifactId>lib-c</artifactId>
    <version>2.0</version>
</dependency>
```

查看依赖树，排查冲突：

```bash
mvn dependency:tree
# 会打印完整的依赖树，显示每个依赖是怎么传递进来的
```

### 2.6 生命周期与常用命令

Maven 定义了三套生命周期，最常用的是 default：

```
validate → compile → test → package → verify → install → deploy
```

每个阶段包含前面所有阶段，执行某个阶段会自动执行它前面的所有阶段：

```bash
# 编译
mvn compile

# 运行测试
mvn test

# 打包（编译 + 测试 + 打 jar/war）
mvn package

# 安装到本地仓库（~/.m2/repository），其他本地项目可以依赖它
mvn install

# 清理 target 目录
mvn clean

# 最常用的组合
mvn clean package              # 清理 + 打包
mvn clean package -DskipTests  # 跳过测试打包（赶时间用）
mvn clean install              # 清理 + 打包 + 安装到本地

# 查看有效 POM（合并了父 POM 和默认配置后的完整配置）
mvn help:effective-pom

# 查看依赖树
mvn dependency:tree
```

### 2.7 Maven 仓库

```
本地仓库（~/.m2/repository/）
  ↑ 找不到就去远程下载
中央仓库（repo.maven.apache.org）
  ↑ 或者公司的私服
私服（Nexus / Artifactory）
```

配置阿里云镜像加速（`~/.m2/settings.xml`）：

```xml
<mirrors>
    <mirror>
        <id>aliyun</id>
        <mirrorOf>central</mirrorOf>
        <name>Aliyun Maven Mirror</name>
        <url>https://maven.aliyun.com/repository/public</url>
    </mirror>
</mirrors>
```

### 2.8 继承与多模块

大型项目通常拆分为多个模块：

```
parent-project/
├── pom.xml                    ← 父 POM（packaging: pom）
├── common/
│   ├── pom.xml
│   └── src/
├── service/
│   ├── pom.xml
│   └── src/
└── web/
    ├── pom.xml
    └── src/
```

父 POM 统一管理版本：

```xml
<!-- 父 POM -->
<project>
    <groupId>com.example</groupId>
    <artifactId>parent-project</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>

    <modules>
        <module>common</module>
        <module>service</module>
        <module>web</module>
    </modules>

    <!-- dependencyManagement：声明版本但不引入，子模块按需引用时不用写版本号 -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.google.guava</groupId>
                <artifactId>guava</artifactId>
                <version>32.1.3-jre</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>

<!-- 子模块 POM -->
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent-project</artifactId>
        <version>1.0.0</version>
    </parent>

    <artifactId>service</artifactId>

    <dependencies>
        <!-- 不用写 version，从父 POM 的 dependencyManagement 继承 -->
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
        </dependency>
    </dependencies>
</project>
```

## 3. Gradle

### 3.1 Gradle vs Maven

| 维度 | Maven | Gradle |
|------|-------|--------|
| 配置文件 | `pom.xml`（XML） | `build.gradle`（Groovy）或 `build.gradle.kts`（Kotlin） |
| 配置风格 | 声明式、冗长 | 声明式 + 编程式、简洁 |
| 构建速度 | 较慢 | 快（增量编译 + 构建缓存 + 守护进程） |
| 灵活性 | 低（约定严格，自定义需写插件） | 高（配置文件本身就是代码，随时写逻辑） |
| 学习曲线 | 低（XML 直白） | 较高（需要了解 Groovy/Kotlin DSL） |
| 主要用户 | 传统企业项目、Spring 生态 | Android（官方）、新项目、Spring Boot |
| IDE 支持 | IntelliJ / Eclipse 都很好 | IntelliJ 很好，Eclipse 一般 |

**怎么选？** 新项目优先 Gradle（更快更灵活），维护老项目用 Maven 也完全没问题。Spring Boot 官方同时支持两者。

### 3.2 标准项目结构

和 Maven 一样（Gradle 也遵循约定优于配置）：

```
my-project/
├── build.gradle               ← 构建配置
├── settings.gradle            ← 项目设置（名称、子模块）
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── gradlew                    ← Linux/Mac 构建脚本
├── gradlew.bat                ← Windows 构建脚本
└── src/
    ├── main/java/
    ├── main/resources/
    ├── test/java/
    └── test/resources/
```

### 3.3 build.gradle 详解（Groovy DSL）

```groovy
plugins {
    id 'java'                                    // Java 插件
    id 'org.springframework.boot' version '3.2.0' // Spring Boot 插件
    id 'io.spring.dependency-management' version '1.1.4'
}

group = 'com.example'
version = '1.0.0'

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenLocal()          // 先找本地仓库
    maven { url 'https://maven.aliyun.com/repository/public' }  // 阿里云镜像
    mavenCentral()        // Maven 中央仓库
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'com.google.guava:guava:32.1.3-jre'

    compileOnly 'org.projectlombok:lombok:1.18.30'
    annotationProcessor 'org.projectlombok:lombok:1.18.30'

    runtimeOnly 'com.mysql:mysql-connector-j:8.2.0'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

tasks.named('test') {
    useJUnitPlatform()
}
```

### 3.4 Kotlin DSL（build.gradle.kts）

```kotlin
plugins {
    java
    id("org.springframework.boot") version "3.2.0"
    id("io.spring.dependency-management") version "1.1.4"
}

group = "com.example"
version = "1.0.0"

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("com.google.guava:guava:32.1.3-jre")
    runtimeOnly("com.mysql:mysql-connector-j:8.2.0")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.test {
    useJUnitPlatform()
}
```

Kotlin DSL 的好处：IDE 自动补全和类型检查更好。新项目推荐用 `.kts`。

### 3.5 依赖配置（对比 Maven Scope）

| Gradle 配置 | 对应 Maven Scope | 说明 |
|-------------|-----------------|------|
| `implementation` | `compile` | 编译 + 运行时需要，**不传递给依赖此模块的项目** |
| `api` | `compile` | 编译 + 运行时需要，**传递给依赖此模块的项目**（需要 java-library 插件） |
| `compileOnly` | `provided` | 只在编译时需要（如 Lombok、Servlet API） |
| `runtimeOnly` | `runtime` | 只在运行时需要（如 JDBC 驱动） |
| `testImplementation` | `test` | 只在测试时需要 |
| `annotationProcessor` | 无直接对应 | 注解处理器（如 Lombok、MapStruct） |

`implementation` vs `api` 是 Gradle 最容易混淆的点：

```groovy
// 模块 A 依赖 Guava
// 模块 B 依赖 模块 A

// 如果模块 A 用 implementation：
//   模块 B 看不到 Guava（编译隔离，防止泄露内部实现细节）

// 如果模块 A 用 api：
//   模块 B 也能直接用 Guava（适合库开发，对外暴露的 API 中用到的依赖）

// 原则：默认用 implementation，只有依赖出现在你的 public API 中才用 api
```

### 3.6 常用命令

```bash
# 编译
./gradlew compileJava

# 运行测试
./gradlew test

# 打包
./gradlew build                  # 编译 + 测试 + 打包
./gradlew build -x test          # 跳过测试

# 清理
./gradlew clean

# 查看依赖树
./gradlew dependencies
./gradlew dependencies --configuration runtimeClasspath  # 只看运行时依赖

# Spring Boot 直接运行
./gradlew bootRun

# 查看所有可用任务
./gradlew tasks
```

> 始终用项目自带的 `./gradlew`（Gradle Wrapper）而不是全局的 `gradle`，保证团队使用相同的 Gradle 版本。

### 3.7 Gradle Wrapper

```bash
# 项目自带的 Wrapper 脚本，保证版本一致
./gradlew build         # Linux/Mac
gradlew.bat build       # Windows

# 升级 Wrapper 版本
./gradlew wrapper --gradle-version 8.5

# gradle-wrapper.properties 中的配置
distributionUrl=https\://services.gradle.org/distributions/gradle-8.5-bin.zip
```

### 3.8 多模块项目

```
parent-project/
├── build.gradle           ← 根项目配置
├── settings.gradle        ← 声明子模块
├── common/
│   └── build.gradle
├── service/
│   └── build.gradle
└── web/
    └── build.gradle
```

```groovy
// settings.gradle
rootProject.name = 'parent-project'
include 'common', 'service', 'web'
```

```groovy
// 根 build.gradle：对所有子模块统一配置
subprojects {
    apply plugin: 'java'

    group = 'com.example'
    version = '1.0.0'

    java {
        sourceCompatibility = JavaVersion.VERSION_17
    }

    repositories {
        mavenCentral()
    }

    dependencies {
        testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
    }

    test {
        useJUnitPlatform()
    }
}
```

```groovy
// service/build.gradle：子模块依赖另一个子模块
dependencies {
    implementation project(':common')  // 依赖 common 模块
    implementation 'org.springframework.boot:spring-boot-starter-web'
}
```

## 4. 版本管理：BOM 与版本目录

### 4.1 BOM（Bill of Materials）

统一管理一组依赖的版本，避免版本冲突：

```xml
<!-- Maven：使用 Spring Boot BOM -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>3.2.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<!-- 之后声明 Spring 相关依赖不用写版本号 -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <!-- 版本由 BOM 统一控制 -->
    </dependency>
</dependencies>
```

```groovy
// Gradle：使用 Spring 的 dependency-management 插件自动导入 BOM
plugins {
    id 'io.spring.dependency-management' version '1.1.4'
}
// 之后 Spring 相关依赖自动不需要版本号
```

### 4.2 Gradle Version Catalog（Gradle 7.0+）

集中管理版本号，比 BOM 更灵活：

```toml
# gradle/libs.versions.toml
[versions]
spring-boot = "3.2.0"
guava = "32.1.3-jre"
junit = "5.10.0"

[libraries]
spring-web = { module = "org.springframework.boot:spring-boot-starter-web", version.ref = "spring-boot" }
guava = { module = "com.google.guava:guava", version.ref = "guava" }
junit = { module = "org.junit.jupiter:junit-jupiter", version.ref = "junit" }

[plugins]
spring-boot = { id = "org.springframework.boot", version.ref = "spring-boot" }
```

```kotlin
// build.gradle.kts 中引用
dependencies {
    implementation(libs.spring.web)   // IDE 有自动补全
    implementation(libs.guava)
    testImplementation(libs.junit)
}
```

## 5. 实际开发中的选择建议

| 场景 | 建议 |
|------|------|
| Spring Boot 新项目 | Gradle Kotlin DSL + Version Catalog |
| 维护已有 Maven 项目 | 继续用 Maven，没必要迁移 |
| Android 项目 | 只能用 Gradle |
| 公司统一规范 | 跟团队保持一致 |
| 个人学习/小项目 | 都行，推荐 Gradle 练手 |
| 需要高度自定义构建逻辑 | Gradle |
| 初始化项目 | 用 [Spring Initializr](https://start.spring.io/)，Maven 和 Gradle 都可以一键生成 |

## 6. 小结

| 主题 | 关键要点 |
|------|---------|
| 构建工具本质 | 自动化依赖管理 + 编译 + 测试 + 打包 + 发布 |
| Maven 核心 | pom.xml + GAV 坐标 + 生命周期（clean → compile → test → package → install） |
| Maven 依赖管理 | scope 控制范围、exclusion 排除冲突、dependencyManagement 统一版本 |
| Maven 多模块 | 父 POM（packaging: pom）+ modules + dependencyManagement |
| Gradle 核心 | build.gradle（Groovy/Kotlin DSL）+ 插件系统 + tasks |
| Gradle 依赖 | implementation（不传递）vs api（传递），默认用 implementation |
| Gradle 优势 | 增量编译 + 构建缓存 + Daemon，速度远快于 Maven |
| Wrapper | 始终用 `./gradlew` 而不是全局 gradle，保证版本一致 |
| 版本管理 | Maven 用 BOM，Gradle 用 Version Catalog（libs.versions.toml） |

---

> **下一篇预告**：Spring 核心思想——IoC 与 AOP 到底解决了什么问题

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
