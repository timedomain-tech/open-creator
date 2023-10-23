from typing import Any, Dict

from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import parse_partial_json

from creator.config.library import config
from creator.utils import load_system_prompt
from creator.llm.llm_creator import create_llm
from creator.utils import print

from creator.agents.base import BaseAgent
import json


class PromptEnhancerAgent(BaseAgent):
    output_key: str = "enhanced_prompt"

    @property
    def _chain_type(self):
        return "PromptEnhancerAgent"

    def construct_prompt(self, langchain_messages: Dict[str, Any]):
        prompt = ChatPromptTemplate.from_messages(messages=[
            *langchain_messages,
            ("system", self.system_template)
        ])
        return prompt

    def parse_output(self, messages):
        orignal_request = messages[0].get("content", "")
        function_call = messages[1].get("function_call", None)
        if function_call is not None:
            rewrited_prompt = parse_partial_json(function_call.get("arguments", "{}"))
            prefix_prompt = rewrited_prompt.get("prefix_prompt", "")
            postfix_prompt = rewrited_prompt.get("postfix_prompt", "")
            print(f"[green]{prefix_prompt}[/green]\n{orignal_request}\n[green]{postfix_prompt}[/green]")
            return {"enhanced_prompt": "\n".join([prefix_prompt, orignal_request, postfix_prompt])}
        return {"enhanced_prompt": orignal_request}


def create_prompt_enhancer_agent(llm):
    template = load_system_prompt(config.prompt_enhancer_agent_prompt_path)

    with open(config.prompt_enhancer_schema_path, encoding="utf-8") as f:
        function_schema = json.load(f)

    chain = PromptEnhancerAgent(
        llm=llm,
        system_template=template,
        function_schemas=[function_schema],
        verbose=False
    )
    return chain


llm = create_llm(config)
