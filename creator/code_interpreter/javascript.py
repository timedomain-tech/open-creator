from .base import BaseInterpreter
import re


class JSInterpreter(BaseInterpreter):
    name: str = "js_interpreter"
    description: str = "A javascript interpreter"
    start_command: str = "node -i"
    print_command: str = "console.log('{}')"

    def __init__(self):
        self.bash_interpreter = None
    
    def postprocess(self, response):
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
