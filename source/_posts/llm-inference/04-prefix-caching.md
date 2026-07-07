---
title: LM推理优化实战(四):Prefix Caching原理详解与TTFT性能实测
date: 2026-04-04
mathjax: true
categories:
    llm-inference
tags:
---

## 一、前言

前两篇文章分别建立了 BF16 基线和 AWQ INT4 量化实验，也验证了 KV Cache 是高并发场景下的显存瓶颈，以及 AWQ 量化通过释放 KV Cache 空间实现吞吐翻倍的根本原因。本文在此基础上，继续探索另一个常见但容易被忽视的推理优化手段——Prefix Caching。

在实际生产中，大量请求共享相同的 system prompt 或上下文前缀，而这部分 KV 每次都被重复计算。Prefix Caching 的思路是把这部分计算结果缓存下来跨请求复用，直接减少 Prefill 开销，降低 TTFT。

本文通过两个实验回答以下问题：

- Prefix Caching 能将 TTFT 降低多少？命中率如何？
- 共享前缀越长，收益是否线性增长？上限在哪里？

先看结论：

| 实验 | 关键发现 |
|---|---|
| 实验一：开关对比（~1500 tokens 前缀） | TTFT 降低 18.5%，命中率 99.2% |
| 实验二：前缀长度梯度（353～3961 tokens） | TTFT 降幅从 67.1% 增长至 92.6%，斜率下降 96.7% |

**最重要的洞察**：Prefix Caching 的收益与共享前缀长度高度相关——前缀越长，可复用的 Prefill 计算越多，TTFT 降幅越大。在 RAG、Agent、长 System Prompt 等典型生产场景中，这项默认开启的优化往往能将首 Token 延迟压缩 80% 以上。

## 二、Prefix Caching

### 2.1 什么是 Prefix Caching

在实际生产环境中，大量请求往往共享相同的前缀。比如一个客服机器人，所有用户的请求都会带上同一段 system prompt：

```
请求 A：[你是一个专业的客服助手，请遵循以下规则...] + [我的订单什么时候发货？]
请求 B：[你是一个专业的客服助手，请遵循以下规则...] + [如何申请退款？]
请求 C：[你是一个专业的客服助手，请遵循以下规则...] + [你们的营业时间是？]
         ↑ 完全相同的前缀                              ↑ 不同的用户输入
```

没有 Prefix Caching 时，每个请求都要在 Prefill 阶段重新计算一遍 system prompt 的 KV，这是纯粹的重复计算。Prefix Caching 的思路很简单：**把首次计算好的前缀 KV Cache 保留下来，后续遇到相同前缀时直接复用，跳过重复的 Prefill 计算。**

### 2.2 工作原理

整个过程分为三步：

**第一步：首次请求，计算并缓存**

请求 A 到达时，vLLM 正常执行 Prefill，计算所有 token 的 $K$、$V$，并将前缀部分的 Block **计算 hash 值后标记为"可复用"**，存入缓存池：

```
请求 A Prefill：
  [system prompt: 1488 tokens] + [用户问题: 16 tokens]
  → 计算全部 1504 tokens 的 KV
  → system prompt 的 93 个 Block 被标记 hash，存入缓存
```

**第二步：后续请求，命中缓存**

请求 B 到达时，vLLM 对前缀逐 Block 计算 hash，发现与缓存匹配，直接跳过这部分 Prefill：

```
请求 B Prefill：
  [system prompt: 1488 tokens] → hash 匹配！复用已有的 93 个 Block
  [用户问题: 13 tokens]        → 只需计算这 13 个 token 的 KV
```

**第三步：缓存保留与淘汰**

请求结束后，普通 KV Cache 被释放，但 prefix Block 保留在缓存池中，等待后续请求复用。当空间不足时，按 LRU 策略淘汰最久未使用的 prefix 缓存。

### 2.3 Prefix Cache 在 KV Cache 中的位置

回顾 PagedAttention 的 Block 结构，Prefix Cache 覆盖的是 KV Cache 中前缀对应的那些 Block：

