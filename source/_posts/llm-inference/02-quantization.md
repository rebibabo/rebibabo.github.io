---
title: quantization
date: 2026-04-02
mathjax: true
categories:
    llm-inference
tags:
---

## 一、前言

上一篇文章我们在 RTX 3090 上建立了 Qwen2.5-7B-Instruct BF16 的完整基线，得出了一个关键结论：**单请求 TPOT 已逼近显存带宽的物理极限（19.7ms vs 理论下限 15ms），纯软件调参已经到顶。**

想进一步压缩延迟，必须减少每次 decode 需要搬运的权重字节数——这正是量化要做的事。

本文使用 AWQ INT4 量化，把模型权重从 BF16（每参数 2 字节）压缩到 INT4（每参数 0.5 字节），然后用与基线完全相同的评测方案跑精度和性能对比，用数据回答一个问题：**这 75% 的压缩率换来了多少性能提升，又付出了多少精度代价？**

先看结论：

| 指标 | BF16 基线 | AWQ INT4 | 变化 |
|---|---|---|---|
| 单请求 TPOT | 19.7 ms | **6.84 ms** | -65% |
| 输出吞吐天花板 | 978 tok/s | **2126 tok/s** | +117% |
| 严格 SLO Goodput | 826 tok/s | **4547 tok/s** | +450% |
| HellaSwag acc_norm | 80.5% | 79.6% | -0.9% |
| GSM8K flexible-extract | 71.3% | 69.2% | -2.1% |
| 模型体积 | ~14 GB | ~4 GB | -71% |

**1~3% 的精度代价，换来 TPOT 降 65%、吞吐翻倍、有效吞吐提升 5.5 倍。** 这是 LLM 推理优化中性价比最高的单一手段。


## 二、量化基础知识

在正式跑量化实验之前，先搞清楚量化是什么、怎么做的——否则后面看到精度数字变化时会不知道该怎么解释。

### 2.1 什么是量化

量化的核心思想很简单：**用更少的 bit 来表示原本高精度的浮点数**。

```
BF16（16 bit）→ INT8（8 bit）：存储减半，带宽减半
BF16（16 bit）→ INT4（4 bit）：存储变为原来的 1/4，带宽变为 1/4
```

代价是精度有损失——用有限个离散的整数值去近似一段连续的浮点区间，必然会有舍入误差。但对于 LLM 推理来说，这个代价通常是可以接受的，换来的收益是显存占用和 TPOT 的大幅下降。

### 2.2 均匀量化 vs 非均匀量化

根据量化后相邻整数值之间的间距是否相等，分为两种：

**均匀量化**：所有量化区间等宽，即每个整数格代表相同的浮点范围。实现简单，硬件友好，是目前工业界的主流方案。

**非均匀量化**：量化区间不等宽，可以在数值密集的区域分配更细的精度。理论精度更高，但硬件实现复杂，实际部署较少使用。

```
均匀量化：   
|———|———|———|———|———|———|———|———|
 -4  -3  -2  -1   0   1   2   3      ← 等间距

非均匀量化： 
|—|——|———|————|—————|————|———|——|
-4 -3 -2   -1    0    1    2  3      ← 0 附近更密，边缘更稀
```

**本文使用的 AWQ 属于均匀量化。** 后文提到的量化公式、缩放因子、截断等概念都基于均匀量化。

### 2.3 量化与反量化公式

量化的本质是一个**线性映射**，把浮点数 `r` 映射到整数 `Q(r)`：

量化：

$$
Q(r) = \mathrm{clamp}\left(
\mathrm{round}\left(\frac{r}{S}\right) - Z\;
-2^{n-1}\;
2^{n-1}-1
\right)
$$

反量化：

$$
\hat{r} = S \times \bigl(Q(r) + Z\bigr)
$$


其中：

- **S**（Scale）：缩放因子，决定每个整数格对应的浮点范围
- **Z**（Zero Point）：零点偏移，决定浮点 0 映射到哪个整数
- **n**：量化位宽（INT8 时 n=8，INT4 时 n=4）

`clamp` 是截断函数，保证量化后的整数值不超出表示范围：

$$
\mathrm{clamp}(x) =
\begin{cases}
\min, & x < \min \\\\
\max, & x > \max \\\\
x,    & \text{otherwise}
\end{cases}
$$

