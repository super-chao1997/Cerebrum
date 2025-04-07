from cerebrum.llm.apis import llm_chat, llm_chat_with_json_output, llm_chat_with_tool_call_output

from litellm import completion

from benchmarks.utils import get_parser

from datasets import load_dataset

from dotenv import load_dotenv

from typing import List, Dict, Any

import asyncio

import json

import uuid

from web_search_worker import WebSearchWorker
from code_execution_worker import CodeExecutionWorker
from calculator import CalculatorWorker

load_dotenv()

class ReActAgent:
    def __init__(self, on_aios: bool = True):
        self.agent_name = "react"
        self.on_aios = on_aios
        self.workers = {
            "web_search": WebSearchWorker(),
            # "code_executor": CodeExecutionWorker(),
            "calculator": CalculatorWorker()
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
    
    async def run_gaia(self, **kwargs):
        task_prompt = kwargs.get("Question", "")
        
        await self.initialize()
        
        worker_hints = self.get_all_worker_hints()
                
        llms = [
            {
                "name": "gpt-4o",
                "backend": "openai"
            }
        ]
        
        system_prompt = f"""You have to utilize your available workers to solve the task.
Here is the overall task: {task_prompt}. Never forget the task!
Please give instructions based on your expertise to complete the task. An instruction is typically a sub-task or question.
You must leverage your available workers: {worker_hints}, try your best to solve the problem, and explain your solutions as the following format:
Solutions should be specific, including detailed explanations and provide preferable detailed implementations and examples and lists for task-solving.
At each step, if you identify a worker that are required to complete the task, you must identify the worker in the format of:
<WORKER>WORKER_NAME exactly exist in the worker list.</WORKER>
Be careful that you do not need to call a worker every time, so before you call a worker, you should think carefully whether it is necessary to call the worker.
When you believe you have successfully completed the overall task at a step, you MUST output the final answer in the following format:
<FINAL_ANSWER>[brief one-line summary of what the task result is]</FINAL_ANSWER>
Before this line, you should double check to ensure the task is completed and verify that your result answers the task requirement.
If the task is not yet completed, do NOT output the TASK_DONE signal. Continue searching, computing, or analyzing until you believe it is complete.
Please note that the overall task may be very complicated. Here are some tips that may help you solve the task:
<tips>
- If one way fails to provide an answer, try other ways or methods. The answer does exist.
- If the search snippet is unhelpful but the URL comes from an authoritative source, try visit the website for more details.  
- When looking for specific numerical values (e.g., dollar amounts), prioritize reliable sources and avoid relying only on search snippets.  
- When solving tasks that require web searches, check wikipedia first before exploring other websites.  
- When using web search, remember to check advanced search options or filterson the search engine if your search condition requires multiple filters like date, location, etc.
- When trying to solve math problems, you can try to write python code and use sympy library to solve the problem.
- Always verify the accuracy of your final answers! Try cross-checking the answers by other ways. (e.g., screenshots, webpage analysis, etc.).  
- Do not be overly confident in your own knowledge. Searching can provide a broader perspective and help validate existing knowledge.  
- After writing codes, do not forget to run the code and get the result. If it encounters an error, try to debug it. Also, bear in mind that the code execution environment does not support interactive input.
- When a tool fails to run, or the code does not run correctly, never assume that it returns the correct result and continue to reason based on the assumption, because the assumed result cannot lead you to the correct answer. The right way is to think about the reason for the error and try again.
- Search results typically do not provide precise answers. It is not likely to find the answer directly using search toolkit only, the search query should be concise and focuses on finding sources rather than direct answers, as it always need to use other tools to further process the url, e.g. interact with the webpage, extract webpage content, etc. 
- For downloading files, you can either use the web browser simulation toolkit or write codes.
</tips>"""
        
        messages = [
            {"content": system_prompt, "role": "system"}
        ]
        
        while True:
            step_instructions = """
Identify the next step to take. Focus on the current single step and do not overthink. 
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
                return final_answer
            
            messages.append({"content": step_response, "role": "assistant"})
            
            print(messages[-1])
            
            if "<WORKER>" in step_response:
                worker_name = step_response.split("<WORKER>")[1].split("</WORKER>")[0]
                breakpoint()
                result = await self.workers[worker_name].execute(messages)
            
                messages.append({"content": result, "role": "assistant"})
    
    async def cleanup(self):
        """Cleanup all resources"""
        for worker in self.workers.values():
            await worker.cleanup()

async def main():
    agent = ReActAgent()
    
    data = {
        "Question": """
Get the temperature difference between Edison and New York today. 
""",
        "Tools": "1. Web browser, 2. Calculator"
    }
    
    result = await agent.run_gaia(**data)
    print(result)
    
if __name__ == "__main__":
    main_parser = get_parser()
    main_args = main_parser.parse_args()
    dataset = load_dataset(main_args.data_name, "2023_all", split=main_args.split)
    asyncio.run(main())

