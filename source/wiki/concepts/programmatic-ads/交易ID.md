---
title: Deal ID
tags:
  - wiki
  - concept
  - programmatic-ads
  - deal-id
type: concept
source_series: programmatic-ads
status: seed
---

# Deal ID

[[wiki/concepts/programmatic-ads/交易模式|返回交易模式框架]]

## 定义

Deal ID 是私有化程序化交易里的唯一标识符。

最直观的理解是：

> 它像一把钥匙，用来告诉系统“这次请求属于哪一份私有约定”。

## 为什么需要它

在公开竞价里，大家按同样规则出价就行；但在私有交易里，不同广告主和媒体之间会有不同的价格、优先级、库存和权限约定。

没有统一标识，这些约定就无法在系统里被识别和执行。

## 它通常出现在哪些模式里

- [[PMP|PMP]]
- [[PD|PD]]
- [[PDB|PDB]]

而像 [[OA|OA]] 和很多公开型 [[wiki/concepts/programmatic-ads/头部竞价|Header Bidding]] 路径，则通常不依赖它。

## 在系列里的位置

Deal ID 是把“私有商业约定”真正落到程序化接口里的关键对象，所以它是理解交易模式从业务规则走向系统实现的重要桥梁。

## 推荐回看原文

- [[_posts/programmatic-ads/07-trading-mode-part2|programmatic-ads (6)：交易模式（下）——Header Bidding 的革命]]
- [[_posts/programmatic-ads/09-openRTB|programmatic-ads (8)：OpenRTB 2.5 协议 & Native Ads Spec 学习笔记]]

## 相关概念

- [[PMP|PMP]]
- [[PD|PD]]
- [[PDB|PDB]]
- [[OpenRTB|OpenRTB]]
