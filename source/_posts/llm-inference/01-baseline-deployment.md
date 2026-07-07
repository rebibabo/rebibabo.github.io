---
title: 
    LLM推理优化实战(一)：RTX3090部署Qwen2.5-7B全记录：TPOT-19.7ms，已逼近显存带宽极限

date: 2026-04-01
categories:
    llm-inference
tags:
---

## 一、前言

在做任何优化之前，你需要一份可信的基线数据——否则你永远不知道优化到底有没有效果。

本文记录在一台 RTX 3090 上从零部署 Qwen2.5-7B-Instruct BF16，并建立完整精度与性能基线的全过程，包括环境搭建、踩坑实录、参数扫描实验和结果分析。这份基线将作为后续量化、投机采样等优化实验的对照组，**每次优化都要打败它**。

先看结论：

| 指标 | 数值 |
|---|---|
| 单请求 TPOT | 19.7 ms（理论极限 15 ms，MBU ≈ 76%）|
| 系统输出吞吐天花板 | 979 tok/s（Out_TPS，conc=32 时趋于饱和）|
| HellaSwag acc_norm | 80.5% |
| GSM8K flexible-extract | 71.3% |
| 最佳生产并发 | 8~16（严格 SLO 下）|

**最重要的一个发现**：单请求 TPOT 已逼近显存带宽的物理极限，纯软件调参已经到顶。想进一步压缩延迟，必须走量化路线——这正是下一篇的主题。

## 二、环境部署

### 2.1 硬件与平台

本文使用 [AutoDL](https://www.autodl.com) 云 GPU 平台，选择以下配置：

| 配置项 | 详情 |
|---|---|
| GPU | NVIDIA GeForce RTX 3090 |
| 显存 | 24 GB |
| 系统盘 | 30 GB |
| 数据盘 | 50 GB（挂载在 `/root/autodl-tmp`） |

> 💡 **为什么选 RTX 3090？** 24GB 显存可以直接跑 Qwen2.5-7B BF16 原始精度模型，无需量化即可建立精度基线，价格也相对实惠。

镜像选择：`PyTorch 2.x | Python 3.10 | CUDA 12.x`

### 2.2 一键安装所有依赖

```bash
# 升级 pip
pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/

# 安装 vLLM
pip install vllm -i https://pypi.mirrors.ustc.edu.cn/simple

# 安装 modelscope 并下载模型
pip install modelscope -i https://mirrors.aliyun.com/pypi/simple/
modelscope download \
    --model qwen/Qwen2.5-7B-Instruct \
    --local_dir /root/autodl-tmp/models/qwen2.5-7b-instruct

# 安装评测工具
pip install lm-eval -i https://mirrors.aliyun.com/pypi/simple/
pip install lm-eval[api] -i https://mirrors.aliyun.com/pypi/simple/

# 配置 HuggingFace 镜像
echo "export HF_ENDPOINT=https://hf-mirror.com
export HF_DATASETS_CACHE=/root/autodl-tmp/hf_cache" >> ~/.bashrc && source ~/.bashrc

# 下载 benchmark 数据集
mkdir -p /root/autodl-tmp/datasets /root/autodl-tmp/results/perf_baseline
wget https://hf-mirror.com/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/resolve/main/ShareGPT_V3_unfiltered_cleaned_split.json \
    -O /root/autodl-tmp/datasets/sharegpt.json

# 验证环境
python -c "
import torch, vllm
print('=== 环境检查 ===')
print(f'PyTorch:  {torch.__version__}')
print(f'vLLM:     {vllm.__version__}')
print(f'CUDA 可用: {torch.cuda.is_available()}')
print(f'GPU 数量:  {torch.cuda.device_count()}')
print(f'GPU 型号:  {torch.cuda.get_device_name(0)}')
print(f'显存总量:  {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
"
```

我的环境输出如下：

```
=== 环境检查 ===
PyTorch:  2.11.0+cu130
vLLM:     0.22.0
CUDA 可用: True
GPU 数量:  1
GPU 型号:  NVIDIA GeForce RTX 3090
显存总量:  23.6 GB
```

> ⚠️ **踩坑：cuDNN 版本冲突**
>
> 启动 vLLM 时遇到报错：`AssertionError: Found 2 libcudnn.so.x`
>
> 原因是同时装了 `nvidia-cudnn-cu12` 和 `nvidia-cudnn-cu13`，用以下命令排查并删除旧版本：
> ```bash
> pip list | grep cudnn   # 查看已安装版本
> pip uninstall nvidia-cudnn-cu12 -y  # 删除旧版本，保留 cu13
> ```

### 2.3 目录结构

安装完成后，目录结构如下：

```
/root/autodl-tmp/
├── models/
│   └── qwen2.5-7b/          ← 模型文件（约 15GB）
├── datasets/
│   └── sharegpt.json        ← benchmark 数据集
├── hf_cache/                ← HuggingFace 数据集缓存
└── results/
    └── perf_baseline/       ← 性能测试结果
```

## 三、启动 vLLM 推理服务

### 3.1 启动命令

```bash
export OMP_NUM_THREADS=4

python -m vllm.entrypoints.openai.api_server \
    --model /root/autodl-tmp/models/qwen2.5-7b-instruct \
    --served-model-name qwen2.5-7b \
    --host 0.0.0.0 \
    --port 8000 \
    --gpu-memory-utilization 0.85 \
    --max-model-len 4096
```

看到以下日志说明启动成功：

```
INFO:     Application startup complete.
```

### 3.2 关键参数解释

| 参数 | 含义 |
|---|---|
| `--model` | 模型本地路径 |
| `--served-model-name` | API 调用时使用的模型别名 |
| `--host 0.0.0.0` | 监听所有网卡，允许外部访问 |
| `--port 8000` | 服务端口 |
| `--gpu-memory-utilization 0.85` | GPU 显存利用率上限（见下文） |
| `--max-model-len 4096` | 最大序列长度（输入+输出 token 总数）|

用 curl 验证服务是否正常：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-7b",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 50
  }'
