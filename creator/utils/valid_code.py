import re
import ast


def is_valid_variable_name(name: str) -> bool:
    return re.match(r"^[a-zA-Z_]\w*$", name) is not None


def extract_variable_names(code: str) -> list:
    try:
        tree = ast.parse(code, mode="eval")
    except SyntaxError:
        return []
    
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def is_code_with_assignment(code: str, namespace: set) -> bool:
    if "=" not in code:
        return False
    
    left, right = code.split("=", 1)
    
    if not is_valid_variable_name(left.strip()):
        return False
    
    try:
        compile(right.strip(), "", "eval")
    except SyntaxError:
        return False


def is_valid_code(code: str, namespace: dict) -> bool:

    if is_expression(code):
        return is_code_with_assignment(code, namespace)
    return is_executable(code)


def is_expression(code: str) -> bool:
    try:
        compile(code, "", "eval")
        return True
    except SyntaxError:
        return False


def is_executable(code: str) -> bool:
    try:
        compile(code, "", "exec")
        return True
    except SyntaxError:
        return False