---
title: 'Java进阶(6) | Grafana 搭建监控大盘：让指标"看得见"'
date: 2026-05-06
abbrlink: 06
tags:
  - Grafana
  - Prometheus
  - 监控
  - 可观测性
  - 数据可视化
categories:
  - java-advanced
---

<!-- series-intro -->
> 📚 本系列系统梳理了 Java 开发的详细知识点，从基础语法到工程实践层层递进，内容详实成体系，建议先**收藏**再慢慢阅读，方便日后随时回顾查阅。


## 前言

[上一篇](/2026/05/05/Java-advanced/05-metric/) 我们把订单服务埋好了点，指标也已经被 Prometheus 抓取、存了下来。但你有没有发现一个问题：要看"下单 QPS 现在多少"，得自己打开 Prometheus 的查询框，手敲一行 `rate(order_create_total[1m])`，回车，看一条灰扑扑的曲线；想再看成功率，又得清空、重敲另一行 PromQL。**这种方式适合临时排查，但完全没法"日常盯着看"。**

真实工作里，你需要的是一块**大盘（Dashboard）**：一屏之内，QPS、成功率、P99 耗时、各渠道分布……全都摆好，自动刷新，谁来都能一眼看懂，异常了还能自动报警。这就是 **Grafana** 干的事。这篇不堆代码，重点讲清楚 Grafana 到底是什么、它和 Prometheus 怎么分工、几个核心概念怎么理解，以及怎么一步步把大盘搭起来。

<!-- more -->

## 1. 为什么需要 Grafana：Prometheus 自带的界面不够吗

Prometheus 其实自带一个查询界面（第 5 篇用过），那为什么还要再搭一个 Grafana？因为它俩的定位完全不同：

| | Prometheus 自带界面 | Grafana |
|---|---|---|
| 定位 | 临时查一下、验证 PromQL 写得对不对 | 长期盯着看的"监控大屏" |
| 一次能看几个指标 | 基本一次一个 | 一屏几十个面板，全局一览 |
| 好不好看、好不好懂 | 朴素，给开发自己看 | 折线/仪表盘/单值/表格，给所有人看 |
| 自动刷新 / 时间范围 | 弱 | 强，可自由切"最近5分钟/1天/7天" |
| 告警 | 要另配 Alertmanager | 内置可视化告警 |
| 多数据源 | 只有它自己 | 同时接 Prometheus、MySQL、日志、链路… |

一句话：**Prometheus 负责"把数据存好、能查"，Grafana 负责"把数据画好、能看、能报警"。** 一个像数据库，一个像在数据库上面搭的 BI 报表。两者是搭档，不是二选一。

## 2. Grafana 在整条链路里的位置

把第 5 篇那张架构图补全，Grafana 在最右边：

<pre style="display:none">
graph LR
    subgraph "① 订单服务"
        direction TB
        App["埋点产生指标<br/>/actuator/prometheus"]
    end
    subgraph "② Prometheus"
        direction TB
        Prom["定时来抓 + 存储<br/>（时序数据库）"]
    end
    subgraph "③ Grafana"
        direction TB
        Graf["定时去查 + 画图<br/>（可视化大盘）"]
    end
    App -->|被抓取| Prom
    Prom -->|被查询| Graf
</pre>
![](/images/Java-advanced/IMG-20260707-000024.png)






这里有个**最关键的认知，一定要建立起来**：

> **Grafana 自己不存任何监控数据。** 它就是一个"画图的前端"——你打开一个面板，它实时去 Prometheus 跑一遍 PromQL 查询，把查回来的数字画成图；过几秒自动刷新，就再查一遍、再画一遍。

很多新手以为数据存在 Grafana 里，于是搞不清"删了 Grafana 数据会不会丢"。答案是：**不会**，数据一直在 Prometheus 里，Grafana 只是个"读数据 + 渲染"的展示层。理解这点，后面所有概念都顺了。

