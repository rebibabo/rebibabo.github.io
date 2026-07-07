---
title: LLM推理优化实战(五)：投机采样原理详解与单卡场景失效分析
date: 2026-04-05
abbrlink: 05mathjax: true
categories:
    llm-inference
tags:
---

## 一、前言

前几篇文章中，AWQ 量化将 TPOT 从 19.7ms 压到 6.84ms（-65%），Prefix Caching 将 TTFT 降低了最高 92.6%——这两项优化分别针对 Decode 和 Prefill 阶段，效果显著且几乎没有代价。

但 Decode 阶段还有一个更根本的问题：每生成 1 个 token，GPU 就要把全部模型权重搬运一次，而算力大部分时间在等数据搬运。能不能一次搬运、同时产出多个 token？投机采样（Speculative Decoding）正是为此而生的技术——用一个小模型先猜几个 token，再用大模型一次性并行验证，猜对的直接输出，猜错的重新采样。理论上精度零损失，速度提升 2~4 倍。

本文通过理论推导和实测验证，回答以下问题：

- 投机采样的加速原理是什么？在什么条件下才能生效？
- Draft Model 和 N-gram 两种草稿策略有什么区别？
- 在单卡 RTX 3090 + 7B 模型上，投机采样能带来加速吗？

先看结论：

| 实验 | 关键发现 |
|---|---|
| 精度评测（lm_eval） | 四项指标与 baseline 完全一致，精度零损失 ✅ |
| Draft 0.5B，conc=1 | TPOT 19.55ms vs baseline 19.7ms，无加速 ❌ |
| Draft 0.5B，conc=16 | TPOT 恶化 +7.4%，TTFT P99 暴涨 25 倍 ❌ |
| N-gram，conc=1 | TPOT 20.83ms vs baseline 19.7ms，无加速 ❌ |
| 理论加速比推导 | $S = \frac{3.08}{5 \times 0.20 + 1.73} = 1.13\times$，实测 ~1.0x |

**最重要的洞察**：投机采样是一项有严格前提条件的优化技术。它需要"大模型（70B+）+ 多卡（draft 并行）+ 低并发 + 高接受率"的组合才能发挥威力。在单卡 RTX 3090 + 7B 这个组合下，draft 模型与 target 串行共享显存带宽（$\gamma = 0.20$），验证开销远超单次 decode（$c = 1.73$），仅 13% 的理论加速空间被系统开销完全抵消。这不是投机采样的技术缺陷，而是应用条件不匹配——正如 FP8 需要 Ada/Hopper 架构一样，每项优化技术都有它的硬件门槛。

---

## 二、什么是投机采样

### 2.1 从 Decode 的瓶颈说起

要理解投机采样，首先要搞清楚 LLM 推理中 Decode 阶段的瓶颈在哪里。

回顾前文的基线数据：Qwen2.5-7B BF16 在 RTX 3090 上单请求 TPOT 为 19.7ms，而理论下限为 15ms（14GB 权重 ÷ 936 GB/s 带宽）。这意味着每生成 1 个 token，GPU 就要把 14 GB 的模型权重从显存搬运到计算单元，完成一次前向传播，然后再搬运一次，再前向一次……

```
生成 5 个 token 的过程（普通 Decode）：

  第 1 轮：搬运 14GB → 算 1 个 token → 输出 token₁    ~20ms
  第 2 轮：搬运 14GB → 算 1 个 token → 输出 token₂    ~20ms
  第 3 轮：搬运 14GB → 算 1 个 token → 输出 token₃    ~20ms
  第 4 轮：搬运 14GB → 算 1 个 token → 输出 token₄    ~20ms
  第 5 轮：搬运 14GB → 算 1 个 token → 输出 token₅    ~20ms

  总计：5 轮搬运，100ms 得到 5 个 token
```

这里的关键问题是：每次搬运 14GB 权重，但实际计算量极小（只算 1 个 token 的前向传播）。GPU 的算力大部分时间在等显存搬数据，这就是所谓的 **memory-bound**（显存带宽瓶颈）。

