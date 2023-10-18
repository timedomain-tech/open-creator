from textual.app import App, ComposeResult
from textual.widgets import Header, Static, TextArea
from typing import ClassVar
from textual.binding import BindingType, Binding

from prompt import MultilineInputWithLabel


class CompoundApp(App):
    TITLE = "Open-Creator REPL"

    CSS = """
    Screen {
        align: left bottom;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="message_display")
        yield MultilineInputWithLabel()

    def on_mount(self):
        self.query_one("#message_display").show_line_numbers = False

    async def action_submit(self):
        submit_text = self.query_one("#input_prompt_area").value
        self.query_one("#message_display").value = submit_text
        self.query_one("#input_prompt_area").clear()


if __name__ == "__main__":
    app = CompoundApp()
    app.run()
