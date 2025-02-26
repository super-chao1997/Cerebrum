from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union, Optional

from cerebrum.utils.communication import Query, send_request, Response

class StorageQuery(Query):
    query_class: str = "storage"
    params: Dict[str, Union[str, Any]]  # List of message dictionaries, each containing role and content.
    operation_type: str = Field(default="text")  # Type of the return message, default is "text".

    class Config:
        arbitrary_types_allowed = True  # Allows the use of arbitrary types such as Any and Dict.

class StorageResponse(Response):
    response_class: str = "storage"
    response_message: Optional[str] = None
    finished: bool = False
    error: Optional[str] = None
    status_code: int = 200

# Storage APIs
def mount(
        agent_name: str, 
        root_dir: str,
        base_url: str = "http://localhost:8000"
    ):
    query = StorageQuery(
        params={"root_dir": root_dir},
        operation_type="mount"
    )

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