```
一个完整请求的 KV Cache 布局（block_size=16）：

  Block 0 ~ Block 92：system prompt 的 KV（1488 tokens）← 缓存，可跨请求复用
  Block 93 ~ Block 94：用户问题的 KV（16 tokens）       ← 每个请求独有
  Block 95 ~ ...：    生成输出的 KV（逐步增长）          ← 每个请求独有
```

当多个请求共享同一 system prompt 时，它们的 Block 0~92 **指向同一组物理 Block**，不会重复存储：

```
请求 A：[Block 0~92（共享）] → [Block 100~102（独有）]
请求 B：[Block 0~92（共享）] → [Block 200~203（独有）]
请求 C：[Block 0~92（共享）] → [Block 300~301（独有）]
              ↑ 只存一份，节省了 2 × 93 = 186 个 Block 的显存
```

### 2.4 适用场景

Prefix Caching 的收益取决于**共享前缀的长度**和**请求的重复率**。

| 场景 | 共享前缀 | 前缀长度 | 收益 |
|---|---|---|---|
| 客服 / 助手类应用 | 固定 system prompt | 几百～几千 tokens | 高，几乎所有请求命中 |
| RAG | 相同检索文档 | 几千 tokens | 中高，同一文档的多个问题命中 |
| 代码补全 | 同一文件上下文 | 几百～几千 tokens | 中，同一文件的连续补全命中 |
| 多轮对话 | 历史对话记录 | 逐轮增长 | 中，每轮新增部分无法命中 |
| 随机独立请求 | 无共享前缀 | 0 | 无收益 |

收益最大的场景是"长 system prompt + 大量短问题"——前缀越长，跳过的 Prefill 计算越多，TTFT 节省越明显。

vLLM 默认开启 Prefix Caching（`enable_prefix_caching=True`），无需额外配置。

---

## 三、实验一：Prefix Caching 开关对比

### 3.1 实验设计

**目标：** 通过控制变量，量化 Prefix Caching 对 TTFT 的影响。

| 项目 | 设置 |
|---|---|
| 模型 | Qwen2.5-7B-Instruct |
| System Prompt | 约 1488 tokens（固定规则说明重复 20 次） |
| 用户问题 | 8 个不同的历史问题 |
| 输出长度 | 64 tokens |
| 对照组 | 开启 / 关闭 Prefix Caching |
| 观测指标 | TTFT |

启动命令：

```bash
# 开启 Prefix Caching（vLLM 默认）
vllm serve /root/autodl-tmp/models/qwen2.5-7b-instruct \
    --served-model-name qwen2.5-7b \
    --gpu-memory-utilization 0.85 --max-model-len 4096

# 关闭 Prefix Caching
vllm serve /root/autodl-tmp/models/qwen2.5-7b-instruct \
    --served-model-name qwen2.5-7b \
    --gpu-memory-utilization 0.85 --max-model-len 4096 \
    --no-enable-prefix-caching
```

### 3.2 测试脚本

脚本的核心逻辑是顺序发送 8 个请求，每次携带完全相同的 system prompt，记录从发出请求到收到完整响应的时间（即 TTFT）。同时从 `/metrics` 接口读取 `prefix_cache_queries_total` 和 `prefix_cache_hits_total` 两个计数器，计算命中率。实验开始前先读取一次初始计数，结束后取差值，排除历史请求的干扰。

