
import json
from typing import Any, Dict

from langchain.output_parsers.json import parse_partial_json

from creator.code_interpreter.safe_python import SafePythonInterpreter
from creator.config.library import config
from creator.utils import load_system_prompt
from creator.llm.llm_creator import create_llm
from creator.core import creator

from .base import BaseAgent


OPEN_CREATOR_API_DOC = load_system_prompt(config.api_doc_path)
ALLOWED_FUNCTIONS = {"create", "save", "search", "CodeSkill"}
ALLOW_METHODS = {".show", ".test", ".run", "__add__", "__gt__", "__lt__", "__annotations__"}


class CreatorAgent(BaseAgent):
    total_tries: int = 5
    allow_user_confirm: bool = config.run_human_confirm
    namespace: dict = {}

    @property
    def _chain_type(self):
        return "CreatorAgent"

    def prep_inputs(self, inputs: Dict[str, Any] | Any) -> Dict[str, str]:
        inputs["OPEN_CREATOR_API_DOC"] = OPEN_CREATOR_API_DOC
        inputs["NAMESPACE"] = self.namespace
        return inputs

    def postprocess_mesasge(self, message):
        function_call = message.additional_kwargs.get("function_call", None)
        if function_call is not None:
            arguments = parse_partial_json(function_call.get("arguments", "{}"))
            if arguments is None and function_call.get("arguments", None) is not None:
                function_call = {
                    "name": "python",
                    "arguments": json.dumps({"code": function_call.get("arguments")}, ensure_ascii=False)
                }
                message.additional_kwargs["function_call"] = function_call
        return message


def create_creator_agent(llm):
    template = load_system_prompt(config.creator_agent_prompt_path)

    code_interpreter = SafePythonInterpreter(allowed_functions=ALLOWED_FUNCTIONS, allowed_methods=ALLOW_METHODS)

    create_skill_obj = creator.create(skill_path=creator.config.build_in_skill_config["create"])
    save_skill_obj = creator.create(skill_path=creator.config.build_in_skill_config["save"])
    search_skill_obj = creator.create(skill_path=creator.config.build_in_skill_config["search"])
    code = "\n\n".join([create_skill_obj.skill_code, save_skill_obj.skill_code, search_skill_obj.skill_code])
    code_interpreter.setup(code)
    namespace = {name:str(value) for name, value in code_interpreter.namespace.items() if name in ALLOWED_FUNCTIONS}
    chain = CreatorAgent(
        llm=llm,
        system_template=template,
        namespace=namespace,
        tools=[code_interpreter],
        function_schemas=[code_interpreter.to_function_schema()],
        verbose=False,
    )
    return chain


llm = create_llm(temperature=config.temperature, model=config.model, streaming=config.use_stream_callback, verbose=True)
open_creator_agent = create_creator_agent(llm=llm)
