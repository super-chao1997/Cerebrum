from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from typing_extensions import Literal

from cerebrum.utils.communication import Query, Response, send_request

class LLMQuery(Query):
    """
    Query class represents the input structure for performing various actions.
    
    Attributes:
        messages (List[Dict[str, Union[str, Any]]]): A list of dictionaries where each dictionary
            represents a message containing 'role' and 'content' or other key-value pairs.
        tools (Optional[List[Dict[str, Any]]]): An optional list of JSON-like objects (dictionaries) 
            representing tools and their parameters. Default is an empty list.
        action_type (Literal): A string that must be one of "message_llm", "call_tool", or "operate_file".
            This restricts the type of action the query performs.
        message_return_type (str): The type of the response message. Default is "text".
    """
    query_class: str = "llm"
    llms: List[Dict[str, Any]] = Field(default_factory=list)
    messages: List[Dict[str, Union[str, Any]]]  # List of message dictionaries, each containing role and content.
    tools: Optional[List[Dict[str, Any]]] = Field(default_factory=list)  # List of JSON-like objects (dictionaries) representing tools.
    action_type: Literal["chat", "tool_use", "operate_file"] = Field(default="chat")  # Restrict the action_type to specific choices.
    message_return_type: str = Field(default="text")  # Type of the return message, default is "text".
    class Config:
        arbitrary_types_allowed = True  # Allows the use of arbitrary types such as Any and Dict.

class LLMResponse(Response):
    """
    Response class represents the output structure after performing actions.
    
    Attributes:
        response_message (Optional[str]): The generated response message.
        tool_calls (Optional[List[Dict[str, Any]]]): Tool calls made during processing.
        finished (bool): Whether the processing is complete.
        error (Optional[str]): Error message if any.
        status_code (int): HTTP status code of the response.
    """
    response_class: str = "llm"
    response_message: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finished: bool = False
    error: Optional[str] = None
    status_code: int = 200

    class Config:
        arbitrary_types_allowed = True

def llm_chat(agent_name: str, llms: List[Dict[str, Any]], messages: List[Dict[str, Any]], base_url: str = "http://localhost:8000"):
    query = LLMQuery(
        llms=llms,
        messages=messages,
        tools=None,
        action_type="chat"
    )
    return send_request(agent_name, query, base_url)

def llm_call_tool(agent_name: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], base_url: str = "http://localhost:8000"):
    query = LLMQuery(
        messages=messages,
        tools=tools,
        action_type="tool_use"
    )
    return send_request(agent_name, query, base_url)

def llm_operate_file(agent_name: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], base_url: str = "http://localhost:8000"):
    query = LLMQuery(
        messages=messages,
        action_type="operate_file"
    )
    return send_request(agent_name, query, base_url)