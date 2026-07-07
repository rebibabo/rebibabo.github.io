# 开启 Prefix Caching（vLLM 默认）
python -m vllm.entrypoints.openai.api_server \
    --model /root/autodl-tmp/models/qwen2.5-7b-instruct \
    --served-model-name qwen2.5-7b \
    --host 0.0.0.0 --port 8000 \
    --gpu-memory-utilization 0.85 \
    --max-model-len 4096