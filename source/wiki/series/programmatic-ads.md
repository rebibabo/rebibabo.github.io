---
title: programmatic-ads系列
tags:
  - wiki
  - series
  - programmatic-ads
type: series
source_series: programmatic-ads
status: seed
---

# programmatic-ads系列

[[wiki/index|返回 Wiki 首页]]

## 系列定位

这是一组按“先看全景，再拆角色，再讲交易规则，最后落到指标与协议”的programmatic-ads入门笔记。

它更像一条完整学习路径，而不是零散词条，所以这一版 `wiki` 先保留“系列页”作为主入口，不急着把每个概念拆成独立知识卡片。

## 这个系列回答什么问题

- programmatic-ads生态里到底有哪些核心角色
- 广告主、DSP、SSP、ADX、Ad Network、Ad Server 分别做什么
- 广告交易为什么会从人工合约演化到 RTB、PMP、PD、PDB、Header Bidding
- 怎么衡量投放效果
- DSP 和 SSP 之间到底靠什么协议通信

## 核心概念入口

- [[wiki/concepts/programmatic-ads/角色总图|角色关系图]]
- [[DSP|DSP]]
- [[SSP|SSP]]
- [[ADX|ADX]]
- [[OpenRTB|OpenRTB]]
- [[wiki/concepts/programmatic-ads/RTB|RTB]]
- [[wiki/concepts/programmatic-ads/服务平台|广告服务平台]]
- [[广告网盟|Ad Network]]
- [[广告服务器|Ad Server]]
- [[wiki/concepts/programmatic-ads/交易模式|交易模式框架]]
- [[wiki/concepts/programmatic-ads/头部竞价|Header Bidding]]
- [[wiki/concepts/programmatic-ads/指标|Metrics]]
- [[wiki/concepts/programmatic-ads/指标与归因|指标与归因]]
- [[wiki/concepts/programmatic-ads/原生广告规范|Native Ads Spec]]

## 当前 Wiki 覆盖范围

现在这个系列已经不是只有一个总入口，而是已经拆出一组可继续展开的概念页。

### 1. 角色与生态

- [[DSP|DSP]]
- [[SSP|SSP]]
- [[ADX|ADX]]
- [[广告网盟|Ad Network]]
- [[广告服务器|Ad Server]]
- [[wiki/concepts/programmatic-ads/服务平台|广告服务平台]]
- [[wiki/concepts/programmatic-ads/角色总图|角色关系图]]

### 2. 交易模式

- [[wiki/concepts/programmatic-ads/RTB|RTB]]
- [[OA|OA]]
- [[PMP|PMP]]
- [[PD|PD]]
- [[PDB|PDB]]
- [[wiki/concepts/programmatic-ads/头部竞价|Header Bidding]]
- [[wiki/concepts/programmatic-ads/瀑布流|Waterfall]]
- [[wiki/concepts/programmatic-ads/优先查看|First Look]]
- [[wiki/concepts/programmatic-ads/底价|Floor Price]]
- [[wiki/concepts/programmatic-ads/交易模式|交易模式框架]]

### 3. 协议与对接

- [[OpenRTB|OpenRTB]]
- [[wiki/concepts/programmatic-ads/原生广告规范|Native Ads Spec]]
- [[wiki/concepts/programmatic-ads/交易ID|Deal ID]]

### 4. 指标与经营

- [[wiki/concepts/programmatic-ads/指标|Metrics]]
- [[wiki/concepts/programmatic-ads/指标与归因|指标与归因]]
- [[wiki/concepts/programmatic-ads/曝光|Impression]]
- [[wiki/concepts/programmatic-ads/CPM|CPM]]
- [[wiki/concepts/programmatic-ads/eCPM|eCPM]]
- [[wiki/concepts/programmatic-ads/可见率|Viewability]]
- [[wiki/concepts/programmatic-ads/CTR|CTR]]
- [[wiki/concepts/programmatic-ads/CPC|CPC]]
- [[wiki/concepts/programmatic-ads/CVR|CVR]]
- [[wiki/concepts/programmatic-ads/CPA|CPA]]
- [[wiki/concepts/programmatic-ads/ROI|ROI]]
- [[wiki/concepts/programmatic-ads/ROAS|ROAS]]
- [[wiki/concepts/programmatic-ads/LTV|LTV]]
- [[wiki/concepts/programmatic-ads/填充率|Fill Rate]]