反量化不能完全还原原始值，$\hat r \approx r$，两者之间的差就是**量化误差**。

### 2.4 单个数值的量化示例

以 INT4 对称量化（$Z=0$，范围 $[-7, 7]$）量化浮点数为例：

**示例 1：r = 3.7（未超出范围）**

```
假设 S = 0.5（即每个整数格代表 0.5 的浮点范围）

第一步 缩放：  r / S = 3.7 / 0.5 = 7.4
第二步 取整：  round(7.4) = 7
第三步 截断：  clamp(7, -7, 7) = 7  ✅ 未超出范围

量化结果：Q(3.7) = 7
反量化：  r̂ = 0.5 × 7 = 3.5
量化误差：|3.7 - 3.5| = 0.2
```

**示例 2：r = 4.2（超出范围，触发截断）**

```
第一步 缩放：  r / S = 4.2 / 0.5 = 8.4
第二步 取整：  round(8.4) = 8
第三步 截断：  clamp(8, -7, 7) = 7  ⚠️ 超出上限，截断到 7！

量化结果：Q(4.2) = 7
反量化：  r̂ = 0.5 × 7 = 3.5
量化误差：|4.2 - 3.5| = 0.7  ← 截断导致误差大幅增加
```

截断（Clipping）是量化精度损失的主要来源之一。截断阈值的选择是一个 trade-off：

```
阈值选大 → 截断误差小，但舍入误差大（步长 S 变大，"格子"更粗）
阈值选小 → 舍入误差小，但截断误差大（超出范围的值全被截到边界）
```

TensorRT 的做法是用 KL 散度遍历所有可能的阈值，找到使量化前后分布差异最小的那个。AWQ 则通过保护重要通道的方式，从源头减少需要截断的异常值。

### 2.5 对称量化 vs 非对称量化

根据零点偏移 Z 是否为 0，分为两种：

**非对称量化$(Z ≠ 0)$**：整数范围 $[-128, 127]$ 全部用上，利用率高，但计算复杂。

**对称量化$(Z = 0)$**：整数范围限制在 $[-127， 127]$（放弃一个值），公式化简为：

$$
\begin{aligned}
Q(r) &= \mathrm{clamp}\left(
\mathrm{round}\left(\frac{r}{S}\right)\;
-2^{n-1}+1\;
2^{n-1}-1
\right) \\\\
\hat{r} &= S \times Q(r)
\end{aligned}
$$

**为什么实际更常用对称量化？** 两个矩阵相乘时能看出来：

非对称量化下，$A = S_A · Q_A + Z_A，B = S_B · Q_B + Z_B$，展开乘法：

$$
\begin{aligned}
A \times B
&= S_A S_B Q_A Q_B && \text{（主项，纯 INT 乘法）} \\\\
&\quad + S_A Q_A Z_B   && \text{（额外计算）} \\\\
&\quad + S_B Q_B Z_A   && \text{（额外计算）} \\\\
&\quad + Z_A Z_B       && \text{（额外计算）}
\end{aligned}
$$

对称量化下$(Z = 0)$，$A = S_A · Q_A，B = S_B · Q_B$：

$$
A \times B = S_A · S_B · Q_A · Q_B      ← 只有这一项！
$$

后面三项全部消掉，矩阵乘法化简为**纯整数乘法 + 一次缩放**，硬件实现更简单、更快。

### 2.6对称量化的代价：量化偏差

对称量化在使用 $[-128, 127]$ 全范围时，整数域负数比正数多一个值，会引入系统偏差。下面用一个完整例子说明：

```
A = [-2.2, -1.1, 1.1, 2.2]（行向量）
B = [0.5, 0.3, 0.3, 0.5]ᵀ（列向量）

向量点积（逐元素相乘再求和）：
AB = (-2.2 × 0.5) + (-1.1 × 0.3) + (1.1 × 0.3) + (2.2 × 0.5)
   = -1.1 + (-0.33) + 0.33 + 1.1
   = 0
```

**用 $[-128, 127]$ 范围做 8-bit 量化：**

