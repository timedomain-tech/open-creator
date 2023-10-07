import json
from rich import print as rich_print
from rich.markdown import Markdown
from rich.json import JSON


def to_str(s):
    if isinstance(s, (dict, list)):
        return json.dumps(s, indent=4)
    return str(s)


class Printer:
    def __init__(self):
        self.callbacks = {}

    def add_callback(self, func):
        self.callbacks[func.__name__] = func

    def remove_callback(self, func_name):
        self.callbacks.pop(func_name, None)

    def print(self, *messages, sep=' ', end='\n', file=None, flush=False, print_type='str'):

        formatted_message = sep.join(map(to_str, messages))
        
        if print_type == 'markdown':
            formatted_message = Markdown(formatted_message)
        elif print_type == 'json':
            formatted_message = JSON(formatted_message)

        for callback in self.callbacks.values():
            callback(formatted_message, end=end, file=file, flush=flush)

    def add_default_callback(self):
        def default_print(message, end='\n', file=None, flush=False):
            rich_print(message, file=file, end=end, flush=flush)

        self.add_callback(default_print)


# Save the original print function
original_print = print

# Example usage:
printer = Printer()
printer.add_default_callback()  


# Replace the built-in print
def print(*args, sep=' ', end='\n', file=None, flush=False, print_type='str', **kwargs):
    printer.print(*args, sep=sep, end=end, file=file, flush=flush, print_type=print_type, **kwargs)

