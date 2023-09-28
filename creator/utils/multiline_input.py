from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.styles import Style
from pygments.lexers.markup import MarkdownLexer
from rich.markdown import Markdown
from creator.utils.printer import print
import time
import os


class MultilineInput:
    prompt_cache_history_path = os.environ.get("PROMPT_CACHE_HISTORY_PATH", os.path.expanduser("~") + "/.cache/open_creator/prompt_cache/history.txt")
    completer = NestedCompleter.from_nested_dict({
        'create': {
            '--save': None,
            '-s': None,
        },
        'save': {
            '--skill_path': None,
            '--huggingface': None,
            '-sp': None,
            '-hf': None,
        },
        'search': {
            '--query': None,
            '-q': None,
            '--top_k': None,
            '-k': None,
        },
        '%exit': None,
        '%clear': None,
        '%reset': None,
        '%undo': None,
        '%help': None,
    })
    style = Style.from_dict(style_dict={
        # Default completion (not selected)
        'completion-menu.completion': 'bg:#ffffff #000000',  # White background with black text for unselected completions
        'completion-menu.completion.current': 'bg:#0000ff #ffffff',  # Blue background with white text for selected completion

        # Matched text
        'completion-menu.completion.current.match': 'fg:#00ffff',  # Light blue text for matched characters in selected completion
        'completion-menu.completion.match': 'fg:#0000ff',  # Blue text for matched characters in unselected completions

        # Non-matched text
        'completion-menu.completion.current.non-match': 'fg:#ffffff',  # White text for non-matched characters in selected completion
        'completion-menu.completion.non-match': 'fg:#000000',  # Black text for non-matched characters in unselected completions

        # Scrollbar
        'scrollbar.background': 'bg:#d0d0d0',  # Light gray background for scrollbar
        'scrollbar.button': 'bg:#222222',  # Dark color for scrollbar button
    })

    def __init__(self):
        self.kb = KeyBindings()

        # emacs control + j new line keybindings
        @self.kb.add(Keys.ControlJ)
        def _(event):
            event.current_buffer.insert_text('\n')

        # Create an instance of PromptSession
        self.session = PromptSession(
            key_bindings=self.kb,
            history=FileHistory(self.prompt_cache_history_path),
            lexer=PygmentsLexer(MarkdownLexer),
            style=self.style,
        )

    # Define a function to get multiline input
    def get_multiline_input(self, prompt_message=HTML("<ansigreen>creator</ansigreen> ◐ ")):
        while 1:
            try:
                input_text = self.session.prompt(
                    message=prompt_message,
                    mouse_support=True,
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=self.completer,
                    complete_in_thread=True,
                )
                print(Markdown(input_text))
                return input_text
            except KeyboardInterrupt:
                print("KeyboardInterrupt")
                time.sleep(0.2)
                continue
            except EOFError:
                exit()


mi = MultilineInput()


multiline_prompt = mi.get_multiline_input
