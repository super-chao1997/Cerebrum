from cerebrum.llm.apis import llm_chat, llm_chat_with_json_output, llm_chat_with_tool_call_output

from litellm import completion

from cerebrum.tool.mcp_tool import MCPPool, MCPClient

class ReActAgent:
    def __init__(self, on_aios: bool = True):
        self.agent_name = "react"
        self.on_aios = on_aios
        self.mcp_pool = self.init_mcp_pool()
        
    def init_mcp_pool(self):
        mcp_pool = MCPPool()
        mcp_pool.add_mcp_client(
            "playwright",
            MCPClient.from_npx(
                "@playwright/mcp@latest",
                suffix_args=[
                    "--headless"
                ],
            ),
        )
        return mcp_pool
        
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
    
    def run_gaia(self, **kwargs):
        task_prompt = kwargs.get("Question", "")
        
        tools = kwargs.get("Annotator Metadata", {}).get("Tools", [])
        
        breakpoint()
        
        system_prompt = f"""You have to utilize your available tools to solve the task.

Here is the overall task: {task_prompt}. Never forget the task!

Please give instructions based on your expertise to complete the task. An instruction is typically a sub-task or question.

You must leverage your available tools from the following list: {tools}, try your best to solve the problem, and explain your solutions as the following format: 
<SOLUTION> Solutions should be specific, including detailed explanations and provide preferable detailed implementations and examples and lists for task-solving.
Please note that the overall task may be very complicated. Here are some tips that may help you solve the task:
</SOLUTION>
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
Identify the next step to take. 
If you identify some tools that are required to complete the task, you must identify the tool in the format of:
<TOOL>
TOOL_NAME
</TOOL>
            """
            messages.append({"content": step_instructions, "role": "user"})
            response = llm_chat(
                self.agent_name, messages,
                llms=[
                    # {
                    #     "name": "gemini-2.0-flash",
                    #     "backend": "google",
                    # }
                    {
                        "name": "qwen2.5:7b",
                        "backend": "ollama",
                    }
                ],
            )
            step_response = response["response"]["response_message"]
            
            if "TASK_DONE" in step_response:
                break
            
            breakpoint()
            
            messages.append({"content": step_response, "role": "assistant"})
            
            if "<TOOL>" in step_response:
                tool_name = step_response.split("<TOOL>")[1].split("</TOOL>")[0]
                
                tool_schemas = self.mcp_pool.get_tool_schema(tool_name)
                messages.append({"content": "Based on the current step, call the tool you need to call.", "role": "user"})
                tool_call_response = llm_chat_with_tool_call_output(
                    self.agent_name, messages,
                    tools=tool_schemas
                )
                tool_calls = tool_call_response["response"]["tool_calls"]
                tool_call_result = ""
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["parameters"]
                    tool_result = self.mcp_pool.run_tool(tool_name, tool_args)
                    tool_call_result += f"Tool {tool_name} called with arguments: {tool_args}. Result: {tool_result}\n"
                    
                messages.append({"content": tool_call_result, "role": "assistant"})
            
            
