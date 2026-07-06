# AI 日志排查系统建设计划书

建设面向高并发实时链路的 AI 辅助故障诊断系统，聚合结构化日志、Prometheus 指标、Trace 和历史故障案例，通过 RAG 检索相似问题，并生成异常摘要、疑似原因排序和 Runbook 建议，降低重复问题排查成本。

## 1、项目背景

广告拍卖引擎属于高并发、低延迟、强实时的收入主链路。一次广告请求从媒体进入系统后，会经过流量接入、广告位配置读取、DSP 路由、并发询价、预算判断、拍卖排序、广告返回、曝光点击回调、日志写入和数据统计等多个环节。

这类系统的线上问题通常不是简单的接口报错，而是业务指标异常，例如：

```text
某个广告位 fill rate 下降
某个 DSP timeout 升高
某个国家 eCPM 下降
预算消耗异常
Native 素材校验失败
曝光 / 点击回传异常
Kafka / RocketMQ 堆积
Redis 缓存异常
线程池队列堆积
```

这些问题往往具有重复性，但排查过程容易依赖老员工经验、群聊沟通和人工翻日志。为了降低重复问题的排查成本，可以建设一套基于结构化日志、监控指标、Trace、历史故障案例和 AI 辅助分析的日志排查系统。

系统目标不是让 AI 自动改配置、自动修复线上问题，而是让 AI 辅助完成：

```text
异常摘要
影响范围识别
相似历史案例检索
疑似原因排序
短期止血建议
长期修复建议
Runbook 推荐
故障复盘初稿生成
```

## 2、项目目标

### 2.1 短期目标

短期先解决“看清链路”和“沉淀经验”两个问题：

```text
打通一次竞价请求的完整链路追踪
统一核心日志字段
沉淀常见故障案例
总结短期止血方案和长期修复方案
形成初版 Runbook
```

短期成果包括：

```text
拍卖链路图
核心埋点字段表
核心 Prometheus 指标表
故障案例模板
常见问题排查 checklist
单 traceId 竞价链路还原能力
```

### 2.2 中期目标

中期建设 AI 辅助诊断能力：

```text
根据 traceId 还原单次竞价链路
根据时间窗口聚合异常指标
根据 slotId / dspId / country 定位影响范围
从历史故障案例中检索相似问题
生成诊断报告和排查建议
```

### 2.3 长期目标

长期沉淀成团队可复用的稳定性工具：

```text
形成故障知识库
形成标准 Runbook
支持告警后自动生成初步诊断报告
支持新人和值班同学快速定位问题
推动监控、告警、降级和复盘体系建设
```

## 3、系统定位

本系统定位为：

> 面向广告拍卖链路的 AI 辅助排查系统。

它不是自动运维机器人，也不是自动故障修复系统。它主要服务于研发、值班同学和团队排查线上问题。

核心边界：

```text
可以做：
  聚合日志
  聚合指标
  还原链路
  检索历史案例
  生成报告
  推荐排查路径
  推荐止血方案
  生成复盘初稿

不直接做：
  自动关闭 DSP
  自动调整预算
  自动修改底价
  自动切流
  自动回滚配置
  自动修复线上代码
```

对于涉及收入、预算、DSP 流量、底价、切流等高风险操作，系统只提供建议，最终动作必须由人工确认。

## 4、核心业务链路

系统首先需要围绕一次广告竞价请求建立完整链路模型：

```text
媒体 / App 发起广告请求
↓
流量接入
↓
请求参数校验
↓
广告位配置读取
↓
DSP 列表加载
↓
频控 / 预算 / 策略过滤
↓
多 DSP 并发询价
↓
DSP 响应校验
↓
底价过滤
↓
拍卖排序
↓
返回中标广告
↓
曝光 / 点击回调
↓
日志 / MQ / 报表链路
```

每一个阶段都需要明确：

```text
输入是什么
输出是什么
可能失败在哪里
失败后表现为什么指标异常
对应哪些日志字段
对应哪些监控指标
是否有短期止血方案
是否有长期修复方案
```

## 5、核心数据来源

系统需要聚合以下数据源。

### 5.1 结构化日志

日志需要从普通文本日志升级为结构化日志，最好使用 JSON 格式，方便程序聚合和 AI 分析。

示例：

