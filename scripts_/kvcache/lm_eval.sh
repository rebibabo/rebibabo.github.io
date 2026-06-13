#!/bin/bash
# nohup ./lm_eval.sh > lm_eval.log 2>&1 &

# 日志和 PID 文件
LOG_FILE="../tmps/lm_eval.log"
PID_FILE="../tmps/lm_eval.pid"

# 设置线程数
export OMP_NUM_THREADS=32

# 启动 lm_eval 后台运行
nohup lm_eval \
  --model local-completions \
  --model_args "model=qwen2.5-7b-fp8kv,base_url=http://localhost:8000/v1/completions,tokenizer_backend=huggingface,tokenizer=/root/autodl-tmp/models/qwen2.5-7b-instruct,num_concurrent=32,max_length=4096" \
  --tasks hellaswag,arc_easy,arc_challenge,gsm8k \
  --num_fewshot 0 \
  --output_path /root/autodl-tmp/results/lm_eval_fp8kv \
  --log_samples \
  > "$LOG_FILE" 2>&1 &


# 保存 PID
echo $! > "$PID_FILE"
echo "lm_eval started with PID $(cat $PID_FILE)"
echo "Logs: $LOG_FILE"