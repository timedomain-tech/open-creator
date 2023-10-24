from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.document import Document
from pygments.lexers.markup import MarkdownLexer
from prompt_toolkit.lexers import PygmentsLexer
import traceback

from .constants import help_text, prompt_message, interpreter_message
from .completer import completer, file_history
from .style import style
from .handler import RequestHandler
from questionary import Question
import sys


class OpenCreatorREPL:
    interpreter = False

    def setup(self):
        self.handler = RequestHandler()
        # The key bindings.
        kb = KeyBindings()

        # emacs control + j new line keybindings
        @kb.add(Keys.ControlJ)
        def _(event):
            event.current_buffer.insert_text('\n')

        self.prompt_session = PromptSession(
            prompt_message if not self.interpreter else interpreter_message,
            style=style,
            multiline=False,
            lexer=PygmentsLexer(MarkdownLexer),
            history=file_history,
            completer=completer,
            auto_suggest=AutoSuggestFromHistory(),
            complete_while_typing=True,
            mouse_support=True,
            key_bindings=kb
        )

    async def ask(self, interpreter=False):
        if self.interpreter != interpreter:
            self.interpreter = interpreter
            self.setup()
        self.prompt_session.default_buffer.reset(Document())
        question = Question(self.prompt_session.app)
        output = await question.unsafe_ask_async(patch_stdout=True)
        return output

    async def run(self, quiet=False, interpreter=False):
        self.setup()
        if not quiet:
            await self.handler.show_output("", help_text, add_prompt_prefix=False)

        while 1:
            try:
                user_request = await self.ask(interpreter)
                user_request = user_request.strip()
                await self.handler.show_output(user_request, "", add_newline=user_request != "", interpreter=interpreter)
                if user_request == "%exit":
                    sys.exit()
                if user_request.startswith("%interpreter"):
                    interpreter = not interpreter
                    mode = "on" if interpreter else "off"
                    await self.handler.show_output("", f"[red]Toggled Interpreter mode {mode}![/red]", add_prompt_prefix=False, add_newline=False, add_request=False)
                    continue
                if user_request:
                    await self.handler.handle(user_request, interpreter=interpreter)
            except KeyboardInterrupt:
                user_request = self.prompt_session.default_buffer.text
                await self.handler.show_output(user_request, "", grey=True, interpreter=interpreter)
                await self.handler.show_output("", "[red]KeyboardInterrupt[/red]", add_prompt_prefix=False, add_newline=False, add_request=False)
            except EOFError:
                sys.exit()
            except Exception:
                err = traceback.format_exc()
                user_request = self.prompt_session.default_buffer.text
                await self.handler.show_output(user_request, "", grey=True, interpreter=interpreter)
                await self.handler.show_output("", f"[red]{err}[/red]", add_prompt_prefix=False, add_newline=False, add_request=False)
