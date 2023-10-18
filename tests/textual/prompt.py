from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input, Label, TextArea
from constants import PROMPT_PREFIX, SUGGESTOR_TREE
from completer import SuggestFromDict
from textual.message import Message
from textual.reactive import reactive
from textual.validation import ValidationResult
from textual.binding import BindingType, Binding
from textual.scroll_view import ScrollView
from dataclasses import dataclass
from typing import ClassVar, Iterable
from textual import events


class MultilineInput(TextArea):
    """A multiline input."""
    CUSTOMER_BINDINGS = [
        Binding("ctrl+j", "add_new_line", "add new line"),
        Binding("enter", "submit", "submit text")
    ]

    DEFAULT_CSS = """
    MultilineInput {
        height: auto;
        max-height: 4;
    }
    """

    def __init__(self, **kwargs) -> None:
        self.BINDINGS = self.BINDINGS + self.CUSTOMER_BINDINGS
        super().__init__(**kwargs)

    def on_mount(self):
        self.show_line_numbers = False

    async def on_key(self, event: events.Key) -> None:
        """Handle key presses which correspond to document inserts."""
        key = event.key
        if key == "enter":
            event.key = ""
            self.clear()
            return

        insert_values = {
            "tab": " " * self._find_columns_to_next_tab_stop(),
            "ctrl+j": "\n",
        }

        self._restart_blink()
        if event.is_printable or key in insert_values:
            event.stop()
            event.prevent_default()
            insert = insert_values.get(key, event.character)
            # `insert` is not None because event.character cannot be
            # None because we've checked that it's printable.
            assert insert is not None
            start, end = self.selection
            self.replace(insert, start, end, maintain_selection_offset=False)

    def action_submit(self):
        self.clear()


class MultilineInputWithLabel(Widget):
    """A multiline input with a label."""
    DEFAULT_CSS = """
    MultilineInputWithLabel {
        layout: horizontal;
        height: auto;
        padding-left: 0;
        margin: 0;
    }
    #input_prompt_label {
        width: 10;
        padding-left: 0;
        padding-right: 1;
        text-align: right;
    }
    #input_prompt_area {
        width: 1fr;
        height: auto;
        max-height: 4;
        padding-left: 0;
        padding-right: 0;
        margin: 0;
        text-align: left;
        border: hidden;
    }
    """
    value = reactive("")

    def __init__(self, input_label: str = PROMPT_PREFIX) -> None:
        self.input_label = input_label
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.input_label, id="input_prompt_label")
        # suggester=SuggestFromDict(SUGGESTOR_TREE)
        yield MultilineInput(id="input_prompt_area")
