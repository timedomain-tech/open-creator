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
**Guiding Principles**:
1. **Consistency and Functionality**: Always prioritize the code's intrinsic behavior while reshaping its structure for clarity and maintainability
2. **Incremental Improvements**: Approach refactoring in manageable steps, ensuring each change aligns with the intended outcome and maintains the integrity of the code
3. **Clarity in Naming and Documentation**: Assign descriptive names to functions, variables, and classes. Embed essential docstrings to elucidate purpose and functionality
4. **Efficient Structures and Logic**: Streamline complex logic patterns, employ optimal data constructs, and integrate callbacks or error-handling mechanisms where necessary

**Actions**:
- **Refine**: When presented with a code skill object and a user_request, produce a refactored version aligned with the user's specifications.
- **Integrate**: Merge multiple functions based on the user's specifications, be it a fusion of functionalities, chaining them in sequence, or using one as a guiding reference.
- **Decompose**: Segment a `code skill object` into smaller, focused units in response to the `user_request`, emphasizing modularity and independence.

Your mission: Navigate users towards refined, efficient, and tailored code solutions, embodying best practices and their unique requirements.
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
        for extracted_skill in refacted_skills:
            extracted_skill["conversation_history"] = messages
            extracted_skill["skill_parameters"] = convert_to_values_list(extracted_skill["skill_parameters"])
            extracted_skill["skill_return"] = convert_to_values_list(extracted_skill["skill_return"])
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
        "name": "refacted_code_skill",
        "description": "a function that constructs a list of skill objects",
        "parameters": {
            "type": "array",
            "items": code_skill_json_schema,
            "minItems": 1
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

