---
title: programmatic-ads生态全景图
tags:
  - wiki
  - map
  - programmatic-ads
  - ecosystem
type: map
status: seed
---

# programmatic-ads生态全景图

[[wiki/index|返回 Wiki 首页]]

一次广告曝光背后的完整链路——从用户打开页面到广告展示，涉及的角色、交易、协议和指标。

## 生态全景

```mermaid
graph TD
    AD["广告主<br/>Advertiser"] -->|"预算 · 定向"| DSP["DSP 需求方平台"]
    TD["Trading Desk"] -.->|"代操作"| DSP
    DMP["DMP 数据管理"] <-->|"用户画像"| DSP

    DSP -->|"Bid Request"| ADX["ADX 广告交易所"]
    ADX -->|"Bid Response"| DSP

    ADX -->|"竞价请求"| SSP["SSP 供给方平台"]
    SSP -->|"出价响应"| ADX

    AN["Ad Network 广告网盟"] <--> SSP
    AP["Analytics 分析平台"] <--> SSP

    SSP --> PUB["媒体方<br/>Publisher"]
    PUB --> AS["Ad Server<br/>广告服务器"]
    AS --> USER["用户"]

    CMP["CMP 同意管理"] -.->|"隐私授权"| DSP
    CMP -.->|"隐私授权"| DMP
    AV["Ad Verification<br/>广告验证"] -.->|"可见率 · 反作弊"| SSP
```

## 角色关系

| 角色 | 一句话 | 概念页 | 词汇表 |
|------|--------|--------|--------|
| DSP | 广告主的自动出价代理人 | [[wiki/concepts/programmatic-ads/DSP\|概念]] | [[wiki/glossary/programmatic-ads/DSP\|词汇]] |
| SSP | 媒体方的流量变现平台 | [[wiki/concepts/programmatic-ads/SSP\|概念]] | [[wiki/glossary/programmatic-ads/SSP\|词汇]] |
| ADX | 连接买卖双方的交易所 | [[wiki/concepts/programmatic-ads/ADX\|概念]] | [[wiki/glossary/programmatic-ads/ADX\|词汇]] |
| Ad Network | 打包流量转售的网盟 | [[wiki/concepts/programmatic-ads/广告网盟\|概念]] | [[wiki/glossary/programmatic-ads/广告网盟\|词汇]] |
| Ad Server | 素材存储与投放服务 | [[wiki/concepts/programmatic-ads/广告服务器\|概念]] | [[wiki/glossary/programmatic-ads/广告服务器\|词汇]] |
| DMP | 数据管理平台 | [[wiki/concepts/programmatic-ads/DMP\|概念]] | [[wiki/glossary/programmatic-ads/DMP\|词汇]] |
| CMP | 用户隐私授权管理 | [[wiki/concepts/programmatic-ads/CMP\|概念]] | [[wiki/glossary/programmatic-ads/CMP\|词汇]] |
| Trading Desk | DSP 的专业操作服务商 | [[wiki/concepts/programmatic-ads/服务平台\|概念]] | [[wiki/glossary/programmatic-ads/交易桌面\|词汇]] |

## 交易模式决策树

```mermaid
graph TD
    IMP["媒体方收到曝光机会"] --> FL{"有 First Look 合约？"}

    FL -->|是| FLD["优先查看<br/>（PD 类）"]
    FL -->|否| HB{"Header Bidding？"}

    HB -->|是| HBD["多 SSP 并行竞价<br/>最高价胜出"]
    HB -->|否| PUB2{"公开竞价？"}

    PUB2 -->|公开| OA["OA 公开竞价"]
    PUB2 -->|私有| VOL{"是否保量？"}

    VOL -->|是| PDB["PDB 程序化保量"]
    VOL -->|否| PD["PD 首选交易"]

    VOL -.->|"也可以是"| PMP["PMP 私有竞价<br/>（竞价 + 私有）"]
```

