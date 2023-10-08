from .base import BaseInterpreter
import re
import ast


class PythonInterpreter(BaseInterpreter):
    name: str = "python_interpreter"
    description: str = "A python interpreter"
    start_command: str = "python -i -q -u"
    print_command: str = "print('{}')"

    def preprocess(self, query: str):
        # Parse the query into an abstract syntax tree
        tree = ast.parse(query)

        # Unparse the tree into code, adding an extra newline after function and class definitions
        modified_code_lines = []
        for node in tree.body:
            code_chunk = ast.unparse(node)
            modified_code_lines.append(code_chunk)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.For, ast.AsyncFor, ast.While, ast.If)):
                # Add an extra newline after function and class definitions, and loop/if statements
                modified_code_lines.append("")

        # Join all code chunks into the final modified code
        modified_code = "\n".join(modified_code_lines)

        return modified_code
    
    def postprocess(self, response):
        def clean_string(s):
            return '\n'.join([line for line in s.split('\n') if not re.match(r'^(\s*>>>\s*|\s*\.\.\.\s*)', line)])
        
        # clean up stdout and stderr
        response['stdout'] = clean_string(response.get('stdout', ''))
        response['stderr'] = clean_string(response.get('stderr', ''))
        return response    