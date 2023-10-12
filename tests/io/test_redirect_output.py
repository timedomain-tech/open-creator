import sys
import os
script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), "../.."))

from rich.console import Console
from creator.callbacks.file_io import LoggerFile


# Example usage:
logger_file = LoggerFile("output.log")
console = Console(file=logger_file)

# Now, when you print to the console, it will also be logged to a file without prefixes:
console.print("This will be logged to a file without prefixes", end="")
