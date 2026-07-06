---
title: DSP
tags:
  - wiki
  - concept
  - programmatic-ads
  - dsp
type: concept
source_series: programmatic-ads
status: seed
---

# DSP

[[wiki/series/programmatic-ads|返回程序化广告系列]]  
[[wiki/concepts/programmatic-ads/角色总图|返回角色关系图]]

## 定义

DSP（Demand Side Platform，需求方平台）是服务广告主的一侧平台。它的核心任务是：

> 用尽量合适的价格，把广告投给更可能产生效果的人。

如果把程序化广告看成一场实时拍卖，DSP 就是广告主的自动化出价代理人。

## 它解决什么问题

- 广告主不可能自己逐个对接大量媒体
- 广告主需要在极短时间内判断“这次曝光值不值得买”
- 广告主希望预算优先花在更可能点击、转化的人群上

## 核心能力

- 接收竞价请求并在时限内出价
- 基于用户画像、上下文和历史效果做定向判断
- 通过召回、排序和出价策略优化 ROI
- 把曝光、点击、转化数据回流到投放优化中

## 它和谁配合

- 它和 [[SSP|SSP]] 在目标上天然对立：DSP 想少花钱，SSP 想多卖钱
- 它常通过 [[ADX|ADX]] 参与竞价
- 它和交易对手之间常用 [[OpenRTB|OpenRTB]] 传递 Bid Request / Bid Response

## 在系列里的位置

这是程序化广告买方视角的第一块核心拼图。理解 DSP 之后，再看 SSP / ADX，就能更容易理解为什么程序化广告本质上是一场多方博弈。

## 推荐回看原文

- [[_posts/programmatic-ads/02-DSP|程序化广告 (1)：DSP——广告主的"代理人"]]
- [[_posts/programmatic-ads/01-introduction|程序化广告 (0)：先看清楚整个江湖]]

## 相关概念

- [[SSP|SSP]]
- [[ADX|ADX]]
- [[OpenRTB|OpenRTB]]
- [[wiki/concepts/programmatic-ads/服务平台|广告服务平台]]
- [[wiki/concepts/programmatic-ads/指标与归因|指标与归因]]
