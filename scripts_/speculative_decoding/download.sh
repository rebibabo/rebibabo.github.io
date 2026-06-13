modelscope download \
    --model Qwen/Qwen2.5-1.5B-Instruct \
    --local_dir /root/autodl-tmp/models/qwen2.5-1.5b-instruct
    
wget https://raw.githubusercontent.com/hemingkx/Spec-Bench/main/data/spec_bench/question.jsonl \
    -O /root/autodl-tmp/datasets/spec_bench.jsonl