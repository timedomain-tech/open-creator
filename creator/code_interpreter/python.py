from .base import BaseInterpreter
import re


def clean_interactive_mode_lines(response):
    def clean_string(s):
        return '\n'.join([line for line in s.split('\n') if not re.match(r'^(\s*>>>\s*|\s*\.\.\.\s*)', line)])
    
    # clean up stdout and stderr
    response['stdout'] = clean_string(response.get('stdout', ''))
    response['stderr'] = clean_string(response.get('stderr', ''))
    
    return response


def sanitize_input(query: str) -> str:
    """Sanitize input to the python REPL.
    Remove whitespace, backtick & python (if llm mistakes python console as terminal)

    Args:
        query: The query to sanitize

    Returns:
        str: The sanitized query
    """

    # Removes `, whitespace & python from start
    query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
    # Removes whitespace & ` from end
    query = re.sub(r"(\s|`)*$", "", query)
    return query


class PythonInterpreter:
    def __init__(self):
        self.bash_interpreter = None

    def run(self, query:str) -> dict:
        if self.bash_interpreter is None:
            self.bash_interpreter = BaseInterpreter()
            resp = self.bash_interpreter.run("python -i -q -u")
            if resp["status"] != "success":
                return clean_interactive_mode_lines(resp)
        resp = self.bash_interpreter.run(query)
        return clean_interactive_mode_lines(resp)
