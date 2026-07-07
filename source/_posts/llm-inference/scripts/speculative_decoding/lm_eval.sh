lm_eval \
  --model local-completions \
  --model_args "model=qwen2.5-7b,num_concurrent=32,base_url=http://localhost:8000/v1/completions,tokenizer_backend=huggingface,tokenizer=/root/autodl-tmp/models/qwen2.5-7b-instruct,max_length=4096" \
  --tasks hellaswag,arc_easy,arc_challenge,gsm8k \
  --num_fewshot 0 \
  --output_path /root/autodl-tmp/results/lm_eval_speculative_ngram \
  --log_samples