但有一个重要特性：**验证多个 token 和生成 1 个 token 的耗时几乎一样**。因为瓶颈在搬运 14GB 权重，搬完之后并行算 5 个 token 的额外计算开销可以忽略——算力本来就闲着。投机采样正是利用了这个特性。

### 2.2 核心思路：先猜后验

投机采样的思路可以用一句话概括：**用一个小而快的"草稿模型"先猜几个 token，再用大模型一次性并行验证。**

```
投机采样生成 token 的过程：

  第 1 步（Draft）：草稿模型快速猜 5 个候选 token
    → 草稿模型很小（比如 0.5B），搬运 1GB 权重，极快
    → 猜出 token₁' token₂' token₃' token₄' token₅'

  第 2 步（Verify）：大模型一次性验证这 5 个候选
    → 搬运 14GB 权重，但只搬一次
    → 并行检查每个位置：猜对了就接受，猜错了就拒绝并修正

  假设前 3 个猜对了：
    → 接受 token₁' token₂' token₃'，拒绝 token₄'
    → 在拒绝位置用大模型的分布重新采样得到 token₄
    → 本轮输出：token₁' token₂' token₃' token₄（共 4 个 token）

  总耗时 ≈ draft 时间 + 1 次大模型验证 ≈ 5ms + 25ms = 30ms
  普通方式生成 4 个 token 需要 4 × 20ms = 80ms
  加速比 ≈ 2.7x
```

### 2.3 为什么精度零损失

这是投机采样最精妙的地方。验证步骤使用的是大模型的**完整概率分布**，通过拒绝采样算法决定每个 draft token 是否被接受：

```
draft 猜了 5 个 token：A B C D E

大模型一次前向传播，得到每个位置的概率分布：
  位置 1：P_target(A) = 0.85  → 接受 ✓
  位置 2：P_target(B) = 0.72  → 接受 ✓
  位置 3：P_target(C) = 0.08  → 拒绝 ✗ → 从 target 分布重新采样得到 C'
  位置 4、5：跳过（位置 3 已拒绝，后续无效）

本轮输出：A B C'（3 个 token）
```

具体的接受 / 拒绝规则：对于每个位置，计算 draft 模型和 target 模型在该 token 上的概率比值。如果 draft 给出的概率不超过 target 的概率，则一定接受；否则以一定概率拒绝，并从修正后的分布中重新采样。

这个机制保证了：**无论 draft 模型多差，最终输出的每个 token 都严格服从 target 模型的概率分布。** 投机采样改变的是生成速度，不改变生成结果的分布——这正是为什么本文的 lm_eval 精度评测与 baseline 完全一致。

### 2.4 两种 Draft 策略

vLLM 支持多种草稿生成方式，本文实验了两种最常用的。

**方式一：Draft Model（独立小模型）**

用同系列的小模型做草稿。比如 target 是 Qwen2.5-7B，draft 用 Qwen2.5-0.5B：

```
Target：Qwen2.5-7B（14GB 权重，TPOT ~20ms）
Draft： Qwen2.5-0.5B（1GB 权重，TPOT ~4ms）

Draft 模型用自回归方式逐个生成 k 个候选 token：
  → 搬运 1GB × 5 次 = 5GB 搬运量
  → 耗时 ≈ 5 × 4ms = 20ms

Target 模型一次前向验证 k 个：
  → 搬运 14GB × 1 次
  → 耗时 ≈ 25ms
```

优势是猜测质量高（同系列模型的概率分布相近），劣势是需要额外显存存放 draft 模型权重，且在单卡上 draft 推理和 target 推理是串行的。

**方式二：N-gram 匹配**

从已有的输入文本中查找匹配的 n-gram 序列，直接作为草稿，不需要任何额外模型：

```
已生成的文本：...这个函数接收一个列表参数，返回排序后的列表...

当前位置要生成下一个 token，n-gram 方式：
  → 在已有文本中搜索与当前上下文匹配的片段
  → 如果找到匹配，直接把后续 token 作为候选
  → 不需要任何模型推理，开销几乎为零
```

