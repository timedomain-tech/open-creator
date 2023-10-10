
from typing import List, Dict, Any, Optional
import json

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.schema.messages import FunctionMessage
from langchain.prompts import ChatPromptTemplate
from langchain.adapters.openai import convert_message_to_dict, convert_openai_messages
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.tools.base import BaseTool
from langchain.output_parsers.json import parse_partial_json

from creator.code_interpreter.safe_python import SafePythonInterpreter
from creator.config.library import config
from creator.utils import truncate_output, ask_run_code_confirm, load_system_prompt, get_user_info

from creator.llm.llm_creator import create_llm
import creator


_SYSTEM_TEMPLATE = load_system_prompt(config.creator_agent_prompt_path)
OPEN_CREATOR_API_DOC = load_system_prompt(config.api_doc_path)


def fix_arguments(function_call):
    arguments = parse_partial_json(function_call.get("arguments", "{}"))
    if arguments is None and function_call.get("arguments", None) is not None:
        return {
            "name": "python",
            "arguments": json.dumps({
                "code": function_call.get("arguments")
            }, ensure_ascii=False)
        }
    return function_call


class CreatorAgent(LLMChain):
    total_tries: int = 5
    tool: BaseTool

    @property
    def _chain_type(self):
        return "CreatorAgent"

    @property
    def input_keys(self) -> List[str]:
        return ["messages"]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManager] = None,
    ) -> Dict[str, Any]:

        messages = inputs.pop("messages")
        inputs["OPEN_CREATOR_API_DOC"] = OPEN_CREATOR_API_DOC
        allow_user_confirm = config.run_human_confirm
        langchain_messages = convert_openai_messages(messages)

        total_tries = self.total_tries
        current_try = 0

        llm_with_functions = self.llm.bind(functions=[self.tool.to_function_schema()])
        
        callback = None
        if self.llm.callbacks is not None:
            callback = self.llm.callbacks.handlers[0]

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
            
            function_call = fix_arguments(function_call)
            message.additional_kwargs["function_call"] = function_call
            langchain_messages[-1] = message
            arguments = parse_partial_json(function_call.get("arguments", "{}"))
            if arguments is None:
                break
            code = arguments.get("code", None)
            if code is None:
                break
            tool_result = self.tool.run(code)
            tool_result = truncate_output(tool_result)
            output = str(tool_result.get("stdout", "")) + str(tool_result.get("stderr", ""))
            if callback:
                callback.on_tool_end(output)
            
            function_message = FunctionMessage(name="python", content=json.dumps(tool_result, ensure_ascii=False))
            langchain_messages.append(function_message)
            current_try += 1
            if callback:
                callback.on_chain_end()

        openai_message = list(map(convert_message_to_dict, langchain_messages))
        if callback:
            callback.end()
        return {
            "messages": openai_message
        }


def create_creator_agent(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_TEMPLATE),
        ]
    )
    code_interpreter = SafePythonInterpreter()
    create_skill_obj = creator.create(skill_path=creator.config.build_in_skill_config["create"])
    save_skill_obj = creator.create(skill_path=creator.config.build_in_skill_config["save"])
    search_skill_obj = creator.create(skill_path=creator.config.build_in_skill_config["search"])
    code = "\n\n".join([create_skill_obj.skill_code, save_skill_obj.skill_code, search_skill_obj.skill_code])
    code_interpreter.setup(code)
    function_schema = code_interpreter.to_function_schema()
    llm_kwargs = {"functions": [function_schema], "function_call": {"name": function_schema["name"]}}
    chain = CreatorAgent(
        llm=llm,
        prompt=prompt,
        llm_kwargs=llm_kwargs,
        output_parser=JsonOutputFunctionsParser(),
        output_key="messages",
        tool=code_interpreter,
        verbose=False,
    )
    return chain


llm = create_llm(temperature=config.temperature, model=config.model, streaming=config.use_stream_callback, verbose=True)
open_creator_agent = create_creator_agent(llm=llm)
