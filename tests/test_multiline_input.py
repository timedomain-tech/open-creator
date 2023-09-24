from prompt_toolkit import Application, PromptSession, print_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import VSplit, Window, HSplit, DynamicContainer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Frame
from rich.markdown import Markdown
from rich.console import Console

console = Console()

def render_markdown():
    rendered = console.render(Markdown(buffer.text))
    return FormattedTextControl([("class:markdown", "".join(segment.text for segment in rendered))])

# 创建一个自定义的 Buffer。
buffer = Buffer()

# 设置键绑定，使得按下 Ctrl-C 或 Ctrl-D 时退出程序。
key_bindings = KeyBindings()

@key_bindings.add(Keys.ControlC)
@key_bindings.add(Keys.ControlD)
def exit_(event):
    event.app.exit()

app = Application(
    layout=Layout(
        HSplit(
            [
                Frame(Window(content=BufferControl(buffer=buffer)), title="Input"),
                Frame(DynamicContainer(lambda: Window(content=render_markdown())), title="Live Markdown Preview"),
            ]
        )
    ),
    full_screen=True,
    key_bindings=key_bindings
)

app.run()