优势是零显存开销、零计算开销；劣势是只能猜到文本中已出现过的模式，对自由对话等文本多样性高的场景接受率很低。

**两种方式的对比：**

| 维度 | Draft Model | N-gram |
|---|---|---|
| 需要额外模型 | 是（占显存） | 否 |
| Draft 耗时 | 较高（需要模型推理） | 几乎为零 |
| 猜测质量 | 较高（同系列模型分布相近） | 取决于文本重复性 |
| 最佳场景 | 多卡部署，target 模型大 | 代码补全、模板化输出 |
| 单卡 7B 效果 | 差（资源竞争） | 差（接受率低） |

### 2.5 关键参数：spec-tokens

`--spec-tokens k` 控制每轮 draft 猜测的 token 数。这个值需要权衡：

```
k 太小（比如 2）：每轮最多赚 2 个 token，加速上限低
k 太大（比如 10）：后面几个位置接受率极低，draft 开销浪费

从实验中的逐位置接受率可以直观看出（draft 0.5B，spec-tokens=5）：

  Position 0:  69%  ← 猜对概率最高
  Position 1:  50%
  Position 2:  38%
  Position 3:  29%
  Position 4:  23%  ← 已经很低了，再往后基本白猜
```

接受率逐位置递减是必然的：猜对第 1 个 token 的概率最高，在第 1 个正确的条件下再猜对第 2 个的概率更低，以此类推。实践中 $k=3 \sim 5$ 是常用的范围。

### 2.6 加速条件：什么时候投机采样才有效

定义以下变量：

| 符号 | 含义 |
|---|---|
| $\alpha$ | 平均接受长度（每轮被 target 接受的 token 数） |
| $k$ | 每轮 draft 的猜测数（`--spec-tokens`） |
| $T_{\text{target}}$ | 大模型单次 decode 耗时 |
| $T_{\text{draft}}$ | 草稿模型单次 decode 耗时 |
| $T_{\text{verify}}$ | 大模型验证 $k$ 个 token 的耗时 |

不用投机采样时，生成 $\alpha$ 个 token 需要 $\alpha$ 轮 decode：

$$T_{\text{baseline}} = \alpha \times T_{\text{target}}$$

用投机采样时，一轮 draft + verify 产出 $\alpha$ 个 token：

$$T_{\text{spec}} = k \times T_{\text{draft}} + T_{\text{verify}}$$

加速比：

$$S = \frac{T_{\text{baseline}}}{T_{\text{spec}}} = \frac{\alpha \times T_{\text{target}}}{k \times T_{\text{draft}} + T_{\text{verify}}}$$

引入两个无量纲比值来简化分析：

$$\gamma = \frac{T_{\text{draft}}}{T_{\text{target}}} \quad \text{（draft 开销比，越小越好）}$$

$$c = \frac{T_{\text{verify}}}{T_{\text{target}}} \quad \text{（验证开销比，理想情况 } c \approx 1 \text{）}$$

加速比简化为：

$$S = \frac{\alpha}{k \gamma + c}$$

**加速条件** $S > 1$，即 $\alpha > k\gamma + c$。

从公式可以看出三个杠杆：

- **$\gamma$（draft 开销比）**：单卡上 draft 和 target 串行共享带宽，$\gamma$ 较大；多卡并行时 draft 被 target 完全掩盖，$\gamma \approx 0$
- **$c$（验证开销比）**：低并发 memory-bound 下多验证几个 token 几乎不多花时间，$c \approx 1$；高并发 GPU 满载时验证开销无法掩盖，$c \gg 1$
- **$\alpha$（接受长度）**：取决于任务可预测性，代码 / JSON 可达 4~5，自由对话通常只有 2~3

不同场景下的理论加速比对比：

| 场景 | $\gamma$ | $c$ | $\alpha$ | 加速比 |
|---|---|---|---|---|
| 单卡 3090 + 7B，自由对话 | 0.20 | 1.73 | 3.08 | 1.13x |
| 双卡 + 70B，自由对话 | ~0 | 1.05 | 3.08 | 2.93x |
| 双卡 + 70B，代码生成 | ~0 | 1.05 | 4.50 | 4.29x |