```

### 3.3 Instruct 模型 vs Base 模型

下载模型时你会发现 Qwen2.5-7B 有两个版本：

- `Qwen2.5-7B`：Base 模型
- `Qwen2.5-7B-Instruct`：Instruct 模型（本文使用）

两者的训练流程不同：

```
海量互联网文本
      ↓
  预训练（Pretrain）
      ↓
  Base 模型 ──→ Qwen2.5-7B
      ↓
  指令微调（SFT）+ 偏好对齐（RLHF/DPO）
      ↓
  Instruct 模型 ──→ Qwen2.5-7B-Instruct
```

直观对比，同样输入 `"中国的首都是"`：

**Base 模型输出**（续写模式）：
```
中国的首都是北京。北京位于华北平原北部，面积约16410平方公里，
人口约2189万。北京有3000多年的建城史...
```

**Instruct 模型输出**（对话模式）：
```
中国的首都是北京。
```

| 维度 | Base 模型 | Instruct 模型 |
|---|---|---|
| 行为模式 | 续写补全 | 听指令、回答问题 |
| 输入格式 | 任意文本 | chat template |
| 适用场景 | 研究、微调起点 | 直接部署给用户 |
| 安全对齐 | 无 | 有 |

**结论**：90% 的部署场景用 Instruct 版本，只有自己做微调才从 Base 开始。

### 3.4 gpu-memory-utilization 与显存预分配

#### 参数含义

`--gpu-memory-utilization 0.85` 表示**让 vLLM 预占 85% 的 GPU 显存**。

RTX 3090 总显存 24GB，计算如下：

```
预留给 vLLM 的总显存 = 24 × 0.85 = 20.4 GB
模型权重占用          = ~14 GB（7B × 2 字节/参数，BF16）
剩余给 KV cache      = 20.4 - 14 ≈ 6.4 GB
```

#### 为什么 vLLM 启动后显存就占满了

很多人第一次用 vLLM 会发现一个反直觉的现象：**即使没有任何请求，nvidia-smi 显示显存已经占用了约 20GB**。

这是 vLLM 的**显存预分配机制**设计的，原因如下：

```
传统按需分配：
  请求来了 → cudaMalloc() → 慢，容易碎片化
  请求结束 → cudaFree()  → 又慢

vLLM 预分配：
  启动时 → 一次性把 KV cache 池全部分配好
  请求来了 → 直接从池子里取，极快
  请求结束 → 还回池子，不释放
