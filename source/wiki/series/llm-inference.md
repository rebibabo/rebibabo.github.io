---
title: LLM Inference 系列
tags:
  - wiki
  - series
  - llm
  - llm-inference
type: series
source_series: llm-inference
status: seed
---

# LLM Inference 系列

[[wiki/index|返回 Wiki 首页]]

## 系列定位

这组文章围绕“单卡 RTX 3090 上如何把 7B 模型推理系统调到更合理的性能区间”展开，属于非常典型的实验驱动型 AI Infra 系列。

它不是百科式介绍，而是沿着“建立基线 -> 做优化 -> 量化收益 -> 总结适用条件”的工程实验路线推进。

## 这个系列回答什么问题

- 在优化之前，怎么建立可信的精度与性能基线
- 量化、KV Cache、Prefix Caching、投机采样分别作用在哪个瓶颈上
- 单卡 7B 场景下，哪些优化真的值得做，哪些只是理论上好看
- 如何把失败实验也纳入一套可复用的方法论

## 推荐阅读顺序

1. [[_posts/llm-inference/01-baseline-deployment|BF16 基线部署：从零建立精度与性能基准]]
2. [[_posts/llm-inference/02-quantization|AWQ INT4 量化：先压权重，再看收益]]
3. [[_posts/llm-inference/03-kvcache|KV Cache 深度解析：吞吐翻倍背后的关键变量]]
4. [[_posts/llm-inference/04-prefix-caching|Prefix Caching：首 Token 延迟为什么能大幅下降]]
5. [[_posts/llm-inference/05-spectulative-decoding|投机采样：一次有价值的失败实验]]
6. [[_posts/llm-inference/06-series-summary|系列收官：RTX 3090 上的 LLM 推理优化全景]]

## 结构脉络

### 1. 建立基线

- [[_posts/llm-inference/01-baseline-deployment|01-baseline-deployment]]

先确定“当前系统已经跑到哪一步”，不然之后所有优化都没有参照系。

### 2. 压缩与显存利用

- [[_posts/llm-inference/02-quantization|02-quantization]]
- [[_posts/llm-inference/03-kvcache|03-kvcache]]

这一段围绕“权重压缩后，显存和吞吐到底怎么重新分配”展开。

### 3. Prefill 阶段优化

- [[_posts/llm-inference/04-prefix-caching|04-prefix-caching]]

这一段聚焦共享前缀命中的收益，以及 TTFT 的改善空间。

### 4. Decode 阶段与系统开销边界

- [[_posts/llm-inference/05-spectulative-decoding|05-spectulative-decoding]]

这一段回答“理论上成立的优化，为什么在特定硬件场景下反而不划算”。

### 5. 方法论收口

- [[_posts/llm-inference/06-series-summary|06-series-summary]]

这一段把所有实验结果收束成配置建议、适用条件和通用流程。

## 当前这页的作用

这页是这个实验系列的总导航，同时也把 raw 层里不太友好的 slug 标题，先在 wiki 层规范成了可读标题。

后续更适合继续拆出的概念页包括：

- AWQ
- KV Cache
- Prefix Caching
- Speculative Decoding
- TTFT / TPOT / Throughput
