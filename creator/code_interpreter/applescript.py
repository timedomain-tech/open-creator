
from .base import BaseInterpreter
import re


class AppleScriptInterpreter(BaseInterpreter):
    name: str = "applescript_interpreter"
    description: str = "An applescript interpreter"
    start_command: str = "osascript -i"
    print_command: str = 'log "{}"'

    def postprocess(self, response):
        def clean_string(s):
            return '\n'.join([line for line in s.split('\n') if not re.match(r'^(\s*>\s*|\s*\.\.\.\s*)', line)])
        
        # clean up stdout and stderr
        response['stdout'] = clean_string(response.get('stdout', ''))
        response['stderr'] = clean_string(response.get('stderr', ''))
        
        return response


if __name__ == "__main__":
    inter = AppleScriptInterpreter()
    res = inter.run('tell application "Finder" to get the name of every disk')
    print(res)
