# prefix_cache_test.py
import requests
import time

SYSTEM_PROMPT = """你是一个专业的AI助手。你需要遵循以下规则：
1. 回答必须准确、客观、有依据
2. 如果不确定，要明确说明
3. 回答要结构化，使用适当的标题和段落
4. 对于技术问题，要给出代码示例
5. 对于历史问题，要注明时间和来源
""" * 20

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
    prompt_tokens = data["usage"]["prompt_tokens"]
    return elapsed * 1000, prompt_tokens

def get_prefix_cache_stats():
    r = requests.get("http://localhost:8000/metrics")
    queries = 0
    hits = 0
    for line in r.text.split("\n"):
        # 精确匹配，排除 _created 和注释行
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

print("=" * 65)
print("Prefix Cache 效果测试")
print("=" * 65)

init_queries, init_hits = get_prefix_cache_stats()
print(f"初始状态 - 查询: {init_queries:.0f}, 命中: {init_hits:.0f}")
print()

print(f"{'序号':>4} {'问题':<20} {'TTFT(ms)':>10} {'Prompt Tokens':>15}")
print("-" * 55)

for i, q in enumerate(questions):
    elapsed, tokens = send_request(q)
    # 每个请求后立即读取 cache 状态
    cur_queries, cur_hits = get_prefix_cache_stats()
    new_q = cur_queries - init_queries
    new_h = cur_hits - init_queries  
    print(f"{i+1:>4} {q[:18]:<20} {elapsed:>10.1f} {tokens:>15}")

final_queries, final_hits = get_prefix_cache_stats()
total_new_queries = final_queries - init_queries
total_new_hits = final_hits - init_hits
hit_rate = total_new_hits / total_new_queries * 100 if total_new_queries > 0 else 0

print()
print(f"本次实验 Prefix Cache 统计:")
print(f"  查询 tokens: {total_new_queries:.0f}")
print(f"  命中 tokens: {total_new_hits:.0f}")
print(f"  命中率: {hit_rate:.1f}%")
print(f"  节省计算: {total_new_hits:.0f} tokens 的 KV 无需重新计算")