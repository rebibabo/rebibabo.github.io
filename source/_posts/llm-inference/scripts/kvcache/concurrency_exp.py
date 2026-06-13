# kv_cache_concurrency.py
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

def get_running():
    r = requests.get("http://localhost:8000/metrics")
    running = 0
    for line in r.text.split("\n"):
        if "num_requests_running" in line and not line.startswith("#"):
            running = int(float(line.split()[-1]))
    return running

def send_request(barrier):
    """等所有线程就绪后同时发请求"""
    barrier.wait()
    try:
        r = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "model": "qwen2.5-7b",
                "messages": [{"role": "user", "content": "请详细介绍一下中国的历史，从远古时代开始讲起，讲1万字"}],
                "max_tokens": 1024,
                "temperature": 0.7
            },
            timeout=300
        )
    except:
        pass

# 获取 KV Cache 配置
token_kv_bytes = 28 * 2 * 4 * 128 * 2
num_blocks, block_size = get_total_kv_cache_info()
total_tokens_capacity = num_blocks * block_size
total_kv_mb = total_tokens_capacity * token_kv_bytes / 1024 / 1024

print(f"KV Cache 配置: {num_blocks} blocks × {block_size} tokens/block")
print(f"KV Cache 总容量: {total_kv_mb:.1f} MB")
print()

print(f"{'并发数':>6} {'峰值KV%':>8} {'峰值KV(MB)':>12} {'运行中':>6}")
print("-" * 50)

# for concurrency in [1, 2, 4, 8, 16, 32, 48, 64, 80, 96, 128]:
for concurrency in [1]:
    # 用 Barrier 让所有线程同时发请求
    barrier = threading.Barrier(concurrency + 1)  # +1 是主线程

    threads = []
    for _ in range(concurrency):
        t = threading.Thread(target=send_request, args=(barrier,))
        t.start()
        threads.append(t)

    # 主线程也参与 barrier，释放所有请求线程
    barrier.wait()

    # 立即开始采样，持续到所有请求结束
    peak_kv = 0.0
    peak_running = 0

    alive = True
    while alive:
        kv = get_kv_cache_usage()
        running = get_running()
        if kv is not None and kv > peak_kv:
            peak_kv = kv
            peak_running = running
        time.sleep(0.1)
        alive = any(t.is_alive() for t in threads)

    for t in threads:
        t.join()

    actual_mb = peak_kv * total_kv_mb

    print(f"{concurrency:>6} {peak_kv*100:>7.2f}% {actual_mb:>12.1f} {peak_running:>6}")

    time.sleep(5)  # 等 KV Cache 完全释放