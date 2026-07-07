# 先升级 pip
pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/

# 安装 vLLM（指定 CUDA 12.1 对应的版本）
pip install vllm -i https://pypi.mirrors.ustc.edu.cn/simple

# 验证安装
python -c "import vllm; print(vllm.__version__)"

pip install modelscope -i https://mirrors.aliyun.com/pypi/simple/

modelscope download \
    --model qwen/Qwen2.5-7B-Instruct \
    --local_dir /root/autodl-tmp/models/qwen2.5-7b-instruct

pip install lm-eval -i https://mirrors.aliyun.com/pypi/simple/
pip install lm-eval[api]

python -c "
import torch
import vllm

print('=== 环境检查 ===')
print(f'PyTorch:  {torch.__version__}')
print(f'vLLM:     {vllm.__version__}')
print(f'CUDA 可用: {torch.cuda.is_available()}')
print(f'GPU 数量:  {torch.cuda.device_count()}')
print(f'GPU 型号:  {torch.cuda.get_device_name(0)}')
print(f'显存总量:  {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
"

echo "export HF_ENDPOINT=https://hf-mirror.com
export HF_DATASETS_CACHE=/root/autodl-tmp/hf_cache" >> ~/.bashrc && source ~/.bashrc

wget https://hf-mirror.com/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/resolve/main/ShareGPT_V3_unfiltered_cleaned_split.json \
-O /root/autodl-tmp/datasets/sharegpt.json

mkdir -p /root/autodl-tmp/results/perf_baseline

