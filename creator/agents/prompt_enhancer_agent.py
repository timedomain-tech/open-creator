from typing import Any, Dict

from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import parse_partial_json

from creator.utils import load_system_prompt, load_json_schema
from creator.llm import create_llm
from creator.utils import print

from creator.agents.base import BaseAgent


class PromptEnhancerAgent(BaseAgent):
    output_key: str = "request"
    agent_name: str = "PromptEnhancerAgent"

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
            # print(f"[green]{prefix_prompt}[/green]\n{orignal_request}\n[green]{postfix_prompt}[/green]")
            return {"request": "\n".join([prefix_prompt, orignal_request, postfix_prompt])}
        return {"request": orignal_request}


def create_prompt_enhancer_agent(config):
    template = load_system_prompt(config.prompt_enhancer_agent_prompt_path)
    function_schema = load_json_schema(config.prompt_enhancer_schema_path)
    chain = PromptEnhancerAgent(
        llm=create_llm(config, config.agent_model_config.PROMPT_ENHANCER_AGENT),
        system_template=template,
        function_schemas=[function_schema],
        verbose=False
    )
    return chain
