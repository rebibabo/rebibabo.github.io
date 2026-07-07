---
title: 'Java进阶(2) | Docker 容器入门：从原理到打包部署'
date: 2026-05-02
abbrlink: 02
tags:
  - Docker
  - 容器
  - 部署
categories:
  - java-advanced
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

写完 Mini-SSP 后会遇到一个现实问题：项目依赖 MySQL、Redis、还有好几个服务，在自己电脑上配好了，换台机器又要重新装一遍环境。Docker 就是为了解决"在我电脑上能跑，在你电脑上跑不起来"这个经典问题。这篇文章用最直白的方式讲清楚容器是什么、常用命令、怎么打包自己的应用。

<!-- more -->

## 1. 什么是容器？

### 1.1 一个比喻

把你的应用想象成一件货物。

**没有容器的年代**：你要把货物从 A 地运到 B 地，但 A 地用卡车、B 地用轮船、中转站用火车，每换一种交通工具都要重新打包、重新适配，非常麻烦。

**集装箱（Container）出现后**：货物先装进标准尺寸的集装箱，不管是卡车、轮船还是火车，都按统一规格搬运集装箱，里面装什么、怎么摆放完全不用关心。

Docker 的 Container（容器）就是软件世界的集装箱——把应用和它需要的一切（代码、运行时、依赖库、配置）打包进一个标准化的"箱子"，这个箱子在任何装了 Docker 的机器上都能原样运行。

### 1.2 解决的核心问题

```
传统部署：
  开发机：装 JDK 17、MySQL 8.0、Redis 7、配一堆环境变量 → 能跑
  测试机：重新装一遍，版本差一点 → 可能跑不起来
  生产机：再装一遍，漏了个配置 → "在我电脑上明明好好的啊"

Docker 部署：
  把 JDK、应用、依赖全打包成一个镜像
  开发机、测试机、生产机：docker run 同一个镜像 → 处处一致
```

### 1.3 容器 vs 虚拟机

很多人会把容器和虚拟机搞混，它们都能"隔离环境"，但原理完全不同：

<pre style="display:none">
graph TB
    subgraph "虚拟机 (VM)"
        direction TB
        VM_Apps["应用 A (完整OS) | 应用 B (完整OS) | 应用 C (完整OS)<br/>← 每个 VM 装一套完整操作系统，很重"]
        VM_Hyper["Hypervisor<br/>← 虚拟化层"]
        VM_Host["宿主机操作系统"]
        VM_Apps --- VM_Hyper --- VM_Host
    end
</pre>
![](/images/Java-advanced/IMG-20260707-000006.png)












<pre style="display:none">
graph TB
    subgraph "容器 (Container)"
        direction TB
        C_Apps["应用 A (依赖) | 应用 B (依赖) | 应用 C (依赖)<br/>← 只打包应用和依赖，共享宿主机内核"]
        C_Engine["Docker Engine"]
        C_Host["宿主机操作系统<br/>← 所有容器共享这一个内核"]
        C_Apps --- C_Engine --- C_Host
    end
</pre>
![](/images/Java-advanced/IMG-20260707-000007.png)












| 维度 | 虚拟机 | 容器 |
|------|--------|------|
| 隔离级别 | 完整操作系统 | 进程级隔离 |
| 体积 | 几个 GB | 几十到几百 MB |
| 启动速度 | 分钟级 | 秒级 |
| 资源占用 | 高（每个都跑一套 OS） | 低（共享内核） |
| 隔离强度 | 强 | 相对弱（共享内核） |

简单说：**虚拟机是"模拟一台完整的电脑"，容器是"在同一台电脑上隔离出独立的运行空间"**。容器更轻、更快，所以现代后端部署几乎都用容器。

---

## 2. 三个核心概念

理解 Docker 只需要先搞懂三个词的关系：

<pre style="display:none">
graph LR
    DF["Dockerfile<br/>（打包脚本）"] -->|build| Image["镜像（Image）<br/>（打包好的模板）"]
    Image -->|run| Container["容器（Container）<br/>（运行中的实例）"]
</pre>
![](/images/Java-advanced/IMG-20260707-000008.png)












| 概念 | 是什么 | 类比 |
|------|--------|------|
| Dockerfile | 一个文本文件，写明"怎么打包" | 菜谱 |
| 镜像（Image） | 按 Dockerfile 打包出来的只读模板 | 按菜谱做好的半成品（冷冻装） |
| 容器（Container） | 镜像运行起来的实例 | 把半成品加热后端上桌的那盘菜 |

