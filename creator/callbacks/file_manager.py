import json

from langchain.adapters.openai import convert_message_to_dict

from .base import OutputManager
from .file_io import logger_file


class FileOutputManager(OutputManager):
    agent_names = []
    messages = []
    tool_results = []

    def add(self, agent_name: str):
        self.agent_names.append(agent_name)
        self.messages.append(None)

    def update(self, chunk):
        if len(self.messages) > 0:
            if self.messages[-1] is None:
                self.messages[-1] = chunk
            else:
                self.messages[-1] += chunk
        else:
            self.messages.append(chunk)

    def update_tool_result(self, chunk):
        self.tool_results.append(chunk)

    def finish(self, message=None, err=None):
        if len(self.agent_names) > 0:
            agent_name = self.agent_names.pop()
            run_message = self.messages.pop() if message is None else message
            if run_message is not None:
                run_message = convert_message_to_dict(run_message)
            tool_result = convert_message_to_dict(self.tool_results.pop()) if len(self.tool_results) > 0 else None
            print_obj = {"agent_name": agent_name, "message": run_message, "tool_result": tool_result}
            if err is not None:
                print_obj["error"] = err
            print_str = json.dumps(print_obj, ensure_ascii=False, sort_keys=True)
            logger_file.write(print_str)


file_output_manager = FileOutputManager()
