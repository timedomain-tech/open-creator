from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from datetime import datetime


########### pydantic models ###########

class BaseSkillMetadata(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description="Creation timestamp")
    author: str = Field(..., description="Author of the skill")
    updated_at: datetime = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description="Last updated timestamp")
    usage_count: int = Field(0, description="Number of times the skill was used")


class BaseSkill(BaseModel):
    skill_name: str = Field(..., description="Skill name in snake_case format, should match the function name")
    skill_description: str = Field(..., description="Description of the skill, summarized in no more than 6 sentences")
    skill_metadata: Optional[BaseSkillMetadata] = Field(None, description="Metadata of the skill")
    skill_tags: List[str] = Field(..., description="List of tags describing the skill")


class CodeSkillParameter(BaseModel):
    param_name: str = Field(...)
    param_type: str = Field(..., description="the type, only support string, integer, float, boolean, array, object")
    param_description: str = Field(..., description="the description. If it is enum, describe the enum values. If it is format, describe the format")
    param_required: bool = Field(..., description="whether it is required")
    param_default: Optional[Union[str, List]] = Field(None, description="the default value, it depends on the type")


class CodeSkillDependency(BaseModel):
    dependency_name: str = Field(...)
    dependency_version: Optional[str] = Field(None, description="the version of the dependency only filled if context provided")
    dependency_type: Optional[str] = Field(enum=["built-in", "package", "function"], default="built-in")


class CodeSkill(BaseSkill):
    skill_parameters: Optional[Union[CodeSkillParameter, List[CodeSkillParameter]]] = Field(None, description="List of parameters the skill requires, defined using json schema")
    skill_return: Optional[Union[CodeSkillParameter, List[CodeSkillParameter]]] = Field(None, description="Return value(s) of the skill")
    skill_usage_example: str = Field(..., description="Example of how to use the skill")
    skill_dependencies: Optional[List[CodeSkillDependency]] = Field(..., description="List of dependencies the skill requires to run, typically packages but can also be other skill functions")
    skill_program_language: str = Field(..., description="Programming language the skill is written in", enum=["python", "R", "shell", "javascript", "applescript", "html"])
    skill_code: str = Field(..., description="Code of the skill, only one function is allowed")

    conversation_history: Optional[List[Dict]] = Field(None, description="Conversation history that the skill was extracted from")
    unit_tests: Optional[Dict] = Field(None, description="Test cases for the skill")

    def to_function_call(self):
        return {
            "name": self.skill_name,
            "description": self.skill_description,
            "arguments": self.skill_parameters
        }

    @classmethod
    def to_skill_function_schema(self):
        # remove all title and its properties's title
        # recursively remove all titles including `$defs`
        def _remove_title(schema):
            if "title" in schema:
                schema.pop("title")
            if "properties" in schema:
                for prop in schema["properties"]:
                    _remove_title(schema["properties"][prop])
            if "$defs" in schema:
                for prop in schema["$defs"]:
                    _remove_title(schema["$defs"][prop])
            return schema
        
        code_skill_json_schema = _remove_title(self.model_json_schema())

        defs = code_skill_json_schema.pop("$defs")
        defs_to_remove = ["BaseSkillMetadata"]
        for prop in defs_to_remove:
            defs.pop(prop)
        code_skill_json_schema["$defs"] = defs

        properties_to_remove = ["skill_metadata", "conversation_history", "unit_tests"]
        for prop in properties_to_remove:
            code_skill_json_schema["properties"].pop(prop)

        return code_skill_json_schema