关键关系：

- **一个镜像可以运行出多个容器**（同一份冷冻半成品，可以加热成多盘菜）
- **镜像是只读的，容器是可读写的**（菜谱和半成品不变，但每盘菜可以单独加调料）
- **镜像可以分享**（推到 Docker Hub，别人 `docker pull` 就能用，就像把菜谱和半成品寄给别人）

---

## 3. 常用命令

### 3.1 镜像相关

```bash
# 从 Docker Hub 拉取镜像
docker pull mysql:8.0           # 拉取 MySQL 8.0 镜像
docker pull redis:7-alpine      # alpine 是精简版 Linux，镜像更小

# 查看本地有哪些镜像
docker images

# 删除镜像
docker rmi mysql:8.0

# 根据 Dockerfile 构建镜像（. 表示当前目录）
docker build -t my-app:1.0 .    # -t 给镜像起名:标签
```

### 3.2 容器相关

```bash
# 运行容器（最常用）
docker run -d -p 8080:8080 --name my-ssp my-app:1.0
# -d        后台运行（detached）
# -p 8080:8080  端口映射，宿主机8080 → 容器8080
# --name    给容器起个名字，方便后续操作

# 查看正在运行的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a

# 停止 / 启动 / 重启容器
docker stop my-ssp
docker start my-ssp
docker restart my-ssp

# 删除容器（要先停止）
docker rm my-ssp

# 查看容器日志
docker logs my-ssp
docker logs -f my-ssp           # -f 持续跟踪输出（类似 tail -f）

# 进入正在运行的容器内部（排查问题用）
docker exec -it my-ssp bash
# -it 表示交互式终端，进去后就像在容器内的 Linux 里操作
```

### 3.3 端口映射详解

`-p 8080:8080` 这个参数最容易迷糊，记住格式是 **宿主机端口:容器端口**：

<pre style="display:none">
graph LR
    Browser["浏览器 localhost:9090"] -->|外部访问| Host["宿主机 9090 端口"]
    Host -->|Docker 转发| Container["容器内部 8080 端口<br/>Spring Boot 应用监听 8080"]
</pre>
![](/images/Java-advanced/IMG-20260707-000009.png)












容器之间是隔离的，不做端口映射，外部就访问不到容器里的服务。

---

## 4. 把 Spring Boot 应用打包成镜像

### 4.1 编写 Dockerfile

在项目根目录创建一个名为 `Dockerfile` 的文件（没有后缀）：

```dockerfile
# 第一阶段：用 Maven 镜像编译打包
FROM eclipse-temurin:17-jdk-alpine AS build
WORKDIR /app
COPY . .
RUN ./mvnw package -DskipTests

# 第二阶段：用更小的 JRE 镜像运行
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/target/mini-ssp-*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

逐行解释：

| 指令 | 作用 |
|------|------|
| `FROM` | 基于哪个基础镜像（站在巨人肩膀上，不用从零搭 Linux） |
| `WORKDIR` | 设置容器内的工作目录（后续命令都在这个目录执行） |
| `COPY` | 把宿主机的文件复制进镜像 |
| `RUN` | 构建镜像时执行的命令（这里是编译打包） |
| `EXPOSE` | 声明容器监听的端口（仅作说明，实际映射靠 `-p`） |
| `ENTRYPOINT` | 容器启动时执行的命令（这里是启动 jar） |

### 4.2 为什么要分两个阶段？

上面的 Dockerfile 用了"多阶段构建"，目的是**减小最终镜像体积**：

```
第一阶段（build）：需要完整 JDK + Maven 来编译，镜像很大（几百 MB）
                   产物只有一个 jar 包

第二阶段（运行）：只需要 JRE 来跑 jar，不需要 JDK 和 Maven
                 从第一阶段只复制 jar 包过来（COPY --from=build）

最终镜像 = 第二阶段的内容（只有 JRE + jar），编译工具全部丢弃
```

这样最终镜像可能从 600MB 降到 200MB，部署更快、占用更少。

### 4.3 构建和运行

```bash
# 构建镜像
docker build -t mini-ssp:1.0 .

# 运行
docker run -d -p 8080:8080 --name ssp mini-ssp:1.0

