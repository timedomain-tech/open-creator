from langchain.callbacks.streamlit.mutable_expander import MutableExpander
from langchain.callbacks.streamlit.streamlit_callback_handler import _convert_newlines
from langchain.output_parsers.json import parse_partial_json
from streamlit.delta_generator import DeltaGenerator
from .base import OutputManager


avatar_mapping = {
    "CreatorAgent": "🌟",
    "CodeInterpreterAgent": "💻",
    "SkillExtractorAgent": "🔧",
    "CodeRefactorAgent": "♻️",
    "CodeTesterAgent": "🐞",
}


class StreamlitOutputManager(OutputManager):
    def __init__(self, container: DeltaGenerator = None):
        self.container = container
        self.content_container = None
        self.history_messages = []
        self.last_chat_message = None
        self.last_expander = None
        self.last_expander_index = None
        self.language = ""
        self.content = ""
        self.code = ""
        self.arguments = ""
        self.name = ""
        self.tool_result = ""

    def add(self, agent_name: str):
        if self.container is not None:
            self.history_messages.append(self.container.chat_message("assistant"))

    def update(self, chunk):
        if self.container is None:
            return
        content = "" if chunk.content is None else chunk.content
        function_call = chunk.additional_kwargs.get('function_call', {})
        name = function_call.get("name", "")
        arguments = function_call.get("arguments", "")

        if not name and not arguments and not content:
            return

        self.name = self.name + name
        self.arguments = self.arguments + arguments
        self.content = self.content + content

        if content:
            if self.content_container is None:
                self.content_container = self.container.empty()
            self.content_container.markdown(_convert_newlines(self.content + "⚪"))

        in_function_call = len(name) > 0

        if len(self.name) > 0:
            if self.name in ("run_code", "python"):
                arguments_dict = parse_partial_json(self.arguments)
                if arguments_dict is None:
                    return
                language = arguments_dict.get("language", "python")
                code = arguments_dict.get("code", "")
                if language:
                    self.language = language
                    self.code = code
            else:
                self.language = "json"
                self.code = self.arguments
        markdown = _convert_newlines(f"""```{self.language}\n{self.code}⚪\n```""")
        if in_function_call and self.last_expander is None:
            self.last_expander = MutableExpander(self.last_chat_message, label=self.name, expanded=True)
            self.last_expander_index = self.last_expander.markdown(markdown, index=self.last_expander_index)
        elif self.last_expander is not None:
            markdown = _convert_newlines(f"""```{self.language}\n{self.code}⚪\n```""")
            self.last_expander_index = self.last_expander.markdown(markdown, index=self.last_expander_index)

    def update_tool_result(self, chunk):
        if self.container is None:
            return
        if chunk is not None and chunk.content is not None and self.last_expander is not None:
            markdown = _convert_newlines(f"""```{self.language}\n{self.code}\n```> STDOUT/STDERR\n```plaintext\n{chunk.content}\n""")
            self.last_expander_index = self.last_expander.markdown(markdown, index=self.last_expander_index)
            self.tool_result = chunk.content

    def finish(self, message=None, err=None):
        if self.container is None:
            return
        if message is not None:
            self.content = message.content
            function_call = message.additional_kwargs.get('function_call', {})
            self.name = function_call.get("name", "")
            arguments = function_call.get("arguments", "")
            if self.name in ("run_code", "python"):
                arguments_dict = parse_partial_json(arguments)
                language = arguments_dict.get("language", "python")
                code = arguments_dict.get("code", "")
                if language:
                    self.language = language
                    self.code = code
            else:
                self.language = "json"
                self.code = arguments
        if err is not None:
            self.content = str(err)
        if self.content:
            if self.content_container is None:
                self.content_container = self.container.empty()
            self.content_container.markdown(_convert_newlines(self.content))

        if self.code and self.language and self.last_expander is not None:
            markdown = _convert_newlines(f"""```{self.language}\n{self.code}\n```> STDOUT/STDERR\n```plaintext\n{self.tool_result}\n""")
            self.last_expander_index = self.last_expander.markdown(markdown, index=self.last_expander_index)

        self.history_messages.append(self.last_chat_message)

        self.last_expander = None
        self.last_expander_index = None
        self.language = ""
        self.content = ""
        self.code = ""
        self.arguments = ""
        self.name = ""