```

**显存占用不会随请求多少而变化**，这是正常现象，不是内存泄漏。

#### KV cache 池大小决定并发能力

显存越大、gpu-memory-utilization 越高，能服务的并发就越多，吞吐越高。

#### 如何监控 KV cache 实时使用率

`nvidia-smi` 看不出 KV cache 用了多少，要用 vLLM 的 metrics 接口：

```bash
watch -n 1 'curl -s http://localhost:8000/metrics | grep -E "kv_cache_usage|num_requests_running|num_requests_waiting"'
```

输出示例：

```
vllm:kv_cache_usage_perc{model_name="qwen2.5-7b"} 0.45   ← KV cache 用了 45%
vllm:num_requests_running{model_name="qwen2.5-7b"} 12     ← 当前处理 12 个请求
vllm:num_requests_waiting{model_name="qwen2.5-7b"} 3      ← 还有 3 个在排队
```

从 metrics 里还能看到 KV cache 的完整配置信息：

```bash
curl -s http://localhost:8000/metrics | grep cache_config_info
```

关键字段含义：

| 字段 | 含义 |
|---|---|
| `num_gpu_blocks=5306` | GPU 上共有 5306 个 KV cache block |
| `block_size=16` | 每个 block 存 16 个 token |
| `gpu_memory_utilization=0.85` | 显存利用率上限 85% |
| `enable_prefix_caching=True` | prefix cache 已开启 |

KV cache 总容量 = 5306 × 16 = **84,896 token**，这决定了系统能同时处理的最大 token 数。

> 💡 **经验总结**：显存"满"是好事，说明 KV cache 池够大，能服务更多并发。
> 真正反映系统忙碌程度的是 `/metrics` 里的指标，不是 `nvidia-smi`。

## 四、精度评测

精度评测的目的是建立模型能力的**基线数据**，后续每做一次优化（量化、投机采样等）都要重新跑一遍，对比精度是否退化。

### 4.1 评测工具：lm-evaluation-harness

本文使用 [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)，这是目前学术界和工业界最通用的 LLM 精度评测框架，支持 100+ 个标准评测数据集。

### 4.2 评测数据集说明

本文选用以下四个数据集：

| 数据集 | 测什么 | 题量 | 任务类型 |
|---|---|---|---|
| **HellaSwag** | 常识推理，从 4 个选项里选最合理的情境续写 | 10,042 | 多选题 |
| **ARC-Easy** | 小学科学知识问答 | 2,376 | 多选题 |
| **ARC-Challenge** | 需要多步推理的科学题，比 Easy 难 | 1,172 | 多选题 |
| **GSM8K** | 小学数学推理，需要多步计算得出数值答案 | 1,319 | 生成题 |

### 4.3 评测指标说明

**acc 和 acc_norm（适用于 HellaSwag、ARC）：**

- **acc**：直接选概率最高的选项
- **acc_norm**：按 token 长度归一化后再选

为什么需要归一化？LLM 计算选项概率时，**选项越长整体概率越小**（每个 token 概率都 < 1 连乘），模型会天然偏向选短选项。归一化后消除长度偏差，结果更客观。HellaSwag、ARC 这类任务统一看 `acc_norm`。

**flexible-extract 和 strict-match（适用于 GSM8K）：**

- **flexible-extract**：从模型的完整输出里提取数字，只要最终数值正确就算对。容忍模型输出带推理过程、单位、多余文字等，只抠最后的数字答案。
- **strict-match**：要求模型输出与标准答案完全一致，格式必须严格匹配。

两者的差距反映了模型的**输出格式规范程度**。本文实测 flexible-extract = 71.3%，strict-match = 0.0%，说明模型数学推理能力本身没问题，但输出格式不够规范——这是 0-shot + 不加 chat template 设置下的正常现象，加了 few-shot 示例后 strict-match 通常会显著提升。本文统一用 **flexible-extract** 作为 GSM8K 的基线指标。

### 4.4 启动 vLLM Server

lm-eval 通过 HTTP API 调用模型，需要先确保 vLLM server 在运行（参考第三章）。

### 4.5 下载评测数据集

AutoDL 无法直接访问 HuggingFace，需要提前下载好数据集：

```bash
export HF_ENDPOINT=https://hf-mirror.com
export HF_DATASETS_CACHE=/root/autodl-tmp/hf_cache

python3 -c "
from datasets import load_dataset
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

print('下载 hellaswag...')
load_dataset('Rowan/hellaswag', cache_dir='/root/autodl-tmp/hf_cache')

print('下载 arc_easy...')
load_dataset('allenai/ai2_arc', 'ARC-Easy', cache_dir='/root/autodl-tmp/hf_cache')

print('下载 arc_challenge...')
load_dataset('allenai/ai2_arc', 'ARC-Challenge', cache_dir='/root/autodl-tmp/hf_cache')

print('下载 gsm8k...')
load_dataset('openai/gsm8k', 'main', cache_dir='/root/autodl-tmp/hf_cache')

