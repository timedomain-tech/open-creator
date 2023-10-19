from typing import Any, Dict
import json
import os

from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import parse_partial_json

from creator.config.library import config
from creator.utils import convert_to_values_list, load_system_prompt, get_user_info
from creator.llm.llm_creator import create_llm

from .base import BaseAgent


class CodeRefactorAgent(BaseAgent):
    output_key: str = "refacted_skills"

    @property
    def _chain_type(self):
        return "CodeRefactorAgent"

    def construct_prompt(self, langchain_messages: Dict[str, Any]):
        prompt = ChatPromptTemplate.from_messages(messages=[
            *langchain_messages,
            ("system", self.system_template + get_user_info())
        ])
        return prompt

    def parse_output(self, messages):
        function_call = messages[-1].get("function_call", None)
        if function_call is not None:
            refacted_skills = parse_partial_json(function_call.get("arguments", "{}"))
            refacted_skills = refacted_skills.get("refacted_skills", [])
            for extracted_skill in refacted_skills:
                extracted_skill["conversation_history"] = messages[:-1]
                extracted_skill["skill_parameters"] = convert_to_values_list(extracted_skill["skill_parameters"]) if "skill_parameters" in extracted_skill else None
                extracted_skill["skill_return"] = convert_to_values_list(extracted_skill["skill_return"]) if "skill_return" in extracted_skill else None
            return {"refacted_skills": refacted_skills}
        return {"refacted_skills": None}


def create_code_refactor_agent(llm):
    template = load_system_prompt(config.refactor_agent_prompt_path)
    path = os.path.join(config.codeskill_function_schema_path)
    with open(path, encoding="utf-8") as f:
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

    chain = CodeRefactorAgent(
        llm=llm,
        system_template=template,
        function_schemas=[function_schema],
        verbose=False
    )
    return chain


llm = create_llm(config)
code_refactor_agent = create_code_refactor_agent(llm)
