from cerebrum.tool.mcp_tool import MCPPool, MCPClient
from typing import List, Dict, Any
import asyncio
from cerebrum.llm.apis import llm_chat, llm_chat_with_tool_call_output

class WebSearchWorker:
    def __init__(self):
        self.name = "web_search_worker"
        self.mcp_pool = MCPPool()
        self.description = "Interact with web pages to search for information"
    
    async def initialize(self):
        """Initialize the web search worker with its own MCP client"""
        playwright_client = MCPClient.from_npx(
            pkg_name="@playwright/mcp@latest",
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
    
    async def execute(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        tool_information = await self.get_all_tool_information()
        tool_hints = self.get_tool_hints(tool_information)
        tool_call_maps = await self.get_all_tool_call_maps()
        llms = [
            {
                "name": "gpt-4o",
                "backend": "openai",
            }
        ]
        # breakpoint()
        tool_schemas = self.get_all_tool_schemas(tool_information)
        """Execute web search using the playwright MCP"""
        system_prompt = f"""You are a web search agent. You are given a question and you can leverage the following tool list: {tool_hints} to perform web search. 
It is important to note that your duty is just to perform web search, you do not need to do any other tasks like mathematical calculations.
If you find a tool is required to solve the problem, you must identify the tool in the following format:
<TOOL>TOOL_NAME exactly exist in the tool list.</TOOL>
When you believe you have successfully completed the overall task at a step, you MUST output the final answer in the following format:
<FINAL_ANSWER>[brief one-line summary of what the task result is]</FINAL_ANSWER>"""
        web_search_messages = [
            {
                "role": "system",
                "content": system_prompt
            },
        ]
        
        web_search_messages.extend(messages[1:])
        
        final_result = ""
        
        while True:
            step_response = llm_chat(
                agent_name=self.name,
                messages=web_search_messages,
                llms=llms
            )["response"]["response_message"]
            
            breakpoint()
            
            web_search_messages.append({"content": step_response, "role": "assistant"})
            
            if "<FINAL_ANSWER>" in step_response:
                final_result = step_response.split("<FINAL_ANSWER>")[1].split("</FINAL_ANSWER>")[0]
                break
            
            if "<TOOL>" in step_response:
                tool_name = step_response.split("<TOOL>")[1].split("</TOOL>")[0]
                tool_schemas = self.get_all_tool_schemas(tool_information, tool_name)
            
                tool_calls = llm_chat_with_tool_call_output(
                    agent_name=self.name,
                    messages=web_search_messages,
                    tools=tool_schemas,
                    llms=llms
                )["response"]["tool_calls"]
            
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["parameters"]
                    tool_result = await tool_call_maps[tool_name](**tool_args)
                    web_search_messages.append({"content": tool_result, "role": "assistant"})
        
        return final_result
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.mcp_pool.stop()