```
缩放因子：
  s_A = 128 / 2.2 ≈ 58.18
  s_B = 128 / 0.5 = 256

量化 A：
  [-2.2 × 58.18, -1.1 × 58.18, 1.1 × 58.18, 2.2 × 58.18]
  = [-128, -64, 64, 128]
  → 截断到 [-128, -64, 64, 127]
                           ↑ 128 超出上限 127，被截断！

量化 B：
  [0.5 × 256, 0.3 × 256, 0.3 × 256, 0.5 × 256]
  = [128, 77, 77, 128]
  → 截断到 [127, 77, 77, 127]
            ↑ 同理截断

量化后的点积：
  (-128 × 127) + (-64 × 77) + (64 × 77) + (127 × 127)
  = -16256 + (-4928) + 4928 + 16129
  = -127

反量化：
  result / (s_A × s_B) = -127 / (58.18 × 256) = -127 / 14894 ≈ -0.00853
```

结果应该是 0，实际得到 **-0.00853**，偏向负无穷。原因是 2.2 量化后从 128 被截断到 127，而 -2.2 量化为 -128 没有被截断，正负不再对称。

**改用 $[-127, 127]$（对称范围）：**

```
缩放因子：
  s_A = 127 / 2.2 ≈ 57.73
  s_B = 127 / 0.5 = 254

量化 A：[-127, -64, 64, 127]   ← 正负完全对称，没有截断
量化 B：[127, 76, 76, 127]

量化后的点积：
  (-127 × 127) + (-64 × 76) + (64 × 76) + (127 × 127)
  = -16129 + (-4864) + 4864 + 16129
  = 0

反量化：0 / (57.73 × 254) = 0  ← 完全正确
```

**结论：对称量化用 $[-127, 127]$ 而不是 $[-128, 127]$**，牺牲 1/256 的表示范围（INT8）或 1/16 的表示范围（INT4），换取无偏差的矩阵乘法。AWQ INT4 量化正是基于这个原理。

### 2.7 PTQ vs QAT

量化有两种主要范式，区别在于**模型参数是否参与训练**：

```
PTQ（训练后量化）：

  Pre-trained model → 校准数据（少量）→ 计算缩放因子 → 量化模型
  参数固定，不重新训练

QAT（量化感知训练）：

  Pre-trained model → 训练数据（大量）→ 重训练/微调 → 量化模型
  参数更新，模型学会适应量化误差
```

| 维度 | PTQ | QAT |
|---|---|---|
| 数据需求 | 少量校准数据（百~千条） | 大量训练数据 |
| 计算成本 | 低，分钟级 | 高，需要完整训练流程 |
| 精度损失 | 略多 | 少，接近原始精度 |
| 适用场景 | 快速部署、资源受限 | 对精度要求极高 |

**本文使用 PTQ**（AWQ 属于 PTQ 的一种），用少量校准数据找到每层最优的缩放因子，不需要重新训练模型。本文从 ModelScope 下载的 `Qwen2.5-7B-Instruct-AWQ` 就是 Qwen 官方已经完成校准和量化的成品，直接加载即可使用。

> 💡 **AWQ 的核心改进**
>
> 普通 PTQ 对所有权重一视同仁地量化。AWQ（Activation-aware Weight Quantization）的改进在于：先用校准数据跑一遍前向传播，找出每层中**对激活值影响最大的重要权重通道**，对这些通道做保护性缩放后再统一量化。这样在同样的 INT4 精度下，能显著减少精度损失。

## 三、实验设置

### 3.1 下载 AWQ 量化模型

Qwen 官方在 ModelScope 上发布了预量化好的 AWQ INT4 版本，直接下载即可：

```bash
modelscope download \
    --model qwen/Qwen2.5-7B-Instruct-AWQ \
    --local_dir /root/autodl-tmp/models/qwen2.5-7b-instruct-awq
```

下载完成后验证量化配置：

```bash
cat /root/autodl-tmp/models/qwen2.5-7b-instruct-awq/config.json | grep -A5 quantization
```

看到 `"bits": 4` 说明是 INT4 量化模型。模型文件总大小约 **4~5 GB**，对比 BF16 的 14 GB 压缩了约 70%。

### 3.2 启动 vLLM 推理服务

