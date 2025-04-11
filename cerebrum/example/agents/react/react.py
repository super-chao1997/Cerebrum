from cerebrum.llm.apis import llm_chat, llm_chat_with_json_output, llm_chat_with_tool_call_output

from litellm import completion

from benchmarks.utils import get_parser

from datasets import load_dataset

from dotenv import load_dotenv

from typing import List, Dict, Any

import asyncio

import json

import uuid

from cerebrum.example.agents.browser_use_agent.agent import BrowserUseAgent
from cerebrum.example.agents.code_executor.agent import CodeExecutor
from cerebrum.example.agents.calculator_agent.agent import CalculatorAgent

load_dotenv()

class ReActAgent:
    def __init__(self, on_aios: bool = True):
        self.agent_name = "react"
        self.on_aios = on_aios
        self.max_steps = 20
        self.workers = {
            "browser_use_agent": BrowserUseAgent(),
            # "code_executor": CodeExecutor(),
            # "calculator_agent": CalculatorAgent()
        }
    
    async def initialize(self):
        """Initialize all workers"""
        for worker in self.workers.values():
            await worker.initialize()
    
    async def get_all_tool_call_map(self):
        """Get a map of all available tool calls from all workers"""
        tool_call_maps = {}
        for worker in self.workers.values():
            for tool_info in worker.get_tool_information():
                tool_name = tool_info["name"]
                tool_call_maps[tool_name] = getattr(worker, tool_name)
        return tool_call_maps
    
    async def get_all_tool_information(self):
        """Get all tool information from all workers"""
        all_tool_information = []
        for worker in self.workers.values():
            all_tool_information.extend(worker.get_tool_information())
        return all_tool_information
    
    def get_all_tool_hints(self):
        """Get formatted tool hints from all workers"""
        hints = ""
        for worker in self.workers.values():
            hints += worker.get_tool_hints()
        return hints
    
    def get_all_worker_hints(self):
        """Get formatted worker hints from all workers"""
        hints = ""
        for worker_name, worker in self.workers.items():
            hints += f"- {worker_name}: {worker.description}\n"
        return hints
    
    def get_tool_schemas_by_name(self, tool_name: str):
        """Get tool schema by name from any worker"""
        for worker in self.workers.values():
            for tool_info in worker.get_tool_information():
                if tool_info["name"] == tool_name:
                    return tool_info["schema"]
        return None
    
    async def run(self, task_input: str):
        await self.initialize()
        
        worker_hints = self.get_all_worker_hints()
                
        llms = [    
            {
                "name": "gpt-4o-mini",
                "backend": "openai"
                # "name": "qwen2.5:72b",
                # "backend": "ollama"
                # "name": "Qwen/Qwen2.5-72B-Instruct",
                # "backend": "sglang"
            }
        ]
        
        system_prompt = f"""# Task Orchestration Instructions

You are an orchestrator agent responsible for coordinating specialized workers to solve complex tasks. Your goal is to break down the main task into subtasks and assign them to appropriate workers.

## Main Task
{task_input}

## Available Workers
{worker_hints}

## Your Responsibilities:
1. **Analyze the task** and break it down into logical subtasks
2. **Assign subtasks** to appropriate workers from your available list
3. **Coordinate the workflow** by processing each worker's output
4. **Synthesize results** into a comprehensive solution
5. **Verify completeness** before finalizing

## Worker Assignment Protocol:
- Before assigning a task to a worker, carefully assess if that worker is truly necessary
- When you need to assign a task to a worker, use this exact format:
  ```
  <WORKER>WORKER_NAME</WORKER>
  ```
- The WORKER_NAME must exactly match a name in your available worker list
- Include clear, specific instructions for the worker

## Solution Requirements:
- Provide detailed explanations for each step
- Include specific implementations and examples where appropriate
- Ensure your solution directly addresses the original task
- If one approach fails, try alternative methods

## Completion Protocol:
- Before submitting your final answer, double-check that you've fully completed the task
- Verify your solution against the original requirements
- When you're confident the task is complete, format your answer as:
  ```
  <FINAL_ANSWER>[brief one-line summary of the task result]</FINAL_ANSWER>
  ```
- Only use the FINAL_ANSWER tag when the task is truly complete

## Problem-Solving Tips:
- Try multiple approaches if your first method fails
- For web searches, check Wikipedia first before exploring other sources
- When searching, use advanced filters when appropriate (date, location, etc.)
- For math problems, consider using Python with the sympy library
- Always verify your answers through cross-checking
- Don't rely solely on your knowledge - use available tools
- When executing code, debug any errors rather than assuming correct results
- Search results rarely provide complete answers - use them to find sources for further analysis
- For file downloads, use web browser simulation or write appropriate code"""
        
        messages = [
            {"content": system_prompt, "role": "system"}
        ]
        
        # response = llm_chat(
        #     agent_name=self.agent_name,
        #     messages=messages,
        #     llms=llms
        # )
        
        # print(response)
        final_answer = ""
        
        # breakpoint()
        rounds = 0
        
        while rounds < self.max_steps:
            step_instructions = """
## Step-by-Step Execution Protocol:
- Clearly state what you're trying to accomplish in this specific step
- Ask yourself: "What is the single most important action I can take right now?"
- Identify only the next immediate action needed
- Consider which worker (if any) is best suited for this specific subtask
Remember: Complex problems are solved through a series of well-executed individual steps. Stay focused on the current step, complete it thoroughly, and then move forward. Don't try to solve everything at once.
            """
            messages.append({"content": step_instructions, "role": "user"})
            
            breakpoint()
            
            response = llm_chat(
                agent_name=self.agent_name,
                messages=messages,
                llms=llms
            )
                        
            step_response = response["response"]["response_message"]
            
            if "<FINAL_ANSWER>" in step_response:
                final_answer = step_response.split("<FINAL_ANSWER>")[1].split("</FINAL_ANSWER>")[0]
                await self.cleanup()
                break
            
            messages.append({"content": step_response, "role": "assistant"})
            
            print(messages[-1])
            
            if "<WORKER>" in step_response:
                worker_name = step_response.split("<WORKER>")[1].split("</WORKER>")[0]
                
                summarization_prompt = f"""
[One-sentence summary of what needs to be accomplished by the worker]
Things that are needed to be included:
- [Specify exactly what you need the worker to produce]
- [Format requirements if applicable]
- [Any limitations or boundaries for this specific subtask]
- [Time constraints, resource limitations, etc. if applicable]
                """
                breakpoint()
                assigned_task = llm_chat(
                    agent_name=self.agent_name,
                    messages=messages + [{"content": summarization_prompt, "role": "user"}],
                    llms=llms
                )["response"]["response_message"]
                
                breakpoint()
                result = await self.workers[worker_name].run(assigned_task)
            
                messages.append({"content": result, "role": "assistant"})
                
            rounds += 1
        
        return {
            "agent_name": self.agent_name,
            "result": final_answer,
            "rounds": rounds
        }
    
    async def cleanup(self):
        """Cleanup all resources"""
        try:
            for worker in self.workers.values():
                try:
                    await worker.cleanup()
                except Exception as e:
                    print(f"Error cleaning up worker: {e}")
        except Exception as e:
            print(f"Error during cleanup: {e}")

async def main():
    agent = ReActAgent()
    
    data = {
        "Question": """
Get the temperature difference between Edison and New York today. 
""",
        "Tools": "1. Web browser, 2. Calculator"
    }
    
    result = await agent.run(data["Question"])
    print(result)
    
if __name__ == "__main__":
    main_parser = get_parser()
    main_args = main_parser.parse_args()
    dataset = load_dataset(main_args.data_name, "2023_all", split=main_args.split)
    asyncio.run(main())