<details>
<summary style="color:#999; font-style:italic;">点击查看完整脚本</summary>
```python
# prefix_cache_test.py
import requests
import time

SYSTEM_PROMPT = """你是一个专业的AI助手。你需要遵循以下规则：
1. 回答必须准确、客观、有依据
2. 如果不确定，要明确说明
3. 回答要结构化，使用适当的标题和段落
4. 对于技术问题，要给出代码示例
5. 对于历史问题，要注明时间和来源
""" * 20  # 重复 20 次，约 1488 tokens

def send_request(question):
    start = time.time()
    r = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json={
            "model": "qwen2.5-7b",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            "max_tokens": 64,
            "temperature": 0
        }
    )
    elapsed = time.time() - start
    data = r.json()
    return elapsed * 1000, data["usage"]["prompt_tokens"]

def get_prefix_cache_stats():
    r = requests.get("http://localhost:8000/metrics")
    queries, hits = 0.0, 0.0
    for line in r.text.split("\n"):
        if line.startswith("vllm:prefix_cache_queries_total{"):
            queries = float(line.split("} ")[1])
        if line.startswith("vllm:prefix_cache_hits_total{"):
            hits = float(line.split("} ")[1])
    return queries, hits

questions = [
    "秦始皇统一六国的过程是怎样的？",
    "汉武帝的主要功绩有哪些？",
    "唐朝的开元盛世是怎么回事？",
    "宋朝的经济发展有哪些特点？",
    "明朝的海禁政策是什么？",
    "清朝的洋务运动取得了哪些成果？",
    "辛亥革命的意义是什么？",
    "五四运动的背景和影响？",
]

init_queries, init_hits = get_prefix_cache_stats()

for i, q in enumerate(questions):
    elapsed, tokens = send_request(q)
    print(f"{i+1:>4} {q[:18]:<20} {elapsed:>10.1f} ms  {tokens:>6} tokens")

final_queries, final_hits = get_prefix_cache_stats()
total_new_queries = final_queries - init_queries
total_new_hits = final_hits - init_hits
hit_rate = total_new_hits / total_new_queries * 100 if total_new_queries > 0 else 0
print(f"\n命中率: {hit_rate:.1f}%，节省 {total_new_hits:.0f} tokens 的 KV 计算")
```
</details>

### 3.3 实验结果

**组一：开启 Prefix Caching（vLLM 默认）**

| 序号 | 问题 | TTFT (ms) | Prompt Tokens |
|---|---|---|---|
| 1 | 秦始皇统一六国的过程是怎样的？ | 1300.2 | 1504 |
| 2 | 汉武帝的主要功绩有哪些？ | 1269.3 | 1501 |
| 3 | 唐朝的开元盛世是怎么回事？ | 1269.9 | 1500 |
| 4 | 宋朝的经济发展有哪些特点？ | 1271.6 | 1500 |
| 5 | 明朝的海禁政策是什么？ | 1275.2 | 1500 |
| 6 | 清朝的洋务运动取得了哪些成果？ | 1275.5 | 1502 |
| 7 | 辛亥革命的意义是什么？ | 1275.5 | 1499 |
| 8 | 五四运动的背景和影响？ | 1276.5 | 1500 |

Prefix Cache 命中率：**99.2%**，节省 11904 tokens 的 KV 计算。

**组二：关闭 Prefix Caching**

| 序号 | 问题 | TTFT (ms) | Prompt Tokens |
|---|---|---|---|
| 1 | 秦始皇统一六国的过程是怎样的？ | 1666.4 | 1504 |
| 2 | 汉武帝的主要功绩有哪些？ | 1561.1 | 1501 |
| 3 | 唐朝的开元盛世是怎么回事？ | 1560.1 | 1500 |
| 4 | 宋朝的经济发展有哪些特点？ | 1565.0 | 1500 |
| 5 | 明朝的海禁政策是什么？ | 1566.9 | 1500 |
| 6 | 清朝的洋务运动取得了哪些成果？ | 1565.8 | 1502 |
| 7 | 辛亥革命的意义是什么？ | 1561.3 | 1499 |
| 8 | 五四运动的背景和影响？ | 1556.5 | 1500 |

Prefix Cache 命中率：**0%**，每次 Prefill 都重新计算全部 1500 tokens 的 KV。

### 3.4 结果分析

去掉第一个请求后，对比第 2~8 个请求的平均 TTFT：

| 配置 | 第 2~8 次平均 TTFT | 差值 | 降幅 |
|---|---|---|---|
| 关闭 Prefix Cache | 1562 ms | — | — |
| 开启 Prefix Cache | 1274 ms | -288 ms | **-18.5%** |

**为什么第一个请求有差异？**

