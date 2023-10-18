from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import Label
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit.widgets import TextArea
from prompt_toolkit import print_formatted_text, ANSI
from prompt_toolkit.widgets import Box, Frame
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.output import create_output
from prompt_toolkit.layout.controls import UIControl
import io
import re
from ansi2html import Ansi2HTMLConverter


# 定义 Markdown 文本
markdown_text = """# This is a title

This is some text.

- This is a list item
- Another item

[This is a link](http://example.com)
<span></span>
"""


# 使用 Rich 渲染 Markdown 到 HTML
console = Console(file=io.StringIO(), force_terminal=True)
md = Markdown(markdown_text)
console.print(md)
rich_text = console.file.getvalue()
console.file.close()

conv = Ansi2HTMLConverter()
html = conv.convert(rich_text, full=True)

print(html)


def add_span_tags_complex(x):
    # Find all contents within <span> tags (with or without class attributes) using regular expressions.
    span_contents_with_tags = re.findall(r'(<span.*?>.*?<\/span>)', x, re.DOTALL)
    span_contents = [content for tag in span_contents_with_tags for content in re.findall(r'<span.*?>(.*?)<\/span>', tag, re.DOTALL)]
    
    # Split the original string using the found contents, which will give us all strings not within <span> tags.
    non_span_parts = re.split(r'<span.*?>.*?<\/span>', x, re.DOTALL)
    
    # Add <span> tags around all strings that were not within <span> tags.
    non_span_parts = [f'\n<span>{part}</span>\n' if part.strip() else part for part in non_span_parts]
    
    # Recombine all the string parts.
    result_parts = []
    for non_span, span_content_with_tag in zip(non_span_parts, span_contents_with_tags + ['']):
        result_parts.append(non_span)
        if span_content_with_tag:
            result_parts.append(span_content_with_tag)
    
    return ''.join(result_parts)

# 使用正则表达式和替换函数修复输入文本
# fixed_text = add_span_tags_complex(html)

# print("\n----------\n")
# 输出修复后的文本
# print(fixed_text)
# print("\n-----------\n")
# print(fixed_text.split("\n")[11])
# fixed_text = "<span></span>"
# print_formatted_text(HTML(fixed_text.strip()))
