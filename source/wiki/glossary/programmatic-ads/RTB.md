---
title: RTB
tags:
  - wiki
  - glossary
  - programmatic-ads
  - rtb
type: glossary
source_series: programmatic-ads
status: seed
---

# RTB（Real-Time Bidding，实时竞价）

[[wiki/glossary/programmatic-ads/index|返回词汇表]]

## 定义

RTB 是programmatic-ads最核心的交易范式：每当有一次广告曝光机会，系统在 100ms 内完成询价、出价、比较和成交的完整流程。

一句话：把过去按周按月谈判的广告采买，变成了按"每一次曝光"实时决策。

## 上下文

RTB 的完整链路是：用户打开页面 → SSP 检测到广告位 → 向 ADX/DSP 发送 Bid Request → DSP 在几十毫秒内出价 → ADX 比价选出胜者 → SSP 返回胜出广告 → Ad Server 渲染展示。

每次竞价只在一次曝光中有效——下次曝光重新开始新一轮竞价。

## 相关术语

- [[wiki/glossary/programmatic-ads/OA|OA]] — RTB 的公开形式
- [[wiki/glossary/programmatic-ads/PMP|PMP]] — RTB 的私有形式
- [[wiki/glossary/programmatic-ads/竞价请求|Bid Request]] — RTB 的核心消息
- [[wiki/glossary/programmatic-ads/第二价格拍卖|Second-Price Auction]] — RTB 常用的拍卖机制

## 深入阅读

- [[wiki/concepts/programmatic-ads/RTB|RTB 概念页（完整版）]]
- [[_posts/programmatic-ads/06-trading-mode-part1|programmatic-ads (5)：交易模式（上）]]