### 5. 广告技术工具链

- [[CMP|CMP]]
- [[DMP|DMP]]
- [[wiki/concepts/programmatic-ads/广告验证|Ad Verification]]
- [[wiki/concepts/programmatic-ads/分析平台|Analytics Platform]]

## 推荐阅读顺序

1. [[_posts/programmatic-ads/01-introduction|programmatic-ads (0)：先看清楚整个江湖]]
2. [[_posts/programmatic-ads/02-DSP|programmatic-ads (1)：DSP——广告主的"代理人"]]
3. [[_posts/programmatic-ads/03-DSP-helper|programmatic-ads (2)：DSP 身边的 4 个帮手——广告服务平台全解]]
4. [[_posts/programmatic-ads/04-SSP|programmatic-ads (3)：SSP 和 ADX——媒体方的"商业化中枢"与"交易所"]]
5. [[_posts/programmatic-ads/05-Ad network&server|programmatic-ads (4)：Ad Network 和 Ad Server——被忽略的两个重要角色]]
6. [[_posts/programmatic-ads/06-trading-mode-part1|programmatic-ads (5)：交易模式（上）——单 SSP 内部的演化史]]
7. [[_posts/programmatic-ads/07-trading-mode-part2|programmatic-ads (6)：交易模式（下）——Header Bidding 的革命]]
8. [[_posts/programmatic-ads/08-key-metrics|programmatic-ads (7)：考核指标——programmatic-ads的"成绩单"]]
9. [[_posts/programmatic-ads/09-openRTB|programmatic-ads (8)：OpenRTB 2.5 协议 & Native Ads Spec 学习笔记]]

## 结构脉络

### 1. 全景认知

- [[_posts/programmatic-ads/01-introduction|01-introduction]]

先建立“广告主、媒体方、平台、交易、效果”这整套生态的总图。

### 2. 需求方视角

- [[_posts/programmatic-ads/02-DSP|02-DSP]]
- [[_posts/programmatic-ads/03-DSP-helper|03-DSP-helper]]

这一段回答“广告主怎么把钱花出去，以及如何花得更准”。

### 3. 供给方视角

- [[_posts/programmatic-ads/04-SSP|04-SSP]]
- [[_posts/programmatic-ads/05-Ad network&server|05-Ad network&server]]

这一段回答“媒体方怎么把流量卖出去，以及旧角色和新角色怎么共存”。

### 4. 交易规则

- [[_posts/programmatic-ads/06-trading-mode-part1|06-trading-mode-part1]]
- [[_posts/programmatic-ads/07-trading-mode-part2|07-trading-mode-part2]]

这一段把 RTB、PMP、PD、PDB、Header Bidding 串成一条演化链。

### 5. 评估与协议

- [[_posts/programmatic-ads/08-key-metrics|08-key-metrics]]
- [[_posts/programmatic-ads/09-openRTB|09-openRTB]]

这一段回答“怎么判断投得好不好，以及系统之间怎么真正对接”。

## 当前这页的作用

这不是原文替代品，而是这个系列在 `wiki` 层的总导航页。

你可以把它理解成两层入口：

- 想按文章顺序学：从“推荐阅读顺序”跳回 `_posts`
- 想按概念关系学：从“当前 Wiki 覆盖范围”进入概念子图

后续继续扩展时，应该优先补这种“能接进现有图谱”的概念页，而不是把原文机械重写一遍。
