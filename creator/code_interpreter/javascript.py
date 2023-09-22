from .base import BaseInterpreter
import re


def clean_interactive_mode_lines(response):
    def clean_string(s):
        new_lines = []
        for line in s.split('\n'):
            if "Welcome to Node.js" in line:
                continue
            if line in ["undefined", 'Type ".help" for more information.']:
                continue
            line = re.sub(r'^\s*(>\s*)+', '', line)
            new_lines.append(line)
        
        return "\n".join(new_lines)
    
    # clean up stdout and stderr
    response['stdout'] = clean_string(response.get('stdout', ''))
    response['stderr'] = clean_string(response.get('stderr', ''))
    
    return response


class JSInterpreter:
    def __init__(self):
        self.bash_interpreter = None
    
    def run(self, query:str) -> dict:
        if self.bash_interpreter is None:
            self.bash_interpreter = BaseInterpreter()
            resp = self.bash_interpreter.run("node -i")
            if resp["status"] != "success":
                return clean_interactive_mode_lines(resp)
        resp = self.bash_interpreter.run(query)
        return clean_interactive_mode_lines(resp)


if __name__ == "__main__":
    inter = JSInterpreter()
    res = inter.run("console.log('hello world')")
    print(res)
