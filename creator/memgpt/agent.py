from typing import List, Dict, Any, Optional
import datetime

from langchain.schema.messages import FunctionMessage
from langchain.output_parsers.json import parse_partial_json
from langchain.callbacks.manager import CallbackManager
from langchain.prompts import ChatPromptTemplate
from langchain.adapters.openai import convert_openai_messages

from creator.utils import load_system_prompt, load_json_schema
from creator.agents.base import BaseAgent
from creator.agents import create_creator_agent
from creator.llm import create_llm

from .memory import MemoryManager
from .constants import (
    MESSAGE_SUMMARY_WARNING_STR,
    FUNC_FAILED_HEARTBEAT_MESSAGE,
    REQ_HEARTBEAT_MESSAGE
)
from .message_handler import (
    get_initial_boot_messages,
    get_login_event,
    package_message
)
from .tools_handler import available_functions


class MemGPT(BaseAgent):
    subagent: Optional[BaseAgent] = None
    pause_heartbeats_start: Optional[datetime.datetime] = None
    function_failed: bool = False
    heartbeat_request: bool = False
    memory_manager: MemoryManager = None
    memgpt_config: dict = None
    pause_heartbeats_start: datetime.datetime = None
    pause_heartbeats_minutes: int = 0

    @property
    def _chain_type(self):
        return "MemGPT"

    @property
    def input_keys(self) -> List[str]:
        return ["user_request"]

    def preprocess_inputs(self, inputs: Dict[str, Any]):
        """Preprocesses inputs to the agent"""
        if "session_id" in inputs and inputs["session_id"] != self.memgpt_config.session_id:
            self.memgpt_config.session_id = inputs["session_id"]
            self.memory_manager = MemoryManager(self.memgpt_config)
        else:
            inputs["session_id"] = self.memory_manager.session_id

        # inputs["memory_edit_timestamp"] = self.memory_manager.memory_edit_timestamp
        inputs["memory_edit_timestamp"] = 0
        inputs["recall_memory_count"] = self.memory_manager.recall_memory_count
        inputs["archival_memory_count"] = self.memory_manager.archival_memory_count

        inputs["persona"] = self.memory_manager.persona
        inputs["human"] = self.memory_manager.human
        inputs["subagent_tasks"] = self.memgpt_config.AGENT_SUBTASKS

        return inputs

    def construct_prompt(self, langchain_messages: Dict[str, Any]):
        extra_messages = []
        if self.memory_manager.is_new_session:
            init_messages = convert_openai_messages(get_initial_boot_messages())
            login_message = convert_openai_messages(get_login_event())
            extra_messages = init_messages + login_message

        prompt = ChatPromptTemplate.from_messages(messages=[
            ("system", self.system_template),
            *extra_messages,
            *langchain_messages
        ])
        return prompt

    async def arun_tool(self, function_call: Dict[str, Any], run_manager: Optional[CallbackManager] = None):
        function_name = function_call.get("name", "")
        # Failure case 1: function name is wrong
        try:
            function_to_call = available_functions[function_name]
        except KeyError:
            extra_info = {"status": 'Failed', "message": f'No function named {function_name}'}
            function_response = package_message(message_type=None, extra_info=extra_info)
            self.heartbeat_request = None
            self.function_failed = True
            message = FunctionMessage(name=function_name, content=function_response)
            return message

        # Failure case 2: function name is OK, but function args are bad JSON
        try:
            raw_function_args = function_call.get("arguments", "{}")
            function_args = parse_partial_json(raw_function_args)
        except Exception:
            extra_info = {"status": 'Failed', "message": f"Error parsing JSON for function '{function_name}' arguments: {raw_function_args}"}
            function_response = package_message(message_type=None, extra_info=extra_info)
            self.heartbeat_request = None
            self.function_failed = True
            message = FunctionMessage(name=function_name, content=function_response)
            return message

        # (Still parsing function args)
        # Handle requests for immediate heartbeat
        heartbeat_request = function_args.pop('request_heartbeat', False)
        if not (isinstance(heartbeat_request, bool) or heartbeat_request is None):
            print(f"> Warning: 'request_heartbeat' arg parsed was not a bool or None, type={type(heartbeat_request)}, value={heartbeat_request}", print_type="markdown")
            heartbeat_request = None
        self.heartbeat_request = heartbeat_request

        # Failure case 3: function failed during execution
        try:
            function_args["memgpt"] = self
            function_response_string = await function_to_call.arun(tool_input=function_args, callbacks=run_manager)
            extra_info = {"status": 'OK', "message": function_response_string}
            function_response = package_message(message_type=None, extra_info=extra_info)
        except Exception as e:
            extra_info = {"status": 'Failed', "message": f"Error calling function {function_name} with args {function_args}: {str(e)}"}
            function_response = package_message(message_type=None, extra_info=extra_info)
            self.heartbeat_request = None
            self.function_failed = True
            message = FunctionMessage(name=function_name, content=function_response)
            return message

        # for send_message, when receiver is human, no need to send heartbeat request
        if function_name == "send_message":
            is_human = "receiver" not in function_args or function_args["receiver"] == "human"
            if is_human:
                self.heartbeat_request = None

        # If no failures happened along the way: ...
        # Step 4: send the info on the function call and function response to GPT
        message = FunctionMessage(name=function_name, content=function_response)
        return message

    async def arun_workflow(self, inputs: Dict[str, Any], run_manager: Optional[CallbackManager] = None) -> Dict[str, Any]:
        run_manager_callbacks = run_manager.get_child() if run_manager else None
        self.llm.function_calls = self.function_schemas
        llm_with_functions = self.llm.bind(functions=self.function_schemas)
        user_request = inputs.get("user_request")
        user_message = package_message(message_type="user_message", extra_info={"message": user_request})

        counter = 0
        while True:
            self.start_callbacks()
            skil_next_user_input = False

            # we need re-preprocess inputs because core memory can be modified
            inputs = self.preprocess_inputs(inputs)

            # handle usre request
            await self.memory_manager.add_user_message(user_message)
            langchain_messages = self.memory_manager.messages

            # construct prompt and run
            prompt = self.construct_prompt(langchain_messages)
            llm_chain = (prompt | llm_with_functions).with_config({"run_name": f"Iteration {counter+1}"})
            message = llm_chain.invoke(inputs, {"callbacks": run_manager_callbacks})
            await self.memory_manager.add_message(message)

            # handle with ai response
            function_call = message.additional_kwargs.get("function_call", None)
            if function_call is None:
                self.heartbeat_request = None
                self.function_failed = None
            else:
                tool_result = await self.arun_tool(function_call, run_manager_callbacks)
                await self.memory_manager.add_message(tool_result)

            user_message = None
            if self.llm.trimed:
                user_message = package_message(message_type="system_alert", extra_info={"message": MESSAGE_SUMMARY_WARNING_STR})
                skil_next_user_input = True
            elif self.function_failed:
                user_message = package_message(message_type="heartbeat", extra_info={"reason": FUNC_FAILED_HEARTBEAT_MESSAGE})
                skil_next_user_input = True
            elif self.heartbeat_request:
                user_message = package_message(message_type="heartbeat", extra_info={"reason": REQ_HEARTBEAT_MESSAGE})
                skil_next_user_input = True

            if not skil_next_user_input or user_message is None:
                self.end_callbacks(message)
                break

            if user_message is not None:
                await self.memory_manager.add_user_message(user_message)
            counter += 1
            self.end_callbacks(message)

        return self.memory_manager.session_id

    async def aparse_output(self, session_id):
        return {self.output_key: session_id}

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManager] = None,
    ) -> Dict[str, str]:
        output = {self.output_key: None}
        try:
            messages = await self.arun_workflow(inputs, run_manager)
            output = await self.aparse_output(messages)
        except Exception as e:
            self.error_callbacks(e)
            raise e
        return output


def create_memgpt(config, subagent=None):
    template = load_system_prompt(config.memgpt_system_prompt_path)
    function_schemas = load_json_schema(config.memgpt_function_schema_path)
    memory_manager = MemoryManager(config.memgpt_config)
    llm = create_llm(config)
    if subagent is None:
        subagent = create_creator_agent(config)
    chain = MemGPT(
        llm=llm,
        subagent=subagent,
        system_template=template,
        function_schemas=function_schemas,
        memory_manager=memory_manager,
        memgpt_config=config.memgpt_config,
        output_key="session_id",
        verbose=False,
    )
    return chain
