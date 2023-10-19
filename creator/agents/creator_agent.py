
import json
from typing import Any, Dict

from langchain.output_parsers.json import parse_partial_json
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import AIMessage, FunctionMessage, SystemMessage
from langchain.schema.runnable import RunnableConfig

from creator.code_interpreter.safe_python import SafePythonInterpreter
from creator.config.library import config
from creator.utils import load_system_prompt, get_user_info, remove_tips
from creator.llm.llm_creator import create_llm

from .base import BaseAgent


OPEN_CREATOR_API_DOC = load_system_prompt(config.api_doc_path)
VERIFY_TIPS = load_system_prompt(config.tips_for_veryfy_prompt_path)
ALLOWED_FUNCTIONS = {"create", "save", "search", "CodeSkill"}
ALLOW_METHODS = {".show", ".show_code", ".test", ".run", ".save", "__add__", "__gt__", "__lt__", "__annotations__"}
IMPORT_CODE = (
    "from creator.core import creator\n"
    "from creator.core.skill import CodeSkill\n"
    "create, save, search = creator.create, creator.save, creator.search\n\n"
)


class CreatorAgent(BaseAgent):
    total_tries: int = 5
    allow_user_confirm: bool = config.run_human_confirm

    @property
    def _chain_type(self):
        return "CreatorAgent"

    def prep_inputs(self, inputs: Dict[str, Any] | Any) -> Dict[str, str]:
        inputs["OPEN_CREATOR_API_DOC"] = OPEN_CREATOR_API_DOC
        return inputs

    def construct_prompt(self, langchain_messages: Dict[str, Any]):
        prompt = ChatPromptTemplate.from_messages(messages=[
            ("system", self.system_template + get_user_info()),
            AIMessage(content="", additional_kwargs={"function_call": {"name": "python", "arguments": IMPORT_CODE}}),
            FunctionMessage(name="python",content="Environment setup done!"),
            *langchain_messages
        ])
        return prompt

    def messages_hot_fix(self, langchain_messages):
        langchain_messages = remove_tips(langchain_messages)
        langchain_messages.append(SystemMessage(content=VERIFY_TIPS))
        return langchain_messages

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

    async def ainvoke(self, inputs: Dict[str, Any], config: RunnableConfig | None = None, **kwargs: Any) -> Dict[str, Any]:
        return {"messages": self.run(inputs)}


def create_creator_agent(llm):
    template = load_system_prompt(config.creator_agent_prompt_path)

    code_interpreter = SafePythonInterpreter(allowed_functions=ALLOWED_FUNCTIONS, allowed_methods=ALLOW_METHODS, redirect_output=True)
    code_interpreter.setup(IMPORT_CODE)

    chain = CreatorAgent(
        llm=llm,
        system_template=template,
        tools=[code_interpreter],
        function_schemas=[code_interpreter.to_function_schema()],
        verbose=False,
    )
    return chain


llm = create_llm(config)
open_creator_agent = create_creator_agent(llm=llm)
