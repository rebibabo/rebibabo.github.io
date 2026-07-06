---
title: ADX
tags:
  - wiki
  - concept
  - programmatic-ads
  - adx
type: concept
source_series: programmatic-ads
status: seed
---

# ADX

[[wiki/series/programmatic-ads|返回程序化广告系列]]  
[[wiki/concepts/programmatic-ads/角色总图|返回角色关系图]]

## 定义

ADX（Ad Exchange，广告交易平台）是连接需求方与供给方的交易撮合层。

最直观的理解是：

> DSP 像买方，SSP 像卖方，ADX 像交易所。

它不直接代表广告主，也不直接代表媒体，而是负责在统一规则下组织实时竞价。

## 它解决什么问题

- 让多个 DSP 和多个 SSP 不必一一私下对接
- 为广告交易提供统一的竞价机制与接口规范
- 让实时拍卖可以在极短时间内大规模发生

## 核心能力

- 接收和分发竞价请求
- 组织拍卖并执行竞价规则
- 做标准化交易与规模化撮合
- 把请求、出价、中标、结算这些链路串起来

## 它和谁配合

- 上游通常连接 [[SSP|SSP]]
- 下游通常连接 [[DSP|DSP]]
- 标准化接口常借助 [[OpenRTB|OpenRTB]]

## 在系列里的位置

ADX 让程序化广告从“平台能力”真正演化成“市场结构”。如果没有 ADX 或类似交换层，大规模的实时竞价很难成立。

## 推荐回看原文

- [[_posts/programmatic-ads/04-SSP|程序化广告 (3)：SSP 和 ADX——媒体方的"商业化中枢"与"交易所"]]
- [[_posts/programmatic-ads/09-openRTB|程序化广告 (8)：OpenRTB 2.5 协议 & Native Ads Spec 学习笔记]]

## 相关概念

- [[DSP|DSP]]
- [[SSP|SSP]]
- [[OpenRTB|OpenRTB]]
- [[wiki/concepts/programmatic-ads/交易模式|交易模式框架]]
- [[wiki/concepts/programmatic-ads/头部竞价|Header Bidding]]