```bash
python -m vllm.entrypoints.openai.api_server \
    --model /root/autodl-tmp/models/qwen2.5-7b-instruct-awq \
    --served-model-name qwen2.5-7b-awq \
    --host 0.0.0.0 \
    --port 8000 \
    --gpu-memory-utilization 0.85 \
    --max-model-len 4096
```

vLLM 会自动识别 AWQ 量化格式，不需要额外参数。启动参数含义参考[上一篇基线文章的第三章]。

> 💡 **量化模型的显存变化**
>
> 模型权重从 ~14 GB 降到 ~4 GB，但 `nvidia-smi` 显示的显存占用不会明显减少——因为 vLLM 的预分配机制会把省出来的 ~10 GB 显存全部分配给 KV cache 池。这意味着系统能同时处理更多并发请求，吞吐天花板会大幅提升。

### 3.3 精度评测

评测设置与基线完全一致（不加 `--apply_chat_template`，0-shot），仅修改模型名和输出路径：

```bash
export OMP_NUM_THREADS=16
export HF_DATASETS_OFFLINE=1
export HF_DATASETS_CACHE=/root/autodl-tmp/hf_cache

lm_eval \
  --model local-completions \
  --model_args "model=qwen2.5-7b-awq,base_url=http://localhost:8000/v1/completions,tokenizer_backend=huggingface,tokenizer=/root/autodl-tmp/models/qwen2.5-7b-instruct-awq,num_concurrent=32,max_length=4096" \
  --tasks hellaswag,arc_easy,arc_challenge,gsm8k \
  --num_fewshot 0 \
  --output_path /root/autodl-tmp/results/lm_eval_awq \
  --log_samples
```

### 3.4 性能基线测试

```bash
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

vllm bench serve \
    --backend openai-chat \
    --base-url http://localhost:8000 \
    --endpoint /v1/chat/completions \
    --model qwen2.5-7b-awq \
    --tokenizer /root/autodl-tmp/models/qwen2.5-7b-instruct-awq \
    --dataset-name sharegpt \
    --dataset-path /root/autodl-tmp/datasets/sharegpt.json \
    --num-prompts 200 \
    --request-rate 4 \
    --max-concurrency 16 \
    --save-result \
    --result-dir /root/autodl-tmp/results/perf_awq
```

### 3.5 参数扫描

与基线相同的扫描方案（实验组 A 扫描 request-rate，实验组 B 扫描 max-concurrency），仅替换模型名和输出路径：

```bash
#!/bin/bash
mkdir -p /root/autodl-tmp/results/sweep_awq

COMMON_ARGS="
    --backend openai-chat
    --base-url http://localhost:8000
    --endpoint /v1/chat/completions
    --model qwen2.5-7b-awq
    --tokenizer /root/autodl-tmp/models/qwen2.5-7b-instruct-awq
    --dataset-name sharegpt
    --dataset-path /root/autodl-tmp/datasets/sharegpt.json
    --num-prompts 200
    --save-result
"

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

echo "=== 实验组 A：扫描 request-rate ==="
for rate in 1 2 4 8 16 inf; do
    vllm bench serve $COMMON_ARGS \
        --request-rate $rate \
        --max-concurrency 32 \
        --result-dir /root/autodl-tmp/results/sweep_awq \
        --result-filename "expA_rate${rate}_conc32.json"
    sleep 5
done

echo "=== 实验组 B：扫描 max-concurrency ==="
for conc in 1 4 8 16 32 64 128; do
    vllm bench serve $COMMON_ARGS \
        --request-rate inf \
        --max-concurrency $conc \
        --result-dir /root/autodl-tmp/results/sweep_awq \
        --result-filename "expB_rateinf_conc${conc}.json"
    sleep 5
done
```

参数扫描的实验设计原理参考[上一篇基线文章的 5.3~5.5 节]。

## 四、实验结果分析

### 4.1 精度对比

| 数据集 | 指标 | BF16 基线 | AWQ INT4 | 绝对下降 | 相对下降 |
|---|---|---|---|---|---|
| HellaSwag | acc_norm | 80.5% | 79.6% | -0.9% | -1.1% |
| ARC-Easy | acc_norm | 81.0% | 78.8% | -2.2% | -2.7% |
| ARC-Challenge | acc_norm | 55.5% | 54.5% | -1.0% | -1.8% |
| GSM8K | flexible-extract | 71.3% | 69.2% | -2.1% | -2.9% |

