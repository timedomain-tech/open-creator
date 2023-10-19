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


def is_code_with_assignment(code: str) -> bool:
    if "=" not in code:
        return False

    left, right = code.split("=", 1)
    return is_valid_variable_name(left.strip()) and is_compilable(right.strip(), "eval")


def is_compilable(code: str, mode: str) -> bool:
    try:
        compile(code, "", mode)
        return True
    except SyntaxError:
        return False


def is_valid_code(code: str, namespace: dict) -> bool:
    variables = extract_variable_names(code)
    if not all(is_valid_variable_name(variable) for variable in variables):
        return False

    return (is_compilable(code, "eval") or
            is_code_with_assignment(code) or
            is_compilable(code, "exec"))


def is_expression(code: str):
    return is_compilable(code, "eval")
