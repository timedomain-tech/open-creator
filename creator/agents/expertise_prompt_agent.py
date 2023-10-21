from typing import Any, Dict

from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import parse_partial_json

from creator.config.library import config
from creator.utils import load_system_prompt
from creator.llm.llm_creator import create_llm

from creator.agents.base import BaseAgent


class ExpertisePromptAgent(BaseAgent):
    output_key: str = "expertise_prompt"

    @property
    def _chain_type(self):
        return "ExpertisePromptAgent"

    def construct_prompt(self, langchain_messages: Dict[str, Any]):
        prompt = ChatPromptTemplate.from_messages(messages=[
            *langchain_messages,
            ("system", self.system_template)
        ])
        return prompt
 
    def parse_output(self, messages):
        function_call = messages[-1].get("function_call", None)
        if function_call is not None:
            rewrited_prompt = parse_partial_json(function_call.get("arguments", "{}"))
            prefix_prompt = rewrited_prompt.get("prefix_prompt", "")
            postfix_prompt = rewrited_prompt.get("postfix_prompt", "")
            result = {"prefix_prompt": prefix_prompt, "postfix_prompt": postfix_prompt}
            return {"expertise_prompt": result}
        return {"expertise_prompt": None}


def create_expertise_prompt_agent(llm):
    template = load_system_prompt(config.expertise_prompt_agent_prompt_path)

    function_schema = {
        "name": "expertise_prompt",
        "description": "a function that guide GPT to act as a specific expert in the field to respond to the user's request",
        "parameters": {
            "properties": {
                "prefix_prompt": {
                    "type": "string",
                    "description": "A concise directive provided at the beginning of the user's request, guiding GPT to adopt a specific expert role or mindset within a particular vertical.",
                },
                "postfix_prompt": {
                    "type": "string",
                    "description": "A brief set of tips or guidelines placed after the user's original request, offering additional context or direction for GPT's response. If you don't know how to give guidance based on the user's request just let the GPT think step-by-step.",
                }
            },
            "type": "object",
            "required": ["prefix_prompt", "postfix_prompt"]
        }
    }

    chain = ExpertisePromptAgent(
        llm=llm,
        system_template=template,
        function_schemas=[function_schema],
        verbose=False
    )
    return chain


llm = create_llm(config)
expertise_prompt_agent = create_expertise_prompt_agent(llm)