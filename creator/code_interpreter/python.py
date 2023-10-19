from .base import BaseInterpreter
import re
import ast


class FunctionFlattener(ast.NodeTransformer):
    def __init__(self):
        self.functions_to_add = []

    def visit_FunctionDef(self, node):
        new_node = self.generic_visit(node)  # Visit child nodes

        # Check if this function contains nested functions
        nested_functions = [n for n in new_node.body if isinstance(n, ast.FunctionDef)]

        # If it does, move them to the top level and update the function body
        if nested_functions:
            new_node.body = [n for n in new_node.body if not isinstance(n, ast.FunctionDef)]
            self.functions_to_add.extend(nested_functions)

        return new_node


def flatten_functions(code):
    # Parse the code to an AST
    tree = ast.parse(code)

    # Flatten the nested functions
    flattener = FunctionFlattener()
    new_tree = flattener.visit(tree)

    # Add the flattened functions back to the top level
    new_tree.body.extend(flattener.functions_to_add)

    # Convert the modified AST back to code
    return ast.unparse(new_tree)


class PythonInterpreter(BaseInterpreter):
    name: str = "python_interpreter"
    description: str = "A python interpreter"
    start_command: str = "python -i -q -u"
    print_command: str = "print('{}')"

    def preprocess(self, query: str):
        query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
        query = re.sub(r"(\s|`)*$", "", query)
        query = "\n".join([line for line in query.split("\n") if line.strip() != ""])

        query = flatten_functions(query)
        # Parse the query into an abstract syntax tree
        tree = ast.parse(query)

        # # Unparse the tree into code, adding an extra newline after function and class definitions
        modified_code_lines = []
        for node in tree.body:
            code_chunk = ast.unparse(node)
            modified_code_lines.append(code_chunk)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.For, ast.AsyncFor, ast.While, ast.If)):
                # Add an extra newline after function and class definitions, and loop/if statements
                modified_code_lines.append("\n")
            elif isinstance(node, ast.Return):
                modified_code_lines.append("\n")

        # # Join all code chunks into the final modified code
        modified_code = "\n".join(modified_code_lines)
        return modified_code

    def postprocess(self, response):
        def clean_string(s):
            return '\n'.join([line for line in s.split('\n') if not re.match(r'^(\s*>>>\s*|\s*\.\.\.\s*)', line)])

        # clean up stdout and stderr
        response['stdout'] = clean_string(response.get('stdout', ''))
        response['stderr'] = clean_string(response.get('stderr', ''))
        return response
