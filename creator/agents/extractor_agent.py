from typing import Dict, Any

from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import parse_partial_json

from creator.utils import convert_to_values_list, get_user_info, load_system_prompt, load_json_schema
from creator.llm import create_llm

from .base import BaseAgent


class SkillExtractorAgent(BaseAgent):
    output_key: str = "extracted_skill"

    @property
    def _chain_type(self):
        return "SkillExtractorAgent"

    def construct_prompt(self, langchain_messages: Dict[str, Any]):
        prompt = ChatPromptTemplate.from_messages(messages=[
            *langchain_messages,
            ("system", self.system_template + get_user_info())
        ])
        return prompt

    def parse_output(self, messages):
        function_call = messages[-1].get("function_call", None)
        try:
            if function_call is not None:
                content = function_call.get("arguments", "{}")
            else:
                content = messages[-1].get("content", "{}")
            extracted_skill = parse_partial_json(content)
            extracted_skill["conversation_history"] = messages[:-1]
            extracted_skill["skill_parameters"] = convert_to_values_list(extracted_skill["skill_parameters"]) if "skill_parameters" in extracted_skill else None
            extracted_skill["skill_return"] = convert_to_values_list(extracted_skill["skill_return"]) if "skill_return" in extracted_skill else None
            return {"extracted_skill": extracted_skill}
        except Exception:
            pass
        return {"extracted_skill": None}


def create_skill_extractor_agent(config):
    template = load_system_prompt(config.extractor_agent_prompt_path)
    # current file's parent as dir
    code_skill_json_schema = load_json_schema(config.codeskill_function_schema_path)
    function_schema = {
        "name": "extract_formmated_skill",
        "description": "a function that extracts a skill from a conversation history",
        "parameters": code_skill_json_schema
    }

    chain = SkillExtractorAgent(
        llm=create_llm(config, config.agent_model_config.EXTRACTOR_AGENT),
        system_template=template,
        function_schemas=[function_schema],
        verbose=False
    )
    return chain
