# Cerebrum: Agent SDK for AIOS

<a href='https://aios-3.gitbook.io/'><img src='https://img.shields.io/badge/Documentation-Cerebrum-blue'></a>
[![Code License](https://img.shields.io/badge/Code%20License-MIT-orange.svg)](https://github.com/agiresearch/AIOS/blob/main/LICENSE)
<a href='https://discord.gg/B2HFxEgTJX'><img src='https://img.shields.io/badge/Community-Discord-8A2BE2'></a>

The goal of AIOS is to build a Large Language Model (LLM) agent operating system, which intends to embed large language model into the operating system as the brain of the OS. AIOS is designed to address problems (e.g., scheduling, context switch, memory management, etc.) during the development and deployment of LLM-based agents, for a better ecosystem among agent developers and users.

## 🏠 Cerebrum Architecture
<p align="center">
<img src="docs/assets/aios-figs/architecture.jpg">
</p>


AIOS provides the AIOS kernel as an abstraction on top of the OS kernel. The kernel facilitates the installation, execution and usage of agents. Furthermore, the AIOS SDK facilitates the development and deployment of agents.

## 📰 News
- **[2024-11-026]** 🔥 Cerebrum is available for public release on PyPi!

## Installation

### Standard Installation

1. **Install the package**
   ```bash
   pip install aios-agent-sdk
   ```

4. **Verify installation**
   ```bash
   python -c "import cerebrum; from cerebrum.client import Cerebrum; print(Cerebrum)"
   ```

### Install From Source
1. **Clone Repo**
   ```bash
   git clone https://github.com/agiresearch/Cerebrum.git

   cd Cerebrum
   ```

3. **Create Virtual Environment**
   ```bash
   conda create -n cerebrum-env python=3.10
   ```
   or
   ```bash
   conda create -n cerebrum-env python=3.11
   ```
   or
   ```bash
   # Windows (cmd)
   python -m venv cerebrum-env

   # Linux/MacOS
   python3 -m venv cerebrum-env
   ```

4. **Activate the environment**
   ```bash
   conda activate myenv
   ```
   or
   ```bash
   # Windows (cmd)
   cd cerebrum-env
   cd Scripts
   activate.bat
   cd ..
   cd ..
   

   # Linux/MacOS
   source cerebrum-env/bin/activate
   ```

6. **Install the package**
   ```bash
   pip install -e .
   ```

7. **Verify installation**
   ```bash
   python -c "import cerebrum; from cerebrum.client import Cerebrum; print(Cerebrum)"
   ```

## ✈️ Quickstart
> [!TIP] 
>
> Please see our ongoing [documentation](https://aios-3.gitbook.io/) for more information.

1. **Start the AIOS Kernel** 
   📝 See [here](https://aios-3.gitbook.io/aios-docs/getting-started/installation).

2. **Run the AIOS Basic Demo**
   ```bash
   aios-basic-demo
   ```

   Code file is located at `example/aios_demo.py`

3. **Run the AIOS Concurrent Agent Demo**
   ```bash
   aios-concurrent-demo
   ```

   Code file is located at `example/aios_demo_concurrent.py`

### Supported LLM Cores

| Provider 🏢 | Model Name 🤖 | Open Source 🔓 | Model String ⌨️ | Backend ⚙️ |
|:------------|:-------------|:---------------|:---------------|:---------------|
| Anthropic | Claude 3.5 Sonnet | ❌ | claude-3-5-sonnet-20241022 |anthropic |
| Anthropic | Claude 3.5 Haiku | ❌ | claude-3-5-haiku-20241022 |anthropic |
| Anthropic | Claude 3 Opus | ❌ | claude-3-opus-20240229 |anthropic |
| Anthropic | Claude 3 Sonnet | ❌ | claude-3-sonnet-20240229 |anthropic |
| Anthropic | Claude 3 Haiku | ❌ | claude-3-haiku-20240307 |anthropic |
| OpenAI | GPT-4 | ❌ | gpt-4 |openai|
| OpenAI | GPT-4 Turbo | ❌ | gpt-4-turbo |openai|
| OpenAI | GPT-4o | ❌ | gpt-4o |openai|
| OpenAI | GPT-4o mini | ❌ | gpt-4o-mini |openai|
| OpenAI | GPT-3.5 Turbo | ❌ | gpt-3.5-turbo |openai|
| Google | Gemini 1.5 Flash | ❌ | gemini-1.5-flash |google|
| Google | Gemini 1.5 Flash-8B | ❌ | gemini-1.5-flash-8b |google|
| Google | Gemini 1.5 Pro | ❌ | gemini-1.5-pro |google|
| Google | Gemini 1.0 Pro | ❌ | gemini-1.0-pro |google|
| Groq | Llama 3.2 90B Vision | ✅ | llama-3.2-90b-vision-preview |groq|
| Groq | Llama 3.2 11B Vision | ✅ | llama-3.2-11b-vision-preview |groq|
| Groq | Llama 3.1 70B | ✅ | llama-3.1-70b-versatile |groq|
| Groq | Llama Guard 3 8B | ✅ | llama-guard-3-8b |groq|
| Groq | Llama 3 70B | ✅ | llama3-70b-8192 |groq|
| Groq | Llama 3 8B | ✅ | llama3-8b-8192 |groq|
| Groq | Mixtral 8x7B | ✅ | mixtral-8x7b-32768 |groq|
| Groq | Gemma 7B | ✅ | gemma-7b-it |groq|
| Groq | Gemma 2B | ✅ | gemma2-9b-it |groq|
| Groq | Llama3 Groq 70B | ✅ | llama3-groq-70b-8192-tool-use-preview |groq|
| Groq | Llama3 Groq 8B | ✅ | llama3-groq-8b-8192-tool-use-preview |groq|
| Ollama[^bignote1] | All Models | ✅ | model-name |ollama|
| VLLM[^bignote2] | All Models | ✅ | model-name |vllm|
| HuggingFace[^bignote3] | All Models | ✅ | model-name |huggingface|

[^bignote1]: **Ollama Model String Format:**
      - Format: `model-name`. Some examples are `llama2`, `mistral`, or `codellama`.
      - Ollama allows you to run models locally using their CLI tool and API
      - See AIOS documentation for setting up Ollama

[^bignote2]: **VLLM Model String Format:**
     - Format: `model-name`. Some examples are `mistral-7b-instruct`, `llama2-70b`, or `mixtral-8x7b`.
     - VLLM is a high-performance inference engine that can serve any HuggingFace model
     - You can specify custom model paths: `vllm/path/to/your/model`
     - Supports quantization parameters: `vllm/mistral-7b-instruct-4bit`
     - See AIOS documentation for setting up VLLM

[^bignote3]: **HuggingFace Model String Format:**
     - Format: `owner/model-name`. Some examples are `mistralai/Mistral-7B-v0.1`, `meta-llama/Llama-2-70b-hf`, or `TheBloke/Llama-2-13B-GPTQ`.
     - Can include specific versions: `owner/model-name@v1.0`
     - Supports multiple model formats (PyTorch, Safetensors, GGUF, GPTQ)
     - Can reference private models with auth token: `huggingface/username/private-model`
     - See AIOS documentation for setting up HuggingFace (if necessary)


## 🖋️ References
```
@article{mei2024aios,
  title={AIOS: LLM Agent Operating System},
  author={Mei, Kai and Li, Zelong and Xu, Shuyuan and Ye, Ruosong and Ge, Yingqiang and Zhang, Yongfeng}
  journal={arXiv:2403.16971},
  year={2024}
}
@article{ge2023llm,
  title={LLM as OS, Agents as Apps: Envisioning AIOS, Agents and the AIOS-Agent Ecosystem},
  author={Ge, Yingqiang and Ren, Yujie and Hua, Wenyue and Xu, Shuyuan and Tan, Juntao and Zhang, Yongfeng},
  journal={arXiv:2312.03815},
  year={2023}
}
```

## 🚀 Contributions
For how to contribute, see [CONTRIBUTE](https://github.com/agiresearch/Cerebrum/blob/main/CONTRIBUTE.md). If you would like to contribute to the codebase, [issues](https://github.com/agiresearch/Cerebrum/issues) or [pull requests](https://github.com/agiresearch/Cerebrum/pulls) are always welcome!

## 🌍 Cerebrum Contributors
[![Cerebrum contributors](https://contrib.rocks/image?repo=agiresearch/Cerebrum&max=300)](https://github.com/agiresearch/Cerebrum/graphs/contributors)


## 🤝 Discord Channel
If you would like to join the community, ask questions, chat with fellows, learn about or propose new features, and participate in future developments, join our [Discord Community](https://discord.gg/B2HFxEgTJX)!

## 📪 Contact

For issues related to Cerebrum development, we encourage submitting [issues](https://github.com/agiresearch/Cerebrum/issues), [pull requests](https://github.com/agiresearch/Cerebrum/pulls), or initiating discussions in AIOS [Discord Channel](https://discord.gg/B2HFxEgTJX). For other issues please feel free to contact the AIOS Foundation ([contact@aios.foundation](mailto:contact@aios.foundation)).




