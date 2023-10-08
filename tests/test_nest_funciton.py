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

code = """
def function_with_multiple_nested_functions(x):
    
    def first_nested(y):
        return y + 5
    
    def second_nested(z):
        return z * 2
    
    return first_nested(x) + second_nested(x)

"""

print(flatten_functions(code))
