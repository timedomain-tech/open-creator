from typing import List, Dict, Any, Optional
import json

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.schema.messages import FunctionMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate
from langchain.adapters.openai import convert_message_to_dict, convert_openai_messages
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.tools.base import BaseTool
from langchain.output_parsers.json import parse_partial_json

from creator.code_interpreter import CodeInterpreter
from creator.config.library import config
from creator.utils import truncate_output, ask_run_code_confirm, get_user_info, load_system_prompt
from creator.llm.llm_creator import create_llm


_SYSTEM_TEMPLATE = load_system_prompt(config.tester_agent_prompt_path)
DEBUGGING_TIPS = load_system_prompt(config.tips_for_testing_prompt_path)


class CodeTesterAgent(LLMChain):
    total_tries: int = 10
    tool: BaseTool
    functions: list = []

    @property
    def _chain_type(self):
        return "CodeTesterAgent"

    @property
    def input_keys(self) -> List[str]:
        return ["messages"]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManager] = None,
    ) -> Dict[str, Any]:

        messages = inputs.pop("messages")
        allow_user_confirm = config.run_human_confirm
        langchain_messages = convert_openai_messages(messages)

        total_tries = self.total_tries
        current_try = 0

        llm_with_functions = self.llm.bind(functions=self.functions)
        callback = None
        if self.llm.callbacks:
            callback = self.llm.callbacks.handlers[0]

        test_summary = []
        while current_try < total_tries:
            if callback:
                callback.on_chain_start()

            prompt = ChatPromptTemplate.from_messages(messages=[
                ("system", _SYSTEM_TEMPLATE + get_user_info()),
                *langchain_messages
            ])
            llm_chain = prompt | llm_with_functions
            message = llm_chain.invoke(inputs)
            langchain_messages.append(message)
            function_call = message.additional_kwargs.get("function_call", None)
            if function_call is None:
                break

            can_run_code = True
            if allow_user_confirm:
                can_run_code = ask_run_code_confirm()
            if not can_run_code:
                break

            function_name = function_call.get("name", "")
            arguments = parse_partial_json(function_call.get("arguments", "{}"))
            if function_name == "test_summary":
                test_summary = arguments.get("test_cases", [])
                break
            tool_result = self.tool.run(arguments)
            tool_result = truncate_output(tool_result)
            output = str(tool_result.get("stdout", "")) + str(tool_result.get("stderr", ""))
            if callback:
                callback.on_tool_end(output)

            function_message = FunctionMessage(name="run_code", content=json.dumps(tool_result, ensure_ascii=False))
            langchain_messages.append(function_message)
            if len(tool_result.get("stderr", "")) > 0 and "error" in tool_result["stderr"].lower():  # add tips for debugging
                langchain_messages.append(HumanMessage(content=DEBUGGING_TIPS))
            elif len(output) > 100:  # tips for avoiding repeating the output of `run_code`
                langchain_messages.append(HumanMessage(content="go on to next step if has, otherwise end."))
            current_try += 1
            if callback:
                callback.on_chain_end()

        openai_message = list(map(convert_message_to_dict, langchain_messages))
        return {
            "output": {
                "messages": openai_message,
                "test_summary": test_summary
            }
        }


def create_code_tester_agent(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_TEMPLATE),
        ]
    )
    tool = CodeInterpreter()
    code_interpreter_function_schema = tool.to_function_schema()
    with open(config.testsummary_function_schema_path) as f:
        test_summary_function_schema = json.load(f)
    chain = CodeTesterAgent(
        llm=llm,
        prompt=prompt,
        functions=[code_interpreter_function_schema, test_summary_function_schema],
        output_parser=JsonOutputFunctionsParser(),
        output_key="output",
        tool=tool,
        verbose=False,
    )
    return chain


llm = create_llm(temperature=config.temperature, model=config.model, streaming=config.use_stream_callback, verbose=True)
code_tester_agent = create_code_tester_agent(llm=llm)
