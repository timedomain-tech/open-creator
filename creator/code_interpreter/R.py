from base import BaseInterpreter
import re


def clean_interactive_mode_lines(response):
    def clean_string(s):
        return '\n'.join([line for line in s.split('\n') if not re.match(r'^(\s*>\s*|\s*\.\.\.\s*)', line)])
    
    # clean up stdout and stderr
    response['stdout'] = clean_string(response.get('stdout', ''))
    response['stderr'] = clean_string(response.get('stderr', ''))
    
    return response


class RInterpreter:
    def __init__(self):
        self.bash_interpreter = None
    
    def run(self, query:str) -> dict:
        if self.bash_interpreter is None:
            self.bash_interpreter = BaseInterpreter()
            resp = self.bash_interpreter.run("R -q --vanilla")
            if resp["status"] != "success":
                return clean_interactive_mode_lines(resp)
        resp = self.bash_interpreter.run(query)
        return clean_interactive_mode_lines(resp)


if __name__ == "__main__":
    inter = RInterpreter()
    res = inter.run("print('hello world')")
    print(res)
