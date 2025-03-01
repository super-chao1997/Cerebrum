#!/bin/bash

# Run local agent
python cerebrum/run_agent.py \
  --mode local \
  --agent_path cerebrum/example/agents/test_agent \
  --agenthub_url https://app.aios.foundation \
  --task "Tell me what is the capital of United States"


# Run remote agent
python cerebrum/run_agent.py \
  --mode remote \
  --agent_author example \
  --agent_name test_agent \
  --agenthub_url https://app.aios.foundation \
  --task "Tell me what is the capital of United States"

# Upload agent to agenthub
python cerebrum/upload_agent.py \
  --agent_path cerebrum/example/agents/test_agent \
  --agenthub_url https://app.aios.foundation


