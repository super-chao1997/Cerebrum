from cerebrum.llm.communication import LLMQuery
from cerebrum.storage.communication import StorageQuery

from cerebrum.apis import chat, call_tool, retrieve, mount, create_file, create_dir, write_file, roll_back, share_file
import json

from cerebrum.interface import AutoTool

from typing import List, Dict, Any

def test_chat():
    messages=[{"role": "user", "content": "What is the capital of France?"}]
    response = chat(agent_name="test", messages=messages, base_url="http://localhost:8000")
    print(response)
    
def test_call_tool():
    messages=[{"role": "user", "content": "Tell me the core idea of OpenAGI paper"}]
    # tool = AutoTool.from_preloaded("demo_author/arxiv")
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
    # breakpoint()
    response = call_tool(agent_name="demo_agent", messages=messages, tools=tools, base_url="http://localhost:8000")
    print(response)
    
def test_operate_file():
    return NotImplementedError

def test_mount():
    query_text = "top 3 papers related to KV cache"
    n = 3
    # keywords = ["KV cache", "cache"]
    keywords = None
    response = retrieve(agent_name="demo_agent", query_text=query_text, n=n, keywords=keywords, base_url="http://localhost:8000")
    print(response)

def test_create_file():
    return NotImplementedError

def test_create_dir():
    return NotImplementedError
        
if __name__ == "__main__":
    # agent = TestAgent("test_agent", "What is the capital of France?")
    # agent.run()
    test_chat()
    test_call_tool()
    # test_operate_file()
    # test_mount()
    # test_create_file()
    # test_create_dir()