# 查看日志确认启动成功
docker logs -f ssp
```

---

## 5. Docker Compose：一键启动多个服务

### 5.1 解决的问题

Mini-SSP 需要 MySQL、Redis、还有 SSP 应用本身，如果用 `docker run` 一个个启动，要敲好几条命令，还要处理它们之间的网络连接和启动顺序。Docker Compose 用一个 YAML 文件描述所有服务，一条命令全部启动。

### 5.2 docker-compose.yml

```yaml
version: '3.8'
services:

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: mini_ssp
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  ssp:
    build: .                    # 用当前目录的 Dockerfile 构建
    ports:
      - "8080:8080"
    depends_on:                 # 等 mysql 和 redis 启动后再启动
      - mysql
      - redis
    environment:
      # 注意：容器之间用服务名互相访问，不是 localhost
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/mini_ssp
      SPRING_DATA_REDIS_HOST: redis
```

### 5.3 关键点：容器间用服务名通信

这是新手最容易踩的坑：

```
在宿主机上：MySQL 是 localhost:3306
在 ssp 容器里：MySQL 不是 localhost，而是服务名 mysql:3306

原因：每个容器有自己独立的网络空间，容器里的 localhost 指的是
容器自己，不是宿主机。Docker Compose 会自动让同一个 compose
文件里的服务可以用"服务名"互相访问。
```

所以 SSP 连接 MySQL 的地址要写 `jdbc:mysql://mysql:3306/...`，这里的 `mysql` 就是上面定义的服务名。

### 5.4 常用命令

```bash
# 启动所有服务（-d 后台运行）
docker-compose up -d

# 构建并启动（代码改了需要重新构建时）
docker-compose up -d --build

# 查看所有服务状态
docker-compose ps

# 查看日志
docker-compose logs -f ssp

# 停止并删除所有容器
docker-compose down

# 停止但不删除
docker-compose stop
```

---

## 6. 容器的原理（简单理解）

容器能做到"隔离"和"轻量"，靠的是 Linux 内核的三个机制：

### 6.1 Namespace（命名空间）—— 负责隔离

让每个容器以为自己独占整个系统：

```
进程隔离：容器里 ps 只能看到自己的进程，看不到宿主机和其他容器的进程
网络隔离：每个容器有自己的 IP、端口、网卡
文件隔离：容器里看到的文件系统是独立的
```

就像每个容器都戴着"眼罩"，只能看到属于自己的那部分。

### 6.2 Cgroups（控制组）—— 负责限制资源

控制每个容器能用多少 CPU、内存：

```bash
# 限制容器最多用 512MB 内存、1 个 CPU
docker run -m 512m --cpus 1 my-app
```

防止某个容器吃光宿主机所有资源，影响其他容器。

### 6.3 联合文件系统（UnionFS）—— 负责分层

镜像是**一层一层叠起来**的，每层只记录和上一层的差异：

<pre style="display:none">
graph TB
    L1["Layer 1: 基础 Linux 系统"] --> L2["Layer 2: 装上 JRE"]
    L2 --> L3["Layer 3: 复制进 jar 包"]
    L3 --> View["合并视图：完整的运行环境"]
</pre>
![](/images/Java-advanced/IMG-20260707-000010.png)












分层的好处：

- **复用**：多个镜像都基于同一个 JRE 层，这一层只存一份
- **缓存**：构建镜像时，没改动的层直接复用缓存，只重新构建变化的层，速度快

这也解释了为什么 Dockerfile 里"把不常变的放前面、常变的放后面"——前面的层能命中缓存，加快构建。

---

## 7. 小结

| 主题 | 关键要点 |
|------|---------|
| 容器是什么 | 把应用和依赖打包成标准"集装箱"，到处一致运行 |
| 容器 vs 虚拟机 | 容器共享宿主机内核，更轻更快；虚拟机模拟完整 OS |
| 三个概念 | Dockerfile（菜谱）→ 镜像（半成品）→ 容器（端上桌的菜） |
| 常用命令 | `build` 构建、`run` 运行、`ps` 查看、`logs` 看日志、`exec` 进入 |
| 端口映射 | `-p 宿主机端口:容器端口` |
| Dockerfile | 多阶段构建减小镜像体积（编译用 JDK，运行用 JRE） |
| Docker Compose | 一个 YAML 启动多服务，容器间用服务名通信 |
| 底层原理 | Namespace 隔离、Cgroups 限资源、UnionFS 分层 |

对 Mini-SSP 来说，Docker 化之后只需要 `docker-compose up` 一条命令，就能在任何装了 Docker 的机器上拉起整套环境（MySQL + Redis + SSP + Mock DSP），不用再手动装一堆东西。

---

> **下一篇预告**：Docker 进阶——数据卷、网络配置与镜像优化

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