```json
{
  "timestamp": "2026-07-05T18:30:00.123Z",
  "traceId": "trace-abc123",
  "requestId": "req-001",
  "event": "DSP_CALL_RESULT",
  "slotId": "slot-test-001",
  "dspId": "dsp-002",
  "country": "ID",
  "status": "SUCCESS",
  "latencyMs": 85,
  "bidPrice": 7.30,
  "bidFloor": 3.00,
  "errorCode": null,
  "message": "dsp bid success"
}
```

建议统一事件类型：

```text
BID_REQUEST_RECEIVED
REQUEST_VALIDATE_FAILED
SLOT_CACHE_HIT
SLOT_CACHE_MISS
SLOT_CONFIG_LOAD_FAILED
DSP_LIST_LOADED
DSP_LIST_EMPTY
FREQ_CAP_FILTERED
BUDGET_FILTERED
DSP_RATE_LIMITED
DSP_CALL_START
DSP_CALL_SUCCESS
DSP_CALL_TIMEOUT
DSP_CALL_ERROR
DSP_NO_BID
BID_FILTERED_BY_FLOOR
BID_RESPONSE_INVALID
WINNER_SELECTED
NO_FILL
BID_LOG_SENT
BID_LOG_WRITE_FAILED
TRACK_IMPRESSION
TRACK_CLICK
TRACK_EVENT_DUPLICATED
```

### 5.2 监控指标

系统需要接入 Prometheus / Grafana 指标，用于描述一段时间内的整体异常。

核心指标包括：

```text
竞价请求 QPS
fill rate
no fill rate
整体竞价耗时 p50 / p95 / p99
各 DSP 调用耗时 p50 / p95 / p99
各 DSP timeout rate
各 DSP error rate
各 DSP bid rate
各 DSP win rate
底价过滤比例
频控过滤比例
预算过滤比例
Redis 延迟
Redis cache hit rate
Kafka / RocketMQ 堆积
线程池活跃线程数
线程池队列长度
DB 写入耗时
曝光 / 点击回调成功率
```

### 5.3 Trace 链路

Trace 用于还原一次请求经过了哪些服务和内部阶段。

核心要求：

```text
所有服务共享 traceId
同一次广告请求共享 requestId / auctionId
每个 DSP 调用生成子 span
每次 MQ 写入和消费可以继续传播 traceId
曝光 / 点击回调可以通过 requestId 关联竞价结果
```

### 5.4 历史故障案例

历史故障案例是 AI 辅助排查的核心知识源。每次线上问题处理后，都需要按照统一模板沉淀。

故障案例建议目录：

```text
docs/incidents/
├── 001-dsp-timeout.md
├── 002-fill-rate-drop.md
├── 003-bid-floor-too-high.md
├── 004-kafka-lag.md
├── 005-redis-cache-miss-storm.md
├── 006-budget-abnormal.md
├── 007-native-asset-invalid.md
└── 008-thread-pool-saturated.md
```

## 6、故障案例模板

每个故障案例使用统一模板，便于检索、复用和 AI 分析。

```markdown
# 故障标题

## 1. 问题现象

- 发生时间：
- 影响范围：
- 影响广告位：
- 影响国家：
- 影响 DSP：
- 业务指标变化：
- 系统指标变化：
- 告警内容：

## 2. 初步判断

- 是否影响收入：
- 是否影响 fill rate：
- 是否影响 eCPM：
- 是否影响请求成功率：
- 是否集中在某个 DSP：
- 是否集中在某个广告位：
- 是否有近期发布：
- 是否有近期配置变更：

## 3. 排查过程

### 3.1 第一阶段：确认影响范围

- 查看了哪些指标：
- 发现了什么异常：
- 排除了哪些方向：

### 3.2 第二阶段：定位异常链路

- 查看了哪些日志：
- 查看了哪些 Trace：
- 查看了哪些中间件状态：
- 异常集中在哪个环节：

### 3.3 第三阶段：确认根因

- 关键证据 1：
- 关键证据 2：
- 关键证据 3：

## 4. 根因分析

- 直接原因：
- 深层原因：
- 为什么之前没有提前发现：
- 为什么现有降级没有生效：

## 5. 短期止血方案

- 操作内容：
- 操作风险：
- 生效时间：
- 回滚方式：
- 结果验证：

## 6. 长期修复方案

- 代码修复：
- 配置修复：
- 监控补充：
- 告警补充：
- 自动化降级：
- 测试补充：
- 文档补充：

## 7. 下次如何快速判断

- 关键指标：
- 关键日志：
- 关键 Trace：
- 推荐排查顺序：
- 推荐处理动作：

## 8. 关联信息

- Grafana 看板：
- PromQL：
- 日志查询语句：
- Trace 查询条件：
- 相关代码模块：
- 相关负责人：
```