print('全部下载完成！')
"
```

### 4.6 运行评测

```bash
export OMP_NUM_THREADS=16
export HF_DATASETS_OFFLINE=1
export HF_DATASETS_CACHE=/root/autodl-tmp/hf_cache

lm_eval \
  --model local-completions \
  --model_args "model=qwen2.5-7b,base_url=http://localhost:8000/v1/completions,tokenizer_backend=huggingface,tokenizer=/root/autodl-tmp/models/qwen2.5-7b-instruct,num_concurrent=32,max_length=4096" \
  --tasks hellaswag,arc_easy,arc_challenge,gsm8k \
  --num_fewshot 0 \
  --output_path /root/autodl-tmp/results/lm_eval_baseline \
  --log_samples
```

> ⚠️ **踩坑：为什么不用 `openai-chat-completions` 后端**
>
> HellaSwag、ARC 这类选择题需要计算每个选项的 loglikelihood（对数概率），
> 而 `openai-chat-completions` 接口不支持返回 prompt logprobs，直接报错：
> ```
> NotImplementedError: Loglikelihood is not supported for chat completions
> ```
> 必须改用 `local-completions` 后端，走 `/v1/completions` 接口才能拿到 logprobs。

> ⚠️ **踩坑：为什么不加 `--apply_chat_template`**
>
> 本文所有任务均**不加** `--apply_chat_template`，原因如下：
>
> **HellaSwag / ARC（续写式选择题）：**
> 加了 template 会把问题包装成对话格式，导致模型在 "assistant" 角色下计算出的选项概率分布异常，分数显著偏低。实测对比：
>
> |  | 不加 template | 加 template |
> |---|---|---|
> | HellaSwag acc_norm | 80.5% | 65.3% |
> | ARC-Easy acc_norm | 81.0% | 51.0% |
> | ARC-Challenge acc_norm | 55.5% | 43.1% |
>
> **GSM8K（生成式推理题）：**
> 直觉上对话模型加 template 应该更自然，但实测结果相反。加了 template 后模型进入对话风格，输出引入更多口语化表达，干扰了答案提取逻辑，分数反而下降：
>
> |  | 不加 template | 加 template |
> |---|---|---|
> | GSM8K flexible-extract | **71.3%** | 57.7% |
> | GSM8K strict-match | 0.0% | 0.0% |
>
> 两类任务的原因不同，但结论一致：**统一不加 template**，后续所有优化实验保持相同设置，确保基线可比。

预计运行时间：四个任务共约 54,356 道题，`num_concurrent=32` 并发下约 **15~20 分钟**。

可以用 `nohup` 后台运行防止断连：

```bash
nohup lm_eval \
  --model local-completions \
  --model_args "model=qwen2.5-7b,base_url=http://localhost:8000/v1/completions,tokenizer_backend=huggingface,tokenizer=/root/autodl-tmp/models/qwen2.5-7b-instruct,num_concurrent=32,max_length=4096" \
  --tasks hellaswag,arc_easy,arc_challenge,gsm8k \
  --num_fewshot 0 \
  --output_path /root/autodl-tmp/results/lm_eval_baseline \
  --log_samples \
  > /root/autodl-tmp/results/lm_eval_baseline/log.txt 2>&1 &

tail -f /root/autodl-tmp/results/lm_eval_baseline/log.txt
```

### 4.7 评测结果

```
=== 精度评测基线结果（Qwen2.5-7B-Instruct，BF16，0-shot，不加 chat template）===

