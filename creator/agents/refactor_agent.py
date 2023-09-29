from typing import Any, Dict, List, Optional
from langchain.chains.llm import LLMChain
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.adapters.openai import convert_openai_messages

from creator.config.library import config
from creator.utils.dict2list import convert_to_values_list
import json
import os

from creator.llm.llm_creator import create_llm

_SYSTEM_TEMPLATE = """**You are the Code Refactoring Agent**, an expert dedicated to elevating the quality of code while preserving its core functionality
Follow the guidelines below:
1. Only extract all the required properties mentioned in the 'create_refactored_codeskills' function
2. When the action type is Refine or Combine, return only one item in the list
3. When the action type is Decompose, return more than one items in the list
4. Your mission: Navigate users towards refined, efficient, and tailored code solutions, embodying best practices and their unique requirements.
5. When creating a new skill object, consider the following principles
    1. **Consistency and Functionality**: Always prioritize the code's intrinsic behavior while reshaping its structure for clarity and maintainability
    2. **Incremental Improvements**: Approach refactoring in manageable steps, ensuring each change aligns with the intended outcome and maintains the integrity of the code
    3. **Clarity in Naming and Documentation**: Assign descriptive names to functions, variables, and classes. Embed essential docstrings to elucidate purpose and functionality
    4. **Efficient Structures and Logic**: Streamline complex logic patterns, employ optimal data constructs, and integrate callbacks or error-handling mechanisms where necessary
5. When you output the skill_dependencies, skill_parameters, and skill_return, always follow definiton of CodeSkillDependency and CodeSkillParameter
"""


class CodeRefactorAgent(LLMChain):
    @property
    def _chain_type(self):
        return "CodeRefactorAgent"

    @property
    def input_keys(self) -> List[str]:
        return ["messages"]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        callback = None
        if self.llm.callbacks is not None:
            callback = self.llm.callbacks.handlers[0]
            callback.on_chain_start()
        
        messages = inputs.pop("messages")
        chat_messages = convert_openai_messages(messages)
        chat_messages.append(("system", _SYSTEM_TEMPLATE))
        prompt = ChatPromptTemplate.from_messages(chat_messages)
        self.prompt = prompt

        response = self.generate([inputs], run_manager=run_manager)

        refacted_skills = self.create_outputs(response)[0]["refacted_skills"]
        refacted_skills = refacted_skills["refacted_skills"]
        for extracted_skill in refacted_skills:
            extracted_skill["conversation_history"] = messages
            extracted_skill["skill_parameters"] = convert_to_values_list(extracted_skill["skill_parameters"]) if "skill_parameters" in extracted_skill else None
            extracted_skill["skill_return"] = convert_to_values_list(extracted_skill["skill_return"]) if "skill_return" in extracted_skill else None
        if callback:
            callback.on_chain_end()
        return {
            "refacted_skills": refacted_skills
        }


def create_code_refactor_agent(llm):
    path = os.path.join(os.path.dirname(__file__), ".", "codeskill_function_schema.json")
    with open(path) as f:
        code_skill_json_schema = json.load(f)
    function_schema = {
        "name": "create_refactored_codeskills",
        "description": "a function that constructs a list of refactored skill objects. return only one item when your action is to combine or refine skill object(s), otherwise return more than one items",
        "parameters": {
            "properties": {
                "refacted_skills": {
                    "type": "array",
                    "items": code_skill_json_schema,
                    "minItems": 1
                }
            },
            "type": "object",
            "required": ["refacted_skills"]
        }
    }

    llm_kwargs = {"functions": [function_schema], "function_call": {"name": function_schema["name"]}}
    output_parser = JsonOutputFunctionsParser()
    # dummy prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_TEMPLATE),
        ]
    )
    chain = CodeRefactorAgent(
        llm=llm,
        prompt=prompt,
        llm_kwargs=llm_kwargs,
        output_parser=output_parser,
        output_key="refacted_skills",
        verbose=False
    )
    return chain


llm = create_llm(temperature=0, model=config.model, streaming=config.use_stream_callback, verbose=True)
code_refactor_agent = create_code_refactor_agent(llm)

