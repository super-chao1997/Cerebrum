#!/bin/bash

# Run local agent
python cerebrum/run_agent.py \
  --mode local \
  --path cerebrum/example/agents/test_agent \
  --agenthub_url https://app.aios.foundation \
  --task "Tell me what is the capital of United States"