hellaswag:     acc_norm = 80.5% ± 0.40%
arc_easy:      acc_norm = 81.0% ± 0.81%
arc_challenge: acc_norm = 55.5% ± 1.45%
gsm8k:         flexible-extract = 71.3% ± 1.25%
```

**为什么加了 chat template 反而更差？**

HellaSwag、ARC 是**续写式任务**，评测框架的做法是把题目作为 prompt，让模型分别计算每个选项的 loglikelihood，选概率最高的那个。

不加 template 时，模型拿到的是裸文本，直接在续写分布下打分，符合任务预期：

```
[prompt] 北极熊为什么能在冷水中保持温暖？A. 毛皮颜色 B. 脚掌大小 ...
[模型续写] C. 皮下脂肪的厚度  ← 直接对选项打分
```

加了 chat template 后，同样的内容被包装成对话格式：

```
<|im_start|>user
北极熊为什么能在冷水中保持温暖？A. 毛皮颜色 B. 脚掌大小 ...<|im_end|>
<|im_start|>assistant
```

此时模型处于"assistant 回复"的上下文中，输出分布已偏移到对话风格（倾向于生成完整句子、解释性语言），而不是直接续写选项。对选项 token 计算出的 loglikelihood 因此产生偏差，导致选错答案的概率上升，分数下降。

GSM8K 虽然是生成式任务，但加了 template 后模型输出引入更多口语化表达，干扰了 flexible-extract 的数字提取逻辑，分数同样下降。

**本文的评测设置：统一不加 `--apply_chat_template`**，后续所有优化实验保持相同设置，以确保基线可比。


## 五、性能 Benchmark

精度评测衡量"模型回答对不对"，性能 benchmark 衡量"模型跑得快不快"。两者缺一不可——后续每次优化都需要同时对比这两条线，才能判断优化是否值得。

### 5.1 核心指标解释

在开始测试之前，先搞清楚每个指标的含义：

| 指标 | 全称 | 含义 |
|---|---|---|
| **TTFT** | Time to First Token | 从发送请求到收到第一个 token 的时间，影响用户"响应感" |
| **TPOT** | Time Per Output Token | 生成每个 token 的平均时间，决定输出速度 |
| **ITL** | Inter-Token Latency | 相邻两个 token 之间的时间间隔 |
| **Out_TPS** | Output Token Throughput | 系统每秒输出的 token 数（不含输入），反映用户实际感知的生成速度 |
| **Total_TPS** | Total Token Throughput | 系统每秒处理的 token 总数（含输入+输出） |
| **P50/P99** | 百分位数 | P50 是中位数，P99 是最慢的 1% 请求的值 |

> ⚠️ **Out_TPS vs Total_TPS**
>
> 本文统一使用 **Out_TPS** 作为吞吐指标，即系统每秒实际输出的 token 数。
> Total_TPS 包含输入 token，数值更大但不反映用户看到的生成速度，两者不可混用。

用户的完整等待时间：

```
端到端延迟 = TTFT + TPOT × 输出 token 数

例：输出 100 个 token，TTFT P99=293ms，TPOT P50=24ms
端到端延迟 = 293 + 24 × 100 = 2693ms ≈ 2.7 秒
```

> 💡 **TTFT 包含排队时间**
>
> TTFT = 排队等待 + Prefill 计算，高并发时排队时间可能占 TTFT 的 90% 以上。
> 这也是为什么高并发下 TTFT 会急剧恶化，而 TPOT 变化相对平稳。

### 5.2 benchmark 工具：vllm bench serve

vLLM 自带 benchmark 工具，使用 ShareGPT 数据集模拟真实对话流量。

> 💡 **为什么用 ShareGPT？**
>
> ShareGPT 是真实用户与 ChatGPT 的对话记录，prompt 长度分布贴近生产环境，
> 比随机生成的数据集更能反映真实性能。

### 5.3 关键参数说明

```
--request-rate   每秒发送请求数（Poisson 分布），模拟真实流量到达
--max-concurrency  同时在飞的最大请求数，超出则在客户端排队
```

两者的区别：

```
request-rate = 餐厅每分钟来几桌客人
max-concurrency = 餐厅同时能服务几桌

rate=inf + conc=1  → 所有请求立即到达，但串行处理 → 测单请求极限速度
rate=inf + conc=32 → 所有请求立即到达，32 个并发 → 测系统吞吐天花板
rate=4  + conc=32  → 模拟每秒 4 个请求的真实负载
```

> 💡 **max-concurrency 是客户端限制**
>
> `max-concurrency` 控制的是客户端同时在飞的 HTTP 请求数，而非 vLLM server 内部的实际并发。
> vLLM 内部会做 continuous batching，实际处理的并发可能高于设定值，
> 这也是为什么实验数据里 `Peak_Conc` 会超过 `max-concurrency` 的设定——这是正常现象，不是参数没生效。

### 5.4 基线测试

先跑一次基准测试：

```bash
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

vllm bench serve \
    --backend openai-chat \
    --base-url http://localhost:8000 \
    --endpoint /v1/chat/completions \
    --model qwen2.5-7b \
    --tokenizer /root/autodl-tmp/models/qwen2.5-7b-instruct \
    --dataset-name sharegpt \
    --dataset-path /root/autodl-tmp/datasets/sharegpt.json \
    --num-prompts 200 \
    --request-rate 4 \
    --max-concurrency 16 \
    --save-result \
    --result-dir /root/autodl-tmp/results/perf_baseline
