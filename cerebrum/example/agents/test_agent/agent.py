from cerebrum.llm.apis import LLMQuery, LLMResponse, llm_chat, llm_call_tool
import json

from cerebrum.config.config_manager import config

aios_kernel_url = config.get_kernel_url()

class TestAgent:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.messages = []

    def run(self, task_input):
        self.messages.append({"role": "user", "content": task_input})
        
        tool_response = llm_chat(
            agent_name=self.agent_name,
            messages=self.messages,
            base_url=aios_kernel_url
        )
        
        final_result = tool_response["response"]["response_message"]
        return final_result
        
def main():
    parser = argparse.ArgumentParser(description="Run test agent")
    parser.add_argument("--task_input", type=str, required=True, help="Task input for the agent")
    args = parser.parse_args()

    agent = TestAgent("test_agent")
    agent.run(args.task_input)

if __name__ == "__main__":
    main()
