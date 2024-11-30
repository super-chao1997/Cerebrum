# Cerebrum: Agent SDK for AIOS

<a href='https://aios-3.gitbook.io/'><img src='https://img.shields.io/badge/Documentation-Cerebrum-blue'></a>
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
> Please see our [documentation](https://aios-3.gitbook.io/) for more information.

1. **Start the AIOS Kernel** 
   📝 See [here](https://aios-3.gitbook.io/aios-docs/getting-started/installation).

2. **Run the AIOS Client**

   Run the client with a single agent
   ```bash
   aios-basic-demo --llm_name gpt-4o-mini --llm_backend openai --agent <replace with the actual agent> --task <replace with the actual task>
   ```

   Code file is located at `cerebrum/example/aios_demo.py`

   Run the client with agents concurrently
   ```bash
   aios-concurrent-demo --llm_name gpt-4o-mini --llm_backend openai
   ```

   Code file is located at `cerebrum/example/aios_demo_concurrent.py`

## 🚀 How to develop and publish your agents
### Agent Format
Before you develop your own agents and would like to run that on AIOS, you need to make sure that structure of agent is strictly organized as below. 
#### Folder format and mandatory files
You need to put the agent folder as the following structure
```
author/
└── agent_name/
      │── entry.py # the entry file to run your new agents
      │── config.json # agent information, e.g., name, usage, license, etc.
      └── meta_requirements.txt # specific dependencies used for running your agent
```
For example, your author name is ‘example’, and you have developed an agent called demo_agent used for searching and summarizing articles. Your local folder will be like the following:
```
example/
   └── dem_agent/
         │── entry.py
         │── config.json
         └── meta_requirements.txt
```

If your agent requires extra libraries (in addition to the AIOS-dependent libraries) to run, you must put them in the meta_requirements.txt.

These three files **(config.json, entry.py, meta_requirements.txt)** are the minimal requirements to be had in the agent implementations. 

After you have setup the agent folder, you can then follow the instructions below to develop your agents. 

### Setup configurations for your agents
#### Setup metadata
You are required to include a JSON file with all the metadata used for the agent you would like to develop including the following attributes:
```
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
#### Setup tools
The table below shows current available tools and provides how to set them in the configuration. 
Their source code can be found at the [tool folder](./cerebrum/example/tools/). 

| Author       | Name                    | How to set them in the configuration                          |
|-------------|-------------------------|-------------------------------------|
| example     | arxiv                   | example/arxiv                       |
| example     | bing_search            | example/bing_search                 |
| example     | currency_converter      | example/currency_converter          |
| example     | wolfram_alpha          | example/wolfram_alpha               |
| example     | google_search          | example/google_search               |
| openai      | speech_to_text         | openai/speech_to_text              |
| example     | web_browser            | example/web_browser                 |
| timbrooks   | image_to_image         | timbrooks/image_to_image           |
| example     | downloader             | example/downloader                  |
| example     | doc_question_answering | example/doc_question_answering      |
| stability-ai| text_to_image          | stability-ai/text_to_image         |
| example     | text_to_speech         | example/text_to_speech             |

If you would like to develop your new tools, you can refer to the too 

#### Develop your agent logic
Here provides a minimal example of how to build your agents.

##### Inherit the BaseAgent and override the methods
First, you need to construct an agent class which is exactly the same name you set up for the module in the JSON file. To connect to the AIOS, you need to inherit the BaseAgent class and override the __init__ and run method.
```python
from cerebrum.agents.base import BaseAgent
import json

class DemoAgent(BaseAgent):
    def __init__(self, agent_name, task_input, config_):
        super().__init__(agent_name, task_input, config_)
        pass
```

##### Import the Query functions
For now, we provide four different query classes to interact with different modules in the AIOS and use the Response format to receive results by sending queries. 
```python
from cerebrum.llm.communication import LLMQuery # use LLMQuery as an example
```
Below shows how to use different queries (MemoryQuery and StorageQuery are under development). 
| class       | Arguments                    | Output|
|-------------|-------------------------|-------------------------------------|
| LLMQuery     | messages: List, tools: List, action_type: str, message_return_type: str | response: Response |
| MemoryQuery     | TBD            | response: Response
| StorageQuery     | TBD      | response: Response          |
| ToolQuery     | tool_calls: List          | response: Response |


##### Construct system prompts
Then you need construct your own system prompts for your agent, below shows a simple example. 
```python
def build_system_instruction(self):
    prefix = "".join(["".join(self.config["description"])])

    plan_instruction = "".join(
        [
            f"You are given the available tools from the tool list: {json.dumps(self.tool_info)} to help you solve problems. ",
            "Generate a plan with comprehensive yet minimal steps to fulfill the task. ",
            "The plan must follow the json format as below: ",
            "[",
            '{"action_type": "action_type_value", "action": "action_value","tool_use": [tool_name1, tool_name2,...]}',
            '{"action_type": "action_type_value", "action": "action_value", "tool_use": [tool_name1, tool_name2,...]}',
            "...",
            "]",
            "In each step of the planned plan, identify tools to use and recognize no tool is necessary. ",
            "Followings are some plan examples. ",
            "[" "[",
            '{"action_type": "tool_use", "action": "gather information from arxiv. ", "tool_use": ["arxiv"]},',
            '{"action_type": "chat", "action": "write a summarization based on the gathered information. ", "tool_use": []}',
            "];",
            "[",
            '{"action_type": "tool_use", "action": "gather information from arxiv. ", "tool_use": ["arxiv"]},',
            '{"action_type": "chat", "action": "understand the current methods and propose ideas that can improve ", "tool_use": []}',
            "]",
            "]",
        ]
    )

    if self.workflow_mode == "manual":
        self.messages.append({"role": "system", "content": prefix})

    else:
        assert self.workflow_mode == "automatic"
        self.messages.append({"role": "system", "content": prefix})
        self.messages.append({"role": "user", "content": plan_instruction})
```

##### Build workflow for agents and run
You can either build workflow by manual definition 
```python
def manual_workflow(self):
    workflow = [
        {
            "action_type": "chat",
            "action": "Identify user's target language and learning goals and create grammar explanations and practice sentences.",
            "tool_use": []
        },
        {
            "action_type": "chat",
            "action": "Provide audio examples of pronunciation.",
            "tool_use": []
        },
        {
            "action_type": "chat",
            "action": "Engage in conversation practice with the user.",
            "tool_use": []
        }
    ]
    return workflow
```
or generate workflow automatically. 
```python
def automatic_workflow(self):
    for i in range(self.plan_max_fail_times):
        response = self.send_request(
            agent_name=self.agent_name,
            query=LLMQuery(
                messages=self.messages, tools=None, message_return_type="json"
            ),
        )["response"]

        workflow = self.check_workflow(response.response_message)

        self.rounds += 1

        if workflow:
            return workflow

        else:
            self.messages.append(
                {
                    "role": "assistant",
                    "content": f"Fail {i+1} times to generate a valid plan. I need to regenerate a plan",
                }
            )
    return None
```
After defining your workflows, you can build the run method. 
```python
def run(self):
    self.build_system_instruction()

    task_input = self.task_input

    self.messages.append({"role": "user", "content": task_input})

    workflow = None

    if self.workflow_mode == "automatic":
        workflow = self.automatic_workflow()
        self.messages = self.messages[:1]  # clear long context

    else:
        assert self.workflow_mode == "manual"
        workflow = self.manual_workflow()

    self.messages.append(
        {
            "role": "user",
            "content": f"[Thinking]: The workflow generated for the problem is {json.dumps(workflow)}. Follow the workflow to solve the problem step by step. ",
        }
    )

    try:
        if workflow:
            final_result = ""

            for i, step in enumerate(workflow):
                action_type = step["action_type"]
                action = step["action"]
                tool_use = step["tool_use"]

                prompt = f"At step {i + 1}, you need to: {action}. "
                self.messages.append({"role": "user", "content": prompt})

                if tool_use:
                    selected_tools = self.pre_select_tools(tool_use)

                else:
                    selected_tools = None

                response = self.send_request(
                    agent_name=self.agent_name,
                    query=LLMQuery(
                        messages=self.messages,
                        tools=selected_tools,
                        action_type=action_type,
                    ),
                )["response"]
                
                self.messages.append({"role": "assistant", "content": response.response_message})

                self.rounds += 1


            final_result = self.messages[-1]["content"]
            
            return {
                "agent_name": self.agent_name,
                "result": final_result,
                "rounds": self.rounds,
            }

        else:
            return {
                "agent_name": self.agent_name,
                "result": "Failed to generate a valid workflow in the given times.",
                "rounds": self.rounds,
            }
            
    except Exception as e:

        return {}
```
#### Run your new developed agents
To run your new developed agents, you can pass the absolute path for the agent and assign the task using the aios_demo.py script by setting up the llm_name and the llm_backend. 
```
python aios_demo.py --llm_name <llm_name> --llm_backend <llm_backend> --
```


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




