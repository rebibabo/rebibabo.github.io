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