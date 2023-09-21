from pydantic.v1 import root_validator
from contextlib import redirect_stdout
from typing import Dict, Optional, Field
import sys
import ast
import io
import re
import traceback


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
    """A tool for running python code in a REPL."""

    name: str = "python_interpreter"
    description: str = (
        "A Python shell. Use this to execute python commands. "
        "Input should be a valid python command. "
        "When using this tool, sometimes output is abbreviated - "
        "make sure it does not look abbreviated before using it in your answer."
    )
    globals: Optional[Dict] = Field(default_factory=dict)
    locals: Optional[Dict] = Field(default_factory=dict)

    @root_validator(pre=True)
    def validate_python_version(cls, values: Dict) -> Dict:
        """Validate valid python version."""
        if sys.version_info < (3, 9):
            raise ValueError(
                "This tool relies on Python 3.9 or higher "
                "(as it uses new functionality in the `ast` module, "
                f"you have Python version: {sys.version}"
            )
        return values

    def run(self, query: str) -> dict:
        try:
            query = sanitize_input(query)
            tree = ast.parse(query)
            module = ast.Module(tree.body[:-1], type_ignores=[])
            exec(ast.unparse(module), self.globals, self.locals)
            
            module_end = ast.Module(tree.body[-1:], type_ignores=[])
            module_end_str = ast.unparse(module_end)
            io_buffer = io.StringIO()
            try:
                with redirect_stdout(io_buffer):
                    ret = eval(module_end_str, self.globals, self.locals)
                    stdout = io_buffer.getvalue() if ret is None else ret
                    return {"status": "success", "stdout": stdout, "stderr": ""}
            except Exception:
                stderr = traceback.format_exc()
                with redirect_stdout(io_buffer):
                    exec(module_end_str, self.globals, self.locals)
                    return {"status": "success", "stdout": io_buffer.getvalue(), "stderr": stderr}
        except Exception:
            return {"status": "error", "stdout": "", "stderr": traceback.format_exc()}
