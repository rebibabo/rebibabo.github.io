import argparse
import json
import time
from pathlib import Path

import requests

# ── 配置 ──────────────────────────────────────────────────────────────────────

BASE_URL = "http://localhost:8000"
MODEL_NAME = "qwen2.5-7b"
RESULTS_DIR = Path("/root/autodl-tmp/results/prefix_length_exp")

# 基础 prompt 单元（约 64 tokens），重复堆叠来控制前缀长度
BASE_UNIT = (
    "你是一个专业的AI助手。你需要遵循以下规则：\n"
    "1. 回答必须准确、客观、有依据。\n"
    "2. 如果不确定，要明确说明不确定的原因。\n"
    "3. 回答要结构化，使用适当的标题和段落。\n"
    "4. 对于技术问题，要给出可运行的代码示例。\n"
    "5. 对于历史问题，要注明具体时间节点和史料来源。\n"
)
# 每个 BASE_UNIT 约 64 tokens（tokenizer 实测）
TOKENS_PER_UNIT = 64

# 目标前缀长度梯度（tokens）：256 / 512 / 1024 / 2048 / 3072
# 对应重复次数：4 / 8 / 16 / 32 / 48
TARGET_PREFIX_TOKENS = [256, 512, 1024, 2048, 3072]

# 固定用户问题（约 15 tokens，保持不变）
USER_QUESTION = "请简要介绍一下汉武帝的主要历史功绩。"

# 每个长度的重复测量次数（取均值以消抖）
REPEAT_PER_LENGTH = 5

# ── 工具函数 ──────────────────────────────────────────────────────────────────

def build_system_prompt(target_tokens: int) -> str:
    """构造目标长度的 system prompt（通过重复 BASE_UNIT 实现）"""
    repeat = max(1, round(target_tokens / TOKENS_PER_UNIT))
    return BASE_UNIT * repeat


def send_request(system_prompt: str) -> tuple[float, int, int]:
    """
    发送一次请求，返回 (ttft_ms, prompt_tokens, completion_tokens)
    max_tokens=1 只生成 1 个 token，将 decode 开销压到最低，让 TTFT ≈ Prefill 时间
    """
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
    data = resp.json()

    prompt_tokens     = data["usage"]["prompt_tokens"]
    completion_tokens = data["usage"]["completion_tokens"]
    return elapsed_ms, prompt_tokens, completion_tokens


def get_cache_stats() -> tuple[float, float]:
    """从 /metrics 读取 prefix cache 累计 queries 和 hits"""
    resp = requests.get(f"{BASE_URL}/metrics", timeout=10)
    queries, hits = 0.0, 0.0
    for line in resp.text.splitlines():
        if line.startswith("vllm:prefix_cache_queries_total{"):
            queries = float(line.split("} ")[1])
        if line.startswith("vllm:prefix_cache_hits_total{"):
            hits    = float(line.split("} ")[1])
    return queries, hits


def warmup():
    """发一条短请求预热 CUDA kernel，避免首次编译干扰计时"""
    print("预热中（发送一条短请求）...")
    try:
        send_request("你好")
        time.sleep(1)
        print("预热完成。\n")
    except Exception as e:
        print(f"预热失败（vLLM 是否已启动？）: {e}")
        raise


# ── 主实验逻辑 ────────────────────────────────────────────────────────────────

def run_experiment(mode: str):
    """
    mode: 'cache_on' | 'cache_off'
    对每个目标前缀长度，连续发 REPEAT_PER_LENGTH 次请求，记录 TTFT。
    第 1 次请求可能是冷 cache（cache_on 模式下首次会 miss），从第 2 次开始命中。
    因此分别记录 first_ttft 和 warm_ttfts（第 2 次起的均值）。
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    warmup()

    results = []

    for target in TARGET_PREFIX_TOKENS:
        system_prompt = build_system_prompt(target)
        print(f"=== 前缀目标 {target} tokens ===")

        ttfts = []
        actual_prompt_tokens = None

        # 如果是 cache_on，第 1 次故意触发 miss，后续才是命中状态
        # 如果是 cache_off，每次都是完整 Prefill，全部记录
        for i in range(REPEAT_PER_LENGTH + 1):  # +1 为了 cache_on 的冷启动
            q_before, h_before = get_cache_stats()
            ttft, prompt_tokens, _ = send_request(system_prompt)
            q_after, h_after = get_cache_stats()

            actual_prompt_tokens = prompt_tokens
            new_hits = h_after - h_before

            if i == 0:
                label = "冷启动" if mode == "cache_on" else "第1次"
                print(f"  [{label}] TTFT={ttft:.1f}ms  prompt_tokens={prompt_tokens}  cache_hits={new_hits:.0f}")
                if mode == "cache_on":
                    # 冷启动不计入结果
                    continue
            else:
                print(f"  [第{i}次]   TTFT={ttft:.1f}ms  prompt_tokens={prompt_tokens}  cache_hits={new_hits:.0f}")

            ttfts.append(ttft)
            time.sleep(0.3)  # 避免请求堆积

        avg_ttft  = sum(ttfts) / len(ttfts)
        min_ttft  = min(ttfts)
        max_ttft  = max(ttfts)

        record = {
            "target_prefix_tokens": target,
            "actual_prompt_tokens": actual_prompt_tokens,
            "mode": mode,
            "ttfts": ttfts,
            "avg_ttft_ms": round(avg_ttft, 1),
            "min_ttft_ms": round(min_ttft, 1),
            "max_ttft_ms": round(max_ttft, 1),
        }
        results.append(record)
        print(f"  → 平均 TTFT: {avg_ttft:.1f}ms  (min={min_ttft:.1f}, max={max_ttft:.1f})\n")

    out_path = RESULTS_DIR / f"results_{mode}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"结果已保存至 {out_path}")


# Plotting has been moved to prefix_length_plot.py


# ── 入口 ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prefix Caching 前缀长度实验")
    parser.add_argument(
        "--cache",
        choices=["on", "off"],
        required=True,
        help="on: 开启 cache 测量  |  off: 关闭 cache 测量",
    )
    args = parser.parse_args()

    if args.cache == "on":
        run_experiment("cache_on")
    else:
        run_experiment("cache_off")