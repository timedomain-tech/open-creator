from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import HSplit, Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.markup import MarkdownLexer
from prompt_toolkit.history import FileHistory
from creator.utils.printer import print
from prompt_toolkit.formatted_text import FormattedText
import os
from prompt_toolkit.document import Document
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.shortcuts import print_formatted_text
import re


help_text = """
<prompt>Open-Creator</prompt> 0.1.2 - Build your costomized skill library
Type "%help" for more information. Pressing Ctrl-Q to exit
  ___                      ____                _             
 / _ \ _ __   ___ _ __    / ___|_ __ ___  __ _| |_ ___  _ __ 
| | | | '_ \ / _ \ '_ \  | |   | '__/ _ \/ _` | __/ _ \| '__|
| |_| | |_) |  __/ | | | | |___| | |  __/ (_| | || (_) | |   
 \___/| .__/ \___|_| |_|  \____|_|  \___|\__,_|\__\___/|_|   
      |_|                                                   
"""


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
    '.test()': None,
    ".run": None,
    ".auto_optimize()": None,
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

    'prompt': 'ansigreen',
    'stderr': 'red',
})


TAG_PATTERNS = [
    (re.compile(r'<stderr>(.*?)<\/stderr>'), 'class:stderr'),
    (re.compile(r'<prompt>(.*?)<\/prompt>'), 'class:prompt'),
]


def parse_line(line):
    tokens = [('class:text', line)]
    new_tokens = []
    for pattern, style in TAG_PATTERNS:
        for token_style, text in tokens:
            # Only apply regex on 'class:text' tokens to avoid overwriting styles
            if token_style == 'class:text':
                start = 0
                for match in pattern.finditer(text):
                    # Append text before match with current style
                    new_tokens.append((token_style, text[start:match.start()]))
                    # Append matched text with new style
                    new_tokens.append((style, match.group(1)))
                    start = match.end()
                # Append text after last match with current style
                new_tokens.append((token_style, text[start:]))
            else:
                new_tokens.append((token_style, text))
        tokens = new_tokens
        new_tokens = []
    return tokens

class CustomLexer(Lexer):
    def lex_document(self, document: Document):
        return lambda lineno: parse_line(document.lines[lineno])


# prompt_message = HTML("<ansigreen>creator</ansigreen> ◐ ")

prompt_message = FormattedText([
    ('class:prompt', 'creator'),
    ('', ' ◐ ')
])

prompt_prefix = "\n<prompt>creator</prompt> ◐ \n"


def main():
    # The layout.
    search_field = SearchToolbar()  # For reverse search.
    output_field = TextArea(text=help_text, height=Dimension(min=3, weight=1), focusable=True, lexer=CustomLexer(), scrollbar=True)
    input_field = TextArea(
        height=Dimension(min=1, weight=100),
        prompt=prompt_message,
        multiline=True,
        wrap_lines=False,
        focus_on_click=True,
        dont_extend_height=False,
        search_field=search_field,
        completer=completer,
        auto_suggest=AutoSuggestFromHistory(),
        history=FileHistory(prompt_cache_history_path),
        lexer=PygmentsLexer(MarkdownLexer),
    )

    container = HSplit(
        [
            output_field,
            input_field,
            search_field,
        ]
    )

    # Attach accept handler to the input field. We do this by assigning the
    # handler to the `TextArea` that we created earlier. it is also possible to
    # pass it to the constructor of `TextArea`.
    # NOTE: It's better to assign an `accept_handler`, rather then adding a
    #       custom ENTER key binding. This will automatically reset the input
    #       field and add the strings to the history.
    def accept(buff, keyboard_interrupt=False):

        if keyboard_interrupt:
            output = "<stderr>KeyboardInterrupt</stderr>"
        else:
            try:
                output = "In:  {}\nOut: {}".format(
                    input_field.text, eval(input_field.text)
                )  # Don't do 'eval' in real code!
            except BaseException as e:
                output = f"<stderr>{e}</stderr>"

        new_text = output_field.text + prompt_prefix + output
        output_field.buffer.document = Document(
            text=new_text, cursor_position=len(new_text)
        )

    input_field.accept_handler = accept

    # The key bindings.
    kb = KeyBindings()

    @kb.add(Keys.ControlD)
    @kb.add(Keys.ControlQ)
    def _(event):
        " Pressing Ctrl-Q will exit the user interface. "
        event.app.exit()
        for line in output_field.text.split("\n"):
            tokens = parse_line(line)
            print_formatted_text(FormattedText(tokens), style=style)

    # emacs control + j new line keybindings
    @kb.add(Keys.ControlJ)
    def _(event):
        event.current_buffer.insert_text('\n')
    
    @kb.add(Keys.ControlC)
    def _(event):
        buffer = event.app.current_buffer
        # print("[red]KeyboardInterrupt[/red]")
        input_field.accept_handler(buffer, keyboard_interrupt=True)
        event.app.current_buffer.reset()
    
    @kb.add(Keys.Enter)
    def _(event):
        " When enter is pressed, we insert a newline. "
        buffer = event.app.current_buffer
        input_field.accept_handler(buffer)
        event.app.current_buffer.reset()

    # Run application.
    application = Application(
        layout=Layout(container, focused_element=input_field),
        key_bindings=kb,
        style=style,
        mouse_support=True,
        full_screen=True,
        
    )
    application.run()


if __name__ == "__main__":
    main()