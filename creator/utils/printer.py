import json
import sys
from rich.markdown import Markdown
from rich.console import Console
from rich import print as rich_print
from rich.json import JSON
import io

# Save the original print function
original_print = print


def to_str(s):
    if isinstance(s, (dict, list)):
        return json.dumps(s, indent=4)
    return str(s)


class Printer:
    def __init__(self):
        self.callbacks = {}
        console = Console()
        self.is_terminal = console.is_terminal
        self.is_jupyter = console.is_jupyter
        self.is_interactive = Console().is_interactive
        self.use_rich = self.is_terminal or self.is_jupyter or self.is_interactive
        self.output_capture = io.StringIO()  # Moved inside the class as an instance variable

    def add_callback(self, func):
        self.callbacks[func.__name__] = func

    def remove_callback(self, func_name):
        self.callbacks.pop(func_name, None)

    def print(self, *messages, sep=' ', end='\n', file=None, flush=False, print_type='str', output_option='both'):
        formatted_message = sep.join(map(to_str, messages))

        if print_type == 'markdown' and self.use_rich:
            formatted_message = Markdown(formatted_message)
        elif print_type == 'json' and self.use_rich:
            formatted_message = JSON(formatted_message)

        for callback in self.callbacks.values():
            try:
                callback(formatted_message, end=end, file=file, flush=flush, output_option=output_option)
            except Exception as e:
                original_print(f"Error in callback {callback.__name__}: {str(e)}", file=sys.stderr)

    def add_default_callback(self):
        if self.use_rich:
            def default_print(message, end='\n', file=None, flush=False, output_option='terminal'):
                target_file = file or self.output_capture
                if output_option in ['terminal', 'both']:
                    console = Console(force_jupyter=self.is_jupyter, force_terminal=self.is_terminal, force_interactive=self.is_interactive, file=target_file)
                    console.print(message, end=end)
                # if output_option in ['stdout', 'both']:
                #     rich_print(message, end=end, file=sys.stdout, flush=flush)
        else:
            def default_print(message, end='\n', file=None, flush=False, output_option='both'):
                target_file = file or self.output_capture
                if output_option in ['stdout', 'both']:
                    original_print(message, end=end, file=target_file, flush=flush)
                if output_option in ['terminal', 'both'] and target_file is not sys.stdout:
                    original_print(message, end=end, file=sys.stdout, flush=flush)

        self.add_callback(default_print)


printer = Printer()
printer.add_default_callback()


# Replace the built-in print
def print(*args, sep=' ', end='\n', file=None, flush=False, print_type='str', output_option='both', **kwargs):
    printer.print(*args, sep=sep, end=end, file=file, flush=flush, print_type=print_type, output_option=output_option, **kwargs)
