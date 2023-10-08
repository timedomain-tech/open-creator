from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown
from rich.box import MINIMAL

from creator.callbacks.base_message_box import BaseMessageBox

from langchain.output_parsers.json import parse_partial_json


class RichMessageBox(BaseMessageBox):
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
        self.code_live = Live(auto_refresh=False, console=Console(), vertical_overflow="visible")
        self.text_live = Live(auto_refresh=False, console=Console())
        
    def start(self):
        self.text_live.start()
        self.code_live.start()

    def end(self) -> None:
        """Ends the live display."""
        if self.content:
            self.refresh(cursor=False, is_code=False)
        if self.code and self.language:
            self.refresh(cursor=False, is_code=True)
        self.text_live.stop()
        self.code_live.stop()

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
        markdown = Markdown(content.strip())
        panel = Panel(markdown, box=MINIMAL)
        self.text_live.update(panel)
        self.text_live.refresh()

    def refresh_code(self, cursor: bool = True) -> None:
        """Refreshes the code display."""
        code_table = self._create_code_table(cursor)
        output_panel = self._create_output_panel()

        group = Group(code_table, output_panel)
        self.code_live.update(group)
        self.code_live.refresh()

    def refresh(self, cursor: bool = True, is_code: bool = True) -> None:
        """General refresh method."""
        if is_code:
            self.refresh_code(cursor=cursor)
        else:
            self.refresh_text(cursor=cursor)

    def update_from_chunk(self, chunk) -> None:
        # print(chunk)
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

    def _create_code_table(self, cursor: bool) -> Panel:
        """Creates a table to display the code."""
        code_table = Table(show_header=False, show_footer=False, box=None, padding=0, expand=True)
        code_table.add_column()

        if cursor:
            self.code += "█"
        else:
            if self.code[-1] == "█":
                self.code = self.code[:-1]

        code_lines = self.code.strip().split('\n')
        for i, line in enumerate(code_lines, start=1):
            syntax = self._get_line_syntax(line, i)
            if i == self.active_line:
                code_table.add_row(syntax, style="black on white")
            else:
                code_table.add_row(syntax)

        return Panel(code_table, box=MINIMAL, style="on #272722")

    def _get_line_syntax(self, line: str, line_number: int) -> Syntax:
        """Fetches the syntax for a given line of code."""
        theme = "monokai"
        if line_number == self.active_line:
            theme = "bw"
        return Syntax(line, self.language, theme=theme, line_numbers=False, word_wrap=True)

    def _create_output_panel(self) -> Panel:
        """Creates a panel for displaying the output."""
        if not self.output or self.output == "None":
            return Panel("", box=MINIMAL, style="#FFFFFF on #3b3b37")
        return Panel(self.output, box=MINIMAL, style="#FFFFFF on #3b3b37")
