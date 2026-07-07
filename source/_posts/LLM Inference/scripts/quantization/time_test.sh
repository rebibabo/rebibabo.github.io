export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
RESULT_DIR=/root/autodl-tmp/results/perf_awq

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
    --result-dir "$RESULT_DIR"