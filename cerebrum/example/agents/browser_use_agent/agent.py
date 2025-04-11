from cerebrum.tool.mcp_tool import MCPPool, MCPClient
from typing import List, Dict, Any
import asyncio
from cerebrum.llm.apis import llm_chat, llm_chat_with_tool_call_output

class BrowserUseAgent:
    def __init__(self):
        self.name = "browser_use_agent"
        self.mcp_pool = MCPPool()
        self.description = "Interact with web pages to search for information"
        self.max_steps = 20
        
    async def initialize(self):
        """Initialize the web search worker with its own MCP client"""
        # playwright_client = MCPClient.from_npx(
        #     pkg_name="@playwright/mcp@latest",
        #     description="Interact with web pages through structured accessibility snapshots, bypassing the need for screenshots or visually-tuned models.",
        #     suffix_args=["--headless"]
        # )
        playwright_client = MCPClient.from_npx(
            pkg_name="@executeautomation/playwright-mcp-server",
            description="Interact with web pages through structured accessibility snapshots, bypassing the need for screenshots or visually-tuned models.",
            suffix_args=["--headless"]
        )
        self.mcp_pool.add_mcp_client("playwright", playwright_client)
        await self.mcp_pool.start()
    
    async def get_all_tool_information(self) -> List[Dict[str, Any]]:
        """Get all tool information for this worker"""
        all_tool_information = []
        for client in self.mcp_pool.get_all_mcp_clients():
            tool_information = await client.get_all_tool_information()
            all_tool_information.extend(tool_information)
        return all_tool_information
    
    def get_tool_hints(self, tool_information: List[Dict[str, Any]]) -> str:
        """Get formatted tool hints for this worker"""
        hints = ""
        for tool_info in tool_information:
            hint = tool_info['hint']
            hints += f"- {hint}\n"
        return hints
    
    async def get_all_tool_call_maps(self) -> Dict[str, Any]:
        """Get all tool call maps for this worker"""
        tool_call_maps = {}
        for client in self.mcp_pool.get_all_mcp_clients():
            for tool in await client.get_available_tools():
                # breakpoint()
                tool_call_maps[tool.name] = client.call_tool(tool.name)
        return tool_call_maps
    
    def get_all_tool_schemas(self, tool_information: List[Dict[str, Any]], tool_name: str=None) -> str:
        """Get all tool schemas for this worker"""
        all_tool_schemas = []
        filtered_tool_information = tool_information if tool_name is None else [tool_info for tool_info in tool_information if tool_info["name"] == tool_name]
        for tool_info in filtered_tool_information:
            tool_schema = tool_info['schema']
            if "$schema" in tool_schema:
                tool_schema.pop("$schema")
            all_tool_schemas.append(tool_schema)
        return all_tool_schemas
    
    async def run(self, task_input: str):
        tool_information = await self.get_all_tool_information()
        tool_hints = self.get_tool_hints(tool_information)
        tool_call_maps = await self.get_all_tool_call_maps()
        llms = [
            {
                "name": "gpt-4o-mini",
                "backend": "openai",
                # "name": "qwen2.5:72b",
                # "backend": "ollama"
                # "name": "Qwen/Qwen2.5-72B-Instruct",
                # "backend": "sglang"
            }
        ]
        # breakpoint()
        tool_schemas = self.get_all_tool_schemas(tool_information)
        """Execute web search using the playwright MCP"""
        system_prompt = f"""
You are a specialized browser use agent designed to interact with web interfaces. Your primary function is to navigate websites, extract information, and interact with web elements to accomplish tasks.

## Task Protocol
1. **Always keep the overall task in mind**: {task_input}
2. **Focus exclusively on browser-related actions**
   - Do NOT perform calculations, analysis, or other non-browsing tasks

## Available Tools
You have access to the following tools: {tool_hints}

## Tool Usage
When you need to use a tool:
```
<TOOL>TOOL_NAME</TOOL>
```
The TOOL_NAME must exactly match one from your available tool list.

## Task Completion
Before submitting your final answer:
1. **Carefully review all information** you've gathered through browser interactions
2. **Verify the accuracy** of your findings across multiple sources when possible
3. **Ensure completeness** - check that you've addressed all aspects of the task
4. **Cross-reference information** to confirm consistency

Only when you are certain your findings are accurate and complete:
```
<FINAL_ANSWER>[brief one-line summary of verified findings from browser interactions]</FINAL_ANSWER>
```"""
        web_search_messages = [
            {
                "role": "system",
                "content": system_prompt
            },
        ]
        
        web_search_messages.append({"content": task_input, "role": "user"})
        
        final_result = ""
        
        rounds = 0
        
        while rounds < self.max_steps:
            step_instructions = """## Step-by-Step Execution Protocol:
- Clearly state what you're trying to accomplish in this specific step
- Ask yourself: "What is the single most important action I can take right now?"
- Identify only the next immediate action needed
- Consider which worker (if any) is best suited for this specific subtask
Remember: Complex problems are solved through a series of well-executed individual steps. Stay focused on the current step, complete it thoroughly, and then move forward. Don't try to solve everything at once.
"""
            web_search_messages.append({"content": step_instructions, "role": "user"})
            
            step_response = llm_chat(
                agent_name=self.name,
                messages=web_search_messages,
                llms=llms
            )["response"]["response_message"]
            
            # breakpoint()
            web_search_messages.append({"content": step_response, "role": "assistant"})
            
            print(web_search_messages[-1])
            
            
            if "<FINAL_ANSWER>" in step_response:
                final_result = step_response.split("<FINAL_ANSWER>")[1].split("</FINAL_ANSWER>")[0]
                break
            
            if "<TOOL>" in step_response:
                tool_name = step_response.split("<TOOL>")[1].split("</TOOL>")[0]
                tool_schemas = self.get_all_tool_schemas(tool_information, tool_name)
                
                web_search_messages.append(
                    {"content": f"Identify the parameters for the tool {tool_name} to perform the browser operation", "role": "user"}
                )
            
                tool_call_response = llm_chat_with_tool_call_output(
                    agent_name=self.name,
                    messages=web_search_messages,
                    tools=tool_schemas,
                    llms=llms
                )
                
                breakpoint()
                
                tool_calls = tool_call_response["response"]["tool_calls"]
                
                print(tool_calls)
            
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["parameters"]
                    tool_result = await tool_call_maps[tool_name](**tool_args)
                    web_search_messages.append({"content": f"I have successfully call the tool {tool_name} with the parameters of {tool_args} and get the following result: {tool_result}", "role": "assistant"})

            rounds += 1
            
        return {
            "agent_name": self.name,
            "result": final_result,
            "rounds": rounds
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.mcp_pool.stop()
