from langchain.output_parsers.json import parse_partial_json

class BaseMessageBox:
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

    def start(self):
        pass


    def end(self) -> None:
        pass

    def refresh_text(self, cursor: bool = True) -> None:
        pass

    def refresh_code(self, cursor: bool = True) -> None:
        pass

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
