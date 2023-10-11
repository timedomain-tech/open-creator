from creator.agents.creator_agent import open_creator_agent
from creator.utils import truncate_output, is_valid_code
from .constants import help_commands, prompt_prefix
from prompt_toolkit.document import Document
import json


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

        if request.startswith("%"):
            self.meta_prompt_handler(request, output_field)
        elif is_valid_code(request, open_creator_agent.tools[0].namespace):
            self.expression_handler(request, output_field)
            self.update_history(request, output_field.text)
        else:
            # output = "<stderr>NOT IMPLEMENTED YET</stderr>"
            # self.show_output(request, output_field, output)
            self.agent_handler(request, output_field)
            self.update_history(request, output_field.text)

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
            self.show_output(request, output_field, output)

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
            self.show_output(request, output_field, output)

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

        self.show_output(request, output_field, output)

    def update_history(self, input_text, output_text):
        """
        Update the history of user inputs and outputs, preserving the state to enable undo functionality.

        Args:
            input_text (str): The user input string.
            output_text (str): The resulting output string.
        """

        self.history.append((input_text, output_text))
        self.message_states.append(self.messages.copy())

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

        self.messages.append({"role":"user", "content": request})
        messages = open_creator_agent.run(
            {
                "messages": self.messages,
                "verbose": True,
            }
        )
        self.messages = messages
        for delta, output in open_creator_agent.iter(messages):
            pre = output_field.text
            output_field.text = pre + delta
            self.show_output(request, output_field, output, add_prompt_prefix=False, add_request=False, add_newline=False)

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

