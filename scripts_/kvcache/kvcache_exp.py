# kv_cache_experiment.py
import requests
import time
import re
import threading

def get_kv_cache_usage():
    r = requests.get("http://localhost:8000/metrics")
    for line in r.text.split("\n"):
        if "kv_cache_usage_perc" in line and not line.startswith("#"):
            return float(line.split()[-1])
    return None

def get_total_kv_cache_info():
    r = requests.get("http://localhost:8000/metrics")
    for line in r.text.split("\n"):
        if "cache_config_info" in line and not line.startswith("#"):
            m1 = re.search(r'num_gpu_blocks="(\d+)"', line)
            m2 = re.search(r'block_size="(\d+)"', line)
            if m1 and m2:
                return int(m1.group(1)), int(m2.group(1))
    return None, None

result = {}

def send_request_async(max_tokens):
    r = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json={
            "model": "qwen2.5-7b",
            "messages": [{"role": "user", "content": "请详细介绍一下中国的历史，从远古时代开始讲起，讲1万字"}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        },
        stream=False
    )
    data = r.json()
    usage = data["usage"]
    result["prompt"] = usage["prompt_tokens"]
    result["completion"] = usage["completion_tokens"]

# 获取 KV Cache 配置
token_kv_bytes = 28 * 2 * 4 * 128 * 2  # Qwen2.5-7B BF16
num_blocks, block_size = get_total_kv_cache_info()
total_tokens_capacity = num_blocks * block_size
total_kv_mb = total_tokens_capacity * token_kv_bytes / 1024 / 1024

print(f"KV Cache 配置: {num_blocks} blocks × {block_size} tokens/block = {total_tokens_capacity} tokens")
print(f"KV Cache 总容量: {total_kv_mb:.1f} MB")
print(f"理论单 token KV: {token_kv_bytes} bytes = {token_kv_bytes/1024:.1f} KB")
print()

print(f"{'max_tokens':>12} {'输入':>6} {'输出':>6} {'总tokens':>8} {'理论KV(MB)':>12} {'实测KV(MB)':>12} {'峰值KV%':>8}")
print("-" * 75)

for max_tokens in [32, 64, 128, 256, 512, 1024, 2048]:
    result.clear()

    t = threading.Thread(target=send_request_async, args=(max_tokens,))
    t.start()

    peak_kv = 0.0
    while t.is_alive():
        kv = get_kv_cache_usage()
        if kv is not None and kv > peak_kv:
            peak_kv = kv
        time.sleep(0.05)

    t.join()

    prompt_tokens = result.get("prompt", 0)
    completion_tokens = result.get("completion", 0)
    total_tokens = prompt_tokens + completion_tokens
    theory_mb = total_tokens * token_kv_bytes / 1024 / 1024
    actual_mb = peak_kv * total_kv_mb

    print(f"{max_tokens:>12} {prompt_tokens:>6} {completion_tokens:>6} {total_tokens:>8} {theory_mb:>12.2f} {actual_mb:>12.2f} {peak_kv*100:>7.2f}%")
    time.sleep(3)