精度损失在 **1~3%** 之间，其中常识推理（HellaSwag）损失最小，数学推理（GSM8K）和科学知识（ARC-Easy）略高，说明这两类任务对权重精度更敏感。总体在可接受范围内。

### 4.2 性能基线对比

先看 rate=4、conc=16 下的单次测试结果：

| 指标 | BF16 基线 | AWQ INT4 | 变化 |
|---|---|---|---|
| TTFT P50 | 113 ms | 93 ms | -18% |
| TTFT P99 | 293 ms | 293 ms | ≈0% |
| TPOT P50 | 23.9 ms | **9.0 ms** | **-62%** |
| TPOT P99 | 34.4 ms | 21.7 ms | -37% |
| Out_TPS | 558 tok/s | **777 tok/s** | +39% |

TPOT P50 直接从 23.9ms 降到 9.0ms，降幅 62%，超出预期的"减半"目标。

### 4.3 参数扫描结果

#### 实验组 A：固定 conc=32，扫描 request-rate

| Rate | BF16 TPOT P50 | AWQ TPOT P50 | BF16 Out_TPS | AWQ Out_TPS |
|---|---|---|---|---|
| 1 | 20.4 ms | **6.9 ms** | 202 | **212** |
| 2 | 22.1 ms | **7.1 ms** | 385 | **418** |
| 4 | 24.2 ms | **7.5 ms** | 695 | **806** |
| 8 | 26.5 ms | **10.0 ms** | 926 | **1451** |
| 16 | 27.0 ms | **13.0 ms** | 967 | **1965** |
| inf | 26.9 ms | **12.9 ms** | 979 | **2128** |

**关键发现 1：低负载下 TPOT 降幅更大**

rate=1~4 时 AWQ 的 TPOT 稳定在 7ms 左右，是 BF16 的 1/3。随着负载增加差距缩小但始终领先。

**关键发现 2：吞吐饱和点后移**

BF16 在 rate=8 就趋于饱和（926→967，+4.4%），AWQ 在 rate=16 才开始饱和（1965→2128，+8.3%）。原因是模型权重压缩后省出的显存全部给了 KV cache，GPU 能同时处理更多请求。

#### 实验组 B：固定 rate=inf，扫描 max-concurrency

| Conc | BF16 TPOT P50 | AWQ TPOT P50 | BF16 TPOT P99 | AWQ TPOT P99 | BF16 Out_TPS | AWQ Out_TPS |
|---|---|---|---|---|---|---|
| 1 | 19.7 ms | **6.8 ms** | 19.8 ms | **6.9 ms** | 50 | **144** |
| 8 | 21.4 ms | **7.5 ms** | 27.2 ms | **7.8 ms** | 345 | **994** |
| 16 | 23.4 ms | **8.7 ms** | 35.2 ms | **9.2 ms** | 595 | **1615** |
| 32 | 26.8 ms | **12.9 ms** | 60.2 ms | **14.5 ms** | 978 | **2126** |
| 64 | 34.4 ms | **23.3 ms** | 165 ms | **30.3 ms** | 1341 | **2319** |
| 128 | 51.9 ms | **39.4 ms** | 387 ms | **60.9 ms** | 1583 | **2509** |

**关键发现 3：单请求 TPOT 远超物理预期**

conc=1 时 TPOT P50 = **6.84ms**，已经超过了基线文章中定的 8ms 目标。

理论下限重新计算：

```
INT4 权重 ≈ 7B × 0.5 bytes ≈ 3.5 GB
RTX 3090 带宽 = 936 GB/s
理论 TPOT = 3.5 / 936 ≈ 3.7 ms
实测 6.84 ms，MBU = 3.7 / 6.84 ≈ 54%
```

MBU 比 BF16（76%）低，差距主要来自 INT4 反量化（dequantize）的额外计算开销——GPU 需要把 INT4 权重实时解压为 FP16 参与计算，这部分开销在 BF16 下不存在。

**关键发现 4：TPOT P99 拐点从 conc=32 后移到 conc=64**