## 7、系统能力设计

### 7.1 单次请求链路还原

输入：

```text
traceId / requestId
```

输出：

```text
一次广告请求完整经过了哪些阶段
每个阶段是否成功
每个 DSP 是否被调用
每个 DSP 的耗时、状态、出价
是否发生 timeout / no bid / error
是否被底价过滤
最终是否 fill
最终 winner 是谁
曝光 / 点击是否回调
```

示例输出：

```text
请求 req-001 进入拍卖引擎
↓
广告位 slot-test-001 配置读取成功
↓
加载到 3 个 DSP
↓
dsp-a 返回出价 1.2，低于底价 3.0，被过滤
↓
dsp-b 返回 no bid
↓
dsp-c 调用 timeout
↓
无有效出价，本次 no fill
```

### 7.2 时间窗口异常聚合

输入：

```text
startTime
endTime
slotId
dspId
country
```

输出：

```text
请求量变化
fill rate 变化
no fill rate 变化
DSP timeout rate 变化
DSP bid rate 变化
DSP win rate 变化
整体 p99 变化
Redis / MQ / DB 是否异常
线程池是否异常
```

### 7.3 相似故障案例检索

系统根据当前异常特征生成检索 query：

```text
slot-test-001 fill rate 下降 dsp-c timeout rate 上升 no fill 增加 p99 升高
```

然后从历史故障案例库中检索相似问题，输出：

```text
相似案例标题
相似度
相似原因
历史根因
历史止血方案
历史长期修复方案
```

### 7.4 AI 诊断报告生成

AI 基于以下信息生成报告：

```text
当前异常指标
相关日志片段
Trace 链路摘要
相似历史案例
Runbook
当前配置变更信息
近期发布信息
```

报告内容包括：

```text
异常摘要
影响范围
疑似原因排序
关键证据
推荐排查步骤
短期止血建议
长期修复建议
关联历史案例
风险提示
```

### 7.5 Runbook 推荐

根据异常类型推荐对应 Runbook：

```text
DSP timeout 排查 Runbook
fill rate 下降排查 Runbook
eCPM 下降排查 Runbook
预算异常排查 Runbook
Kafka 堆积排查 Runbook
Redis 缓存异常排查 Runbook
线程池饱和排查 Runbook
Native 素材异常排查 Runbook
```

## 8、系统架构设计

整体架构：

```text
广告拍卖引擎
  ├─ 结构化日志
  ├─ Prometheus 指标
  ├─ OTEL Trace
  └─ 历史故障案例 / Runbook
          ↓
数据采集层
          ↓
特征提取层
          ↓
故障知识库 / 向量索引
          ↓
AI 诊断服务
          ↓
诊断报告 / Runbook 推荐 / 复盘初稿
```

更细一点：

```text
Spring Boot Auction Service
        │
        ├── JSON Structured Logs
        ├── Prometheus Metrics
        ├── OTEL Trace
        └── Incident Docs
                │
                ▼
        Context Collector
                │
                ▼
        Feature Extractor
                │
                ▼
        Retriever
        ├── Keyword Search
        └── Vector Search
                │
                ▼
        LLM Diagnosis Generator
                │
                ▼
        Diagnosis Report
```

## 9、模块拆分

### 9.1 日志采集模块

职责：

```text
读取结构化日志
按 traceId 聚合单次请求
按时间窗口聚合异常日志
过滤无关日志
脱敏敏感字段
```

输入：

```text
auction-events.jsonl
日志平台查询结果
```

输出：

```text
单次请求链路摘要
时间窗口日志摘要
```

### 9.2 指标采集模块

职责：

```text
查询 Prometheus
聚合核心业务指标
聚合 DSP 维度指标
聚合中间件指标
识别异常变化
```

