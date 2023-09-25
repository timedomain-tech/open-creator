from .base import BaseInterpreter
import re


class JuliaInterpreter(BaseInterpreter):
    name: str = "julia_interpreter"
    description: str = "A julia interpreter"
    start_command: str = "julia -i -q"
    print_command: str = 'println("{}")'

    def __init__(self):
        self.bash_interpreter = None
    
    def postprocess(self, response):
        def clean_string(s):
            return '\n'.join([line for line in s.split('\n') if not re.match(r'^(julia>\s*|\s*\.\.\.\s*)', line)])
        
        # clean up stdout and stderr
        response['stdout'] = clean_string(response.get('stdout', ''))
        response['stderr'] = clean_string(response.get('stderr', ''))
        
        return response


if __name__ == "__main__":
    inter = JuliaInterpreter()
    res = inter.run('println("hello world")')
    print(res)