## 3. 五个核心概念，理解了就全通了

Grafana 的术语不多，核心就这五个，用"做一份报表"来类比最好懂：

| 概念 | 是什么 | 类比"做报表" |
|---|---|---|
| **Data Source（数据源）** | 数据从哪来，比如你的 Prometheus | 报表的数据来自哪个数据库 |
| **Dashboard（仪表盘/大盘）** | 一整个监控页面，由多个面板组成 | 一整页报表 |
| **Panel（面板）** | 大盘里的一个小图块，画一个指标 | 报表里的一张图 / 一个表格 |
| **Query（查询）** | 面板背后那行 PromQL，决定画什么数据 | 这张图背后的 SQL |
| **Variable（变量）** | 大盘顶部的下拉框，用来动态筛选 | 报表上方的"选择月份/部门"下拉 |

它们的层级关系是：

<pre style="display:none">
graph TB
    Dashboard["Dashboard（一整块大盘）"] --> P1["Panel 1：下单 QPS<br/>Query: rate(order_create_total[1m])"]
    Dashboard --> P2["Panel 2：下单成功率<br/>另一行 PromQL"]
    Dashboard --> P3["Panel 3：各渠道下单占比<br/>又一行 PromQL"]
    Dashboard --> P4["Panel 4：P99 耗时"]
    DS["Data Source: Prometheus"] -.- P1
    DS -.- P2
    DS -.- P3
    DS -.- P4
</pre>
![](/images/Java-advanced/IMG-20260707-000025.png)






**记住这条主线：一个大盘装很多面板，每个面板背后是一行查询，查询跑在某个数据源上。** 搭大盘的过程，本质就是"加面板 → 给面板写一行 PromQL → 选个合适的图表样式"，重复 N 次。

## 4. 第一步：把 Grafana 跑起来并连上 Prometheus

接着第 5 篇的 `docker-compose.yml`，再加一个 Grafana 容器即可（Prometheus 已经在里面了）：

```yaml
# docker-compose.yml 里追加
grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"     # Grafana 默认端口 3000
  depends_on:
    - prometheus
```

`docker-compose up` 起来后，浏览器打开 `http://localhost:3000`，初始账号密码都是 `admin`（第一次登录会让你改密码）。

进去之后只做一件事：**告诉 Grafana 去哪读数据**，也就是配数据源。在 `Connections → Data sources → Add data source` 里选 Prometheus，地址填：

```
http://prometheus:9090
```

> 注意这里写的是 `prometheus`（服务名），不是 `localhost`。因为 Grafana 和 Prometheus 是同一个 docker-compose 里的两个容器，容器之间用**服务名**互相访问——这点和第 5 篇/Docker 篇讲的容器网络是一回事。如果你的 Grafana 不是容器、而是装在本机，那就填 `http://localhost:9090`。

保存后点"Test"，提示连接成功，就说明 Grafana 能读到 Prometheus 的数据了。**数据源只配一次，之后所有面板共用它。**

## 5. 做第一个面板：下单 QPS

数据源通了，来做第一个图。新建一个 Dashboard，点"Add panel"，核心就填两样东西：

**① 查询（Query）**——在面板下方的查询框里写 PromQL，就是第 5 篇学的那些：

```promql
rate(order_create_total[1m])
```

这行的意思第 5 篇讲过：把只增不减的 Counter 算成"每秒增量"，也就是 QPS。写完 Grafana 立刻把结果画成一条随时间起伏的曲线。

**② 可视化类型（Visualization）**——在面板右上角选用什么图来画。QPS 是随时间变化的量，选 **Time series（时间序列折线图）** 最合适。

就这么两步，一个"实时下单 QPS"面板就成了。再点"Add panel"重复一次，换一行 PromQL，就有了第二个面板。常用的几行（都来自第 5 篇）：

