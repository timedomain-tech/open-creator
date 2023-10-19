from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import HSplit, Layout
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.markup import MarkdownLexer
from prompt_toolkit.filters import to_filter

import traceback

from .constants import prompt_message, help_text
from .completer import completer, file_history
from .style import style
from .lexer import CustomLexer


class OpenCreatorREPL:

    def __init__(self, accept_callback=None):
        self.accept_callback = accept_callback

    def run(self, quiet=False):
        output_text = "" if quiet else help_text
        self.output_field = TextArea(text=output_text, height=Dimension(min=0, weight=1), focusable=True, read_only=True, focus_on_click=True, lexer=CustomLexer(), scrollbar=True)
        self.input_field = TextArea(
            height=Dimension(min=1, weight=100),
            prompt=prompt_message,
            multiline=True,
            wrap_lines=False,
            focus_on_click=True,
            dont_extend_height=False,
            completer=completer,
            auto_suggest=AutoSuggestFromHistory(),
            history=file_history,
            lexer=PygmentsLexer(MarkdownLexer),
            complete_while_typing=True,
        )
        self.input_field.buffer.enable_history_search = to_filter(True)
        self.input_field.accept_handler = self.accept

        # The key bindings.
        kb = KeyBindings()

        @kb.add(Keys.ControlD)
        @kb.add(Keys.ControlQ)
        def _(event):
            " Pressing Ctrl-Q will exit the user interface. "
            self.accept_callback.handle_exit(event.app, self.output_field.text)

        # emacs control + j new line keybindings
        @kb.add(Keys.ControlJ)
        def _(event):
            event.current_buffer.insert_text('\n')

        @kb.add(Keys.ControlC)
        def _(event):
            buffer = event.app.current_buffer
            self.input_field.accept_handler(buffer, keyboard_interrupt=True)
            event.app.current_buffer.reset()

        @kb.add(Keys.Enter)
        def _(event):
            " When enter is pressed, we insert a newline. "
            buffer = event.app.current_buffer
            if self.input_field.text.startswith("%exit"):
                self.accept_callback.handle_exit(event.app, self.output_field.text)
                return

            self.input_field.accept_handler(buffer)
            event.app.current_buffer.reset()

        container = HSplit(
            [
                self.output_field,
                self.input_field,
            ]
        )
        # Run application.
        self.application = Application(
            layout=Layout(container, focused_element=self.input_field),
            key_bindings=kb,
            style=style,
            mouse_support=True,
            full_screen=True,
        )
        self.application.run()

    def accept(self, buff, keyboard_interrupt=False):

        self.output_field.buffer.read_only = to_filter(False)

        show_stderr = True
        if keyboard_interrupt:
            output = "<stderr>KeyboardInterrupt</stderr>"
        else:
            try:
                self.accept_callback.handle(self.input_field.text, self.output_field)
                show_stderr = False
            except Exception:
                output = f"<stderr>{traceback.format_exc()}</stderr>"
        if self.input_field.text.strip() != "":
            self.input_field.buffer.history.store_string(self.input_field.text)
        if show_stderr:
            self.accept_callback.show_output(self.input_field.text, self.output_field, output)
        self.output_field.buffer.read_only = to_filter(True)
