import re
from prompt_toolkit.document import Document
from prompt_toolkit.lexers import Lexer


TAG_PATTERNS = [
    (re.compile(r'<stderr>(.*?)<\/stderr>', re.DOTALL), 'class:stderr'),
    (re.compile(r'<prompt>(.*?)<\/prompt>', re.DOTALL), 'class:prompt'),
    (re.compile(r'<system>(.*?)<\/system>', re.DOTALL), 'class:system'),
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
