
from typing import List, Dict, Any, Optional
import json

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.schema.messages import FunctionMessage
from langchain.prompts import ChatPromptTemplate
from langchain.adapters.openai import convert_message_to_dict, convert_openai_messages
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.tools.base import BaseTool
from langchain.output_parsers.json import parse_partial_json

from creator.code_interpreter import CodeInterpreter
from creator.config.library import config
from creator.utils import truncate_output, ask_run_code_confirm

from creator.llm.llm_creator import create_llm


_SYSTEM_TEMPLATE = """You are a helpful assistant for leveraging open-creator's API created by TimeDomain-tech. 
To fullfill the user's request, you need to write the **python** code in the `run_code` function.
The pre-defined variables and functions you can use in `run_code` have run in the user's local environment, so you can use them directly.
### Functions:
#### create
Create a skill from various sources
#### save
Save a skill to a local path or a huggingface repo
#### search
Search for skills by query

### Methods or Overloaded Operators in skill object:
#### run (Method)
Run a skill with arguments or request.
Example Usage
```python
# we use create/search function to have a skill object first.
skills = search("pdf extract section")
if len(skills) > 0:
    skill = skills[0]
    input_args = {
        "pdf_path": "creator.pdf",
        "start_page": 3,
        "end_page": 8,
        "output_path": "creator3-8.pdf"
    }
    # or you can
    # input_args = "extract 3-8 page form creator.pdf and save it as creator3-8.pdf"
    print(skill.run(input_args))
```

#### test (Method)
Test a skill by using the tester agent
skill = create(request="filters the number of prime numbers in a given range, e.g. filter_prime_numbers(2, 201)")
test_summary = skill.test()
print(test_summary)
# to see the intermediate results
print(skill.conversation_history)
```

#### refactor using Operator Overloading
Modify skills through various operations
1. **Combining Skills:**
   Use the `+` operator to chain or parallelly execute skills and further describe the sequence or parallelism using the `>` operator.
   ```python
   new_skill = skillA + skillB > "Descriptive string of how skills A and B should work together"
   ```

2. **Refactoring Skills:**
   Use the `>` operator to enhance, modify, or add functionalities/parameters to the existing skill.
   ```python
   refactored_skill = skill > "Descriptive string explaining the desired changes or enhancements"
   ```

3. **Decomposing Skills:**
   Use the `<` operator to break down a skill into simpler, more basic skills.
   ```python
   simpler_skills = skill < "Descriptive string explaining how to decompose the skill"
   ```

### code skill object schema and properties:
```python
class BaseSkillMetadata(BaseModel):
    created_at: Union[datetime, str]
    author: str
    updated_at: Union[datetime, str]
    usage_count: int
    version: str
    additional_kwargs: dict

class BaseSkill(BaseModel):
    skill_name: str
    skill_description: str
    skill_metadata: Optional[BaseSkillMetadata]
    skill_tags: List[str]

class CodeSkillParameter(BaseModel):
    param_name: str
    param_type: str
    param_description: str
    param_required: bool
    param_default: Optional[Any]

class CodeSkillDependency(BaseModel):
    dependency_name: str
    dependency_version: Optional[str]
    dependency_type: Optional[str]

class TestCase(BaseModel):
    test_input: str
    run_command: str
    expected_result: str
    actual_result: str
    is_passed: bool

class TestSummary(BaseModel):
    test_cases: List[TestCase]

class CodeSkill:
    skill_program_language: str
    skill_code: str
    skill_parameters: Optional[Union[CodeSkillParameter, List[CodeSkillParameter]]]
    skill_return: Optional[Union[CodeSkillParameter, List[CodeSkillParameter]]]
    skill_dependencies: Optional[Union[CodeSkillDependency, List[CodeSkillDependency]]]
    skill_usage_example: str
    conversation_history: Optional[List[Dict]]
    test_summary: Optional[TestSummary]
```

### Additional functions
#### show help
```python
print(HELP_STR)
```
#### modify config
```python
from creator.config.open_config import open_user_config
open_user_config()
```

[User Info]
Name: {username}
CWD: {current_working_directory}
OS: {operating_system}
"""

# creator.config.build_in_skill_config["create"]

class CreatorAgent(LLMChain):
    tool: BaseTool

    @property
    def _chain_type(self):
        return "CreatorAgent"

    @property
    def input_keys(self) -> List[str]:
        return ["username", "current_working_directory", "operating_system", "messages"]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManager] = None,
    ) -> Dict[str, Any]:

        messages = inputs.pop("messages")
        allow_user_confirm = config.run_human_confirm
        langchain_messages = convert_openai_messages(messages)

        total_tries = self.total_tries
        current_try = 0

        llm_with_functions = self.llm.bind(functions=[self.tool.to_function_schema()])
        
        callback = None
        if self.llm.callbacks is not None:
            callback = self.llm.callbacks.handlers[0]

        while current_try < total_tries:
            if callback:
                callback.on_chain_start()

            prompt = ChatPromptTemplate.from_messages(messages=[
                ("system", _SYSTEM_TEMPLATE),
                *langchain_messages
            ])
            llm_chain = prompt | llm_with_functions
            message = llm_chain.invoke(inputs)
            langchain_messages.append(message)
            function_call = message.additional_kwargs.get("function_call", None)
            if function_call is None:
                break

            can_run_code = True
            if allow_user_confirm:
                can_run_code = ask_run_code_confirm()
            if not can_run_code:
                break
            
            arguments = parse_partial_json(function_call.get("arguments", "{}"))
            tool_result = self.tool.run(arguments)
            tool_result = truncate_output(tool_result)
            output = str(tool_result.get("stdout", "")) + str(tool_result.get("stderr", ""))
            if callback:
                callback.on_tool_end(output)
            
            function_message = FunctionMessage(name="run_code", content=json.dumps(tool_result, ensure_ascii=False))
            langchain_messages.append(function_message)
            current_try += 1
            if callback:
                callback.on_chain_end()

        openai_message = list(map(convert_message_to_dict, langchain_messages))
        if callback:
            callback.message_box.end()
        return {
            "messages": openai_message
        }


def create_creator_agent(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_TEMPLATE),
        ]
    )
    tool = CodeInterpreter()
    function_schema = tool.to_function_schema()
    llm_kwargs = {"functions": [function_schema], "function_call": {"name": function_schema["name"]}}
    chain = CreatorAgent(
        llm=llm,
        prompt=prompt,
        llm_kwargs=llm_kwargs,
        output_parser=JsonOutputFunctionsParser(),
        output_key="messages",
        tool=tool,
        verbose=False,
    )
    return chain


llm = create_llm(temperature=0, model=config.model, streaming=config.use_stream_callback, verbose=True)
code_interpreter_agent = create_creator_agent(llm=llm)
