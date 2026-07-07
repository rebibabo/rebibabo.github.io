---
title: ADX
tags:
  - wiki
  - glossary
  - programmatic-ads
  - adx
type: glossary
source_series: programmatic-ads
status: seed
---

# ADX（Ad Exchange，广告交易所）

[[wiki/glossary/programmatic-ads/index|返回词汇表]]

## 定义

ADX 是连接 DSP（需求方）和 SSP（供给方）的广告交易平台。它像一个股票交易所：卖方挂出广告位，买方出价竞买，ADX 撮合成交。

## 上下文

在实际链路中，SSP 将广告曝光机会送入 ADX，ADX 向接入的 DSP 群发竞价请求，DSP 在极短时间内返回出价，ADX 选出最高出价者并通知 SSP 返回广告。

ADX 和 SSP 的边界在实践中常常交叉——大平台（如 Google AdX）往往同时具备 SSP 和 ADX 的能力。

## 相关术语

- [[wiki/glossary/programmatic-ads/DSP|DSP]] — ADX 对接的需求方
- [[wiki/glossary/programmatic-ads/SSP|SSP]] — ADX 对接的供给方
- [[wiki/glossary/programmatic-ads/RTB|RTB]] — ADX 的核心交易机制
- [[wiki/glossary/programmatic-ads/竞价请求|Bid Request]] — ADX 发出的竞价请求

## 深入阅读

- [[wiki/concepts/programmatic-ads/ADX|ADX 概念页（完整版）]]
- [[_posts/programmatic-ads/04-SSP|programmatic-ads (3)：SSP 和 ADX——媒体方的"商业化中枢"与"交易所"]]