关闭 cache 时，第 1 次（1666ms）比后续（1562ms）慢约 100ms，是 CUDA kernel 首次编译的预热开销，与 prefix cache 无关。开启 cache 时，第 1 次（1300ms）比关闭时快很多，原因是实验开始前已积累了 10416 次命中记录——同一 system prompt 已在历史请求中被缓存，第一个请求同样命中了缓存，没有出现冷启动延迟。

**为什么 TTFT 没有降低 99%？**

每次请求中，1488 tokens 的 system prompt 命中缓存，只有约 12~16 tokens 的用户问题需要重新计算 KV，跳过的 Prefill 比例约为：

$$\frac{1488}{1504} \approx 98.9\%$$

但 TTFT 不只是 Prefill，还包含排队等待和 Decode 第一个 token 的固定开销：

```
TTFT = 排队等待 + Prefill + Decode 第 1 token

关闭 cache：1562 ms = 排队 + 1500 tokens Prefill + decode
开启 cache：1274 ms = 排队 +   12 tokens Prefill + decode
           差值 288 ms ≈ 1488 tokens 的 Prefill 计算时间
```

节省的 288ms 就是 1488 tokens Prefill 的时间，剩余的 ~1274ms 是排队和 decode 第一个 token 的固定开销，Prefix Caching 无法优化这部分。

> **Prefix Caching 的收益随前缀长度线性增长。** 本实验的 system prompt 约 1488 tokens，TTFT 降低 288ms。如果前缀更长（如 RAG 场景下的 4000 tokens 检索文档），节省的时间会等比例增加，TTFT 降幅可达 50% 以上。这正是下一个实验的验证目标。

---

## 四、实验二：前缀长度对收益的影响

### 4.1 实验设计

实验一验证了 Prefix Caching 的有效性，但没有回答：**Prefix 越长，收益是否线性增长？**

为此，构造 5 种不同长度的 system prompt，分别在开启和关闭 Prefix Cache 两种配置下测量 TTFT。

| 项目 | 设置 |
|---|---|
| 模型 | Qwen2.5-7B-Instruct |
| Prefix 长度 | 256 / 512 / 1024 / 2048 / 3072 tokens |
| 输出长度 | 1 token（压缩 Decode 开销，使 TTFT ≈ Prefill 时间） |
| 用户问题 | 固定（约 15 tokens） |
| 每组重复次数 | 5（取均值） |

设置 `max_tokens=1` 是为了尽量隔离 Decode 阶段的影响，使测量结果主要反映 Prefill 开销的变化。

### 4.2 测试脚本

system prompt 通过重复同一段约 64 tokens 的规则说明来构造，用重复次数控制前缀长度。对于开启 Prefix Cache 的实验，每种前缀长度首先发送一次冷启动请求构建缓存，随后连续发 5 次并取均值；对于关闭 Prefix Cache 的实验，每次都是完整 Prefill。

