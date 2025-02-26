from pydantic import BaseModel
from typing import List, Dict, Any, Union, Optional
from cerebrum.utils.communication import Query, send_request, Response

class ToolQuery(Query):
    query_class: str = "tool"
    tool_calls: List[Dict[str, Union[str, Any]]]  # List of message dictionaries, each containing role and content.

    class Config:
        arbitrary_types_allowed = True  # Allows the use of arbitrary types such as Any and Dict.

class ToolResponse(Response):
    response_class: str = "tool"
    response_message: Optional[str] = None
    finished: bool = False
    error: Optional[str] = None
    status_code: int = 200

def call_tool(
        agent_name: str, 
        tool_name: str,
        base_url: str = "http://localhost:8000"
    ):
    query = ToolQuery(
        tool_calls=tool_calls
    )
    return send_request(agent_name, query, base_url)