import json

from langchain.schema.messages import SystemMessage
from langchain.output_parsers.json import parse_partial_json

from creator.code_interpreter import CodeInterpreter, language_map
from creator.config.library import config
from creator.utils import load_system_prompt
from creator.llm.llm_creator import create_llm
from langchain.tools import StructuredTool

from .base import BaseAgent


def send_message(message: str, receiver: str):
    pass


def pause_heartbeats(minutes: int):
    pass


def add_memory(name: str, content: str, request_heartbeat: bool):
    pass


def modify_memory(name: str, old_content:str, new_content: str, request_heartbeat: bool):
    pass


def search_memory(memory_type: str, page: int, request_heartbeat: bool, query: str = "", start_date: str = "", end_date: str = ""):
    pass


class MemGPTAgent(BaseAgent):
    total_tries: int = 10
    allow_user_confirm: bool = config.run_human_confirm

    @property
    def _chain_type(self):
        return "MemGPTAgent"


def create_memGPT_agent(llm):
    template = load_system_prompt(config.memGPT_prompt_path)
    with open(config.codeskill_function_schema_path, "r") as f:
        function_schemas = json.load(f)
    functions = [send_message, pause_heartbeats, add_memory, modify_memory, search_memory]
    tools = [StructuredTool.from_function(function) for function in functions]
    chain = MemGPTAgent(
        llm=llm,
        system_template=template,
        function_schemas=function_schemas,
        tools=tools,
        verbose=False,
    )
    return chain


llm = create_llm(config)
code_interpreter_agent = create_memGPT_agent(llm=llm)
