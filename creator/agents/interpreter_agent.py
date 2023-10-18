import json

from langchain.schema.messages import SystemMessage
from langchain.output_parsers.json import parse_partial_json

from creator.code_interpreter import CodeInterpreter, language_map
from creator.config.library import config
from creator.utils import load_system_prompt, remove_tips
from creator.llm.llm_creator import create_llm

from .base import BaseAgent


DEBUGGING_TIPS = load_system_prompt(config.tips_for_debugging_prompt_path)
VERIFY_TIPS = load_system_prompt(config.tips_for_veryfy_prompt_path)


class CodeInterpreterAgent(BaseAgent):
    total_tries: int = 10
    allow_user_confirm: bool = config.run_human_confirm

    @property
    def _chain_type(self):
        return "CodeInterpreterAgent"
    
    def postprocess_mesasge(self, message):
        function_call = message.additional_kwargs.get("function_call", None)
        if function_call is not None:
            name = function_call.get("name", "run_code")
            arguments = function_call.get("arguments", "{}")
            arguments_json = parse_partial_json(arguments)
            if name != "run_code" or not arguments_json:
                language = name if name in language_map else "python"
                function_call = {
                    "name": "run_code",
                    "arguments": json.dumps({"language": language, "code": arguments}, ensure_ascii=False)
                }
                message.additional_kwargs["function_call"] = function_call
        return message

    def messages_hot_fix(self, langchain_messages):
        langchain_messages = remove_tips(langchain_messages)
        tool_result = langchain_messages[-1].content
        tool_result = parse_partial_json(tool_result)
        if len(tool_result.get("stderr", "")) > 0 and "error" in tool_result["stderr"].lower():  # add tips for debugging
            langchain_messages.append(SystemMessage(content=DEBUGGING_TIPS))
        else:
            langchain_messages.append(SystemMessage(content=VERIFY_TIPS))
        return langchain_messages


def create_code_interpreter_agent(llm):
    tool = CodeInterpreter()
    function_schema = tool.to_function_schema()
    template = load_system_prompt(config.interpreter_agent_prompt_path)
    chain = CodeInterpreterAgent(
        llm=llm,
        system_template=template,
        function_schemas=[function_schema],
        tools=[tool],
        verbose=False,
    )
    return chain


llm = create_llm(config)
code_interpreter_agent = create_code_interpreter_agent(llm=llm)
