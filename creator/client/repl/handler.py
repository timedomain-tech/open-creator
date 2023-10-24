import json

from .constants import help_commands, prompt_prefix, interpreter_prefix

from creator.agents.creator_agent import open_creator_agent
from creator.agents import code_interpreter_agent
from creator.utils import truncate_output, is_valid_code
from rich.console import Console
from rich.markdown import Markdown

from langchain.output_parsers.json import parse_partial_json


class RequestHandler:
    """This is a class that will be used to handle the request from the REPL."""
    def __init__(self):
        self.messages = []
        self.message_states = [self.messages]
        self.history = []
        self.output = []
        self.interpreter = False
        self.console = Console()

    async def handle(self, request, interpreter):
        """
        Handle the user request input, and dispatch to the appropriate handler based on
        the request type: meta-prompt command, expression, or agent.

        Args:
            request (str): The user input string.
        Returns:
            str: The output text to be displayed in the output_field.
        """
        if request.startswith("%"):
            await self.meta_prompt_handler(request)
        elif is_valid_code(request, open_creator_agent.tools[0].namespace):
            await self.expression_handler(request)
            self.update_history(request)
        else:
            await self.agent_handler(request, interpreter)
            self.update_history(request)

    async def meta_prompt_handler(self, request):
        """
        Handle meta-prompt commands that start with '%'. These commands control the
        REPL environment and provide functionalities like clear, reset, undo, and help.

        Args:
            request (str): The user input string.
        Returns:
            None
        """
        output = ""

        if request.startswith("%reset"):
            self.messages = []
            output = "[blue]Conversation Message Reset![/blue]"
            await self.show_output(request=request, output=output, add_prompt_prefix=False, add_request=False, add_newline=False)

        if request.startswith("%clear"):
            self.history = []
            self.output = []
            output = ""
            await self.show_output(request=request, output=output, add_prompt_prefix=False, add_request=False, add_newline=False)

        if request.startswith("%undo"):
            if len(self.history) == 0 or len(self.message_states) == 0:
                output = "[red]Nothing to undo![/red]"
                self.output = []
                await self.show_output(request=request, output=output)
                return

            self.history.pop(-1)
            if len(self.history) > 0:
                _, self.output = self.history[-1]
            else:
                self.output = []

            self.message_states.pop(-1)
            if len(self.message_states) > 0:
                self.messages = self.message_states[-1]
            else:
                self.messages = []
            output = ""
            await self.show_output(request, output)

        if request.startswith("%help"):
            output = help_commands
            await self.show_output(request, output, add_prompt_prefix=False, add_request=False, add_newline=False)

    async def expression_handler(self, request):
        """
        Handle user input that is recognized as a Python expression. The expression will
        be executed, and the result (or any error message) will be displayed.

        Args:
            request (str): The user input string, identified as a Python expression.

        Returns:
            str: The result of the executed expression or error message to be displayed in the output_field.
        """

        tool_result = open_creator_agent.tools[0].run_with_return(request)
        truncate_tool_result = truncate_output(tool_result)
        outputs = [tool_result["stdout"], tool_result["stderr"]]
        output = "\n".join([o for o in outputs if o != ""])

        self.messages.append({"role":"user", "content": request})
        self.messages.append({"role":"function", "name": "user_executed_code_output","content": json.dumps(truncate_tool_result)})

        await self.show_output(request=request, output=output, add_prompt_prefix=False, add_newline=False, add_request=False)

    def update_history(self, input_text):
        """
        Update the history of user inputs and outputs, preserving the state to enable undo functionality.

        Args:
            input_text (str): The user input string.
            output_text (str): The resulting output string.
        """

        self.history.append((input_text, self.output))
        self.message_states.append(self.messages.copy())

    def convert_agent_message(self, message):
        content = message["content"] if message["content"] else ""
        if message["role"] == "function":
            content = f"```\n{content}\n```"
        function_call = {}
        if "function_call" in message:
            function_call = message["function_call"]
        name = function_call.get("name", "")
        arguments = function_call.get("arguments", "")
        code = ""
        language = "python"
        if name in ("run_code", "python"):
            arguments_dict = parse_partial_json(arguments)
            if arguments_dict is not None:
                language = arguments_dict.get("language", "python")
                if not language:
                    language = "python"
                code = arguments_dict.get("code", "")
        else:
            language = "json"
            code = arguments
        output = f"{content}\n"
        if len(code) > 0:
            output += f"```{language}\n{code}\n```"
        return output

    async def agent_handler(self, request, interpreter):
        """
        Handle user input that is intended to be processed by the agent. The input will
        be sent to the agent, and the agent's response will be displayed.

        Args:
            request (str): The user input string to be processed by the agent.
            output_field (prompt_toolkit.widgets.text_area.TextArea): The output field.

        Returns:
            None
        """
        messages = self.messages + [{"role": "user", "content": request}]
        inputs = {"messages": messages, "verbose": True}
        with self.console.status("[blue]Thinking[/blue]", spinner="circleHalves"):
            if interpreter:
                messages = code_interpreter_agent.run(inputs)
            else:
                messages = open_creator_agent.run(inputs)
        output = "\n".join([self.convert_agent_message(message) for message in messages[len(self.messages):]])
        self.messages = messages
        self.output.append((output, "Markdown"))

    async def show_output(self, request, output, add_prompt_prefix=True, add_request=True, add_newline=True, grey=False, interpreter=False):
        new_text = ""
        if add_prompt_prefix:
            prefix = prompt_prefix
            if interpreter:
                prefix = interpreter_prefix
            if grey:
                new_text += prefix.replace("green]", "grey62]")
            else:
                new_text += prefix
        if add_request:
            new_text += request
        if add_newline:
            new_text += "\n"
        new_text += output
        self.console.clear()
        self.output.append((new_text, "Text"))
        for text, style in self.output:
            if style == "Text":
                self.console.print(text, end="")
            elif style == "Markdown":
                self.console.print(Markdown(text), end="")
        self.console.print()
