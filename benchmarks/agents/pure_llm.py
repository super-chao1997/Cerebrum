from cerebrum.llm.apis import llm_chat

from litellm import completion

class PureLLM:
    def __init__(self, on_aios: bool = True):
        self.agent_name = "llm"
        self.on_aios = on_aios

    def run_swebench(self, input_str: str):
        messages = [
            {"content": "You are a helpful assistant that can answer questions and help with tasks.", "role": "system"},
            {"content": input_str, "role": "user"}
        ]
        if self.on_aios:
            response = llm_chat(self.agent_name, messages)
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
        comments. You need to help me complete this function. I will help you check your code. If you think it is ok to
        give the final answer. Give me final output in the format:
        <FINAL ANSWER>
        YOUR FINAL ANSWER (YOUR FINAL ANSWER must be a piece of code that you want to add. Just
        contains what you add, don't contains original definition and comments)
    </FINAL ANSWER>"""
        messages = [
            {"content": system_prompt, "role": "system"},
            {"content": input_str, "role": "user"}
        ]
        if self.on_aios:
            response = llm_chat(self.agent_name, messages)
        else:
            response = completion(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.0,
            )
        result = response["response"]["response_message"]
        return result
    
    def run_gaia(self, input_str: str):
        messages = [
            {"content": input_str, "role": "user"}
        ]
        if self.on_aios:
            response = llm_chat(self.agent_name, messages)
        else:
            response = completion(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.0,
            )
        result = response["response"]["response_message"]
        return result