<details>
<summary style="color:#999; font-style:italic;">点击查看完整脚本</summary>
```python
# prefix_length_exp.py
import argparse
import json
import time
from pathlib import Path
from statistics import mean

import requests

BASE_URL = "http://localhost:8000"
MODEL_NAME = "qwen2.5-7b"
RESULTS_DIR = Path("/root/autodl-tmp/results/prefix_length_exp")

BASE_UNIT = (
    "你是一个专业的AI助手。你需要遵循以下规则：\n"
    "1. 回答必须准确、客观、有依据。\n"
    "2. 如果不确定，要明确说明不确定的原因。\n"
    "3. 回答要结构化，使用适当的标题和段落。\n"
    "4. 对于技术问题，要给出可运行的代码示例。\n"
    "5. 对于历史问题，要注明具体时间节点和史料来源。\n"
)
TOKENS_PER_UNIT = 64
TARGET_PREFIX_TOKENS = [256, 512, 1024, 2048, 3072]
USER_QUESTION = "请简要介绍一下汉武帝的主要历史功绩。"
REPEAT_PER_LENGTH = 5

def build_system_prompt(target_tokens: int) -> str:
    repeat = max(1, round(target_tokens / TOKENS_PER_UNIT))
    return BASE_UNIT * repeat

def send_request(system_prompt: str) -> tuple[float, int]:
    start = time.perf_counter()
    resp = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": USER_QUESTION},
            ],
            "max_tokens": 1,
            "temperature": 0,
        },
        timeout=60,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    prompt_tokens = resp.json()["usage"]["prompt_tokens"]
    return elapsed_ms, prompt_tokens

def warmup():
    print("预热中...")
    send_request("你好")
    time.sleep(1)
    print("预热完成。\n")

def run_experiment(mode: str):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    warmup()
    results = []

    for target in TARGET_PREFIX_TOKENS:
        system_prompt = build_system_prompt(target)
        print(f"=== 前缀目标 {target} tokens ===")

        if mode == "cache_on":
            ttft, pt = send_request(system_prompt)
            print(f"  [冷启动] TTFT={ttft:.1f}ms  prompt_tokens={pt}")

        ttfts = []
        for i in range(REPEAT_PER_LENGTH):
            ttft, pt = send_request(system_prompt)
            ttfts.append(ttft)
            print(f"  [第{i+1}次] TTFT={ttft:.1f}ms  prompt_tokens={pt}")
            time.sleep(0.3)

        avg = mean(ttfts)
        record = {
            "target_prefix_tokens": target,
            "mode": mode,
            "avg_ttft_ms": round(avg, 1),
            "min_ttft_ms": round(min(ttfts), 1),
            "max_ttft_ms": round(max(ttfts), 1),
        }
        results.append(record)
        print(f"  → 平均 TTFT: {avg:.1f}ms\n")

    out_path = RESULTS_DIR / f"results_{mode}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"结果已保存至 {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", choices=["on", "off"], required=True)
    args = parser.parse_args()
    run_experiment("cache_on" if args.cache == "on" else "cache_off")
```
</details>

### 4.3 实验结果

| Prompt Tokens | 关闭 Cache TTFT (ms) | 开启 Cache TTFT (ms) | 节省 (ms) | 降幅 |
|---|---:|---:|---:|---:|
| 353  | 111.4 | 36.7 | 74.7  | 67.1% |
| 681  | 168.7 | 43.0 | 125.7 | 74.5% |
| 1337 | 279.4 | 45.1 | 234.3 | 83.9% |
| 2649 | 574.0 | 56.1 | 517.9 | 90.2% |
| 3961 | 852.7 | 62.8 | 789.9 | 92.6% |

![Impact of Prefix Length on TTFT](images/llm-inference/prefix_length_exp.png)

图 (a) 展示了 TTFT 随 Prompt Tokens 的变化趋势。关闭 Prefix Cache 时（蓝色实线），TTFT 从 353 tokens 下的 111ms 线性增长至 3961 tokens 下的 853ms，绿色虚线拟合斜率为 207.6 ms/k tokens，线性关系拟合极好，说明 Prefill 计算量与输入长度严格正比。开启 Prefix Cache 后（橙色实线），TTFT 几乎没有随前缀长度变化，始终维持在 37~63ms 的低位，粉色虚线拟合斜率仅 6.9 ms/k tokens，两条曲线的差距随前缀增长持续扩大。

图 (b) 展示了 TTFT 降幅随前缀长度的变化。在 353 tokens 时降幅已达 67.1%，随前缀增长单调递增，到 3961 tokens 时达到 92.6%。降幅的持续增长反映了一个事实：前缀越长，被命中缓存省掉的计算量越大，而不可优化的固定开销（排队 + decode 第一个 token）在 TTFT 中的占比越来越低。

### 4.4 线性拟合分析

对实验数据进行线性回归，以 $L$（单位：千 tokens）为自变量：

**关闭 Prefix Cache：**

$$TTFT_{\text{off}} = 207.6 \times L + 38.1 \quad \text{(ms)}$$

每增加 1000 tokens 的前缀，TTFT 平均增加约 207.6 ms。

**开启 Prefix Cache：**

$$TTFT_{\text{on}} = 6.9 \times L + 34.3 \quad \text{(ms)}$$

每增加 1000 tokens 的前缀，TTFT 仅增加约 6.9 ms。斜率下降幅度：