核心查询：

```text
fill rate
no fill rate
DSP timeout rate
DSP error rate
DSP latency p95 / p99
auction latency p95 / p99
Redis latency
Kafka lag
thread pool queue size
```

### 9.3 特征提取模块

职责：

```text
把日志和指标转换成结构化异常特征
减少直接把大量原始日志丢给 LLM
提高诊断稳定性
```

示例特征：

```json
{
  "slotId": "slot-test-001",
  "timeWindow": "2026-07-05 18:00:00 ~ 18:10:00",
  "fillRateDrop": true,
  "fillRateBefore": 0.82,
  "fillRateAfter": 0.57,
  "mainAbnormalDsp": "dsp-c",
  "dspTimeoutRateBefore": 0.03,
  "dspTimeoutRateAfter": 0.28,
  "auctionP99BeforeMs": 180,
  "auctionP99AfterMs": 620,
  "redisAbnormal": false,
  "kafkaAbnormal": false,
  "suspectedStage": "DSP_CALL"
}
```

### 9.4 知识库检索模块

职责：

```text
读取历史故障案例
切分文档
生成 embedding
建立向量索引
支持关键词 + 向量混合检索
返回相似历史案例
```

检索对象：

```text
故障案例
Runbook
排查 checklist
配置说明
指标说明
协议说明
```

### 9.5 AI 报告生成模块

职责：

```text
根据异常特征、历史案例和 Runbook 生成报告
给出疑似原因排序
输出短期止血建议
输出长期修复建议
生成复盘初稿
```

输出格式：

```markdown
# AI 诊断报告

## 1. 异常摘要

## 2. 影响范围

## 3. 指标变化

## 4. 链路分析

## 5. 相似历史案例

## 6. 疑似原因排序

## 7. 推荐排查步骤

## 8. 短期止血建议

## 9. 长期修复建议

## 10. 风险提示
```

## 10、MVP 实现方案

第一版不追求复杂平台化，只做最小闭环。

### 10.1 MVP 范围

```text
结构化日志落盘
按 traceId 还原单次竞价链路
沉淀 5～10 个故障案例
RAG 检索相似故障
生成 Markdown 诊断报告
```

### 10.2 MVP 输入

```text
traceId
或
startTime + endTime + slotId / dspId
```

### 10.3 MVP 输出

```text
链路摘要
异常阶段
相似案例
疑似原因
推荐排查步骤
短期止血建议
长期修复建议
```

### 10.4 MVP 技术选型

```text
Java / Spring Boot：
  负责竞价服务和结构化日志输出

Python / FastAPI：
  负责 AI 诊断服务

JSONL：
  本地结构化日志文件

Markdown：
  故障案例和 Runbook

FAISS / Chroma / pgvector：
  向量检索

LLM API：
  生成诊断报告

Prometheus API：
  查询监控指标
```

## 11、项目目录设计

可以在现有 Mini-SSP 项目中增加：

```text
mini-ssp/
├── docs/
│   ├── incidents/
│   │   ├── 001-dsp-timeout.md
│   │   ├── 002-bid-floor-too-high.md
│   │   ├── 003-kafka-down.md
│   │   └── 004-thread-pool-saturated.md
│   ├── runbooks/
│   │   ├── dsp-timeout-runbook.md
│   │   ├── fill-rate-drop-runbook.md
│   │   └── kafka-lag-runbook.md
│   └── observability/
│       ├── metrics.md
│       ├── log-fields.md
│       └── trace-model.md
│
├── logs/
│   └── auction-events.jsonl
│
└── ai-diagnosis/
    ├── app.py
    ├── ingest.py
    ├── log_loader.py
    ├── metric_loader.py
    ├── feature_extractor.py
    ├── retriever.py
    ├── report_generator.py
    ├── prompts/
    │   └── diagnosis_prompt.md
    ├── vector_store/
    └── reports/
```

## 12、典型故障场景设计

### 12.1 DSP timeout

现象：

```text
某 DSP timeout rate 上升
整体 p99 上升
fill rate 下降
no fill 增加
```

短期方案：

```text
降低该 DSP 流量
缩短单 DSP timeout
临时熔断该 DSP
保留少量探测流量
```

长期方案：

