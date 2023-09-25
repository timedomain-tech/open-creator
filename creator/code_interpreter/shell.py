from .base import BaseInterpreter
import os
import platform


class ShellInterpreter(BaseInterpreter):
    name: str = "shell_interpreter"
    description: str = "A shell interpreter"
    start_command: str = 'cmd.exe' if platform.system() == 'Windows' else os.environ.get('SHELL', 'bash')
    print_command: str = "echo '{}'" if platform.system() == 'Windows' else "echo -e '{}'"
