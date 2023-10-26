from typing import List, Dict, Any, Optional
import datetime
import json

from langchain.schema.messages import SystemMessage, AIMessage, FunctionMessage
from langchain.output_parsers.json import parse_partial_json
from langchain.prompts import ChatPromptTemplate
from creator.code_interpreter import CodeInterpreter, language_map
from langchain.adapters.openai import convert_message_to_dict, convert_openai_messages
from creator.config.library import config
from creator.utils import load_system_prompt
from creator.llm import create_llm
from langchain.tools import StructuredTool
from creator.utils import get_user_info, get_local_time
from creator.callbacks.streaming_stdout import OutputBufferStreamingHandler

from creator.agents.base import BaseAgent


def package_function_response(was_success, response_string, timestamp=None):

    formatted_time = get_local_time() if timestamp is None else timestamp
    packaged_message = {
        "status": 'OK' if was_success else 'Failed',
        "message": response_string,
        "time": formatted_time,
    }
    return json.dumps(packaged_message)


def get_initial_boot_messages():
    return [
        # first message includes both inner monologue and function call to send_message
        {
            "role": "assistant",
            "content": "Bootup sequence complete. Persona activated. Testing messaging functionality.",
            "function_call": {
                "name": "send_message",
                "arguments": "{\n  \"message\": \"" + "More human than human is our motto." + "\"\n}"
            }
        },
        # obligatory function return message
        {
            "role": "function",
            "name": "send_message",
            "content": package_function_response(True, None)
        }
    ]


def get_login_event_message(last_login='Never (first login)', include_location=False, location_name='San Francisco, CA, USA'):
    # Package the message with time and location
    formatted_time = get_local_time()
    packaged_message = {
        "type": 'login',
        "last_login": last_login,
        "time": formatted_time,
    }
    if include_location:
        packaged_message["location"] = location_name
    return {"role": "user", "content": json.dumps(packaged_message)},


class MemGPTAgent(BaseAgent):
    total_tries: int = 10
    allow_user_confirm: bool = config.run_human_confirm
    subagent: Optional[BaseAgent] = None
    pause_heartbeats_start: Optional[datetime.datetime] = None

    @property
    def _chain_type(self):
        return "MemGPTAgent"

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

    def construct_prompt(self, langchain_messages: Dict[str, Any]):
        init_messages = convert_openai_messages(get_initial_boot_messages())
        login_message = convert_openai_messages(get_login_event_message())

        prompt = ChatPromptTemplate.from_messages(messages=[
            ("system", self.system_template + get_user_info()),
            *init_messages,
            *login_message,
            *langchain_messages
        ])
        return prompt

    def get_callbacks(self):
        callbacks = []
        if self.llm.callbacks is not None:
            for callback in self.llm.callbacks.handlers:
                if isinstance(callback, OutputBufferStreamingHandler):
                    callbacks.append(callback)
                    break
        return callbacks

    def preprocess_inputs(self, inputs: Dict[str, Any]):
        inputs["memory_edit_timestamp"] = 0
        inputs["recall_memory_count"] = 0
        inputs["archival_memory_count"] = 0
        inputs["persona"] = """
The following is a blank slate starter persona, I need to expand this to develop my own personality.

My name is MemGPT.
I am kind, thoughtful, and inquisitive.
"""
        inputs["human"] = """
This is what I know so far about the user, I should expand this as I learn more about them.

First name: Chad 
Last name: ?
Gender: Male
Age: ?
Nationality: ?
Occupation: Computer science PhD student at UC Berkeley
Interests: Formula 1, Sailing, Taste of the Himalayas Restaurant in Berkeley, CSGO 
"""
        inputs["subagent_tasks"] = """
- create/save/search skill
- run/test/refactor skill
- show skill
"""
        return inputs


def create_memGPT_agent(llm, subagent):
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
