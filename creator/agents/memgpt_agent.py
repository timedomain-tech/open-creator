from typing import List, Dict, Any, Optional
import datetime
import json
import uuid

from langchain.schema.messages import FunctionMessage
from langchain.output_parsers.json import parse_partial_json
from langchain.callbacks.manager import CallbackManager
from langchain.prompts import ChatPromptTemplate
from langchain.adapters.openai import convert_openai_messages, convert_message_to_dict
from creator.config.library import config
from creator.utils import load_system_prompt, get_user_info
from creator.callbacks.streaming_stdout import OutputBufferStreamingHandler
from creator.agents.base import BaseAgent
from creator.utils.memgpt_utils import (
    get_initial_boot_messages,
    get_login_event,
    DEFAULT_PERSONA,
    DEFAULT_HUMAN,
    DEFAULT_AGENT_SUBTASKS,
    package_message,
    MESSAGE_SUMMARY_WARNING_TOKENS,
    MESSAGE_SUMMARY_WARNING_STR
)
from creator.memory.schema import MessageConverter, ChatMessageHistory
from creator.llm.tokentrim import num_tokens_from_messages


class MemGPTAgent(BaseAgent):
    total_tries: int = 10
    allow_user_confirm: bool = config.run_human_confirm
    subagent: Optional[BaseAgent] = None
    pause_heartbeats_start: Optional[datetime.datetime] = None
    is_new_session: bool = True
    heartbeat_request: bool = False
    long_term_memory: ChatMessageHistory = None

    @property
    def _chain_type(self):
        return "MemGPTAgent"

    @property
    def input_keys(self) -> List[str]:
        return ["user_request"]

    def build_memory(self, session_id=None):
        if session_id is None:
            session_id = str(uuid.uuid4())
        self.long_term_memory = ChatMessageHistory(
            session_id=session_id,
            connection_string=f"sqlite:///{config.memory_path}/.langchain.db",
            custom_message_converter=MessageConverter()
        )

    async def send_message(self, message: str, receiver: str = "human"):
        """Sends a message to a specified receiver"""
        if receiver == "human":
            return None
        else:
            # run subagent
            pass

    async def pause_heartbeats(self, minutes: int, max_pause: int = 360):
        """Pauses heartbeats for a specified number of minutes"""
        minutes = min(max_pause, minutes)
        self.pause_heartbeats_start = datetime.datetime.now()
        self.pause_heartbeats_minutes = int(minutes)
        return f'Pausing timed heartbeats for {minutes} min'

    async def add_memory(self, name: str, content: str):
        """Adds a memory with a specified name and content, and optionally requests a heartbeat"""
        pass

    async def modify_memory(self, name: str, old_content:str, new_content: str):
        """Modifies a memory with a specified name, replacing old content with new content, and optionally requests a heartbeat"""
        pass

    async def search_memory(self, memory_type: str, page: int = 0, query: str = "", start_date: str = "", end_date: str = ""):
        """Searches memory of a specified type, with optional query, start date, end date, and request for heartbeat"""
        pass

    def get_callbacks(self):
        callbacks = []
        if self.llm.callbacks is not None:
            for callback in self.llm.callbacks.handlers:
                if isinstance(callback, OutputBufferStreamingHandler):
                    callbacks.append(callback)
                    break
        return callbacks

    def preprocess_inputs(self, inputs: Dict[str, Any]):
        """Preprocesses inputs to the agent"""
        session_id = inputs.get("session_id", None)
        if session_id is None:
            session_id = str(uuid.uuid4())
            inputs["session_id"] = session_id
            self.is_new_session = True
        if self.long_term_memory is None:
            self.build_memory(session_id=session_id)

        inputs["memory_edit_timestamp"] = self.long_term_memory.memory_edit_timestamp
        inputs["recall_memory_count"] = self.long_term_memory.recall_memory_count
        inputs["archival_memory_count"] = self.long_term_memory.archival_memory_count
        if inputs["recall_memory_count"] > 0:
            self.is_new_session = False

        if "persona" not in inputs:
            inputs["persona"] = DEFAULT_PERSONA
        if "human" not in inputs:
            inputs["human"] = DEFAULT_HUMAN
        if "subagent_tasks" not in inputs:
            inputs["subagent_tasks"] = DEFAULT_AGENT_SUBTASKS

        return inputs

    def construct_prompt(self, langchain_messages: Dict[str, Any]):
        extra_messages = []
        if self.is_first:
            init_messages = convert_openai_messages(get_initial_boot_messages())
            login_message = convert_openai_messages(get_login_event())
            extra_messages = init_messages + login_message

        prompt = ChatPromptTemplate.from_messages(messages=[
            ("system", self.system_template + get_user_info()),
            *extra_messages,
            *langchain_messages
        ])
        return prompt


    async def arun_tool(self, function_call: Dict[str, Any], run_manager: Optional[CallbackManager] = None):
        function_name = function_call.get("name", "")

        available_functions = {
            "pause_heartbeats": self.pause_heartbeats,
            "send_message": self.send_message,
            "add_memory": self.add_memory,
            "modify_memory": self.modify_memory,
            "search_memory": self.search_memory,
        }

        # Failure case 1: function name is wrong
        try:
            function_to_call = available_functions[function_name]
        except KeyError:
            extra_info = {"status": 'Failed', "message": f'No function named {function_name}'}
            function_response = package_message(message_type=None, extra_info=extra_info)
            self.heartbeat_request = True
            message = FunctionMessage(name=function_name, content=function_response)
            return message

        # Failure case 2: function name is OK, but function args are bad JSON
        try:
            raw_function_args = function_call.get("arguments", "{}")
            function_args = parse_partial_json(raw_function_args)
        except Exception:
            extra_info = {"status": 'Failed', "message": f"Error parsing JSON for function '{function_name}' arguments: {raw_function_args}"}
            function_response = package_message(message_type=None, extra_info=extra_info)
            self.heartbeat_request = True
            message = FunctionMessage(name=function_name, content=function_response)
            return message

        # (Still parsing function args)
        # Handle requests for immediate heartbeat
        heartbeat_request = function_args.pop('request_heartbeat', False)
        if not (isinstance(heartbeat_request, bool) or heartbeat_request is None):
            print(f"> Warning: 'request_heartbeat' arg parsed was not a bool or None, type={type(heartbeat_request)}, value={heartbeat_request}", print_type="markdown")
            heartbeat_request = False
        self.heartbeat_request = heartbeat_request

        # Failure case 3: function failed during execution
        try:
            function_response_string = await function_to_call(**function_args)
            extra_info = {"status": 'OK', "message": function_response_string}
            function_response = package_message(message_type=None, extra_info=extra_info)
        except Exception as e:
            extra_info = {"status": 'Failed', "message": f"Error calling function {function_name} with args {function_args}: {str(e)}"}
            function_response = package_message(message_type=None, extra_info=extra_info)
            self.heartbeat_request = True
            message = FunctionMessage(name=function_name, content=function_response)
            return message

        # If no failures happened along the way: ...
        # Step 4: send the info on the function call and function response to GPT
        message = FunctionMessage(name=function_name, content=function_response)
        return message
    
    def check_token_limit(self, langchain_messages):
        """Check if the token limit is reached, if so, return the messages with a warning message"""
        token_cnt = num_tokens_from_messages(convert_message_to_dict(langchain_messages), model=config.model)
        if token_cnt > self.token_limit:
            warning_message = package_message(message_type="system_alert", extra_info={"message": MESSAGE_SUMMARY_WARNING_STR})
            langchain_messages.append(warning_message)

    async def arun_workflow(self, inputs: Dict[str, Any], run_manager: Optional[CallbackManager] = None) -> Dict[str, Any]:
        run_manager_callbacks = run_manager.get_child() if run_manager else None
        inputs = self.preprocess_inputs(inputs)
        # handle usre request
        user_request = inputs.get("user_request")
        user_message = package_message(message_type="user_message", extra_info={"message": user_request})
        self.long_term_memory.add_user_message(user_message)
        langchain_messages = self.long_term_memory.messages()

        # check token limit warning
        # convert_message_to_dict(langchain_messages)

        # llm_with_functions = self.llm.bind(functions=self.function_schemas)
        # current_try = 0
        # while current_try < self.total_tries:
        #     self.start_callbacks()
        #     prompt = self.construct_prompt(langchain_messages)
        #     llm_chain = (prompt | llm_with_functions | self.postprocess_mesasge).with_config({"run_name": f"Iteration {current_try+1}"})
        #     message = llm_chain.invoke(inputs, {"callbacks": run_manager_callbacks})
        #     langchain_messages.append(message)
        #     function_call = message.additional_kwargs.get("function_call", None)
        #     if function_call is None:
        #         self.end_callbacks(message)
        #         break

        #     tool_result = self.run_tool(function_call, run_manager_callbacks)
        #     if tool_result is None:
        #         self.end_callbacks(message)
        #         break
        #     langchain_messages.append(tool_result)
        #     langchain_messages = self.messages_hot_fix(langchain_messages)
        #     current_try += 1
        #     self.end_callbacks(message)
        # langchain_messages = remove_tips(langchain_messages)
        # openai_messages = list(map(convert_message_to_dict, langchain_messages))
        # return openai_messages


def create_memgpt_agent(llm, subagent=None):
    template = load_system_prompt(config.memGPT_prompt_path)
    with open(config.memGPT_schema_path) as f:
        function_schemas = json.load(f)
    chain = MemGPTAgent(
        llm=llm,
        subagent=subagent,
        system_template=template,
        function_schemas=function_schemas,
        verbose=False,
    )
    return chain
