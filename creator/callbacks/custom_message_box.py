from langchain.output_parsers.json import parse_partial_json

from loguru import logger
from creator.callbacks.base_message_box import BaseMessageBox


class CustomMessageBox(BaseMessageBox):

    def __init__(self):
        super().__init__()  
        self.start_callbacks = {}
        self.update_callbacks = {}
        self.update_code_callbacks = {}
        self.end_callbacks = {}

    def add_callback(self, type, func):
        if type == "start":
            self.start_callbacks[func.__name__] = func
        elif type == "update":
            self.update_callbacks[func.__name__] = func
        elif type == "update_code":
            self.update_code_callbacks[func.__name__] = func
        elif type == "end":
            self.end_callbacks[func.__name__] = func

    def remove_callback(self, type, func_name):
        if type == "start":
            if func_name in self.start_callbacks:
                del self.start_callbacks[func_name]
        elif type == "update":
            if func_name in self.update_callbacks:
                del self.update_callbacks[func_name]
        elif type == "update_code":
            if func_name in self.update_code_callbacks:
                del self.update_code_callbacks[func_name]
        elif type == "end":
            if func_name in self.end_callbacks:
                del self.end_callbacks[func_name]
        
    def start(self):
        super().start()
        for callback in self.start_callbacks.values():
            callback()

    def end(self) -> None:
        super().end()
        if self.content:
            self.refresh(cursor=False, is_code=False)
        if self.code and self.language:
            self.refresh(cursor=False, is_code=True)
        self.arguments=""
        self.content=""
        self.code=""
        self.name=""
        for callback in self.end_callbacks.values():
            callback()

    def refresh_text(self, cursor: bool = True) -> None:
        text = self.content
        lines = text.split('\n')
        inside_code_block = False
        for line in lines:
            # find the start of the code block
            if line.startswith("```"):
                inside_code_block = not inside_code_block

        content = '\n'.join(lines)
        # if cursor:
        #     content += "█"
        # if inside_code_block:
        #     content += "\n```"
        for callback in self.update_callbacks.values():
            # print(f"update_callbacks {callback.__name__} {content}")
            callback(content)

    def refresh_code(self, cursor: bool = True) -> None:
        """Refreshes the code display."""
        # if cursor:
        #     self.code += "█"
        # else:
        #     if self.code[-1] == "█":
        #         self.code = self.code[:-1]

        for callback in self.update_code_callbacks.values():
            # print(f"update_callbacks {callback.__name__} {self.code}")
            callback(f"""```{self.code}```""")

    def refresh(self, cursor: bool = True, is_code: bool = True) -> None:
        """General refresh method."""
        if is_code:
            self.refresh_code(cursor=cursor)
        else:
            self.refresh_text(cursor=cursor)

    def update_from_chunk(self, chunk) -> None:
        super().update_from_chunk(chunk)

custom_message_box = None

def add_callback(type, func):
    global custom_message_box
    if custom_message_box is None:
        init_custom_message_box()
    custom_message_box.add_callback(type, func)

def remove_callback(type, func_name):
    global custom_message_box
    if custom_message_box is not None:
        custom_message_box.remove_callback(type, func_name)

def init_custom_message_box():
    global custom_message_box
    custom_message_box = CustomMessageBox()

def get_custom_message_box():
    global custom_message_box
    if custom_message_box is None:
        init_custom_message_box()
    return custom_message_box