```
BF16：  conc=32 → conc=64，TPOT P99 从 60ms 暴涨至 165ms  ← 质变
AWQ：   conc=32 → conc=64，TPOT P99 从 14.5ms 涨至 30.3ms ← 翻倍但仍可控
        conc=64 → conc=128，TPOT P99 从 30.3ms 涨至 60.9ms ← 这里才开始恶化
```

拐点后移一档，说明量化后 KV cache 池更大，系统能承受更高的并发压力。生产甜点区从 conc=8\~16 扩大到了 **conc=16\~32**。

**关键发现 5：并发越高，系统越快，用户越慢（依然成立）**

| Conc | AWQ Duration (s) | AWQ TTFT P99 | AWQ TPOT P99 |
|---|---|---|---|
| 1 | 300 s | 36 ms | 6.9 ms |
| 8 | 43 s | 92 ms | 7.8 ms |
| 32 | 20 s | 235 ms | 14.5 ms |
| 128 | 17 s | 640 ms | 60.9 ms |

同样处理 200 个请求，conc=128 只需 17 秒（是 conc=1 的 18 倍速），但用户等首个 token 的 P99 已经达到 640ms。这个结构性矛盾量化无法消除，只是把整条曲线向下平移了。

### 4.4 SLO 分析

**严格 SLO（TTFT P99 < 300ms，TPOT P99 < 40ms）：**

| | BF16 | AWQ INT4 |
|---|---|---|
| 达标档位 | 仅 rate=1~2 | **全部达标（rate=1 到 inf）** |
| 最佳 Goodput | 826 tok/s（rate=2） | **4547 tok/s（rate=inf）** |
| 提升倍数 | — | **5.5×** |

这是量化收益最震撼的一个数字：BF16 下只有最轻的两档负载能满足严格 SLO，AWQ 下连 rate=inf 全速压测都轻松达标。**有效吞吐提升 5.5 倍**。

原因是双重收益叠加：TPOT 大幅下降让每个请求处理更快 → 排队时间缩短 → TTFT 也跟着下降 → 全链路延迟改善。

### 4.5 基线 vs AWQ 汇总

```
=== BF16 基线 vs AWQ INT4 完整对比 ===

精度（0-shot，不加 chat template）：
  HellaSwag:          80.5% → 79.6%    (-0.9%)
  ARC-Easy:           81.0% → 78.8%    (-2.2%)
  ARC-Challenge:      55.5% → 54.5%    (-1.0%)
  GSM8K:              71.3% → 69.2%    (-2.1%)

性能：
  单请求 TPOT P50:    19.7 ms → 6.84 ms     (-65%)
  吞吐天花板(Out_TPS): 978 → 2126 tok/s      (+117%)
  TPOT P99 拐点:      conc=32 → conc=64     (后移一档)
  严格 SLO Goodput:   826 → 4547 tok/s      (+450%)
  生产甜点区:          conc=8~16 → conc=16~32

模型体积：
  权重大小:           ~14 GB → ~4 GB         (-71%)
```

**结论：AWQ INT4 量化用 1~3% 的精度代价，换来了 TPOT 降 65%、吞吐翻倍、Goodput 提升 5.5 倍的收益。从投入产出比来看，这是 LLM 推理优化中性价比最高的单一手段。**


## 五、总结与下一步计划

### 5.1 本文完成的工作

本文在上一篇基线数据的基础上，完成了 AWQ INT4 量化的完整实验闭环：

| 步骤 | 内容 | 结果 |
|---|---|---|
| 量化原理 | 均匀/非均匀、对称/非对称、截断、PTQ/QAT | ✅ 完成 |
| 模型部署 | 下载官方 AWQ 模型 + vLLM 加载 | ✅ 完成 |
| 精度评测 | lm-eval + HellaSwag/ARC/GSM8K | ✅ 完成 |
| 性能评测 | vllm bench + 参数扫描 | ✅ 完成 |
| 对比分析 | 精度、TPOT、吞吐、SLO 全面对比 | ✅ 完成 |

### 5.2 关键结论

**一句话总结：AWQ INT4 是 LLM 推理优化中性价比最高的单一手段。**

具体数据：

