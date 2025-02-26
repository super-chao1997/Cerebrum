from pydantic import BaseModel, Field
from typing_extensions import Literal

import requests
from typing import Dict, Any, List

class Query(BaseModel):
    query_class: Literal["llm", "memory", "storage", "tool"]
    
class Response(BaseModel):
    response_class: Literal["llm", "memory", "storage", "tool"]

def post(base_url: str, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{base_url}{endpoint}", json=data)
    response.raise_for_status()
    return response.json()

def send_request(agent_name: str, query: Query, base_url: str = "http://localhost:8000"):
    query_type = query.query_class
    result = post(base_url, "/query", {
        'query_type': query_type,
        'agent_name': agent_name,
        'query_data': query.model_dump()})

    return result