from .applescript import AppleScriptInterpreter
from .base import BaseInterpreter
from .julia import JuliaInterpreter
from .python import PythonInterpreter
from .R import RInterpreter
from .html import HTMLInterpreter
from .javascript import JSInterpreter
from .shell import ShellInterpreter
from langchain.tools import StructuredTool, format_tool_to_openai_function
from typing import Type, Optional, Any
from pydantic import BaseModel, Field
from langchain.callbacks.manager import CallbackManagerForToolRun
from creator.utils import remove_title
import re


__all__ = [
    'AppleScriptInterpreter',
    'BaseInterpreter',
    'JuliaInterpreter',
    'PythonInterpreter',
    'RInterpreter',
    'HTMLInterpreter',
    'JavascriptInterpreter',
    'ShellInterpreter',
    "CodeInterpreter"
]


language_map = {
    'applescript': AppleScriptInterpreter,
    'bash': ShellInterpreter,
    'julia': JuliaInterpreter,
    'python': PythonInterpreter,
    'r': RInterpreter,
    'html': HTMLInterpreter,
    'javascript': JSInterpreter,
    'shell': ShellInterpreter,
}


class CodeInterpreterSchema(BaseModel):
    language: str = Field(description="The programming language", enum=list(language_map.keys()))
    code: str = Field(description="The code to execute")


class CodeInterpreter(StructuredTool):
    name: str = "run_code"
    description: str = "Executes code on the user's machine and returns the output"
    args_schema: Type[BaseModel] = CodeInterpreterSchema
    interpreters: dict[str, Any] = {}

    def add_interpreter(self, language:str):
        self.interpreters[language] = language_map[language]()

    # use re to remove ``` and ` from start and end of code
    def clean_code(self, code: str) -> str:
        code = re.sub(r'^(```|`)', '', code)
        code = re.sub(r'(```|`)$', '', code)
        return code

    def _run(
        self,
        language: str,
        code: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> dict[str, str]:
        if language not in language_map:
            return {"status": "error", "stdout": "", "stderr": f"Language {language} not supported"}
        if language not in self.interpreters:
            self.add_interpreter(language=language)
        return self.interpreters[language].run(code)

    def to_function_schema(self):
        function_schema = format_tool_to_openai_function(self)
        function_schema["parameters"] = remove_title(function_schema["parameters"])
        return function_schema