```text
增加 DSP 级熔断
增加 DSP 健康评分
增加 timeout rate 告警
增加自动降权机制
```

### 12.2 底价设置过高

现象：

```text
请求量正常
DSP 响应正常
bid rate 正常
但大量 bid 被 bidfloor 过滤
fill rate 下降
```

短期方案：

```text
回滚底价配置
降低异常广告位底价
观察 fill rate 和 eCPM 是否恢复
```

长期方案：

```text
底价变更增加灰度
底价变更增加效果监控
增加 bidfloor filter rate 告警
```

### 12.3 Kafka / RocketMQ 堆积

现象：

```text
竞价主链路可能正常
bid_log / event_log 延迟入库
报表延迟
对账数据异常
```

短期方案：

```text
扩容消费者
降低非核心日志写入
临时切换直写或降级采样
```

长期方案：

```text
优化批量消费
增加堆积告警
增加死信队列
增加消费失败重试和幂等
```

### 12.4 Redis 缓存异常

现象：

```text
缓存命中率下降
DB QPS 上升
接口延迟升高
部分请求超时
```

短期方案：

```text
启用本地缓存兜底
降低回源频率
临时扩容 Redis
```

长期方案：

```text
增加本地缓存
增加缓存预热
增加防击穿机制
增加 Redis 降级策略
```

### 12.5 线程池饱和

现象：

```text
QPS 到达平台期
p99 延迟线性升高
线程池队列堆积
请求超时增加
```

短期方案：

```text
限流
扩容实例
降低单请求 fan-out 数量
关闭低优先级 DSP
```

长期方案：

```text
线程池隔离
DSP 分组调用
异步链路优化
容量评估和压测基线建设
```

## 13、AI 诊断报告示例

```markdown
# AI 诊断报告：slot-test-001 fill rate 下降

## 1. 异常摘要

在 18:00～18:10 时间窗口内，slot-test-001 的 fill rate 从 82% 下降到 57%，no fill rate 明显上升。

## 2. 影响范围

- 广告位：slot-test-001
- 主要异常 DSP：dsp-c
- 链路阶段：DSP 并发询价
- 影响类型：有效出价减少

## 3. 指标变化

- dsp-c timeout rate 从 3% 上升到 28%
- 整体竞价 p99 从 180ms 上升到 620ms
- Redis 延迟无明显异常
- Kafka 堆积无明显异常
- bidfloor filter rate 小幅上升，但不是主因

## 4. 疑似原因排序

1. dsp-c 响应超时升高，导致有效出价减少
2. 部分出价被底价过滤，进一步降低 fill rate
3. 缓存和 MQ 暂未发现明显异常

## 5. 关键证据

- timeout 日志集中在 dsp-c
- 其他 DSP success rate 基本稳定
- 异常时间窗口与 dsp-c p99 升高一致
- Redis / Kafka 指标正常

## 6. 相似历史案例

- 001-dsp-timeout.md：DSP 响应超时导致 fill rate 下降
- 004-thread-pool-saturated.md：线程池饱和导致外部调用超时

## 7. 推荐排查步骤

1. 查看 dsp-c 最近 30 分钟 timeout rate 和 p99
2. 查看是否有近期 DSP 配置变更
3. 查看 bidExecutor 队列是否堆积
4. 查看 dsp-c 是否集中影响某些广告位或国家
5. 判断是否需要临时降权或熔断

## 8. 短期止血建议

- 临时降低 dsp-c 流量权重
- 对 dsp-c 启用熔断
- 保留少量探测流量观察恢复情况

## 9. 长期修复建议

- 增加 DSP 级健康评分
- 增加 timeout rate 自动降权机制
- 增加 DSP 维度 p99 告警
- 将本次故障补充到 Runbook

## 10. 风险提示

关闭或降低 dsp-c 流量可能影响部分广告位的竞争强度，需要观察 fill rate 和 eCPM 的综合变化。
```

## 14、建设阶段规划

### 阶段一：链路和埋点梳理

时间：入职后 1～3 个月

目标：

```text
熟悉拍卖主链路
梳理核心日志字段
梳理核心指标
梳理 Trace 传播方式
整理一次请求完整链路
```

产物：

```text
链路图
字段表
指标表
Trace 示例
常见异常状态表
```

### 阶段二：故障案例和 Runbook 沉淀

