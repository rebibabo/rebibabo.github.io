#!/bin/bash
# 保存为 run_experiments.sh

mkdir -p /root/autodl-tmp/results/sweep_spec

export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1

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

echo "=== Speculative Decoding：扫描 max-concurrency ==="
for conc in 1 4 8 16 32 64 128; do
    vllm bench serve $COMMON_ARGS \
        --request-rate inf \
        --max-concurrency $conc \
        --result-dir /root/autodl-tmp/results/sweep_spec \
        --result-filename "spec_rateinf_conc${conc}.json"
    sleep 5
done