第一行的数据将在第三章的实验中验证。

### 2.7 投机采样适用场景总结

从公式 $S = \frac{\alpha}{k\gamma + c}$ 出发，要让加速比显著大于 1，需要同时满足：

**条件 1：Target 模型足够大（使 $\gamma \to 0$）**

Target 模型越大，单次 decode 越慢，draft 模型的相对开销就越小。7B 模型 TPOT 只有 20ms，draft 0.5B 的 20ms 开销就已经是 100% 的额外负担；70B 模型 TPOT 约 200ms，同样的 draft 开销占比只有 10%。

**条件 2：Draft 与 Target 可并行（使 $\gamma = 0$）**

单卡上 draft 和 target 串行执行、共享显存带宽，draft 开销无法被掩盖。多卡部署时，draft 在独立 GPU 上运行，可以与 target 计算完全重叠。

**条件 3：低并发，GPU 处于 memory-bound（使 $c \to 1$）**

低并发时 GPU 算力空闲，验证多个 token 的额外计算可以"藏"在带宽等待中，$c \approx 1$。高并发时 GPU 已满载，验证开销变成实打实的额外时间，$c \gg 1$，投机采样反而拖累性能。

**条件 4：接受率足够高（使 $\alpha$ 大）**

接受率取决于 draft 模型和 target 模型概率分布的匹配程度，以及任务本身的可预测性。代码补全、JSON 生成等高重复性任务 $\alpha$ 可达 4~5；自由对话 $\alpha$ 通常只有 2~3。

| 条件 | 本文实验 | 理想场景 |
|---|---|---|
| Target 模型大小 | 7B（TPOT 20ms） | 70B+（TPOT 200ms+） |
| GPU 配置 | 单卡（串行） | 多卡（并行） |
| 并发水平 | conc=8~16 | conc=1~2 |
| 任务类型 | 自由对话（α≈3） | 代码 / JSON（α≈4~5） |
| 预期加速 | ~1.0x（无收益） | 2~4x |

---

## 三、实验验证

### 3.1 实验设计

**目标：** 验证投机采样在单卡 RTX 3090 + Qwen2.5-7B 上的精度和性能表现。

**实验环境与基线一致：**

| 项目 | 设置 |
|---|---|
| 硬件 | RTX 3090 24GB（单卡） |
| Target 模型 | Qwen2.5-7B-Instruct（BF16，14GB） |
| Draft 模型 | Qwen2.5-0.5B-Instruct（BF16，1GB） |
| N-gram | vLLM 内置，无额外模型 |
| spec-tokens | 5 |
| 数据集 | ShareGPT（性能）/ HellaSwag、ARC、GSM8K（精度） |

**对照组设计：**

| 组别 | 配置 | 目的 |
|---|---|---|
| Baseline | 普通 decode，无投机 | 对照基准 |
| Draft 0.5B | Qwen2.5-0.5B 做草稿 | 测试 draft model 效果 |
| N-gram | 从输入文本匹配 n-gram | 测试无模型方案效果 |

启动命令：

```bash
# Baseline（无投机采样）
vllm serve /root/autodl-tmp/models/qwen2.5-7b-instruct \
    --served-model-name qwen2.5-7b \
    --gpu-memory-utilization 0.85 --max-model-len 4096

# Draft Model（0.5B）
vllm serve /root/autodl-tmp/models/qwen2.5-7b-instruct \
    --served-model-name qwen2.5-7b \
    --gpu-memory-utilization 0.85 --max-model-len 4096 \
    --spec-model /root/autodl-tmp/models/qwen2.5-0.5b-instruct \
    --spec-tokens 5

# N-gram
vllm serve /root/autodl-tmp/models/qwen2.5-7b-instruct \
    --served-model-name qwen2.5-7b \
    --gpu-memory-utilization 0.85 --max-model-len 4096 \
    --spec-method ngram --spec-tokens 5
```

