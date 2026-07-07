---
title: Deal ID
tags:
  - wiki
  - glossary
  - programmatic-ads
  - deal-id
type: glossary
source_series: programmatic-ads
status: seed
---

# Deal ID（交易ID）

[[wiki/glossary/programmatic-ads/index|返回词汇表]]

## 定义

Deal ID 是程序化私有交易中用来唯一标识一个交易合约的字符串。在 Bid Request 中携带 Deal ID，DSP 就能识别出"这次曝光机会属于哪个私有交易"并匹配对应策略。

## 上下文

Deal ID 是 PMP、PD、PDB、First Look 等技术实现的基础设施。没有 Deal ID，私有交易中的合约条款（价格、优先级、保量要求）就无法在竞价请求中传递，买卖双方就无法识别和匹配。

Deal ID 由 SSP/ADX 或媒体方生成，在合约签订时分发给对应的 DSP。

## 相关术语

- [[wiki/glossary/programmatic-ads/PMP|PMP]] — 每个 PMP 合约有一个 Deal ID
- [[wiki/glossary/programmatic-ads/PD|PD]] — 每个 PD 合约有一个 Deal ID
- [[wiki/glossary/programmatic-ads/PDB|PDB]] — 每个 PDB 合约有一个 Deal ID

## 深入阅读

- [[wiki/concepts/programmatic-ads/交易ID|Deal ID 概念页（完整版）]]
- [[_posts/programmatic-ads/07-trading-mode-part2|programmatic-ads (6)：交易模式（下）——Header Bidding 的革命]]
