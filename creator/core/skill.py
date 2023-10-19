from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from creator.utils import remove_title
from creator.config.library import config
from creator.utils import generate_skill_doc, generate_install_command, print, generate_language_suffix
from creator.agents import code_interpreter_agent, code_tester_agent, code_refactor_agent
from creator.hub.huggingface import hf_repo_update, hf_push
import json
import getpass
import os


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

    @classmethod
    def construct_with_aliases(cls, **data):
        keys = {
            "name": "param_name",
            "type": "param_type",
            "description": "param_description",
            "required": "param_required",
            "default": "param_default"
        }

        actual_keys = list(data.keys())
        for actual_key in actual_keys:
            for key_alias, expected_key in keys.items():
                if key_alias in actual_key:
                    data[expected_key] = data.pop(actual_key)
                    break
        if "param_name" not in data and "param_description" in data:
            data["param_name"] = "_".join(data["param_description"].split(" ")).lower()[0:20]
        return data

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
    dependency_type: Optional[str] = Field(enum=["built-in", "package", "function"], default="built-in", description="when the dependency is an another code skill, please set it as function")


class TestCase(BaseModel):
    test_input: str = Field(description="The input data or conditions used for the test.")
    run_command: str = Field(description="The command or function that was executed for the test.")
    expected_result: str = Field(description="The expected outcome or result of the test.")
    actual_result: str = Field(description="The actual outcome or result observed after the test was executed.")
    is_passed: bool = Field(description="A boolean indicating whether the test passed or failed.")

    def __repr__(self):
        return (
            f"- **Test Input:** {self.test_input}\n"
            f"- **Run Command:** {self.run_command}\n"
            f"- **Expected Result:** {self.expected_result}\n"
            f"- **Actual Result:** {self.actual_result}\n"
            f"- **Is Passed:** {'Yes' if self.is_passed else 'No'}\n"
        )


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

    def __repr__(self):
        output = ["## Test Summary\n"]
        for i, test_case in enumerate(self.test_cases):
            output.append(f"### Test Case {i}\n")
            output.append(repr(test_case))
            output.append("---\n")
        return "\n".join(output)

    def show(self):
        print(repr(self), print_type="markdown")


