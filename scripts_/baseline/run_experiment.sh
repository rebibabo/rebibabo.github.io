#!/bin/bash
# 保存为 run_experiments.sh

mkdir -p /root/autodl-tmp/results/sweep

# 通用参数
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

# ===== 实验组 A: 固定 max-concurrency=32, 扫 request-rate =====
echo "=========== Experiment A: Sweep request-rate ==========="
for rate in 1 2 4 8 16 inf; do
    echo ">>> request-rate=$rate, max-concurrency=32"
    vllm bench serve $COMMON_ARGS \
        --request-rate $rate \
        --max-concurrency 32 \
        --result-dir /root/autodl-tmp/results/sweep \
        --result-filename "expA_rate${rate}_conc32.json"
    sleep 5  # 让 server 喘口气
done

# ===== 实验组 B: request-rate=inf, 扫 max-concurrency =====
echo "=========== Experiment B: Sweep concurrency ==========="
for conc in 1 4 8 16 32 64 128; do
    echo ">>> request-rate=inf, max-concurrency=$conc"
    vllm bench serve $COMMON_ARGS \
        --request-rate inf \
        --max-concurrency $conc \
        --result-dir /root/autodl-tmp/results/sweep \
        --result-filename "expB_rateinf_conc${conc}.json"
    sleep 5
done

echo "All experiments done!"