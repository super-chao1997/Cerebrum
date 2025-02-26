from cerebrum.llm.communication import LLMQuery
from cerebrum.memory.communication import MemoryQuery
from cerebrum.storage.communication import StorageQuery
from cerebrum.tool.communication import ToolQuery

import requests
from typing import Dict, Any, List

def post(base_url: str, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{base_url}{endpoint}", json=data)
    response.raise_for_status()
    return response.json()

def send_request(agent_name: str, query: LLMQuery | MemoryQuery | StorageQuery | ToolQuery, base_url: str = "http://localhost:8000"):
    if isinstance(query, LLMQuery):
        query_type = "llm"
    elif isinstance(query, MemoryQuery):
        query_type = "memory"
    elif isinstance(query, StorageQuery):
        query_type = "storage"
    elif isinstance(query, ToolQuery):
        query_type = "tool"
    
    result = post(base_url, "/query", {
        'query_type': query_type,
        'agent_name': agent_name,
        'query_data': query.model_dump()})

    return result

def chat(agent_name: str, messages: List[Dict[str, Any]], base_url: str = "http://localhost:8000"):
    query = LLMQuery(
        messages=messages,
        tools=None,
        action_type="chat"
    )
    return send_request(agent_name, query, base_url)

def call_tool(agent_name: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], base_url: str = "http://localhost:8000"):
    query = LLMQuery(
        messages=messages,
        tools=tools,
        action_type="tool_use"
    )
    return send_request(agent_name, query, base_url)

def operate_file(agent_name: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], base_url: str = "http://localhost:8000"):
    query = LLMQuery(
        messages=messages,
        action_type="operate_file"
    )
    return send_request(agent_name, query, base_url)

def retrieve(
        agent_name: str, 
        query_text: str,
        n: int,
        keywords: List[str] = None,
        base_url: str = "http://localhost:8000"
    ):
    params = {
        "query_text": query_text,
        "n": n,
        "keywords": keywords
    }
    query = StorageQuery(
        params=params,
        operation_type="retrieve"
    )
    return send_request(agent_name, query, base_url)

def mount(
        agent_name: str, 
        root_dir: str,
        base_url: str = "http://localhost:8000"
    ):
    query = StorageQuery(
        params={"root_dir": root_dir},
        operation_type="mount"
    )
    
def create_file(
        agent_name: str, 
        file_path: str,
        base_url: str = "http://localhost:8000"
    ):
    query = StorageQuery(
        params={"file_path": file_path},
        operation_type="create_file"
    )
    return send_request(agent_name, query, base_url)

def create_dir(
        agent_name: str, 
        dir_path: str,
        base_url: str = "http://localhost:8000"
    ):
    query = StorageQuery(
        params={"dir_path": dir_path},
        operation_type="create_dir"
    )
    return send_request(agent_name, query, base_url)


def write_file(
        agent_name: str, 
        file_path: str,
        content: str,
        base_url: str = "http://localhost:8000"
    ):
    query = StorageQuery(
        params={"file_path": file_path, "content": content},
        operation_type="write"
    )
    return send_request(agent_name, query, base_url)

def roll_back(
        agent_name: str, 
        file_path: str,
        n: int,
        base_url: str = "http://localhost:8000"
    ):
    query = StorageQuery(
        params={"file_path": file_path, "n": n},
        operation_type="rollback"
    )
    return send_request(agent_name, query, base_url)

def share_file(
        agent_name: str, 
        file_path: str,
        base_url: str = "http://localhost:8000"
    ):
    query = StorageQuery(
        params={"file_path": file_path},
        operation_type="share"
    )
    return send_request(agent_name, query, base_url)