import json

from .constants import help_commands, prompt_prefix, prompt_message
from .style import style
from .lexer import parse_line

from creator.agents.creator_agent import open_creator_agent
from creator.utils import truncate_output, is_valid_code

from langchain.output_parsers.json import parse_partial_json

from prompt_toolkit.document import Document
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText


class RequestHandler:
    """This is a class that will be used to handle the request from the REPL."""
    def __init__(self):
        self.messages = []
        self.message_states = [self.messages]
        self.history = []

    def handle(self, request, output_field):
        """
        Handle the user request input, and dispatch to the appropriate handler based on
        the request type: meta-prompt command, expression, or agent.

        Args:
            request (str): The user input string.
            output_field (prompt_toolkit.widgets.text_area.TextArea): The output field to display results.

        Returns:
            str: The output text to be displayed in the output_field.
        """
        self.show_output(request, output_field, "")

        if request.startswith("%"):
            self.meta_prompt_handler(request, output_field)
        elif is_valid_code(request, open_creator_agent.tools[0].namespace):
            self.expression_handler(request, output_field)
            self.update_history(request, output_field.text)
        else:
            # output = "<stderr>NOT IMPLEMENTED YET</stderr>"
            # self.show_output(request, output_field, output, add_prompt_prefix=False, add_request=False, add_newline=False)
            self.agent_handler(request, output_field)
            self.update_history(request, output_field.text)

    def handle_exit(self, app, output):
        app.exit()
        tokens = parse_line(output)
        print_formatted_text(FormattedText(tokens), style=style)
        print_formatted_text(prompt_message, style=style)

    def meta_prompt_handler(self, request, output_field):
        """
        Handle meta-prompt commands that start with '%'. These commands control the
        REPL environment and provide functionalities like clear, reset, undo, and help.

        Args:
            request (str): The user input string.
            output_field (prompt_toolkit.widgets.text_area.TextArea): The output field.

        Returns:
            None
        """
        output = ""

        if request.startswith("%reset"):
            self.messages = []
            output = "<system>Conversation Message Reset!</system>"
            self.show_output(request, output_field, output, add_prompt_prefix=False, add_request=False, add_newline=False)

        if request.startswith("%clear"):
            self.history = []
            output_field.text = ""
            output = ""
            self.show_output(request, output_field, output, add_prompt_prefix=False, add_request=False, add_newline=False)

        if request.startswith("%undo"):
            if len(self.history) == 0 or len(self.message_states) == 0:
                output = "<stderr>Nothing to undo!</stderr>"
                output_field.text = ""
                self.show_output(request, output_field, output)
                return

            self.history.pop(-1)
            if len(self.history) > 0:
                _, output_field.text = self.history[-1]
            else:
                output_field.text = ""

            self.message_states.pop(-1)
            if len(self.message_states) > 0:
                self.messages = self.message_states[-1]
            else:
                self.messages = []
            output = ""
            self.show_output(request, output_field, output)

        if request.startswith("%help"):
            output = help_commands
            self.show_output(request, output_field, output, add_prompt_prefix=False, add_request=False, add_newline=False)

    def expression_handler(self, request, output_field):
        """
        Handle user input that is recognized as a Python expression. The expression will
        be executed, and the result (or any error message) will be displayed.

        Args:
            request (str): The user input string, identified as a Python expression.
            output_field (prompt_toolkit.widgets.text_area.TextArea): The output field.

        Returns:
            str: The result of the executed expression or error message to be displayed in the output_field.
        """

        tool_result = open_creator_agent.tools[0].run_with_return(request)
        truncate_tool_result = truncate_output(tool_result)
        outputs = [tool_result["stdout"], tool_result["stderr"]]
        output = "\n".join([o for o in outputs if o != ""])

        self.messages.append({"role":"user", "content": request})
        self.messages.append({"role":"function", "name": "user_executed_code_output","content": json.dumps(truncate_tool_result)})

        self.show_output(request, output_field, output, add_prompt_prefix=False, add_newline=False, add_request=False)

    def update_history(self, input_text, output_text):
        """
        Update the history of user inputs and outputs, preserving the state to enable undo functionality.

        Args:
            input_text (str): The user input string.
            output_text (str): The resulting output string.
        """

        self.history.append((input_text, output_text))
        self.message_states.append(self.messages.copy())

    def convert_agent_message(self, langchain_message):
        content = langchain_message.content if langchain_message.content else ""
        function_call = {}
        if langchain_message.additional_kwargs is not None:
            function_call = langchain_message.additional_kwargs.get('function_call', {})
        name = function_call.get("name", "")
        arguments = function_call.get("arguments", "")
        code = ""
        language = ""
        if name in ("run_code", "python"):
            arguments_dict = parse_partial_json(arguments)
            if arguments_dict is not None:
                language = arguments_dict.get("language", "python")
                code = arguments_dict.get("code", "")
        else:
            language = "json"
            code = arguments
        output = f"{content}\n"
        if len(code) > 0:
            output += f"```{language}\n{code}```"
        return output

    def agent_handler(self, request, output_field):
        """
        Handle user input that is intended to be processed by the agent. The input will
        be sent to the agent, and the agent's response will be displayed.

        Args:
            request (str): The user input string to be processed by the agent.
            output_field (prompt_toolkit.widgets.text_area.TextArea): The output field.

        Returns:
            None
        """
        inputs = {"messages": self.messages, "verbose": True}
        messages = open_creator_agent.run(inputs)
        self.messages += messages
        # last_cursor = len(output_field.text)
        # for stop, (agent_name, (delta_message, full_message)) in open_creator_agent.iter(inputs):
        #     print(agent_name, full_message)
        #     if delta_message is None and full_message is None:
        #         output = f"Runing {agent_name}\n"
        #         last_cursor = len(output_field.text) + len(output)
        #     else:
        #         output_field.text = output_field.text[:last_cursor]
        #         if not isinstance(full_message, list):
        #             output = self.convert_agent_message(full_message)
        #     if not stop:
        #         pass
        #         # self.show_output(request, output_field, output, add_prompt_prefix=False, add_request=False, add_newline=False)
        #     else:
        #         self.messages += full_message

    def show_output(self, request, output_field, output, add_prompt_prefix=True, add_request=True, add_newline=True):
        new_text = output_field.text
        if add_prompt_prefix:
            new_text += prompt_prefix
        if add_request:
            new_text += request
        if add_newline:
            new_text += "\n"
        new_text += output
        output_field.buffer.document = Document(text=new_text, cursor_position=len(new_text))
