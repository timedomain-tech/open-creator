
from typing import List, Dict, Any, Optional
from threading import Thread
import json

from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.tools.base import BaseTool
from langchain.adapters.openai import convert_message_to_dict, convert_openai_messages
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import parse_partial_json
from langchain.schema.messages import FunctionMessage

from creator.utils import get_user_info, ask_run_code_confirm, remove_tips
from creator.callbacks.buffer_manager import buffer_output_manager


class BaseAgent(LLMChain):
    total_tries: int = 1
    tools: List[BaseTool] = []
    function_schemas: List[dict] = []
    output_key: str = "messages"
    system_template: str = ""
    allow_user_confirm: bool = False
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(messages=["system", ""])

    @property
    def _chain_type(self):
        return "BaseAgent"

    @property
    def input_keys(self) -> List[str]:
        return ["messages"]

    def construct_prompt(self, langchain_messages: Dict[str, Any]):
        prompt = ChatPromptTemplate.from_messages(messages=[
            ("system", self.system_template + get_user_info()),
            *langchain_messages
        ])
        return prompt

    def get_callbacks(self):
        callbacks = []
        if self.llm.callbacks is not None:
            callbacks = self.llm.callbacks.handlers
        return callbacks

    def start_callbacks(self):
        for callback in self.get_callbacks():
            callback.on_chain_start(inputs=None, serialized=None, run_id=1, agent_name=self._chain_type)

    def update_tool_result_in_callbacks(self, tool_result: FunctionMessage):
        if tool_result:
            for callback in self.get_callbacks():
                callback.on_tool_end(chunk=tool_result)

    def end_callbacks(self, message):
        for callback in self.get_callbacks():
            callback.on_chain_end(message=message, outputs=message, run_id=1)

    def error_callbacks(self, err):
        for callback in self.get_callbacks():
            callback.on_chain_error(error=err, run_id=1)

    def postprocess_mesasge(self, message):
        return message

    def tool_result_to_str(self, tool_result) -> str:
        if isinstance(tool_result, dict):
            return json.dumps(tool_result, ensure_ascii=False)
        return str(tool_result)

    def run_tool(self, function_call: Dict[str, Any]):
        function_name = function_call.get("name", "")
        arguments = parse_partial_json(function_call.get("arguments", "{}"))
        tool_result = None
        for tool in self.tools:
            if tool.name == function_name:
                if self.human_confirm():
                    tool_result = tool.run(arguments)
                    tool_result = self.tool_result_to_str(tool_result)
                    tool_result = FunctionMessage(name=function_name, content=tool_result)
                    self.update_tool_result_in_callbacks(tool_result)
                break
        return tool_result

    def human_confirm(self):
        can_run_tool = True
        if self.allow_user_confirm:
            can_run_tool = ask_run_code_confirm()
        return can_run_tool

    def messages_hot_fix(self, langchain_messages):
        return langchain_messages

    def preprocess_inputs(self, inputs: Dict[str, Any]):
        return inputs

    def run_workflow(self, inputs: Dict[str, Any], run_manager: Optional[CallbackManager] = None) -> Dict[str, Any]:
        inputs = self.preprocess_inputs(inputs)
        messages = inputs.pop("messages")
        langchain_messages = convert_openai_messages(messages)
        llm_with_functions = self.llm.bind(functions=self.function_schemas)
        current_try = 0
        while current_try < self.total_tries:
            self.start_callbacks()
            prompt = self.construct_prompt(langchain_messages)
            llm_chain = prompt | llm_with_functions | self.postprocess_mesasge
            message = llm_chain.invoke(inputs)
            langchain_messages.append(message)
            function_call = message.additional_kwargs.get("function_call", None)
            if function_call is None:
                self.end_callbacks(message)
                break

            tool_result = self.run_tool(function_call)
            if tool_result is None:
                self.end_callbacks(message)
                break
            langchain_messages.append(tool_result)
            langchain_messages = self.messages_hot_fix(langchain_messages)
            current_try += 1
            self.end_callbacks(message)
        langchain_messages = remove_tips(langchain_messages)
        openai_messages = list(map(convert_message_to_dict, langchain_messages))
        return openai_messages

    def parse_output(self, messages):
        return {"messages": messages}

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManager] = None,
    ) -> Dict[str, Any]:
        output = {self.output_key: None}
        try:
            messages = self.run_workflow(inputs, run_manager)
            output = self.parse_output(messages)
        except Exception as e:
            self.error_callbacks(e)
            raise e
        return output

    def iter(self, inputs):
        output_queue = []

        def task_target():
            result = self.run(inputs)
            m = (self._chain_type, (result, result))
            output_queue.append(m)

        task = Thread(target=task_target)
        task.start()
        while 1:
            for e in buffer_output_manager:
                yield False, e
            if len(output_queue) > 0:
                result = output_queue.pop()
                yield True, result
                return