时间：入职后 3～6 个月

目标：

```text
记录真实问题
沉淀短期止血方案
沉淀长期修复方案
形成高频问题 Runbook
```

产物：

```text
10+ 故障案例
5+ Runbook
问题排查 checklist
复盘模板
```

### 阶段三：AI 诊断 MVP

时间：入职后 6～9 个月

目标：

```text
完成日志聚合
完成相似案例检索
完成诊断报告生成
支持单 traceId 和时间窗口两种查询方式
```

产物：

```text
AI 诊断服务 MVP
诊断报告样例
相似案例检索能力
故障报告生成能力
```

### 阶段四：团队试用和优化

时间：入职后 9～12 个月

目标：

```text
在小范围场景内试用
收集研发和值班同学反馈
优化检索准确率
优化报告格式
补充故障案例库
```

产物：

```text
团队可用版本
实际使用反馈
效率提升数据
后续平台化规划
```

## 15、效果评估指标

系统是否有价值，需要通过结果衡量。

核心指标：

```text
重复问题平均定位时间是否下降
故障报告生成时间是否下降
新人排查问题所需时间是否下降
Runbook 覆盖的故障类型是否增加
历史相似案例命中率是否提升
AI 报告被采纳比例
故障复盘文档生成效率
```

可量化示例：

```text
沉淀 20+ 个故障案例
覆盖 8 类高频异常
某类 DSP timeout 问题定位时间从 30 分钟降低到 10 分钟
故障报告初稿生成时间从 20 分钟降低到 2 分钟
新人排查 checklist 覆盖 80% 常见问题
```

## 16、风险与边界

### 16.1 数据安全风险

广告日志可能包含用户、设备、广告主、DSP、价格、预算、国家等敏感信息。

处理原则：

```text
日志脱敏
字段最小化
禁止直接上传敏感日志到外部 AI
优先使用公司内部合规 AI 工具
控制访问权限
保留审计记录
```

### 16.2 AI 误判风险

AI 可能生成错误判断，因此系统不能直接执行高风险操作。

处理原则：

```text
AI 只给建议
所有止血动作必须人工确认
报告中必须引用证据
报告中必须标注不确定性
不能把 AI 结论当成最终根因
```

### 16.3 知识库过期风险

历史解决方案可能随着系统改造而失效。

处理原则：

```text
故障案例标注适用版本
Runbook 标注最后更新时间
过期案例需要归档
重要案例定期复查
```

## 17、项目价值

### 17.1 对个人价值

```text
帮助快速理解广告拍卖主链路
沉淀线上问题排查方法论
提升可观测性和稳定性治理能力
形成 AI 后端 / RAG / Agent 工程化项目经验
为后续转 AI 后端或 AI Infra 提供项目支撑
```

### 17.2 对团队价值

```text
减少重复问题排查成本
降低新人上手难度
沉淀老员工经验
提升故障复盘质量
推动监控和告警体系完善
提升大促和重点活动保障效率
```

### 17.3 对后续职业发展的价值

该项目可以作为从广告拍卖引擎后端转向 AI 后端的桥梁：

```text
广告高并发主链路经验
+
日志 / 指标 / Trace 可观测性
+
故障知识库
+
RAG / Agent 辅助诊断
+
团队真实落地效果
```

这类经历可以支撑后续投递：

```text
AI 应用后端
RAG 平台后端
Agent 平台开发
LLMOps
AI 工程效率平台
AI 可观测性平台
模型网关中上层后端
```

## 18、总结

AI 日志排查系统的核心不是“用 AI 替代人排查故障”，而是把广告拍卖链路中的日志、指标、Trace 和历史经验组织起来，让故障处理从“靠人肉经验”逐步变成“可观测、可检索、可复用、可沉淀”的工程体系。

短期，它帮助个人快速理解业务和链路。  
中期，它帮助团队减少重复排查成本。  
长期，它可以成为稳定性治理和 AI 工程化结合的项目样板。

最终目标是：

```text
看清链路
↓
沉淀案例
↓
复用经验
↓
辅助诊断
↓
推动治理
```

这套能力不仅适用于广告拍卖引擎，也可以迁移到 AI 后端、模型网关、Agent 平台、LLMOps 和复杂生产系统的故障排查场景中。