---
title: OpenRTB
tags:
  - wiki
  - concept
  - programmatic-ads
  - openrtb
type: concept
source_series: programmatic-ads
status: seed
---

# OpenRTB

[[wiki/series/programmatic-ads|返回programmatic-ads系列]]  
[[wiki/concepts/programmatic-ads/角色总图|返回角色关系图]]

## 定义

OpenRTB 是programmatic-ads里最常见的实时竞价通信协议之一。

它定义了 DSP、SSP、ADX 之间如何用统一格式传递：

- Bid Request
- Bid Response
- No Bid
- 以及中标、计费、丢标相关通知

可以把它理解成programmatic-ads交易里的“通用语言”。

## 它解决什么问题

- 不同公司的平台不需要各自发明一套私有竞价格式
- 竞价请求与响应可以在统一对象结构下流转
- 拍卖链路更容易标准化、规模化和系统化集成

## 核心对象

- BidRequest：一次竞价请求
- Imp：一次展示机会
- Device / User / Site / App：定向相关上下文
- BidResponse：DSP 的响应
- Bid：对某个展示机会的具体出价

## 它和谁配合

- [[DSP|DSP]] 用它理解“这次曝光是什么”
- [[SSP|SSP]] / [[ADX|ADX]] 用它把展示机会标准化发出去

## 在系列里的位置

前面的文章主要解释角色和交易逻辑，而 OpenRTB 解释的是这些角色在系统层面怎么真正对接起来。

所以它更偏“接口协议层”，是把业务结构落到工程实现的一步。

## 推荐回看原文

- [[_posts/programmatic-ads/09-openRTB|programmatic-ads (8)：OpenRTB 2.5 协议 & Native Ads Spec 学习笔记]]
- [[_posts/programmatic-ads/04-SSP|programmatic-ads (3)：SSP 和 ADX——媒体方的"商业化中枢"与"交易所"]]

## 相关概念

- [[DSP|DSP]]
- [[SSP|SSP]]
- [[ADX|ADX]]
- [[wiki/concepts/programmatic-ads/原生广告规范|Native Ads Spec]]
- [[wiki/concepts/programmatic-ads/交易模式|交易模式框架]]
- [[wiki/concepts/programmatic-ads/头部竞价|Header Bidding]]