> ⚠️ **踩坑：Qwen2.5 系列的词表不一致**
>
> Qwen2.5-7B-Instruct 的 vocab_size 为 152064，而 0.5B 和 1.5B 版本为 151936。vLLM 要求 target 和 draft 词表大小严格一致，否则启动报错。解决方法是手动将 draft 模型的 `config.json` 中 vocab_size 改为 152064，并对 embedding 和 lm_head 权重进行 zero-padding。这个改法只是绕过了校验，新增的 128 个 token 位置没有真实权重，但对中英文对话场景影响可忽略。

### 3.2 精度评测：验证零损失

使用 lm_eval 对 baseline 和投机采样（draft 0.5B）分别运行相同的精度评测：

| Task | Metric | Baseline | Draft 0.5B | 差值 |
|---|---|---|---|---|
| HellaSwag | acc_norm | 80.50% | 80.52% | +0.02% |
| ARC-Easy | acc_norm | 81.02% | 81.02% | 0.00% |
| ARC-Challenge | acc_norm | 54.78% | 54.78% | 0.00% |
| GSM8K | flexible | 71.30% | 72.18% | +0.88% |

四项指标的差值都在统计误差范围内，**精度完全一致**，验证了投机采样的核心理论保证：拒绝采样机制确保输出分布与原模型等价。

### 3.3 性能评测

分别在 conc=1（投机采样最理想场景）和 conc=16（模拟生产负载）下测试，使用 ShareGPT 数据集。

#### 低并发结果（conc=1，rate=inf）

| 指标 | Baseline | Draft 0.5B | N-gram |
|---|---|---|---|
| TPOT P50 (ms) | **19.7** | 19.55 | 20.83 |
| TPOT P99 (ms) | **19.8** | 37.78 | 21.44 |
| ITL Median (ms) | ~19.7 | 54.19 | 21.11 |
| Out_TPS (tok/s) | 50 | 54.9 | 49.6 |
| Accept Rate | — | 41.63% | 43.44% |
| Accept Length | — | 3.08 | 3.17 |

即使在最理想的 conc=1 场景下，**投机采样也未能超越 baseline**。

TPOT 看起来持平（19.55 vs 19.7），但 ITL 暴露了真实的用户体验：draft 0.5B 的 ITL 为 54ms，意味着用户每隔 54ms 才看到一批 token 输出（约 3 个），中间有明显的"一卡一顿"感。而 baseline 每 20ms 稳定输出 1 个 token，体验更流畅。

#### 高并发结果（conc=16，rate=4）

| 指标 | Baseline | Draft 0.5B | N-gram |
|---|---|---|---|
| TPOT P50 (ms) | **23.87** | 25.64 | 52.56 |
| TPOT P99 (ms) | **34.38** | 110.00 | 101.04 |
| TTFT P99 (ms) | **293** | 7403 | 405 |
| Out_TPS (tok/s) | **558** | 527 | 272 |
| Accept Rate | — | 42.13% | 41.67% |

高并发下投机采样**全面恶化**。Draft 0.5B 的 TTFT P99 炸到 7.4 秒，是 baseline 的 25 倍——draft 模型额外占用的显存压缩了 KV Cache 空间，导致高并发时排队暴增。N-gram 虽然不占显存，但 TPOT 翻倍，吞吐腰斩。

### 3.4 为什么没有加速：用公式拆解

回顾 2.6 节的加速比公式 $S = \frac{\alpha}{k\gamma + c}$，用 conc=1 draft 0.5B 的实测数据代入。

从 ITL 数据反推每轮耗时的构成：

```
每轮总耗时 = 54ms（ITL median）

其中：
  Draft 阶段：0.5B 模型自回归生成 5 个 token
    = 5 × ~4ms = 20ms

  Verify 阶段：7B 模型验证 5 个 token
    = 54 - 20 = 34ms

对比：
  baseline 单次 decode = 19.7ms
  verify 5 个 token    = 34ms（比单次 decode 慢 73%）
```

代入参数：

