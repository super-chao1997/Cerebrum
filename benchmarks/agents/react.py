from cerebrum.llm.apis import llm_chat, llm_chat_with_json_output, llm_chat_with_tool_call_output

from litellm import completion

from cerebrum.tool.mcp_tool import MCPPool, MCPClient

from benchmarks.utils import get_parser

from datasets import load_dataset

from dotenv import load_dotenv

from typing import List

import asyncio

import json

import uuid

load_dotenv()

class ReActAgent:
    def __init__(self, on_aios: bool = True, mcp_pool = None):
        self.agent_name = "react"
        self.on_aios = on_aios
        self.mcp_pool = mcp_pool
    
    def get_all_tool_hints(self, tool_information: List[dict]):
        hints = ""
        for tool_info in tool_information:
            hint = tool_info['hint']
            hints += f"- {hint}\n"
        return hints
    
    def get_tool_hint_by_name(self, tool_information: List[dict], tool_name: str):
        for tool_info in tool_information:
            if tool_info['name'] == tool_name:
                return tool_info['hint']
        return ""
    
    def get_tool_schemas_by_name(self, tool_information: List[dict], tool_name: str):
        for tool_info in tool_information:
            if tool_info['name'] == tool_name:
                return tool_info['schema']
        return ""
    
    def get_all_tool_schemas(self, tool_information: List[dict]):
        schemas = []
        for tool_info in tool_information:
            schemas.append(tool_info["schema"])
        return schemas
    
    async def get_all_tool_call_map(self):
        tool_call_maps = {}
        for client in self.mcp_pool.get_all_mcp_clients():
            for tool in await client.get_available_tools():
                tool_call_maps[tool.name] = client.call_tool(tool.name)
        return tool_call_maps
    
    async def get_all_tool_information(self, client_name: str = None):
        clients = self.mcp_pool.get_all_mcp_clients() if client_name is None else [self.mcp_pool.get_mcp_client(client_name)]
        all_tool_information = []
        for client in clients:
            tool_info = await client.get_all_tool_information()
            all_tool_information.extend(tool_info)
        return all_tool_information
    
    def get_client_description(self, client_name: str=None):
        client_descriptions = ""
        clients = self.mcp_pool.get_all_mcp_clients() if client_name is None else [self.mcp_pool.get_mcp_client(client_name)]
        for client in clients:
            client_descriptions += f"- {client.name}: {client.description}\n"
        return client_descriptions
    
    
    def generator_tool_call_id():
        """
        Generate a unique identifier for a tool call.

        This function creates a new UUID (Universally Unique Identifier) and returns it as a string.

        Returns:
            str: A unique tool call ID.
        
        Example:
            ```python
            tool_call_id = generator_tool_call_id()
            print(tool_call_id)  # Example output: 'f3f2e850-b5d4-11ef-ac7e-96584d5248b2'
            ```
        """
        return str(uuid.uuid4())

    def decode_litellm_tool_calls(self,response):
        """
        Decode tool call responses from LiteLLM API format.

        Args:
            response: The response object from LiteLLM API.

        Returns:
            list: A list of dictionaries, each containing:
                - "name": The name of the function being called.
                - "parameters": The arguments passed to the function.
                - "id": The unique identifier of the tool call.

        Example:
            ```python
            response = <LiteLLM API response>
            decoded_calls = decode_litellm_tool_calls(response)
            print(decoded_calls)  
            # Output: [{'name': 'translate', 'parameters': {'text': 'hello', 'lang': 'fr'}, 'id': 'uuid1234'}]
            ```
        """
        decoded_tool_calls = []
        
        if response.choices[0].message.content is None:
            assert response.choices[0].message.tool_calls is not None
            tool_calls = response.choices[0].message.tool_calls

            for tool_call in tool_calls:
                parameters = tool_call.function.arguments
                if isinstance(parameters, str):
                    parameters = json.loads(parameters)
                decoded_tool_calls.append(
                    {
                        "name": tool_call.function.name,
                        "parameters": parameters,
                        "id": tool_call.id
                    }
                )
        else:
            assert response.choices[0].message.content is not None
            
            # breakpoint()
            tool_calls = response.choices[0].message.content
            if isinstance(tool_calls, str):
                tool_calls = json.loads(tool_calls)
            
            if not isinstance(tool_calls, list):
                tool_calls = [tool_calls]
                
            for tool_call in tool_calls:
                decoded_tool_calls.append(
                    {
                        "name": tool_call["name"],
                        "parameters": tool_call["arguments"],
                        "id": self.generator_tool_call_id()
                    }
                )
            
        return decoded_tool_calls
    
    def run_swebench(self, input_str: str):
        messages = [
            {"content": "You are a helpful assistant that can answer questions and help with tasks.", "role": "system"},
            {"content": input_str, "role": "user"}
        ]
        if self.on_aios:
            response = llm_chat(
                agent_name=self.agent_name, 
                messages=messages,
                llms=[
                    {
                        "model": "gpt-4o-mini",
                        "backend": "openai",
                    }
                ],
                temperature=1.0
            )
        else:
            response = completion(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.0,
            )
        result = response["response"]["response_message"]
        
        return result
    
    def run_humaneval(self, input_str: str):
        system_prompt = """You are an AI assistant good at coding. You will receive a function definition and
        comments. You need to help me complete this function. The completion should strictly follow the following format and requirements:
        
        Format:
        <FINAL_ANSWER>
        YOUR FINAL ANSWER
        </FINAL_ANSWER>
        
        Requirements: 
        1. YOUR FINAL ANSWER must be a piece of code that can be directly filled into the given code at the <CURRENT_CURSOR_POSITION> marker.
        2. Only include the code you're adding, don't include the original function definition or comments.
        3. Do not use extra code quotes like ```python``` to wrap the code.
        4. Make sure the syntax of the code is correct, especially pay attention to proper indentation.
        5. Maintain the same indentation level as the surrounding code.
        6. If you're completing a function body, ensure all code is properly indented inside the function.
        7. Check that all return statements, loops, and conditional blocks have correct indentation.
        8. Ensure your code aligns with the original code style and indentation pattern.
        
        Example of proper formatting:
        For a function like:
        ```
        def example_function(x):
            # Some comment
            # More comments
        ```
        
        Your answer should be:
        <FINAL_ANSWER>
            result = x * 2
            return result
        </FINAL_ANSWER>
        
        Notice how the code maintains proper indentation relative to the function definition.
        """
        messages = [
            {"content": system_prompt, "role": "system"},
            {"content": f"Given the following code: {input_str}, complete the function. ", "role": "user"}
        ]
        if self.on_aios:
            response = llm_chat(self.agent_name, messages)
            result = response["response"]["response_message"]
        else:
            response = completion(
                model="gpt-4o-mini",
                messages=messages,
                temperature=1.0,
            )
        return result
    
    def decode_litellm_tool_call(self, tool_call: dict):
        tool_name = tool_call["name"]
        tool_args = tool_call["parameters"]
        return tool_name, tool_args
    
    async def run_gaia(self, **kwargs):
        task_prompt = kwargs.get("Question", "")
        
        tools = kwargs.get("Annotator Metadata", {}).get("Tools", [])
        
        # client_descriptions = self.get_client_description()
        tool_information = await self.get_all_tool_information()
        
        tool_call_maps = await self.get_all_tool_call_map()
        
        llms = [
            {
                "name": "gpt-4o",
                "backend": "openai",
            }
        ]
        
        breakpoint()
        
        tool_hints = self.get_all_tool_hints(tool_information)
        
        system_prompt = f"""You have to utilize your available tools to solve the task.

Here is the overall task: {task_prompt}. Never forget the task!

Please give instructions based on your expertise to complete the task. An instruction is typically a sub-task or question.

You must leverage your available tools from the tool list: {tool_hints}, try your best to solve the problem, and explain your solutions as the following format: 
Solutions should be specific, including detailed explanations and provide preferable detailed implementations and examples and lists for task-solving.
Please note that the overall task may be very complicated. Here are some tips that may help you solve the task:
<tips>
- If one way fails to provide an answer, try other ways or methods. The answer does exist.
- If the search snippet is unhelpful but the URL comes from an authoritative source, try visit the website for more details.  
- When looking for specific numerical values (e.g., dollar amounts), prioritize reliable sources and avoid relying only on search snippets.  
- When solving tasks that require web searches, check Wikipedia first before exploring other websites.  
- When trying to solve math problems, you can try to write python code and use sympy library to solve the problem.
- Always verify the accuracy of your final answers! Try cross-checking the answers by other ways. (e.g., screenshots, webpage analysis, etc.).  
- Do not be overly confident in your own knowledge. Searching can provide a broader perspective and help validate existing knowledge.  
- After writing codes, do not forget to run the code and get the result. If it encounters an error, try to debug it. Also, bear in mind that the code execution environment does not support interactive input.
- When a tool fails to run, or the code does not run correctly, never assume that it returns the correct result and continue to reason based on the assumption, because the assumed result cannot lead you to the correct answer. The right way is to think about the reason for the error and try again.
- Search results typically do not provide precise answers. It is not likely to find the answer directly using search toolkit only, the search query should be concise and focuses on finding sources rather than direct answers, as it always need to use other tools to further process the url, e.g. interact with the webpage, extract webpage content, etc. 
- For downloading files, you can either use the web browser simulation toolkit or write codes.
</tips>"""
        messages = [
            {"content": system_prompt, "role": "system"},
            # {"content": "Based on the overall task, generate the workflow you will take to solve the task.", "role": "user"}
        ]
        
        while True:
            step_instructions = """
Identify the next step to take. Focus on the current single step and do not overthink. 
If you identify a client that are required to complete the task, you must identify the client in the format of:
<TOOL>TOOL_NAME exactly exist in the tool list.</TOOL>
But you do not need to call a tool every time, so be careful.
            """
            breakpoint()
            messages.append({"content": step_instructions, "role": "user"})
            # response = llm_chat(
            #     agent_name=self.agent_name,
            #     messages=messages,
            #     llms=llms
            # )
            
            # step_response = response["response"]["response_message"]
            response = completion(
                model="gemini/gemini-2.0-flash",
                messages=messages,
                temperature=1.0,
            )
            step_response = response.choices[0].message.content
            
            breakpoint()
            
            
            if "TASK_DONE" in step_response:
                break
            
            breakpoint()
            
            messages.append({"content": step_response, "role": "assistant"})
            
            if "<TOOL>" in step_response:
                tool_name = step_response.split("<TOOL>")[1].split("</TOOL>")[0]
                
                tool_schemas = self.get_tool_schemas_by_name(tool_information, tool_name)
                
                if not isinstance(tool_schemas, list):
                    tool_schemas = [tool_schemas]
                
                breakpoint()
                messages.append({"content": f"Identify the tool parameters of tool {tool_name} to solve the problem for the current step.", "role": "user"})
                # tool_call_response = llm_chat_with_tool_call_output(
                #     agent_name=self.agent_name,
                #     messages=messages,
                #     llms=llms,
                #     tools=tool_schemas,
                # )
                # tool_calls = tool_call_response["response"]["tool_calls"]
                tool_call_response = completion(
                    model="gemini/gemini-2.0-flash",
                    messages=messages,
                    temperature=1.0,
                    tools=tool_schemas,
                    tool_choice="required"
                )
                
                breakpoint()
                # tool_calls = tool_call_response.choices[0].message.tool_calls
                tool_calls = self.decode_litellm_tool_calls(tool_call_response)
                tool_call_result = ""
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["parameters"]
                    tool_result = await tool_call_maps[tool_name](**tool_args)
                    tool_call_result += f"Tool {tool_name} called with arguments: {tool_args}. Result: {tool_result}\n"
                    
                messages.append({"content": tool_call_result, "role": "assistant"})

async def main():
    mcp_pool = MCPPool()
    mcp_pool.add_mcp_client(
        "playwright",
        MCPClient.from_npx(
            pkg_name="@playwright/mcp@latest",
            description="Interact with web pages through structured accessibility snapshots, bypassing the need for screenshots or visually-tuned models.",
            suffix_args=["--headless"]
        )
    )
    mcp_pool.add_mcp_client(
        "desktop-commander",
        MCPClient.from_smithery(
            "@wonderwhy-er/desktop-commander",
            "Execute terminal commands and manage files with diff editing capabilities. Coding, shell and terminal, task automation."
        )
    )
    await mcp_pool.start()
    
    agent = ReActAgent(mcp_pool=mcp_pool)
    
    for data in dataset:
        result = await agent.run_gaia(**data)
        breakpoint()
        # print(result)
        break

if __name__ == "__main__":
    main_parser = get_parser()
    
    main_args = main_parser.parse_args()

    dataset = load_dataset(main_args.data_name, "2023_all", split=main_args.split)
    
    asyncio.run(main())