from rich.markdown import Markdown
from rich import print as rich_print

class Printer:
    def __init__(self):
        self.callbacks = {}

    def add_callback(self, func):
        """
        message may be a Markdown object, so we need to handle this cases, define your callback like this:

        from rich.markdown import Markdown
        def custom_print(message):
            if type(message) is Markdown:
                print(message.markup)
            else:
                print(message)
        """
        self.callbacks[func.__name__] = func

    def remove_callback(self, func_name):
        if func_name in self.callbacks:
            del self.callbacks[func_name]

    def print(self, message):
        for callback in self.callbacks.values():
            callback(message)


printer = Printer()

printer.add_callback(rich_print)

def print(message):
    printer.print(message)
