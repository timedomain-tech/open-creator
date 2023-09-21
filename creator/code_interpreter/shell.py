from base import BaseInterpreter
import os
import platform


class ShellInterpreter:
    
    def __init__(self):
        self.bash_interpreter = None

    def interpret(self, query):
        if self.bash_interpreter is None:
            self.bash_interpreter = BaseInterpreter()
            start_cmd = 'cmd.exe' if platform.system() == 'Windows' else os.environ.get('SHELL', 'bash'),
            resp = self.bash_interpreter.run(start_cmd)
            if resp["status"] != "success":
                return resp
        resp = self.bash_interpreter.run(query)
        return resp