$$1 - \frac{6.9}{207.6} = 96.7\%$$

原理很直接：设共享前缀长度为 $N$，用户输入长度为 $U$。关闭 Cache 时 Prefill 开销正比于 $N+U$；开启 Cache 后只需计算 $U$ 部分，$N$ 已完全命中缓存。因此关闭 Cache 的 TTFT 随 $N$ 线性增长，而开启 Cache 的 TTFT 对 $N$ 几乎不敏感。

两条拟合直线的截距接近（38.1 ms vs 34.3 ms），反映的正是那部分无法被 Prefix Caching 优化的固定开销——排队等待和 decode 第一个 token 的时间在两种配置下基本相同。

---

## 五、总结

### 5.1 本文完成的工作

| 内容 | 结果 |
|---|---|
| Prefix Caching 原理解析 | ✅ 完成（hash 机制、Block 复用、LRU 淘汰） |
| 实验一：开关对比（~1500 tokens 前缀） | ✅ TTFT 降低 18.5%，命中率 99.2% |
| 实验二：前缀长度梯度实验 | ✅ 验证线性关系，4000 tokens 前缀下降幅 92.6% |
| 线性拟合分析 | ✅ OFF 斜率 207.6 ms/k tok，ON 斜率 6.9 ms/k tok |

### 5.2 关键结论

**结论 1：Prefix Caching 的收益与前缀长度高度相关**

关闭 Prefix Cache 时，TTFT 随前缀长度近似线性增长（207.6 ms / 千 tokens）；开启后增长斜率下降 **96.7%**（仅 6.9 ms / 千 tokens）。在约 4000 tokens 的共享前缀下，TTFT 降幅达到 **92.6%**。

**结论 2：TTFT 降幅存在上限**

Prefix Caching 只能优化 Prefill 阶段，无法消除排队等待和 decode 第一个 token 的固定开销。两条拟合线的截距（~35ms）揭示了这个不可优化的下界。在生产环境中，系统负载越高、排队时间越长，Prefix Caching 对 TTFT 的相对贡献也会相应缩小。

**结论 3：长上下文场景是 Prefix Caching 的主战场**

```
System Prompt ~350 tokens：  TTFT 降幅 67.1%
RAG 上下文   ~4000 tokens：  TTFT 降幅 92.6%
```

Agent 系统的长指令、RAG 的检索文档、企业应用的大型 System Prompt、多轮对话的共享历史——这些场景都是 Prefix Caching 效益最显著的地方。共享前缀越长、复用次数越高，收益越大，这也解释了 vLLM 将其作为默认开启项的原因。

### 5.3 三篇文章的完整对照表

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
  严格 SLO Goodput:     826 tok/s           4547 tok/s (+450%)

Prefix Caching（本文，BF16 模型）:
  ~1500 tokens 前缀：    TTFT 降低 18.5%，命中率 99.2%
  ~4000 tokens 前缀：    TTFT 降低 92.6%
  OFF 拟合斜率：         207.6 ms / 千 tokens
  ON  拟合斜率：         6.9 ms / 千 tokens（下降 96.7%）
```

### 5.4 下一步计划

| 实验 | 方法 | 预期收益 |
|---|---|---|
| 投机采样（Speculative Decoding） | 小模型草稿 + 大模型验证，加速 decode | 低并发 TPOT 降 30~50%，精度零损失 |
| Chunked Prefill | 将长 Prefill 分块执行，与 decode 交错调度 | 降低 Prefill 对在途请求 TPOT 的干扰 |

---

> 本系列下一篇：[投机采样实验：精度零损失的加速方案]（待更新）

---

**参考资料：**

- [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180)（SOSP 2023）
- [Automatic Prefix Caching — vLLM 官方文档](https://docs.vllm.ai/en/latest/automatic_prefix_caching/apc.html)
- [vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention](https://blog.vllm.ai/2023/06/20/vllm.html)
- [SGLang: Efficient Execution of Structured Language Model Programs](https://arxiv.org/abs/2312.07104)（RadixAttention 同类机制对比参考）