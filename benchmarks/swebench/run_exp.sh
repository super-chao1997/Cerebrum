python -m benchmarks.swebench.inference \
  --data_name princeton-nlp/SWE-bench_Lite \
  --split test \
  --output_file benchmarks/swebench/eval_prediction.json \
  --on_aios \
  --agent_type llm