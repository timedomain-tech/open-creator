from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from datetime import datetime

########### pydantic models ###########

class BaseSkillMetadata(BaseModel):
    created_at: Union[datetime, str] = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description="Creation timestamp")
    author: str = Field(..., description="Author of the skill")
    updated_at: Union[datetime, str] = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description="Last updated timestamp")
    usage_count: int = Field(0, description="Number of times the skill was used")
    version: str = Field("1.0.0", description="Version of the skill")
    additional_kwargs: dict = Field(default_factory=dict, description="Any additional information")


class BaseSkill(BaseModel):
    skill_name: str = Field(..., description="Skill name in snake_case format, should match the function name")
    skill_description: str = Field("", description=(
        "Please provide a description for this skill. Ensure your description is clear, concise, and specific, limited to no more than 6 sentences." 
        "Explain the primary functionality of the skill and offer specific applications or use cases." 
    ))
    skill_metadata: Optional[BaseSkillMetadata] = Field(None, description="Metadata of the skill")
    skill_tags: List[str] = Field(..., description="Write 3-5 keywords describing the skill, avoid terms that might lead to confusion, and ensure consistency in style and language")


class CodeSkillParameter(BaseModel):
    param_name: str = Field(...)
    param_type: str = Field(..., description="the type, only support string, integer, float, boolean, array, object")
    param_description: str = Field(..., description="the description. If it is enum, describe the enum values. If it is format, describe the format")
    param_required: bool = Field(..., description="whether it is required")
    param_default: Optional[Union[str, List]] = Field(None, description="the default value, it depends on the type")

    def to_json_schema(self):
        json_schema = {
            "type": self.param_type,
            "description": self.param_description,
        }
        if self.param_default:
            json_schema["default"] = self.param_default
        return json_schema


class CodeSkillDependency(BaseModel):
    dependency_name: str = Field("")
    dependency_version: Optional[str] = Field("", description="the version of the dependency only filled if context provided")
    dependency_type: Optional[str] = Field(enum=["built-in", "package", "function"], default="built-in")


class CodeSkill(BaseSkill):
    skill_parameters: Optional[Union[CodeSkillParameter, List[CodeSkillParameter]]] = Field(None, description="List of parameters the skill requires, defined using json schema")
    skill_return: Optional[Union[CodeSkillParameter, List[CodeSkillParameter]]] = Field(None, description="Return value(s) of the skill")
    skill_usage_example: str = Field(..., description="Example of how to use the skill")
    skill_dependencies: Optional[List[CodeSkillDependency]] = Field(..., description="List of dependencies the skill requires to run, typically packages but can also be other skill functions")
    skill_program_language: str = Field(..., description="Programming language the skill is written in", enum=["python", "R", "shell", "javascript", "applescript", "html"])
    skill_code: str = Field(..., description="""Code of the skill, written in the programming language specified above.
When writing code, it's imperative to follow industry standards and best practices to ensure readability, maintainability, and efficiency. Here are some guidelines to consider:
1. **Module Imports**: Place at the file's top. Organize by standard, third-party, then local modules.
2. **Class and Function Definitions**: Use CamelCase for classes and snake_case for functions. Every class and function should have a descriptive docstring detailing its purpose, parameters, and returns.
3. **Class Attributes**: Clearly annotate and describe attributes. Ensure their relevance and purpose are evident.
4. **Function Parameters**: Annotate parameter types. Indicate optional parameters and their default behavior.
5. **Examples and Tips**: Embed short examples for complex functionalities. Highlight essential information.
6. **Code Readability**: Structure for clarity. Aim for 80-100 characters per line. Use comments judiciously to explain non-obvious behaviors.
7. **Error Handling**: Anticipate potential errors. Implement exception handling mechanisms.
8. **Compatibility**: Ensure adaptability across platforms or frameworks, like PyTorch and TensorFlow.
9. **Externally Callable**: Design functions and classes to be callable externally. Their public interfaces should be well-defined and intuitive.
10. **Comments**: Provide context for complex segments. Keep them concise and meaningful.
11. **Consistent Interfaces**: Uniformity in function and method interfaces ensures easier integration and usage.
""")

    conversation_history: Optional[List[Dict]] = Field(None, description="Conversation history that the skill was extracted from")
    unit_tests: Optional[Dict] = Field(None, description="Test cases for the skill")

    def to_function_call(self):
        parameters = {
            "type": "object",
            "properties": {
                "dummy_property": {
                    "type": "null",
                }
            }
        }
        if self.skill_parameters:
            if isinstance(self.skill_parameters, list):
                parameters["properties"] = {param.param_name:param.to_json_schema() for param in self.skill_parameters}
                parameters["required"] = [param.param_name for param in self.skill_parameters if param.param_required]
            elif isinstance(self.skill_parameters, CodeSkillParameter):
                parameters["properties"] = self.skill_parameters.to_json_schema()
                parameters["required"] = [self.skill_parameters.param_name] if self.skill_parameters.param_required else []
        return {
            "name": self.skill_name,
            "description": self.skill_description + "\n\n" + self.skill_usage_example,
            "parameters": parameters
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