```

> ⚠️ **踩坑：bench serve 的三个坑**
>
> **坑 1：`--base-url` 不能加路径**
> ```bash
> # 错误
> --base-url http://localhost:8000/v1/chat/completions
> # 正确
> --base-url http://localhost:8000
> ```
> vLLM 内部会把 `base_url + endpoint` 拼接，多加路径会导致 URL 错误。
>
> **坑 2：必须显式传 `--endpoint`**
> ```bash
> # openai-chat 后端默认 endpoint 是 /v1/completions（错误）
> # 必须手动指定
> --endpoint /v1/chat/completions
> ```
>
> **坑 3：`--model` 要用 server 启动时的别名**
> ```bash
> # 错误（用路径）
> --model /root/autodl-tmp/models/qwen2.5-7b-instruct
> # 正确（用 --served-model-name 设置的别名）
> --model qwen2.5-7b
> ```

基线测试结果：

```
============ Serving Benchmark Result ============
Successful requests:                     200
Failed requests:                         0
Request throughput (req/s):              2.64
Output token throughput (tok/s):         558.58
Total token throughput (tok/s):          1209.61
---------------Time to First Token----------------
Mean TTFT (ms):                          127.67
Median TTFT (ms):                        113.43
P99 TTFT (ms):                           293.48
-----Time per Output Token (excl. 1st token)------
Mean TPOT (ms):                          23.91
Median TPOT (ms):                        23.87
P99 TPOT (ms):                           34.38
==================================================
```

### 5.5 参数扫描实验

单次测试只能反映某个负载下的性能，要全面了解系统行为需要做参数扫描。

**实验组 A：固定并发 = 32，扫描请求速率**

目的：找到吞吐饱和点和延迟开始恶化的拐点。

**实验组 B：固定速率 = inf，扫描并发数**

目的：找到系统吞吐天花板和单请求速度极限。

使用以下脚本批量运行：

```bash
#!/bin/bash
mkdir -p /root/autodl-tmp/results/sweep

COMMON_ARGS="
    --backend openai-chat
    --base-url http://localhost:8000
    --endpoint /v1/chat/completions
    --model qwen2.5-7b
    --tokenizer /root/autodl-tmp/models/qwen2.5-7b-instruct
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
        --result-dir /root/autodl-tmp/results/sweep \
        --result-filename "expA_rate${rate}_conc32.json"
    sleep 5
done

echo "=== 实验组 B：扫描 max-concurrency ==="
for conc in 1 4 8 16 32 64 128; do
    vllm bench serve $COMMON_ARGS \
        --request-rate inf \
        --max-concurrency $conc \
        --result-dir /root/autodl-tmp/results/sweep \
        --result-filename "expB_rateinf_conc${conc}.json"
    sleep 5
