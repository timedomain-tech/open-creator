from pydantic import BaseModel, field_validator
from pydantic.v1 import root_validator
from typing import List, Optional
import os


class CreateParams(BaseModel):
    messages: Optional[List[dict]] = []
    request: Optional[str] = ""
    skill_path: Optional[str] = ""
    skill_json_path: Optional[str] = ""
    messages_json_path: Optional[str] = ""
    huggingface_repo_id: Optional[str] = ""
    huggingface_skill_path: Optional[str] = ""
    langchain_hub_path: Optional[str] = ""
    file_content: Optional[str] = ""
    file_path: Optional[str] = ""

    @field_validator("skill_path", "skill_json_path", "messages_json_path", "file_path", mode="before")
    def validate_path_exists(cls, value):
        if value and not os.path.exists(value):
            raise ValueError(f"The path {value} does not exist.")
        return value

    @root_validator(pre=True)
    def validate_only_one_param(cls, values) -> None:
        print(values)
        params = ["messages", "request", "skill_path", "skill_json_path", "messages_json_path", "file_content", "file_path"]
        valid_count = sum(1 for param in params if values.get(param))
        
        if valid_count > 1:
            raise ValueError("Please only provide one of the following parameters: messages, request, skill_path, or messages_json_path.")
        
        if valid_count == 0:
            raise ValueError("Please provide one of the following parameters: messages, request, skill_path, or messages_json_path.")
    
    @root_validator(pre=True)
    def validate_huggingface_param(cls, values) -> None:
        params = ["huggingface_repo_id", "huggingface_skill_path"]
        print(values)
        valid_count = sum(1 for param in params if values.get(param))
        if valid_count == 1:
            raise ValueError("Please provide both parameters: huggingface_repo_id and huggingface_skill_path.")


class SaveParams(BaseModel):
    skill_path: Optional[str] = ""
    huggingface_repo_id: Optional[str] = ""
    langchain_hub_path: Optional[str] = ""

    @root_validator(pre=True)
    def validate_only_one_param(cls, values):
        params = ["skill_path", "huggingface_repo_id", "langchain_hub_path"]
        valid_count = sum(1 for param in params if values.get(param))
        
        if valid_count > 1:
            raise ValueError("Please only provide one of the following parameters: skill_path, huggingface_repo_id, or langchain_hub_path.")
        
        if valid_count == 0:
            raise ValueError("Please provide one of the following parameters: skill_path, huggingface_repo_id, or langchain_hub_path.")
        
        return values