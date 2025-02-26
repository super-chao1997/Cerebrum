from cerebrum.llm.apis import LLMQuery, LLMResponse, llm_chat, llm_call_tool
import json

class TestAgent:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.messages = []

    def manual_workflow(self):
        workflow = [
            {
                "action_type": "tool_use",
                "action": "Search for relevant papers",
                "tool_use": ["demo_author/arxiv"],
            },
            {
                "action_type": "chat",
                "action": "Provide responses based on the user's query",
                "tool_use": [],
            },
        ]
        return workflow

    def run(self, task_input):
        # workflow = self.manual_workflow()
        self.messages.append({"role": "user", "content": task_input})

        # self.messages.append(
        #     {
        #         "role": "user",
        #         "content": f"[Thinking]: The workflow generated for the problem is {json.dumps(workflow)}. Follow the workflow to solve the problem step by step. ",
        #     }
        # )
        
        tools = [
            {
                'type': 'function', 
                'function': {
                    'name': 'demo_author/arxiv', 
                    'description': 'Query articles or topics in arxiv', 
                    'parameters': {
                        'type': 'object', 
                        'properties': {
                            'query': {
                                'type': 'string', 
                                'description': 'Input query that describes what to search in arxiv'
                            }
                        }, 
                        'required': ['query']
                    }
                }
            }
        ]
        
        tool_response = llm_call_tool(
            agent_name=self.agent_name,
            messages=self.messages,
            base_url="http://localhost:8000",
            tools=tools
        )
        
        print(tool_response)
        return tool_response
        
def main():
    agent = TestAgent("demo_agent")
    agent.run("Tell me what is the core idea of AIOS? ")

if __name__ == "__main__":
    main()
