from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from creator.utils import remove_title
from creator.config.library import config
from creator.utils import generate_skill_doc, generate_install_command
from creator.agents import code_interpreter_agent, code_tester_agent, code_refactor_agent
import getpass
import json
import os
import platform


class BaseSkillMetadata(BaseModel):
    created_at: Union[datetime, str] = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description="Creation timestamp")
    author: str = Field(default_factory=lambda:getpass.getuser(), description="Author of the skill")
    updated_at: Union[datetime, str] = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description="Last updated timestamp")
    usage_count: int = Field(0, description="Number of times the skill was used")
    version: str = Field("1.0.0", description="Version of the skill")
    additional_kwargs: dict = Field(default_factory=dict, description="Any additional information")


class BaseSkill(BaseModel):
    skill_name: str = Field(..., description="Skill name in snake_case format or camelCase format, should match the function name or class name")
    skill_description: str = Field("", description=(
        "Please provide a description for this skill. Ensure your description is clear, concise, and specific, limited to no more than 6 sentences." 
        "Explain the primary functionality of the skill and offer specific applications or use cases." 
    ))
    skill_metadata: Optional[BaseSkillMetadata] = Field(None, description="Metadata of the skill")
    skill_tags: List[str] = Field(..., description="Write 3-5 keywords describing the skill, avoid terms that might lead to confusion, and ensure consistency in style and language")


class CodeSkillParameter(BaseModel):
    param_name: str = Field(default="query", description="the name of the parameter")
    param_type: str = Field(default="string", description="the type, only support string, integer, float, boolean, array, object", enum=["string", "integer", "float", "boolean", "array", "object"])
    param_description: str = Field(default="the input query", description="the description of the parameter. If it is enum, describe the enum values. If it is format, describe the format")
    param_required: bool = Field(default=True, description="whether it is required")
    param_default: Optional[Any] = Field(default=None, description="the default value, it depends on the type")

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


class TestCase(BaseModel):
    test_input: str = Field(description="The input data or conditions used for the test.")
    run_command: str = Field(description="The command or function that was executed for the test.")
    expected_result: str = Field(description="The expected outcome or result of the test.")
    actual_result: str = Field(description="The actual outcome or result observed after the test was executed.")
    is_passed: bool = Field(description="A boolean indicating whether the test passed or failed.")


class TestSummary(BaseModel):
    test_cases: List[TestCase] = Field(description="Extract a list of test cases that were run.")

    @classmethod
    def to_test_function_schema(self):
        test_function_schema = remove_title(self.model_json_schema())
        return {
            "name": "test_summary",
            "description": "A method to be invoked once all test cases have been successfully completed. This function provides a comprehensive summary of each test case, detailing their input, execution command, expected results, actual results, and pass status.",
            "parameters": test_function_schema
        }


