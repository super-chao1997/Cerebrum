python cerebrum/example/run_agent.py \
    --llm_name llama3:8b \
    --llm_backend ollama \
    --agent_name_or_path demo_author/demo_agent \
    --task "Tell me what is core idea of AIOS" \
    --aios_kernel_url http://localhost:8000


run-agent \
    --llm_name qwen2.5:3b \
    --llm_backend ollama \
    --agent_name_or_path /common/home/km1558/projects/dongyuanjushi/Cerebrum/cerebrum/example/agents/language_tutor \
    --task "How should I use the word help?" \
    --aios_kernel_url "http://localhost:8000" \
    --timeout 3000000