```promql
# 下单成功率（用 1 减去失败率，更直观）
1 - rate(order_create_failed[5m]) / rate(order_create_total[5m])

# P99 下单耗时
histogram_quantile(0.99, rate(order_create_duration_seconds_bucket[5m]))

# 各渠道下单速率（按 channel 标签拆开，会画出多条线）
sum(rate(order_create_total[1m])) by (channel)
```

最后一行用到了第 5 篇讲的**标签**：`by (channel)` 让 Grafana 按渠道把曲线拆成支付宝、微信、银联好几条，一个面板就看清了各渠道的走势。**标签在埋点时埋下，在 Grafana 这里"开花"——这就是当初强调标签价值的地方。**

## 6. 可视化类型怎么选：什么数据配什么图

Grafana 提供十几种图表，新手容易乱选。其实记住"**指标的特性决定图表类型**"这条原则就够了，和第 5 篇"指标特性决定用 Counter 还是 Gauge"是同一种思维：

| 图表类型 | 长什么样 | 适合什么数据 | 例子 |
|---|---|---|---|
| **Time series** | 随时间起伏的折线 | 任何"随时间变化的趋势" | QPS、耗时、成功率走势 |
| **Stat** | 一个醒目的大数字 | "此刻是多少"的单值，要一眼看到 | 当前在线数、今日总下单 |
| **Gauge** | 仪表盘/油表 | 有明确上下限、想看"逼近红线没" | 内存使用率、磁盘占用 |
| **Bar gauge** | 横向条形 | 多个项目横向对比 | 各渠道下单量排名 |
| **Table** | 表格 | 要看明细、多列数据 | 各接口的 QPS+耗时+错误数一览 |
| **Heatmap** | 热力图 | 看"分布"随时间的变化 | 耗时分布、慢请求集中在哪个区间 |

选图的小窍门：

- **要看趋势** → Time series（90% 的面板都是它）
- **要看一个当前值、想突出** → Stat
- **要看"有没有超标"** → Gauge，配上阈值变色（绿/黄/红）
- **要做对比/排名** → Bar gauge
- **要看分布** → Heatmap

## 7. 让大盘"活"起来：变量（模板）

到目前为止，"各渠道下单"是把所有渠道画在一个面板里。但如果渠道有几十个，挤在一张图上就糊了。更好的做法是用**变量**做一个下拉框，让看的人自己选要看哪个渠道。

变量的原理很简单：**在大盘顶部定义一个下拉框，把它的选中值当成一个"占位符"塞进面板的 PromQL 里。** 比如定义一个变量 `channel`，面板查询写成：

```promql
rate(order_create_total{channel="$channel"}[1m])
#                                ↑ 这里的 $channel 会被下拉框选中的值替换
```

当你在顶部下拉框里选"alipay"，Grafana 就把 `$channel` 替换成 `alipay` 再去查；选"wechat"就替换成 `wechat`。**一个大盘，通过切换下拉框，就能复用着看所有渠道**，不用为每个渠道各做一份。

变量的可选项甚至能自动从 Prometheus 里拉——比如让它自动列出"当前所有出现过的 channel 取值"，这样新增了渠道，下拉框里自动就多一项，又一次体现了标签的威力。

> 这就是 Grafana 大盘"可复用、可分享"的关键：把"看哪个服务、哪个渠道、哪个时间段"做成变量，一份大盘模板，所有人按需切换着用。

## 8. 告警：让大盘主动"喊你"

光靠人盯着大盘是不现实的——总不能 24 小时有人盯着屏幕。**告警（Alerting）** 就是让 Grafana 自动帮你盯，出问题时主动通知你。

它的原理也不复杂，就是"**定时跑查询 → 和阈值比 → 超了就触发 → 走通知**"四步：

<pre style="display:none">
graph TB
    Timer["每隔 1 分钟"] --> Query["跑一遍查询<br/>下单失败率 = rate(order_create_failed[5m]) / rate(order_create_total[5m])"]
    Query --> Compare{"和阈值比：> 5% 吗？"}
    Compare -->|没超| OK["状态 OK<br/>啥也不做"]
    Compare -->|超了| Alert["状态 Alerting → 触发！"]
    Alert --> Notify["通过通知渠道发出去<br/>钉钉/企业微信/邮件/Slack…"]
