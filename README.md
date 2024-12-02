# Cerebrum: Agent SDK for AIOS

<a href='https://docs.aios.foundation/'><img src='https://img.shields.io/badge/Documentation-Cerebrum-blue'></a>
[![Code License](https://img.shields.io/badge/Code%20License-MIT-orange.svg)](https://github.com/agiresearch/AIOS/blob/main/LICENSE)
<a href='https://discord.gg/B2HFxEgTJX'><img src='https://img.shields.io/badge/Community-Discord-8A2BE2'></a>

The goal of AIOS is to build a Large Language Model (LLM) agent operating system, which intends to embed large language model into the operating system as the brain of the OS. AIOS is designed to address problems (e.g., scheduling, context switch, memory management, etc.) during the development and deployment of LLM-based agents, for a better ecosystem among agent developers and users.

## 🏠 Cerebrum Architecture
<p align="center">
<img src="docs/assets/details.png">
</p>

The AIOS-Agent SDK is designed for agent users and developers, enabling them to build and run agent applications by interacting with the [AIOS kernel](https://github.com/agiresearch/AIOS.git). 

## 📰 News
- **[2024-11-26]** 🔥 Cerebrum is available for public release on PyPI!

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
> Please see our [documentation](https://docs.aios.foundation/) for more information.

1. **Start the AIOS Kernel** 
   📝 See [here](https://docs.aios.foundation/getting-started/installation).

2. **Run the AIOS Client**

   Run the client with a single agent
   ```bash
   aios-basic-demo --llm_name gpt-4o-mini --llm_backend openai --agent <replace with the actual agent> --task <replace with the actual task>
   ```
   which is the same as using 
   ```bash
   python cerebrum/example/aios_demo.py --llm_name gpt-4o-mini --llm_backend openai --agent <replace with the actual agent> --task <replace with the actual task>
   ```
   Code file is located at `cerebrum/example/aios_demo.py`

   Run the client with agents concurrently
   
   ```bash
   aios-concurrent-demo --llm_name gpt-4o-mini --llm_backend openai
   ```
   which is the same as using 
   ```bash
   python cerebrum/example/aios_demo_concurrent.py --llm_name gpt-4o-mini --llm_backend openai --agent <replace with the actual agent> --task <replace with the actual task>
   ```

   Code file is located at `cerebrum/example/aios_demo_concurrent.py`


## 🚀 Develop and customize new agents

This guide will walk you through creating and publishing your own agents for AIOS. 
### Agent Structure

First, let's look at how to organize your agent's files. Every agent needs three essential components:

```
author/
└── agent_name/
      │── entry.py        # Your agent's main logic
      │── config.json     # Configuration and metadata
      └── meta_requirements.txt  # Additional dependencies
```

For example, if your name is 'example' and you're building a demo_agent that searches and summarizes articles, your folder structure would look like this:

```
example/
   └── demo_agent/
         │── entry.py
         │── config.json
         └── meta_requirements.txt
```

Note: If your agent needs any libraries beyond AIOS's built-in ones, make sure to list them in meta_requirements.txt. Apart from the above three files, you can have any other files in your folder. 

### Configuring Your Agent

#### Setting Up Metadata

Your agent needs a config.json file that describes its functionality. Here's what it should include:

```json
{
   "name": "name of the agent",
   "description": [
      "description of the agent functionality"
   ],
   "tools": [
      "tools need to be used"
   ],
   "meta": {
      "author": "",
      "version": "",
      "license": ""
   },
   "build": {
      "entry": "entry file to start the agent",
      "module": "the module name of the agent"
   }
}
```

### Available Tools

When setting up your agent, you'll need to specify which tools it will use. Below is a list of all currently available tools and how to reference them in your configuration:

| Author | Name | How to Use |
|:--|:--|:--|
| example | arxiv | example/arxiv |
| example | bing_search | example/bing_search |
| example | currency_converter | example/currency_converter |
| example | wolfram_alpha | example/wolfram_alpha |
| example | google_search | example/google_search |
| openai | speech_to_text | openai/speech_to_text |
| example | web_browser | example/web_browser |
| timbrooks | image_to_image | timbrooks/image_to_image |
| example | downloader | example/downloader |
| example | doc_question_answering | example/doc_question_answering |
| stability-ai | text_to_image | stability-ai/text_to_image |
| example | text_to_speech | example/text_to_speech |

To use these tools in your agent, simply include their reference (from the "How to Use" column) in your agent's configuration file. For example, if you want your agent to be able to search academic papers and convert currencies, you would include both `example/arxiv` and `example/currency_converter` in your configuration.

If you would like to create your new tools, you can either integrate the tool within your agent code or you can follow the tool examples in the [tool folder](./cerebrum/example/tools/) to develop your standalone tools. The detailed instructions are in [How to develop new tools](#develop-and-publish-new-tools)

### Building Your Agent's Logic

Let's walk through creating your agent's core functionality.

#### 1. Setting Up the Base Class

First, create your agent class by inheriting from BaseAgent:

```python
from cerebrum.agents.base import BaseAgent
import json

class DemoAgent(BaseAgent):
    def __init__(self, agent_name, task_input, config_):
        super().__init__(agent_name, task_input, config_)
        pass
```

#### 2. Using Query Functions

AIOS provides several `Query` classes for different types of interactions and use the `Response` class in [here](./cerebrum/llm/communication.py) to receive results from the AIOS kernel. 

| Query Class | Arguments | Output |
|:--|:--|:--|
| `LLMQuery` | messages: `List`, tools: `List`, action_type: `str`, message_return_type: `str` | response: `Response` |
| `MemoryQuery` | TBD | response: `Response` |
| `StorageQuery` | TBD | response: `Response` |
| `ToolQuery` | tool_calls: `List` | response: `Response` |

Here's how to import a specific query
```python
from cerebrum.llm.communication import LLMQuery  # Using LLMQuery as an example
```

#### 3. Creating System Instructions

Here's how to set up your agent's system instructions:

```python
def build_system_instruction(self):
    prefix = "".join(["".join(self.config["description"])])

    plan_instruction = "".join([
        f"You are given the available tools from the tool list: {json.dumps(self.tool_info)} to help you solve problems. ",
        "Generate a plan with comprehensive yet minimal steps to fulfill the task. ",
        "The plan must follow this JSON format: ",
        "[",
        '{"action_type": "action_type_value", "action": "action_value", "tool_use": [tool_name1, tool_name2,...]}',
        "]",
    ])

    if self.workflow_mode == "manual":
        self.messages.append({"role": "system", "content": prefix})
    else:
        self.messages.append({"role": "system", "content": prefix})
        self.messages.append({"role": "user", "content": plan_instruction})
```

#### 4. Creating Workflows

You can create workflows either manually or automatically:

Manual Workflow Example:
```python
def manual_workflow(self):
    workflow = [
        {
            "action_type": "chat",
            "action": "Identify user's goals and create explanations",
            "tool_use": []
        },
        {
            "action_type": "chat",
            "action": "Provide examples",
            "tool_use": []
        }
    ]
    return workflow
```

Automatic Workflow Example:
```python
def automatic_workflow(self):
    for i in range(self.plan_max_fail_times):
        response = self.send_request(
            agent_name=self.agent_name,
            query=LLMQuery(
                messages=self.messages, 
                tools=None, 
                message_return_type="json"
            ),
        )["response"]

        workflow = self.check_workflow(response.response_message)
        
        if workflow:
            return workflow
        
        self.messages.append({
            "role": "assistant",
            "content": f"Attempt {i+1} failed to generate a valid plan. Retrying..."
        })
    return None
```

#### 5. Implementing the Run Method

Finally, implement the run method to execute your agent's workflow:

```python
def run(self):
    self.build_system_instruction()
    
    # Add task input to messages
    self.messages.append({"role": "user", "content": self.task_input})
    
    # Get workflow
    workflow = self.automatic_workflow() if self.workflow_mode == "automatic" else self.manual_workflow()
    
    if not workflow:
        return {
            "agent_name": self.agent_name,
            "result": "Failed to generate a valid workflow",
            "rounds": self.rounds
        }
    
    try:
        final_result = ""
        for i, step in enumerate(workflow):
            # Execute each step in the workflow
            response = self.execute_step(step, i)
            final_result = response.response_message
            
        return {
            "agent_name": self.agent_name,
            "result": final_result,
            "rounds": self.rounds
        }
        
    except Exception as e:
        return {
            "agent_name": self.agent_name,
            "result": f"Error occurred: {str(e)}",
            "rounds": self.rounds
        }
```

### Running Your Agent

To test your agent, use the aios_demo.py script:

```bash
python aios_demo.py --llm_name <llm_name> --llm_backend <llm_backend> --agent <your_agent_folder_path> --task <task_input>
```
Replace the placeholders with your specific values:
- `<llm_name>`: The name of the language model you want to use
- `<llm_backend>`: The backend service for the language model
- `<your_agent_folder_path>`: The path to your agent's folder
- `<task_input>`: The task you want your agent to perform

## 🔧Develop and customize new tools
### Tool Structure
Similar as developing new agents, developing tools also need to follow a simple directory structure:
```
example/
└── demo_tool/
    │── entry.py      # Contains your tool's main logic
    └── config.json   # Tool configuration and metadata
```

### Setting Up config.json
Your tool needs a configuration file that describes its properties. Here's an example of how to set it up:

```json
{
    "name": "Your Tool Name",
    "description": [
        "A clear description of what your tool does",
        "You can add multiple lines of description"
    ],
    "meta": {
        "author": "",
        "version": "",
        "license": ""
    },
    "build": {
        "entry": "entry.py",
        "module": "YourToolClass"
    }
}
```
### Creating Your Tool Class
In `entry.py`, you'll need to implement a tool class which is identified in the config.json with two essential methods:

1. `get_tool_call_format`: Defines how LLMs should interact with your tool
2. `run`: Contains your tool's main functionality

Here's an example:

```python
class YourTool:
    def get_tool_call_format(self):
        """
        Define how LLMs should call your tool.
        Follow OpenAI's function calling format.
        """
        return {
            "type": "function",
            "function": {
                "name": "example/your_tool",
                "description": "What your tool does",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param_name": {
                            "type": "string",
                            "description": "What this parameter does"
                        }
                    },
                    "required": ["param_name"]
                }
            }
        }

    def run(self, params: dict):
        """
        Main tool logic goes here.
        Args:
            params: Dictionary containing tool parameters
        Returns:
            Your tool's output
        """
        # Your code here
        result = do_something(params['param_name'])
        return result
```

### Integration Tips
When integrating your tool for the agents you develop:
- Use absolute paths to reference your tool in agent configurations
- Example: `/path/to/your/tools/example/your_tool` instead of just `author/tool_name`

## Supported LLM Cores
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
| ollama | [All Models](https://ollama.com/search) | ✅ | model-name |ollama|
| vLLM | [All Models](https://docs.vllm.ai/en/latest/) | ✅ | model-name |vllm|
| HuggingFace | [All Models](https://huggingface.co/models/) | ✅ | model-name |huggingface|


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