class CodeSkill(BaseSkill):
    skill_usage_example: str = Field(..., description="Example of how to use the skill")
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
11. **Consistent Interfaces**: Uniformity in function and method interfaces ensures easier integration and usage. Normally the same with the skill name.
""")

    skill_parameters: Optional[Union[CodeSkillParameter, List[CodeSkillParameter]]] = Field(None, description="List of parameters the skill requires, defined using json schema")
    skill_return: Optional[Union[CodeSkillParameter, List[CodeSkillParameter]]] = Field(None, description="Return value(s) of the skill")
    skill_dependencies: Optional[Union[CodeSkillDependency, List[CodeSkillDependency]]] = Field(None, description="List of dependencies the skill requires to run, typically packages but can also be other skill functions")
    
    conversation_history: Optional[List[Dict]] = Field(None, description="Conversation history that the skill was extracted from")
    test_summary: Optional[TestSummary] = Field(None, description="Test cases for the skill")

    class Config:
        # Properties from Refactorable
        refactorable = False
        skills_to_combine = []
        user_request = "please help me refine the skill object"
        refactor_type = "refine"

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
        code_skill_json_schema = remove_title(self.model_json_schema())
        defs = code_skill_json_schema.pop("$defs")
        defs_to_remove = ["BaseSkillMetadata", "TestSummary"]
        for prop in defs_to_remove:
            defs.pop(prop)
        code_skill_json_schema["$defs"] = defs

        properties_to_remove = ["skill_metadata", "conversation_history", "test_summary"]
        for prop in properties_to_remove:
            code_skill_json_schema["properties"].pop(prop)

        return code_skill_json_schema

    def check_and_install_dependencies(self):
        if self.skill_dependencies is None:
            return
        install_script = generate_install_command(self.skill_program_language, self.skill_dependencies)
        result = config.code_interpreter.run({
            "language": "shell",
            "code": install_script,
        })
        print(result)
        return

    def __add__(self, other_skill):
        assert isinstance(other_skill, type(self)), f"Cannot combine {type(self)} with {type(other_skill)}"
        self.Config.refactorable = True
        # If the list is empty, add the current object to it
        if not self.Config.skills_to_combine:
            self.Config.skills_to_combine.append(self)
        
        # Add the other_skill to the list
        self.Config.skills_to_combine.append(other_skill)
        
        return self  # Return the current object to support continuous addition
    
    def __radd__(self, other_skill):
        self.Config.refactorable = True
        self.__add__(other_skill)

    def __lt__(self, user_request:str):
        self.Config.refactorable = True
        self.Config.user_request = user_request
        self.Config.refactor_type = "decompose"
        return self.refactor()

    def __gt__(self, user_request:str):
        self.Config.refactorable = True
        self.Config.user_request = user_request
        self.Config.refactor_type = "combine"
        return self.refactor()

    def run(self, inputs: Union[str, dict[str, Any]]):
        self.check_and_install_dependencies()
        messages = [
            {"role": "assistant", "content": "ok I will run your code", "function_call": {
                "name": self.skill_name,
                "arguments": json.dumps({"language": self.skill_program_language, "code": self.skill_code})
            }}
        ]
        tool_result = config.code_interpreter.run({
            "language": self.skill_program_language,
            "code": self.skill_code
        })
        params = json.dumps(inputs) if isinstance(inputs, dict) else inputs
        messages.append({"role": "function", "name": "run_code", "content": json.dumps(tool_result)})
        messages.append({"role": "user", "content": params})
        previews_tool = code_interpreter_agent.tool
        code_interpreter_agent.tool = config.code_interpreter
        messages = code_interpreter_agent.run(
            {
                "messages": messages,
                "username": getpass.getuser(),
                "current_working_directory": os.getcwd(),
                "operating_system": platform.system(),
                "verbose": True,
            }
        )
        code_interpreter_agent.tool = previews_tool
        return messages
    
    def test(self):
        if self.conversation_history is None or len(self.conversation_history) == 0:
            print("No conversation history provided, cannot test")
            return
        if not self.skill_code:
            print("No code provided, cannot test")
            return
        
        self.check_and_install_dependencies()
        tool_result = config.code_interpreter.run({
            "language": self.skill_program_language,
            "code": self.skill_code
        })
        messages = [
            {"role": "user", "content": repr(self)},
            {"role": "function", "name": "run_code", "content": json.dumps(tool_result)}
        ]
        test_result = code_tester_agent.run(
            {
                "messages": messages,
                "username": getpass.getuser(),
                "current_working_directory": os.getcwd(),
                "operating_system": platform.system(),
                "verbose": True,
            }
        )
        if "test_summary" in test_result:
            self.test_summary = TestSummary(**test_result["test_summary"])
        self.conversation_history = self.conversation_history + test_result["messages"]
        return self.test_summary

    def refactor(self):
        if not self.Config.refactorable:
            print("This skill is not refactorable since it is not combined with other skills or add any user request")
            return
        
        num_output_skills = "one" if self.Config.refactor_type != "decompose" else "appropriate number of"
        messages = [
            {"role": "system", "content": f"Your refactor type is: {self.Config.refactor_type} and output {num_output_skills} skill object(s)"},
            {"role": "function", "name": "show_skill", "content": repr(self)}
        ]
        messages.append({
            "role": "user",
            "content": self.Config.user_request
        })
        refactored_skill_jsons = code_refactor_agent.run(
            {
                "messages": messages,
                "verbose": True,
            }
        )
        refactored_skills = []
        for refactored_skill_json in refactored_skill_jsons:
            refactored_skill = self.__class__(refactored_skill_json)
            refactored_skill.skill_metadata = BaseSkillMetadata()
            refactored_skills.append(refactored_skill)

        return refactored_skills
    
    def __repr__(self):

        if self.Config.refactorable:
            if len(self.Config.skills_to_combine) == 0:
                self.Config.skills_to_combine.append(self)
            skill_docs = []
            for skill in self.Config.skills_to_combine:
                skill_docs.append(generate_skill_doc(skill))
            refactor_config_str = f"""
    ## Refactorable Config
    - **Refactor Way**: {self.Config.refactor_type}
    - **User Request**: {self.Config.user_request}
    """
            return "\n---\n".join(skill_docs) + refactor_config_str
        else:
            return generate_skill_doc(self)
