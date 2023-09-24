from rich.console import Console
from rich.live import Live
from rich.text import Text
import time

console = Console()
loading_chars = ['◒', '◐', '◓', '◑']


def loading(second=10):
    with Live(console=console, auto_refresh=True) as live:
        for _ in range(second):  # Run for a few cycles; adjust as needed
            for char in loading_chars:
                live.update(Text(char))
                time.sleep(0.25)
