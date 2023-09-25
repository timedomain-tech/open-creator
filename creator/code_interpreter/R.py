from .base import BaseInterpreter
import re


class RInterpreter(BaseInterpreter):
    name: str = "r_interpreter"
    description: str = "An R interpreter"
    start_command: str = "R --quiet --no-save --no-restore-data"
    print_command: str = "cat('{}\n')"

    def postprocess(self, response):
        def clean_string(s):
            return '\n'.join([line for line in s.split('\n') if not re.match(r'^(\s*>\s*|\s*\.\.\.\s*)', line)])
        
        # clean up stdout and stderr
        response['stdout'] = clean_string(response.get('stdout', ''))
        response['stderr'] = clean_string(response.get('stderr', ''))
        
        return response