| 交易模式 | 竞价 | 公开 | 保量 | 词汇表 |
|----------|------|------|------|--------|
| OA (Open Auction) | 是 | 公开 | 否 | [[wiki/glossary/programmatic-ads/OA\|OA]] |
| PMP (Private Marketplace) | 是 | 私有 | 否 | [[wiki/glossary/programmatic-ads/PMP\|PMP]] |
| PD (Preferred Deal) | 否 | 私有 | 否 | [[wiki/glossary/programmatic-ads/PD\|PD]] |
| PDB (Programmatic Direct) | 否 | 私有 | 是 | [[wiki/glossary/programmatic-ads/PDB\|PDB]] |
| Header Bidding | 是 | 跨 SSP | 否 | [[wiki/glossary/programmatic-ads/头部竞价\|词汇]] |
| Waterfall | 串行 | — | — | [[wiki/glossary/programmatic-ads/瀑布流\|词汇]] |

## 指标漏斗

```mermaid
graph TD
    IMP2["曝光 Impression<br/>100 万次"] -->|"CTR 1%"| CLICK["点击 Click<br/>1 万次"]
    CLICK -->|"CVR 1%"| CONV["转化 Conversion<br/>100 次"]
    CONV -->|"客单价 × 转化数"| REV["收入 Revenue<br/>5 万元"]

    IMP2 -.->|"计费"| CPM["CPM / eCPM / vCPM / RPM"]
    IMP2 -.->|"质量"| VIEW["Viewability · Fill Rate"]
    CLICK -.->|"计费"| CPC["CPC"]
    CONV -.->|"计费"| CPA["CPA"]
    REV -.->|"效果"| ROI["ROI · ROAS · LTV"]
```

| 层级 | 核心指标 | 计费方式 |
|------|----------|----------|
| 曝光层 | Impression、Viewability、Fill Rate | CPM、eCPM、vCPM、RPM |
| 点击层 | CTR | CPC |
| 转化层 | CVR | CPA |
| 效果层 | ROI、ROAS、LTV | — |

## 协议层

```mermaid
sequenceDiagram
    participant SSP as SSP/ADX
    participant DSP as DSP

    SSP->>DSP: Bid Request (HTTP POST + JSON)<br/>设备信息 · 用户信息 · 广告位 · Deal ID
    DSP-->>SSP: Bid Response<br/>出价(CPM) · 广告素材 · 跳转地址
    DSP-->>SSP: 或 HTTP 204 No Bid (不出价)
```

## 推荐阅读路线

| 阶段 | 主题 | 原始文章 |
|------|------|----------|
| 1 全景 | 生态总览 | [[_posts/programmatic-ads/01-introduction\|post 01]] |
| 2 需求方 | DSP + 服务平台 | [[_posts/programmatic-ads/02-DSP\|post 02]] · [[_posts/programmatic-ads/03-DSP-helper\|post 03]] |
| 3 供给方 | SSP/ADX + Ad Network/Server | [[_posts/programmatic-ads/04-SSP\|post 04]] · [[_posts/programmatic-ads/05-Ad network&server\|post 05]] |
| 4 交易 | 交易模式（上+下） | [[_posts/programmatic-ads/06-trading-mode-part1\|post 06]] · [[_posts/programmatic-ads/07-trading-mode-part2\|post 07]] |
| 5 指标 | 考核指标与归因 | [[_posts/programmatic-ads/08-key-metrics\|post 08]] |
| 6 协议 | OpenRTB 协议 | [[_posts/programmatic-ads/09-openRTB\|post 09]] |

## 相关入口

- [[wiki/series/programmatic-ads\|programmatic-ads系列]]
- [[wiki/glossary/programmatic-ads/index\|programmatic-ads词汇表]]
- [[wiki/concepts/programmatic-ads/角色总图\|角色关系图]]
- [[wiki/concepts/programmatic-ads/交易模式\|交易模式框架]]
- [[wiki/concepts/programmatic-ads/指标\|Metrics]]
