from .base import BaseInterpreter
import re


def clean_interactive_mode_lines(response):
    def clean_string(s):
        return '\n'.join([line for line in s.split('\n') if not re.match(r'^(julia>\s*|\s*\.\.\.\s*)', line)])
    
    # clean up stdout and stderr
    response['stdout'] = clean_string(response.get('stdout', ''))
    response['stderr'] = clean_string(response.get('stderr', ''))
    
    return response


class JuliaInterpreter:
    def __init__(self):
        self.bash_interpreter = None
    
    def run(self, query:str) -> dict:
        if self.bash_interpreter is None:
            self.bash_interpreter = BaseInterpreter()
            resp = self.bash_interpreter.run("julia -i -q")
            if resp["status"] != "success":
                return clean_interactive_mode_lines(resp)
        resp = self.bash_interpreter.run(query)
        return clean_interactive_mode_lines(resp)


if __name__ == "__main__":
    inter = JuliaInterpreter()
    res = inter.run('println("hello world")')
    print(res)
