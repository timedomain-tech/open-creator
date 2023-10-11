

def is_valid_code(code: str) -> bool:
    for mode in ["eval", "exec"]:
        try:
            compile(code, "", mode)
            return True
        except SyntaxError:
            pass
    return False


def is_expression(code: str) -> bool:
    try:
        compile(code, "", "eval")
        return True
    except SyntaxError:
        return False
