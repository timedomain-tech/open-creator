from typing import Union, Dict, Any
import math
import json

from langchain.adapters.openai import convert_dict_to_message
from langchain.tools import StructuredTool

from .time_utils import get_local_time


class Tool(StructuredTool):

    def _parse_input(
        self,
        tool_input: Union[str, Dict],
    ) -> Union[str, Dict[str, Any]]:
        """Return the original tool_input"""
        return tool_input


async def send_message(memgpt, message: str, receiver: str = "human"):
    """Sends a message to a specified receiver"""
    if receiver == "human":
        return
    else:
        # request subagent first
        messages = memgpt.subagent.run({"messages": [{"role": "user", "content": message}]})
        for m in messages:
            langchain_message = convert_dict_to_message(m)
            langchain_message.additional_kwargs["subagent"] = memgpt.subagent._chain_type
            memgpt.memory_manager.add_message(message)
        last_m = messages[-1]
        return last_m.content


async def pause_heartbeats(memgpt, minutes: int, max_pause: int = 360):
    """Pauses heartbeats for a specified number of minutes"""
    minutes = min(max_pause, minutes)
    memgpt.pause_heartbeats_start = get_local_time()
    memgpt.pause_heartbeats_minutes = int(minutes)
    return f'Pausing timed heartbeats for {minutes} min'


async def add_memory(memgpt, name: str, content: str):
    """Adds a memory with a specified name and content, and optionally requests a heartbeat"""
    if name == "archival":
        memory_type = "archival"
    else:
        memory_type = "core"
    await memgpt.memory_manager.add(memory_type, content, name)


async def modify_memory(memgpt, name: str, old_content:str, new_content: str):
    """Modifies a memory with a specified name, replacing old content with new content, and optionally requests a heartbeat"""
    # only core memory can be modified
    memory_type = "core"
    await memgpt.memory_manager.modify(memory_type, old_content, new_content, name)


async def search_memory(memgpt, memory_type: str, page: int = 0, query: str = "", start_date: str = "", end_date: str = ""):
    """Searches memory of a specified type, with optional query, start date, end date, and request for heartbeat"""
    memory_type = "recall" if memory_type == "conversation" else memory_type
    results, total = await memgpt.memory_manager.search(memory_type, query, page, start_date, end_date)
    results_str = ""
    if len(results) == 0:
        results_str = "No results found"
    else:
        num_pages = math.ceil(total / memgpt.memory_manager.page_size) - 1  # 0 index
        results_pref = f"Showing {len(results)} of {total} results (page {page}/{num_pages}):"
        results_formatted = [f"timestamp: {d['timestamp']}, memory: {d['content']}" for d in results]
        results_str = f"{results_pref} {json.dumps(results_formatted)}"
    return results_str


tools = [Tool.from_function(coroutine=func) for func in [send_message, pause_heartbeats, add_memory, modify_memory, search_memory]]
available_functions = {tool.name:tool for tool in tools}
