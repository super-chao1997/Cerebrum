from pydantic import BaseModel
from typing import List, Dict, Any, Union, Optional
from cerebrum.utils.communication import send_request, Query, Response

class MemoryQuery(Query):
    query_class: str = "memory"
    params: Dict[str, Union[str, Any]]
    operation_type: str

    class Config:
        arbitrary_types_allowed = True  # Allows the use of arbitrary types such as Any and Dict.

class MemoryResponse(Response):
    response_class: str = "memory"
    response_message: Optional[str] = None
    finished: bool = False
    error: Optional[str] = None
    status_code: int = 200

# Memory APIs
def alloc_memory(
        agent_name: str, 
        base_url: str = "http://localhost:8000"
    ):
    return NotImplementedError

def read_memory(
        agent_name: str, 
        round: int,
        base_url: str = "http://localhost:8000"
    ):
    return NotImplementedError

def write_memory(
        agent_name: str, 
        round: int,
        content: str,
        base_url: str = "http://localhost:8000"
    ):
    return NotImplementedError

def clear_memory(
        agent_name: str, 
        base_url: str = "http://localhost:8000"
    ):
    return NotImplementedError