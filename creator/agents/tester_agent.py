import json

from langchain.schema.messages import SystemMessage
from langchain.output_parsers.json import parse_partial_json

from creator.code_interpreter import CodeInterpreter, language_map
from creator.config.library import config
from creator.utils import load_system_prompt, remove_tips
from creator.llm.llm_creator import create_llm

from .base import BaseAgent


DEBUGGING_TIPS = load_system_prompt(config.tips_for_testing_prompt_path)
VERIFY_TIPS = load_system_prompt(config.tips_for_veryfy_prompt_path)


class CodeTesterAgent(BaseAgent):
    total_tries: int = 10
    output_key: str = "output"
    allow_user_confirm: bool = config.run_human_confirm

    @property
    def _chain_type(self):
        return "CodeTesterAgent"

    def postprocess_mesasge(self, message):
        function_call = message.additional_kwargs.get("function_call", None)
        if function_call is not None:
            name = function_call.get("name", "run_code")
            arguments = function_call.get("arguments", "{}")
            arguments_json = parse_partial_json(arguments)
            if name not in ("run_code", "test_summary") or not arguments_json:
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

    def parse_output(self, messages):
        function_call = messages[-1].get("function_call", None)
        test_summary = None
        if function_call is not None:
            function_name = function_call.get("name", "")
            arguments = parse_partial_json(function_call.get("arguments", "{}"))
            if function_name == "test_summary":
                test_summary = arguments.get("test_cases", [])
                messages = messages[:-1]
        return {
            "output":{
                "messages": messages,
                "test_summary": test_summary,
            }
        }


def create_code_tester_agent(llm):
    template = load_system_prompt(config.tester_agent_prompt_path)
    tool = CodeInterpreter()

    code_interpreter_function_schema = tool.to_function_schema()
    with open(config.testsummary_function_schema_path, encoding="utf-8") as f:
        test_summary_function_schema = json.load(f)

    chain = CodeTesterAgent(
        llm=llm,
        system_template=template,
        function_schemas=[code_interpreter_function_schema, test_summary_function_schema],
        tools=[tool],
        verbose=False,
    )
    return chain


llm = create_llm(config)
code_tester_agent = create_code_tester_agent(llm=llm)