done
```

### 5.6 实验结果分析

**实验组 A 结果：**

| Rate | TTFT P50 | TTFT P99 | TPOT P50 | Out_TPS (tok/s) |
|---|---|---|---|---|
| 1 | 73 ms | 236 ms | 20.4 ms | 202 |
| 2 | 113 ms | 290 ms | 22.1 ms | 385 |
| 4 | 100 ms | 327 ms | 24.2 ms | 695 |
| 8 | 100 ms | 334 ms | 26.5 ms | 926 |
| 16 | 111 ms | 348 ms | 27.0 ms | 967 |
| inf | 139 ms | **1213 ms** | 26.9 ms | 979 |

**关键发现 1：输出吞吐在 rate=8 附近饱和**

```
rate 1  →  202 tok/s
rate 8  →  926 tok/s  （↑358%）
rate 16 →  967 tok/s  （↑4.4%，几乎不涨了）
rate inf →  979 tok/s  （↑1.2%）
```

rate ≥ 8 之后 GPU 已经被压满，再加流量吞吐不再增长。

**关键发现 2：rate=inf 时 TTFT P99 炸了**

TTFT P99 从 rate=16 时的 348ms 跳到 rate=inf 时的 1213ms，**暴涨 3.5 倍**。

原因是请求全部同时到达，队列瞬间堆积，后到的请求需要等前面的全部处理完才能开始 prefill。这是经典的**排队论拐点**现象。

**实验组 B 结果：**

| Conc | TTFT P50 | TTFT P99 | TPOT P50 | TPOT P99 | Out_TPS (tok/s) |
|---|---|---|---|---|---|
| 1 | 41 ms | 196 ms | **19.7 ms** | 19.8 ms | 50 |
| 4 | 92 ms | 234 ms | 20.0 ms | 25.8 ms | 190 |
| 8 | 94 ms | 355 ms | 21.4 ms | 27.2 ms | 345 |
| 16 | 83 ms | 787 ms | 23.4 ms | 35.2 ms | 595 |
| 32 | 127 ms | 1352 ms | 26.8 ms | 60.2 ms | 978 |
| 64 | 212 ms | 2018 ms | 34.4 ms | **165 ms** | 1341 |
| 128 | 892 ms | 3598 ms | 51.9 ms | **387 ms** | 1583 |

**关键发现 3：单请求 TPOT 接近物理极限**

conc=1 时 TPOT P50 = **19.7ms**，对应 51 tok/s。

理论下限计算：
```
Qwen2.5-7B BF16 权重 = 7 × 10⁹ × 2 bytes ≈ 14 GB
RTX 3090 显存带宽 = 936 GB/s
理论最快 TPOT = 14 GB ÷ 936 GB/s ≈ 15 ms
```

实测 19.7ms vs 理论 15ms，**显存带宽利用率 MBU = 15 ÷ 19.7 ≈ 76%**，已经非常接近物理极限。

**关键发现 4：conc=32→64 是 TPOT P99 的质变拐点**

conc=32 时 TPOT P99 为 60ms，conc=64 时暴涨至 **165ms**，conc=128 时进一步恶化至 **387ms**。这个非线性暴涨说明 conc=32 是本硬件配置下 decode 质量的实际边界——超过后 KV cache 内存压力急剧上升，每个请求分到的计算资源显著减少，TPOT 开始失控。这也从数据上印证了"生产甜点区 conc=8~16"的结论。

**关键发现 5：系统吞吐 vs 用户体验的 trade-off**

| Conc | Out_TPS (tok/s) | TTFT P99 | TPOT P99 | 用户体验 |
|---|---|---|---|---|
| 1 | 50 | 196 ms | 20 ms | 极佳，但 GPU 利用率低 |
| 8 | 345 | 355 ms | 27 ms | 良好 ✅ |
| 32 | 978 | 1352 ms | 60 ms | 吞吐高但用户开始感知卡顿 |
| 128 | 1583 | 3598 ms | 387 ms | 吞吐最高，但用户体验灾难 |

这是 LLM serving 最核心的矛盾：**提高并发能提升系统吞吐，但会损害每个用户的体验**。

**关键发现 6：并发越高，系统越快，用户越慢**

从实验组 B 的 `Duration` 数据可以直接看到这个现象：

| Conc | Duration (s) | TTFT P99 | TPOT P99 |
|---|---|---|---|
| 1 | 857 s | 196 ms | 20 ms |
| 8 | 125 s | 355 ms | 27 ms |
| 32 | 44 s | 1352 ms | 60 ms |
| 128 | 27 s | 3598 ms | 387 ms |

同样是处理 200 个请求，conc=128 只需 27 秒，是 conc=1 的 **32 倍速**——但此时每个用户等第一个 token 的 P99 已经长达 3.6 秒，生成每个 token 也要等 387ms。

原因是两个效应叠加：

```
并发↑ → GPU 每次 decode 处理更多请求 → 单次计算的"摊销成本"降低 → 系统总耗时↓
并发↑ → 每个请求抢占更少的 KV cache 和算力 → 单请求等待时间↑
```

这个矛盾无法通过软件调参消除，是 LLM serving 的结构性问题。实际部署时需要根据业务场景做取舍：**批量离线任务**（文档处理、数据标注）可以拉满并发榨干吞吐；**实时对话**则必须限制并发保护用户体验。

### 5.7 生产部署的甜点区

根据实验结果，定义两种 SLO（服务等级目标）下的最佳参数：

| SLO 标准 | 满足条件 | 最佳 rate | Goodput |
|---|---|---|---|
| 严格（chatbot 实时对话） | TTFT P99 < 300ms，TPOT P99 < 40ms | rate = 2 | 385 tok/s |
| 宽松（普通服务） | TTFT P99 < 500ms，TPOT P99 < 60ms | rate = 16 | 967 tok/s |

> 💡 **Goodput（有效吞吐）**
>
> 不满足 SLO 的请求对用户毫无意义。rate=inf 看起来 Out_TPS 最高（979 tok/s），
> 但在严格 SLO 下 TTFT P99 = 1213ms 远超 300ms 上限，实际 Goodput = 0。
> **Goodput = 满足 SLO 前提下的有效吞吐**，才是生产环境真正关心的指标。

### 5.8 基线数据汇总

至此，建立了完整的性能基线：

```
=== 基线 v0：Qwen2.5-7B BF16，无优化 ===
硬件:           RTX 3090 24GB
模型:           Qwen2.5-7B-Instruct (BF16)
TTFT P50:       113 ms
TTFT P99:       293 ms
TPOT P50:       23.9 ms（理论下限 15ms，MBU ≈ 76%）
TPOT P99:       34.4 ms
输出吞吐:       558 tok/s（rate=4，conc=16，Out_TPS）
吞吐趋于饱和:   ~979 tok/s（rate=inf，conc=32，Out_TPS）
TPOT P99 拐点:  conc=32→64（60ms 暴涨至 165ms）
生产甜点区:     rate=4~8，conc=8~16
```

这份基线数据将作为后续所有优化实验的对照组。

## 六、总结与下一步计划

### 6.1 本文完成的工作

本文从零开始，在一台 RTX 3090 上完成了 Qwen2.5-7B-Instruct 的完整部署和基线评测：

| 步骤 | 内容 | 结果 |
|---|---|---|
| 环境部署 | AutoDL + vLLM + ModelScope | ✅ 完成 |
| 精度基线 | lm-eval + HellaSwag/ARC/GSM8K | ✅ 完成 |
| 性能基线 | vllm bench + ShareGPT | ✅ 完成 |
| 参数扫描 | 扫描 rate 和 concurrency | ✅ 完成 |

**踩过的坑：**

1. cuDNN 版本冲突（cu12 和 cu13 共存）→ 删除旧版本
2. lm-eval 后端选错（chat-completions 不支持 loglikelihood）→ 改用 local-completions
3. lm-eval 未设置 `num_concurrent`，默认串行发请求，GPU 利用率极低 → 加上 `num_concurrent=32`，评测时间从 1~2 小时压缩到 10~20 分钟
4. vllm bench 的 URL 拼接规则 → base-url 不能带路径，endpoint 要显式传
5. HuggingFace 数据集下载失败 → 提前下载 + 设置 OFFLINE 模式

### 6.2 关键结论

**精度方面（0-shot，不加 chat template）：**

```
HellaSwag     acc_norm = 80.5%
ARC-Easy      acc_norm = 81.0%
ARC-Challenge acc_norm = 55.5%
GSM8K         flexible-extract = 71.3%
```

**性能方面：**

```
单请求 TPOT = 19.7ms（MBU ≈ 76%，理论下限 15ms）
输出吞吐天花板  = ~979 tok/s（Out_TPS，rate=inf，conc=32）
TPOT P99 拐点  = conc=32→64（60ms 暴涨至 165ms）
生产甜点区     = rate=4~8，conc=8~16
```

**最重要的洞察：**

TPOT 已逼近显存带宽极限，说明**纯软件调参已经到顶**，想进一步提速必须走量化路线——减少每次 decode 需要搬运的权重字节数，从根本上降低 TPOT。

### 6.3 下一步计划

接下来将围绕这份基线数据，逐步做优化对比实验，**每次优化都同时测精度和性能，量化收益和代价**。

计划的实验序列：

| 实验 | 方法 | 预期收益 |
|---|---|---|
| **实验 1** | AWQ INT4 量化 | TPOT 减半，吞吐翻倍 |
| **实验 2** | KV Cache 深度分析 | 理解吞吐翻倍的根本原因 |
| **实验 3** | Prefix Caching | 降低 TTFT |
| **实验 4** | 投机采样 | 低并发 TPOT 加速 |

最终目标：在保证精度损失可控的前提下，找到 RTX 3090 + 7B 的最优部署配置。

### 6.4 方法论总结

做 AI Infra 优化的标准流程：

```
建立基线
   ↓
提出优化方案
   ↓
实施优化
   ↓
双线评测（精度 + 性能）
   ↓
决策：收益 > 代价 → 采纳，否则回退
   ↓
记录结果，继续下一个优化
```

**核心原则：没有免费的午餐。** 每一个性能优化几乎都有精度代价，必须用数据说话，而不是凭感觉判断值不值。

---

> 本系列下一篇：[AWQ INT4 量化实验：TPOT 从 19.7ms 到 10ms 的优化过程]（待更新）

---

**参考资料：**

- [vLLM 官方文档](https://docs.vllm.ai)
- [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180)（SOSP 2023）
- [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)
- [AWQ: Activation-aware Weight Quantization](https://arxiv.org/abs/2306.00978)（MLSys 2024 Best Paper）