```
精度代价（可接受）：
  四个数据集平均下降 ~1.6%，最大 2.9%（GSM8K）

性能收益（远超预期）：
  TPOT:     19.7 ms → 6.84 ms    降 65%，超过 8ms 目标
  吞吐:      978 → 2126 tok/s     翻倍
  Goodput:  826 → 4547 tok/s     提升 5.5 倍
  甜点区:    conc=8~16 → 16~32    扩大一倍
  模型体积:  14 GB → 4 GB         压缩 71%
```

### 5.3 为什么量化收益这么大

量化的收益不是简单的"权重变小了"，而是**三重复利效应**叠加：

```
第一重：TPOT 下降
  权重从 14GB 压到 4GB → 每次 decode 搬运的数据量降 71%
  → TPOT 从 19.7ms 降到 6.84ms

第二重：KV cache 扩容
  省出 ~10GB 显存全部给 KV cache → 能同时处理更多请求
  → 吞吐天花板从 978 涨到 2126 tok/s

第三重：SLO 全面达标
  TPOT 下降 → 每个请求处理更快 → 排队时间缩短 → TTFT 跟着下降
  → 严格 SLO 下从仅 rate=1~2 达标变为全部达标
  → Goodput 提升 5.5 倍
```

这三重收益互相放大，最终效果远大于单纯的"4倍压缩"所暗示的线性提升。

### 5.4 方法论回顾

回顾上一篇提出的优化流程：

```
建立基线 ✅（上一篇）
   ↓
提出优化方案：AWQ INT4 量化 ✅
   ↓
实施优化：下载官方量化模型 ✅
   ↓
双线评测（精度 + 性能）✅
   ↓
决策：精度损失 1~3%，TPOT 降 65%，吞吐翻倍 → 收益远大于代价 → 采纳 ✅
```

**核心原则再次验证：没有免费的午餐，但这顿饭确实很便宜。** 1~3% 的精度换 5.5 倍的有效吞吐，对绝大多数生产场景来说都值得。

### 5.5 下一步计划

AWQ INT4 已经把 TPOT 压到了 6.84ms，距离理论下限 3.7ms 还有空间，但剩余优化的难度和收益比会逐渐递减。后续计划：

| 实验 | 方法 | 预期收益 | 预期代价 |
|---|---|---|---|
| **实验 2** | FP8 KV Cache | 叠加在 AWQ 之上，KV cache 减半，吞吐再涨 20~30% | < 0.5% |
| **实验 3** | 投机采样（ngram） | 低并发 TPOT 再降 30~50%，输出完全一致 | 0% |
| **实验 4** | 组合优化 | AWQ + FP8 KV + 投机采样，冲击 TPOT < 4ms | 综合评估 |

### 5.6 两篇文章的完整基线对照表

```
=== 完整实验记录 ===

                       基线 v0 (BF16)       实验 1 (AWQ INT4)
硬件:                   RTX 3090 24GB       RTX 3090 24GB
模型:                   Qwen2.5-7B BF16     Qwen2.5-7B AWQ INT4
权重大小:                ~14 GB              ~4 GB

精度:
  HellaSwag:            80.5%               79.6%  (-0.9%)
  ARC-Easy:             81.0%               78.8%  (-2.2%)
  ARC-Challenge:        55.5%               54.5%  (-1.0%)
  GSM8K:                71.3%               69.2%  (-2.1%)

性能:
  TPOT P50 (conc=1):    19.7 ms             6.84 ms    (-65%)
  Out_TPS (conc=32):    978 tok/s           2126 tok/s (+117%)
  TPOT P99 拐点:         conc=32→64          conc=64→128
  严格 SLO Goodput:      826 tok/s           4547 tok/s (+450%)
  生产甜点区:             conc=8~16           conc=16~32
```

---

> 本系列下一篇：[FP8 KV Cache 实验：在 AWQ 基础上进一步压榨吞吐]（待更新）

---

**参考资料：**

- [AWQ: Activation-aware Weight Quantization](https://arxiv.org/abs/2306.00978)（MLSys 2024 Best Paper）
- [vLLM 官方文档](https://docs.vllm.ai)
- [Qwen2.5 技术报告](https://qwenlm.github.io/blog/qwen2.5/)
- [A Survey of Quantization Methods for Efficient Neural Network Inference](https://arxiv.org/abs/2103.13630)
- CMSC 5743 Mo03: Quantization, Bei Yu, CUHK