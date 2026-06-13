#!/bin/bash
# nohup ./start.sh > start.log 2>&1 &

# 输出日志文件
LOG_FILE="../tmps/vllm.log"
PID_FILE="../tmps/vllm.pid"

# 启动 vLLM API server
nohup python -m vllm.entrypoints.openai.api_server \
    --model /root/autodl-tmp/models/qwen2.5-7b-instruct\
    --served-model-name qwen2.5-7b \
    --host 0.0.0.0 \
    --port 8000 \
    --gpu-memory-utilization 0.85 \
    --max-model-len 4096 \
    > "$LOG_FILE" 2>&1 &

# 保存 PID
echo $! > "$PID_FILE"
echo "vLLM started with PID $(cat $PID_FILE)"
echo "Logs are in $LOG_FILE"