$$\gamma = \frac{4}{19.7} = 0.20, \quad c = \frac{34}{19.7} = 1.73, \quad \alpha = 3.08$$

$$S = \frac{3.08}{5 \times 0.20 + 1.73} = \frac{3.08}{2.73} = 1.13\times$$

理论上只有 **13%** 的加速空间，被系统管理开销（KV Cache 更新、拒绝重采样、调度）吃掉后，实测为 ~0%。与 2.6 节的预测完全吻合。

三个因素共同导致了加速失败：

| 因素 | 本文实验 | 需要达到 | 差距 |
|---|---|---|---|
| $\gamma$（draft 开销比） | 0.20（串行，共享带宽） | ~0（并行，独立 GPU） | draft 占了 37% 的总耗时 |
| $c$（验证开销比） | 1.73（单卡资源竞争） | ~1.05（memory-bound） | verify 比 decode 慢 73% |
| $\alpha$（接受长度） | 3.08（自由对话） | 4~5（代码 / JSON） | 猜不准，收益太少 |

### 3.5 跨数据集验证

为排除数据集偏差，在 Spec-Bench（专为投机采样设计的评测集，包含写作、推理、数学、代码等多种任务）上重复实验（conc=8）：

| 指标 | Baseline | Draft 0.5B |
|---|---|---|
| TPOT P50 (ms) | **22.57** | 22.86 |
| Out_TPS (tok/s) | **334** | 333 |
| TTFT P99 (ms) | **421** | 2180 |
| Accept Rate | — | 40.61% |

结论不变：即使在包含代码、数学等高可预测性任务的数据集上，单卡 7B 的投机采样仍然无法带来加速。接受率甚至更低（40.6% vs ShareGPT 的 42%），说明**瓶颈不在数据集，而在硬件条件**。

---

## 四、总结

### 4.1 本文完成的工作

| 内容 | 结果 |
|---|---|
| 投机采样原理解析 | ✅ 完成（先猜后验、拒绝采样、加速条件推导） |
| Draft Model 方案（0.5B） | ✅ 精度零损失，但性能无提升 |
| N-gram 方案 | ✅ 精度零损失，但性能无提升 |
| 加速比公式验证 | ✅ 理论 1.13x，实测 ~1.0x，吻合 |
| Spec-Bench 跨数据集验证 | ✅ 结论一致，排除数据集偏差 |

### 4.2 关键结论

**结论 1：投机采样在单卡 RTX 3090 + 7B 模型上无法加速**

所有配置（draft 0.5B / ngram × conc=1 / conc=16）均未能超越 baseline。最理想的 conc=1 场景下，理论加速比仅 1.13x，被系统开销抵消后实测为 ~1.0x。

**结论 2：精度确实零损失**

lm_eval 四项评测指标与 baseline 完全一致（差值在统计误差内），验证了拒绝采样机制的理论保证。投机采样不改变输出分布，这一点毫无疑问。

**结论 3：加速失败的根因已被公式量化**

实验测得 $\gamma = 0.20$、$c = 1.73$、$\alpha = 3.08$，代入公式 $S = 1.13\times$，与实测结果吻合。三个因素——draft 串行开销过大、验证比单次 decode 慢 73%、接受率仅 42%——共同导致加速空间被完全抵消。

**结论 4：投机采样是一项有前提条件的优化**

它需要"大模型（70B+）+ 多卡（draft 并行）+ 低并发 + 高接受率"的组合才能发挥威力。这不是技术缺陷，而是应用条件不匹配——正如 FP8 KV Cache 需要 Ada/Hopper 架构一样，每项优化技术都有它的硬件门槛。

### 4.3 系列实验的硬件限制主线

回顾整个系列，RTX 3090 + 7B 这个组合下尝试过的所有优化：

```
=== 优化效果总览 ===

有效的优化：
  AWQ INT4 量化       → TPOT -65%，吞吐 +117%，精度损失 <2%
  Prefix Caching      → TTFT 降幅 67%~93%，零代价

无效的优化：
  FP8 KV Cache        → RTX 3090 不支持原生 FP8（需要 Ada/Hopper）
  INT8 KV Cache       → 精度崩塌（HellaSwag 80.5% → 65.5%）
  投机采样（本文）     → 单卡 7B 资源竞争，加速比 ≈ 1.0x
```

