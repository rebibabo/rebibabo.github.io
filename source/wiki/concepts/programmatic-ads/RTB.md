---
title: RTB
tags:
  - wiki
  - concept
  - programmatic-ads
  - rtb
type: concept
source_series: programmatic-ads
status: seed
---

# RTB

[[wiki/concepts/programmatic-ads/交易模式|返回交易模式框架]]

## 定义

RTB（Real-Time Bidding，实时竞价）是programmatic-ads最核心的交易范式之一。

一句话理解：

> 每当有一次广告曝光机会出现，系统会在极短时间内完成询价、出价、比较和成交。

## 它解决什么问题

RTB 把过去按周、按月谈判的广告采买，变成了按“每一次曝光机会”实时决策。

这带来了两层变化：

- 对广告主来说，预算可以更细粒度地花在“更值得买”的流量上
- 对媒体方来说，广告位可以更动态地找到愿意出价的买家

## 它和交易模式的关系

RTB 不是某一个具体按钮，而是很多交易模式的上层框架。

常见分支包括：

- [[OA|OA]]：最公开的实时竞价
- [[PMP|PMP]]：受邀参与的私有竞价
- [[wiki/concepts/programmatic-ads/头部竞价|Header Bidding]]：多 SSP 场景下更公平的并行竞价

## 它和系统接口的关系

RTB 要真正落到系统实现里，通常依赖 [[OpenRTB|OpenRTB]] 这类标准协议来组织请求和响应。

## 在系列里的位置

RTB 是理解programmatic-ads“为什么能自动化、高频、规模化交易”的基础概念。后面的 OA、PMP、Header Bidding 都是在这个框架里继续演化。

## 推荐回看原文

- [[_posts/programmatic-ads/06-trading-mode-part1|programmatic-ads (5)：交易模式（上）——单 SSP 内部的演化史]]
- [[_posts/programmatic-ads/07-trading-mode-part2|programmatic-ads (6)：交易模式（下）——Header Bidding 的革命]]
- [[_posts/programmatic-ads/09-openRTB|programmatic-ads (8)：OpenRTB 2.5 协议 & Native Ads Spec 学习笔记]]

## 相关概念

- [[OA|OA]]
- [[PMP|PMP]]
- [[wiki/concepts/programmatic-ads/头部竞价|Header Bidding]]
- [[OpenRTB|OpenRTB]]
- [[wiki/concepts/programmatic-ads/交易模式|交易模式框架]]
