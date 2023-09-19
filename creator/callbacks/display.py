from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown
from rich.box import MINIMAL
from creator.utils import stream_partial_json_to_dict
import re


class MessageBox:
    """
    Code Blocks display code and outputs in different languages.
    """

    def __init__(self):
        self.language = ""
        self.content = ""
        self.code = ""
        self.output = ""
        self.active_line = None
        self.arguments = ""
        self.name = ""

        self.live = Live(auto_refresh=False, console=Console(), vertical_overflow="visible")
        self.live.start()

    def end(self):
        if self.content:
            self.refresh(cursor=False, is_code=False)
        if self.code and self.language:
            self.refresh(cursor=False, is_code=True)
        self.live.stop()

    def refresh_text(self, cursor=True):
        text = self.content
        replacement = "```text"
        lines = text.split('\n')
        inside_code_block = False

        for i in range(len(lines)):
            # If the line matches ``` followed by optional language specifier
            if re.match(r'^```(\w*)$', lines[i].strip()):
                inside_code_block = not inside_code_block

            # If we just entered a code block, replace the marker
            if inside_code_block:
                lines[i] = replacement

        content = '\n'.join(lines)
        if cursor:
            content += "█"
        markdown = Markdown(content.strip())
        panel = Panel(markdown, box=MINIMAL)
        self.live.update(panel)
        self.live.refresh()

    def refresh_code(self, cursor=True):
        code_table = self._create_code_table(cursor)
        output_panel = self._create_output_panel()

        group = Group(code_table, output_panel)
        self.live.update(group)
        self.live.refresh()
    
    def refresh(self, cursor=True, is_code=True):
        if is_code:
            self.refresh_code(cursor=cursor)
        else:
            self.refresh_text(cursor=cursor)

    def update_from_chunk(self, chunk):
        content = chunk.content
        function_call = chunk.additional_kwargs.get('function_call', {})
        name = function_call.get("name", "")
        arguments = function_call.get("arguments", "")
        if not name and not arguments and not content:
            return
        self.name += name
        self.arguments += arguments
        self.content += content

        if content:
            self.refresh(cursor=True, is_code=False)
        
        if not name and arguments:
            if self.name == "extract_formmated_skill":
                self.language = "json"
                self.code = self.arguments
            elif not self.language and self.name == "run_code":
                arguments_dict = stream_partial_json_to_dict(self.arguments)
                language = arguments_dict.get("language", "")
                if language:
                    self.language = language
                    self.code = arguments_dict.get("code", "")

        if self.language:
            self.refresh(cursor=True, is_code=True)

    def _create_code_table(self, cursor):
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

    def _get_line_syntax(self, line, line_number):
        theme = "monokai"
        if line_number == self.active_line:
            theme = "bw"
        return Syntax(line, self.language, theme=theme, line_numbers=False, word_wrap=True)

    def _create_output_panel(self):
        if not self.output or self.output == "None":
            return ""
        return Panel(self.output, box=MINIMAL, style="#FFFFFF on #3b3b37")
