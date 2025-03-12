# Step 0: Install the SWE-bench
git clone https://github.com/princeton-nlp/SWE-bench.git
cd SWE-bench
pip install -e .

# Step 1: Run the inference
python -m benchmarks.swebench.inference \
  --data_name princeton-nlp/SWE-bench_Lite \
  --split test \
  --output_file benchmarks/swebench/eval_prediction.json \
  --on_aios \
  --agent_type llm

# Step 2: Evaluate the functional correctness
