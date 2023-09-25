from .base import BaseInterpreter
import re


class PythonInterpreter(BaseInterpreter):
    name: str = "python_interpreter"
    description: str = "A python interpreter"
    start_command: str = "python -i -q -u"
    print_command: str = "print('{}')"

    def preprocess(self, query: str):
        # Removes `, whitespace & python from start
        query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
        # Removes whitespace & ` from end
        query = re.sub(r"(\s|`)*$", "", query)
        query = "\n".join([line for line in query.split("\n") if line.strip() != ""])
        return query
    
    def postprocess(self, response):
        def clean_string(s):
            return '\n'.join([line for line in s.split('\n') if not re.match(r'^(\s*>>>\s*|\s*\.\.\.\s*)', line)])
        
        # clean up stdout and stderr
        response['stdout'] = clean_string(response.get('stdout', ''))
        response['stderr'] = clean_string(response.get('stderr', ''))
        return response    