class CodeSkill(BaseSkill):
    skill_program_language: str = Field(..., description="Programming language the skill is written in", enum=["python", "R", "shell", "javascript", "applescript", "html"])
    skill_code: str = Field(..., description="""Code of the skill, written in the programming language specified above. Remeber to import all the dependencies and packages you need.
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
    skill_usage_example: str = Field(..., description="Example of how to use the skill")

    conversation_history: Optional[List[Dict]] = Field([], description="Conversation history that the skill was extracted from")
    test_summary: Optional[TestSummary] = Field(None, description="Test cases for the skill")

    class Config:
        # Properties from Refactorable
        refactorable = False
        skills_to_combine = []
        user_request = "please help me refine the skill object"
        refactor_type = "Refine"

    def __init__(self, **data):
        super().__init__(**data)
        if "skill_parameters" in data and data["skill_parameters"]:
            if isinstance(data["skill_parameters"], list):
                self.skill_parameters = [CodeSkillParameter(**CodeSkillParameter.construct_with_aliases(**param)) for param in data["skill_parameters"]]
            elif isinstance(data["skill_parameters"], dict):
                self.skill_parameters = CodeSkillParameter(**CodeSkillParameter.construct_with_aliases(**data["skill_parameters"]))

        if "skill_return" in data and data["skill_return"]:
            if isinstance(data["skill_return"], list):
                self.skill_return = [CodeSkillParameter(**CodeSkillParameter.construct_with_aliases(**param)) for param in data["skill_return"]]
            elif isinstance(data["skill_return"], dict):
                self.skill_return = CodeSkillParameter(**CodeSkillParameter.construct_with_aliases(**data["skill_return"]))
                if self.skill_return.param_name in ("null", "None") or self.skill_return.param_type in ("null", "None"):
                    self.skill_return = None

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
        defs_to_remove = ["BaseSkillMetadata", "TestSummary", "TestCase"]
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
        print(result, print_type="json")
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
        self.Config.refactor_type = "Decompose"
        return self.refactor()

    def __gt__(self, user_request:str):
        self.Config.refactorable = True
        self.Config.user_request = user_request
        if len(self.Config.skills_to_combine) <= 1:
            self.Config.refactor_type = "Refine"
        else:
            self.Config.refactor_type = "Combine"
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
        previews_tool = code_interpreter_agent.tools[0]
        code_interpreter_agent.tools[0] = config.code_interpreter
        messages = code_interpreter_agent.run(
            {
                "messages": messages,
                "verbose": True,
            }
        )
        code_interpreter_agent.tools[0] = previews_tool
        return messages

    def test(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if not self.skill_code:
            print("> No code provided, cannot test", print_type="markdown")
            return

        previews_tool = code_tester_agent.tools[0]
        code_tester_agent.tools[0] = config.code_interpreter

        self.check_and_install_dependencies()
        extra_import = """\n\n
import io
import unittest
stream = io.StringIO()
runner = unittest.TextTestRunner(stream=stream)
"""
        tool_input = {
            "language": self.skill_program_language,
            "code": self.skill_code + extra_import
        }
        tool_result = config.code_interpreter.run(tool_input)
        messages = [
            {"role": "user", "content": repr(self)},
            {"role": "assistant", "content": "", "function_call": {"name": "run_code", "arguments": json.dumps(tool_input)}},
            {"role": "function", "name": "run_code", "content": json.dumps(tool_result)},
            {"role": "user", "content": "I have already run the function for you so you can directy use the function by passing the parameters without import the function"},
        ]

        test_result = code_tester_agent.run(
            {
                "messages": messages,
                "verbose": True,
            }
        )
        code_tester_agent.tools[0] = previews_tool
        if "test_summary" in test_result:
            self.test_summary = TestSummary(**{"test_cases": test_result["test_summary"]})

        self.conversation_history = self.conversation_history + test_result["messages"]
        return self.test_summary

    def refactor(self):
        if self.conversation_history is None:
            self.conversation_history = []

        if not self.Config.refactorable:
            print("> This skill is not refactorable since it is not combined with other skills or add any user request", print_type="markdown")
            return
        messages = [
            {"role": "system", "content": f"Your action type is: {self.Config.refactor_type}"},
            {"role": "function", "name": "show_skill", "content": repr(self)},
            {"role": "function", "name": "show_code", "content": f"current skill code:\n```{self.skill_program_language}\n{self.skill_code}\n```"}
        ]
        additional_request = "\nplease output only one skill object" if self.Config.refactor_type in ("Combine", "Refine") else "\nplease help me decompose the skill object into different independent skill objects"
        messages.append({
            "role": "user",
            "content": self.Config.user_request + additional_request
        })
        messages = self.conversation_history + [{"role": "system", "content": "Above context is conversation history from other agents. Now let's refactor our skill."}] + messages
        refactored_skill_jsons = code_refactor_agent.run(
            {
                "messages": messages,
                "verbose": True,
            }
        )
        refactored_skills = []
        for refactored_skill_json in refactored_skill_jsons:
            refactored_skill = CodeSkill(**refactored_skill_json)
            refactored_skill.Config.refactorable = False
            refactored_skill.Config.skills_to_combine = []
            refactored_skill.skill_metadata = BaseSkillMetadata()
            refactored_skills.append(refactored_skill)
        if len(refactored_skills) == 1:
            return refactored_skills[0]
        return refactored_skills

    def auto_optimize(self, retry_times=3):
        skill = self.model_copy(deep=True)
        refined = False
        for i in range(retry_times):
            if skill.test_summary is None:
                test_summary = skill.test()
                if test_summary is None:
                    print("> Skill test failed, cannot auto optimize", print_type="markdown")
                    return skill

            all_passed = all(test_case.is_passed for test_case in test_summary.test_cases)
            if all_passed and refined:
                return skill
            print(f"> Auto Refine Skill {i+1}/{retry_times}", print_type="markdown")
            skill = skill > "I have tested the skill, but it failed, please refine it."
            if all_passed:
                skill.test_summary = test_summary
            refined = True
        return self

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

    def __str__(self):
        return self.__repr__()

    def show(self):
        print(self.__repr__(), print_type="markdown")
    
    def show_code(self):
        code = f"""```{self.skill_program_language}\n{self.skill_code}\n```"""
        print(code, print_type="markdown")

    def save(self, skill_path=None, huggingface_repo_id=None):
        if skill_path is None:
            skill_path = os.path.join(config.local_skill_library_path, self.skill_name)

        if skill_path is not None and not os.path.exists(skill_path):
            os.makedirs(skill_path, exist_ok=True)

        if huggingface_repo_id:
            local_dir = os.path.join(config.remote_skill_library_path, huggingface_repo_id)
            hf_repo_update(huggingface_repo_id, local_dir)
            remote_skill_path = os.path.join(local_dir, self.skill_name)
            skill_path = os.path.join(config.local_skill_library_path, self.skill_name)

        if skill_path:
            os.makedirs(os.path.dirname(skill_path), exist_ok=True)
            # save json file
            with open(os.path.join(skill_path, "skill.json"), mode="w", encoding="utf-8") as f:
                json.dump(self.model_dump(), f, ensure_ascii=False, indent=4)

            # save function call
            with open(os.path.join(skill_path, "function_call.json"), mode="w", encoding="utf-8") as f:
                json.dump(self.to_function_call(), f, ensure_ascii=False, indent=4)

            # save dependencies
            command_str = ""
            if self.skill_dependencies:
                command_str = generate_install_command(self.skill_program_language, self.skill_dependencies)
                with open(os.path.join(skill_path, "install_dependencies.sh"), mode="w", encoding="utf-8") as f:
                    f.write(command_str)

            # save code
            if self.skill_program_language:
                language_suffix = generate_language_suffix(self.skill_program_language)
                with open(os.path.join(skill_path, "skill_code" + language_suffix), mode="w", encoding="utf-8") as f:
                    f.write(self.skill_code)

            # save conversation history
            if self.conversation_history:
                with open(os.path.join(skill_path, "conversation_history.json"), mode="w", encoding="utf-8") as f:
                    f.write(json.dumps(self.conversation_history, ensure_ascii=False, indent=4))

            # skill description
            doc = generate_skill_doc(self)
            with open(os.path.join(skill_path, "skill_doc.md"), mode="w", encoding="utf-8") as f:
                f.write(doc)

            # embedding_text
            embedding_text = "{skill.skill_name}\n{skill.skill_description}\n{skill.skill_usage_example}\n{skill.skill_tags}".format(skill=self)
            with open(os.path.join(skill_path, "embedding_text.txt"), mode="w", encoding="utf-8") as f:
                f.write(embedding_text)

            # save test code
            if self.test_summary:
                with open(os.path.join(skill_path, "test_summary.json"), mode="w", encoding="utf-8") as f:
                    json.dump(self.test_summary.model_dump(), f, ensure_ascii=False, indent=4)

            if huggingface_repo_id:
                # cp to local path
                os.system(command=f"cp -r {skill_path} {remote_skill_path}")
                hf_push(remote_skill_path)

        print(f"> saved to {skill_path}", print_type="markdown")
