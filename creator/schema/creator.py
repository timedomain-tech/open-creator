from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
import os


class CreateParams(BaseModel):
    messages: Optional[List[str]] = []
    request: Optional[str] = ""
    skill_path: Optional[str] = ""
    messages_json_path: Optional[str] = ""
    huggingface_hub_path: Optional[str] = ""
    langchain_hub_path: Optional[str] = ""

    @field_validator("skill_path", "messages_json_path", mode="before")
    def validate_path_exists(cls, value):
        if value and not os.path.exists(value):
            raise ValueError(f"The path {value} does not exist.")
        return value

    @model_validator(mode="before")
    def validate_only_one_param(cls, values):
        params = ["messages", "request", "skill_path", "messages_json_path"]
        valid_count = sum(1 for param in params if values.get(param))
        
        if valid_count > 1:
            raise ValueError("Please only provide one of the following parameters: messages, request, skill_path, or messages_json_path.")
        
        if valid_count == 0:
            raise ValueError("Please provide one of the following parameters: messages, request, skill_path, or messages_json_path.")
        
        return values


class SaveParams(BaseModel):
    skill_path: Optional[str] = ""
    huggingface_hub_path: Optional[str] = ""
    langchain_hub_path: Optional[str] = ""