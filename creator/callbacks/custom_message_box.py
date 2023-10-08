from langchain.output_parsers.json import parse_partial_json

from loguru import logger


class CustomMessageBox:
    """
    Represents a MessageBox for displaying code blocks and outputs in different languages.
    
    Attributes:
        language (str): Language of the code.
        content (str): Content of the message box.
        code (str): Code content.
        output (str): Output after code execution.
        active_line (int): Line which is active or being executed.
        arguments (str): Arguments passed to the function.
        name (str): Name of the function.
        live (Live): Instance for refreshing the display.
    """

    def __init__(self):
        self.language = ""
        self.content = ""
        self.code = ""
        self.output = ""
        self.active_line = None
        self.arguments = ""
        self.name = ""
        self.callbacks = {}
    
    def start(self):
        pass

    def add_callback(self, func):
        self.callbacks[func.__name__] = func

    def remove_callback(self, func_name):
        if func_name in self.callbacks:
            del self.callbacks[func_name]

    def end(self) -> None:
        """Ends the live display."""
        if self.content:
            self.refresh(cursor=False, is_code=False)
        if self.code and self.language:
            self.refresh(cursor=False, is_code=True)
        self.arguments=""
        self.content=""
        self.code=""
        self.name=""

    def refresh_text(self, cursor: bool = True) -> None:
        """Refreshes the content display."""
        text = self.content
        lines = text.split('\n')
        inside_code_block = False
        for line in lines:
            # find the start of the code block
            if line.startswith("```"):
                inside_code_block = not inside_code_block

        content = '\n'.join(lines)
        if cursor:
            content += "█"
        if inside_code_block:
            content += "\n```"
        logger.debug(f"refresh_text: {len(self.callbacks)} {content}")
        
        for callback in self.callbacks.values():
            callback(content)

    def refresh_code(self, cursor: bool = True) -> None:
        """Refreshes the code display."""
        if cursor:
            self.code += "█"
        else:
            if self.code[-1] == "█":
                self.code = self.code[:-1]

        for callback in self.callbacks.values():
            callback(f"""```{self.code}```""")

    def refresh(self, cursor: bool = True, is_code: bool = True) -> None:
        """General refresh method."""
        if is_code:
            self.refresh_code(cursor=cursor)
        else:
            self.refresh_text(cursor=cursor)

    def update_from_chunk(self, chunk) -> None:
        """Updates message box from a given chunk."""
        content = "" if chunk.content is None else chunk.content
        function_call = chunk.additional_kwargs.get('function_call', {})
        name = function_call.get("name", "")
        arguments = function_call.get("arguments", "")

        if not name and not arguments and not content:
            return

        self.name = self.name + name
        self.arguments = self.arguments + arguments
        self.content = self.content + content
        if content:
            self.refresh(cursor=True, is_code=False)
        elif arguments:
            self.content = self.arguments
            self.refresh(cursor=True, is_code=False)
        if len(self.name) > 0:
            if self.name == "run_code":
                arguments_dict = parse_partial_json(self.arguments)
                if arguments_dict is None:
                    return
                language = arguments_dict.get("language", "python")
                code = arguments_dict.get("code", "")
                if language:
                    self.language = language
                    self.code = code
            else:
                self.language = "json"
                self.code = self.arguments
            self.refresh(cursor=True, is_code=True)


custom_message_box = None

callbacks = {}

def add_callback(func):
    global custom_message_box
    global callbacks
    callbacks[func.__name__] = func
    if custom_message_box is not None:
        custom_message_box.add_callback(func)

def update_callback(func):
    global custom_message_box
    global callbacks
    callbacks= {}
    callbacks[func.__name__] = func
    custom_message_box.callbacks = callbacks

def remove_callback(func_name):
    global custom_message_box
    global callbacks
    if func_name in callbacks:
        del callbacks[func_name]
    custom_message_box.callbacks = callbacks

def init_custom_message_box():
    global custom_message_box
    custom_message_box = CustomMessageBox()
    custom_message_box.callbacks = callbacks
    return custom_message_box

def set_custom_message_box(message_box, callbacks):
    global custom_message_box
    custom_message_box = message_box
    

def get_custom_message_box():
    global custom_message_box
    return custom_message_box
