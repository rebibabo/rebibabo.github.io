---
title: OpenRTB
tags:
  - wiki
  - glossary
  - programmatic-ads
  - openrtb
type: glossary
source_series: programmatic-ads
status: seed
---

# OpenRTB（Open Real-Time Bidding）

[[wiki/glossary/programmatic-ads/index|返回词汇表]]

## 定义

OpenRTB 是由 IAB Tech Lab 制定的programmatic-ads实时竞价通信协议，定义了 SSP/ADX 与 DSP 之间竞价请求和响应的标准 JSON 格式。它是programmatic-ads的"通用语言"——就像 HTTP 之于 Web。

## 上下文

OpenRTB 的版本演进：1.0（2011）→ 2.3（新增 Native）→ 2.5（2016，当前最主流版本）→ 2.6（CTV 等增量更新）。

核心传输方式：HTTP POST + JSON。关键消息类型：Bid Request（竞价请求）、Bid Response（竞价响应）、No Bid（不出价）、以及计费和丢标通知。

## 相关术语

- [[wiki/glossary/programmatic-ads/竞价请求|Bid Request]] — OpenRTB 的核心请求对象
- [[wiki/glossary/programmatic-ads/竞价响应|Bid Response]] — OpenRTB 的核心响应对象
- [[wiki/glossary/programmatic-ads/原生广告|Native Ads]] — OpenRTB 2.3+ 支持的原生广告规范

## 深入阅读

- [[wiki/concepts/programmatic-ads/OpenRTB|OpenRTB 概念页（完整版）]]
- [[_posts/programmatic-ads/09-openRTB|programmatic-ads (8)：OpenRTB 2.5 协议 & Native Ads Spec]]