</pre>
![](/images/Java-advanced/IMG-20260707-000026.png)






配一条告警，你需要定义三样东西：

1. **查询什么**：一行 PromQL，比如失败率、P99 耗时
2. **什么条件算异常**：阈值，比如"持续 5 分钟 > 5%"（加"持续一段时间"是为了避免偶尔抖一下就误报）
3. **通知谁、怎么通知**：配置通知渠道（Contact point），比如发到团队的钉钉群

这样一来，凌晨支付接口超时率飙高，你不用守着屏幕，手机自然会响。**这也是监控体系真正的闭环：从"事后查"升级到"出事前/出事时主动告诉你"。**

## 9. 别从零开始：导入现成的大盘模板

最后一个非常实用的点：**很多大盘不用自己一个个面板地搭。** Grafana 官方有一个 [Dashboard 市场](https://grafana.com/grafana/dashboards/)，里面有海量别人做好的大盘模板——JVM 监控、Spring Boot 监控、MySQL、Redis、Kubernetes…… 应有尽有。

用法极简单：找到合适的模板，记下它的 **Dashboard ID**（一串数字），在 Grafana 里 `Dashboards → Import`，填上 ID，选好数据源，一个专业的大盘瞬间就有了。

比如第 5 篇加了 actuator 后自动产生的那一堆 JVM、HTTP 指标，社区早有现成的 Spring Boot 大盘模板，导进来就能看 JVM 内存、GC、线程、HTTP 请求情况，完全不用自己写 PromQL。

> 实践建议：**通用指标（JVM、HTTP、数据库）直接导现成模板，自己只手搓"业务指标"那几个面板**（下单 QPS、各渠道成功率这种只有你的业务才有的）。省时间，效果还专业。

## 10. 小结

| 主题 | 关键要点 |
|---|---|
| 为什么要 Grafana | Prometheus 负责存和查，Grafana 负责画成"能日常盯的大盘"，两者是搭档 |
| 核心认知 | **Grafana 自己不存数据**，只是实时去数据源查询再画图的展示层 |
| 五个概念 | 数据源（数据从哪来）、大盘（一整页）、面板（一张图）、查询（背后的 PromQL）、变量（下拉筛选） |
| 搭建主线 | 配一次数据源 → 不断"加面板 + 写一行 PromQL + 选图表类型" |
| 选图原则 | 指标特性决定图表：趋势用折线、单值用 Stat、超标用 Gauge、分布用 Heatmap |
| 变量 | 把"看哪个渠道/服务"做成下拉框，一份大盘复用着看，呼应埋点时埋的标签 |
| 告警 | 定时跑查询 → 比阈值 → 超了触发 → 发通知，把监控从"事后查"变"主动喊你" |
| 现成模板 | 通用指标（JVM/HTTP）直接导社区 Dashboard，业务指标自己搓，省时又专业 |

到这里，"指标"这条线就完整了：[埋点产生指标](/2026/05/05/Java-advanced/05-metric/) → Prometheus 抓取存储 → Grafana 可视化 + 告警。你拥有了一双"能实时看见系统健康状况的眼睛"。

但大盘只能告诉你"哪个指标异常了"，没法告诉你"某一次具体的慢请求，到底卡在了哪一环"——那是可观测性第三根支柱要解决的问题。

---

> **下一篇预告**：链路追踪——给每个请求发一个"快递单号"，把它在各个服务间的流转全程跟拍下来。

<!-- follow-me -->
---

> 🎯 如果这篇文章对你有帮助，别忘了**点赞、收藏、关注**三连！关注我，让你在 Java 学习的道路上不迷路，持续为你带来成体系的 Java 干货~