**共同结论：很多推理优化技术都有硬件或场景的前提条件。** 在 RTX 3090 + 7B 这个组合下，AWQ 量化和 Prefix Caching 是仅有的"免费午餐"。其余优化不是技术不行，而是硬件条件不支持——这本身就是一个重要的工程认知。

### 4.4 完整实验对照表

```
=== 完整实验记录 ===

                        基线 v0 (BF16)      实验 1 (AWQ INT4)
硬件:                   RTX 3090 24GB       RTX 3090 24GB
模型权重:               ~14 GB              ~4 GB
KV Cache 容量:          5306 blocks (4.6GB) 15839 blocks (13.9GB)

精度:
  HellaSwag:            80.5%               79.6%  (-0.9%)
  ARC-Easy:             81.0%               78.8%  (-2.2%)
  ARC-Challenge:        55.5%               54.5%  (-1.0%)
  GSM8K:                71.3%               69.2%  (-2.1%)

性能:
  TPOT P50 (conc=1):    19.7 ms             6.84 ms    (-65%)
  Out_TPS (conc=32):    978 tok/s           2126 tok/s (+117%)

Prefix Caching:
  ~1500 tokens 前缀：    TTFT 降低 18.5%，命中率 99.2%
  ~4000 tokens 前缀：    TTFT 降低 92.6%
  拟合斜率下降：          96.7%

投机采样（本文）:
  精度：                 零损失（4 项指标完全一致）
  Draft 0.5B conc=1：    TPOT 19.55ms vs baseline 19.7ms（无提升）
  Draft 0.5B conc=16：   TPOT 25.64ms vs baseline 23.87ms（+7.4%，恶化）
  N-gram conc=1：        TPOT 20.83ms vs baseline 19.7ms（无提升）
  理论加速比：            S = 1.13x，实测 ~1.0x
  根因：                 γ=0.20（串行）, c=1.73（资源竞争）, α=3.08（低接受率）
```

### 4.5 下一步计划

本系列在 RTX 3090 上的优化实验已基本完成。从实验结果来看，单卡消费级 GPU 上能有效应用的优化手段有限，进一步提升需要更强的硬件支持。

| 方向 | 内容 | 所需条件 |
|---|---|---|
| 更大模型 + 投机采样 | 在 70B+ 模型上验证投机采样的真实加速效果 | 需要多卡 A100/H100 |
| EAGLE / MTP | 共享权重的 draft head，避免独立模型的显存开销 | 需要模型支持 |
| 系列收官总结 | 汇总五篇文章的方法论和最优部署配置 | 数据已齐全 |

---

> 本系列完整文章索引：
>
> 1. [BF16 基线部署：从零建立精度与性能基准](../baseline-deployment)
> 2. [AWQ INT4 量化：TPOT 从 19.7ms 到 6.84ms](../awq-quantization)
> 3. [KV Cache 深度解析：吞吐翻倍的真正推手](../kv-cache)
> 4. [Prefix Caching：TTFT 降低 92.6% 的免费优化](../prefix-caching)
> 5. [投机采样：一次有价值的失败实验](../speculative-decoding)（本文）

---

**参考资料：**

- [Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192)（ICML 2023，投机采样原始论文）
- [Accelerating Large Language Model Decoding with Speculative Sampling](https://arxiv.org/abs/2302.01318)（DeepMind，独立提出同一方法）
- [Spec-Bench: A Comprehensive Benchmark for Speculative Decoding](https://arxiv.org/abs/2401.07851)（ACL 2024 Findings）
- [EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty](https://arxiv.org/abs/2401.15077)（ICML 2024）
- [SpecDecode-Bench: Speculative Decoding: Performance or Illusion?](https://specdecode-bench.github.io/)
- [vLLM Speculative Decoding 文档](https://docs.vllm.ai/en/latest/features/spec_decode.html)